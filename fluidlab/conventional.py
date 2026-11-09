"""Explicit upwind momentum update and a MAC pressure projection.

The obstacle is represented by stair-step fluid/solid cells. Normal flow across
solid faces is forbidden; tangential no-slip is approximated on this grid.
This is an educational first-order solver, not a precision force calculator.
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized

def plate_fd(kind='couette', n=40, nu=.1, height=1., wall_speed=1.,
             acceleration=.1, duration=8., sample_every=100):
    """1-D startup flow, with exact steady solution for validation."""
    y=np.linspace(0,height,n+1); dy=height/n
    u=np.zeros(n+1); times=[0.]; profiles=[u.copy()]
    dt=.45*dy**2/nu; steps=int(np.ceil(duration/dt)); dt=duration/steps
    if kind not in ('couette','poiseuille'): raise ValueError(kind)
    for k in range(steps):
        force=acceleration if kind=='poiseuille' else 0.
        u[1:-1]+=dt*(nu*(u[2:]-2*u[1:-1]+u[:-2])/dy**2+force)
        u[0]=0.; u[-1]=wall_speed if kind=='couette' else 0.
        if (k+1)%sample_every==0 or k==steps-1:
            times.append((k+1)*dt); profiles.append(u.copy())
    exact=wall_speed*y/height if kind=='couette' else acceleration*y*(height-y)/(2*nu)
    error=np.linalg.norm(u-exact)/np.linalg.norm(exact)
    return dict(y=y,u=u,exact=exact,times=np.array(times),profiles=np.array(profiles),error=error)

def _derivatives(q,dx,dy):
    # Edge padding gives an outlet zero-gradient approximation for prediction.
    z=np.pad(q,1,mode='edge')
    west=z[1:-1,:-2]; east=z[1:-1,2:]
    south=z[:-2,1:-1]; north=z[2:,1:-1]
    return (q-west)/dx,(east-q)/dx,(q-south)/dy,(north-q)/dy, \
           (east-2*q+west)/dx**2+(north-2*q+south)/dy**2

class ProjectionFlow:
    def __init__(self,geometry,re=20.,mean_speed=1.,cfl=.35,advection='upwind',seed_perturbation=0.):
        if re<=0 or mean_speed<=0: raise ValueError('Re and speed must be positive.')
        if advection not in ('upwind','central'): raise ValueError('Unknown advection scheme.')
        self.g=geometry; self.re=re; self.U=mean_speed; self.cfl=cfl; self.advection=advection
        self.nu=mean_speed*geometry['diameter']/re
        ny,nx=geometry['solid'].shape; self.fluid=~geometry['solid']
        self.u=np.zeros((ny,nx+1)); self.v=np.zeros((ny+1,nx)); self.p=np.zeros((ny,nx))
        self.um=np.zeros_like(self.u,bool); self.vm=np.zeros_like(self.v,bool)
        self.um[:,1:-1]=self.fluid[:,:-1]&self.fluid[:,1:]
        self.um[:,0]=self.fluid[:,0]; self.um[:,-1]=self.fluid[:,-1]
        self.vm[1:-1]=self.fluid[:-1]&self.fluid[1:]
        y=geometry['y']; H=geometry['height']
        self.inlet=6*mean_speed*(y/H)*(1-y/H)
        self.inlet*=mean_speed/self.inlet.mean()
        self.u[:]=self.inlet[:,None]; self.u[~self.um]=0
        if seed_perturbation:
            self.v[1:-1]=seed_perturbation*mean_speed*np.sin(2*np.pi*geometry['X'][:-1]/geometry['length'])*np.sin(np.pi*geometry['Y'][:-1]/geometry['height'])
            self.v[~self.vm]=0.
        self.t=0.; self.history=[]; self._make_poisson()

    def _make_poisson(self):
        # Pressure exists only in fluid cells. Missing solid neighbours impose
        # zero normal pressure correction; outlet pressure is fixed to zero.
        g=self.g; ny,nx=self.fluid.shape
        ids=-np.ones((ny,nx),int); ids[self.fluid]=np.arange(self.fluid.sum())
        rows=[]; cols=[]; data=[]
        for j,i in zip(*np.where(self.fluid)):
            k=ids[j,i]; diag=0.
            for dj,di,h in ((0,-1,g['dx']),(0,1,g['dx']),(-1,0,g['dy']),(1,0,g['dy'])):
                jj,ii=j+dj,i+di
                if 0<=jj<ny and 0<=ii<nx and self.fluid[jj,ii]:
                    diag+=1/h**2; rows.append(k); cols.append(ids[jj,ii]); data.append(-1/h**2)
            if i==nx-1: diag+=2/g['dx']**2
            rows.append(k); cols.append(k); data.append(diag)
        self.solve=factorized(coo_matrix((data,(rows,cols)),shape=(self.fluid.sum(),)*2).tocsc())

    def step(self):
        g=self.g; dx,dy=g['dx'],g['dy']; u,v=self.u,self.v
        rate=np.max(abs(u))/dx+np.max(abs(v))/dy
        dt=min(self.cfl/max(rate,1e-12), .45/(self.nu*(1/dx**2+1/dy**2)))
        if self.advection=='central':
            # Forward Euler with centred transport needs a viscosity-dependent
            # restriction too; use a conservative sufficient bound.
            dt=min(dt,.5*self.nu/max(np.max(u*u)+np.max(v*v),1e-12))
        # Interpolate the transverse velocity onto each component's own faces.
        vu=np.zeros_like(u); uv=np.zeros_like(v)
        vu[:,1:-1]=.25*(v[:-1,:-1]+v[1:,:-1]+v[:-1,1:]+v[1:,1:])
        uv[1:-1]=.25*(u[:-1,:-1]+u[:-1,1:]+u[1:,:-1]+u[1:,1:])
        a,b,c,d,lap=_derivatives(u,dx,dy)
        # Odd tangential ghost values enforce no-slip at the channel walls.
        lap[0]-=2*u[0]/dy**2; lap[-1]-=2*u[-1]/dy**2
        # Odd ghost values across tangential solid interfaces.
        lap[1:]-=u[1:]*(~self.um[:-1])/dy**2
        lap[:-1]-=u[:-1]*(~self.um[1:])/dy**2
        ax=np.where(u>=0,a,b) if self.advection=='upwind' else .5*(a+b)
        ay=np.where(vu>=0,c,d) if self.advection=='upwind' else .5*(c+d)
        us=u+dt*(-u*ax-vu*ay+self.nu*lap)
        a,b,c,d,lap=_derivatives(v,dx,dy)
        lap[:,1:]-=v[:,1:]*(~self.vm[:,:-1])/dx**2
        lap[:,:-1]-=v[:,:-1]*(~self.vm[:,1:])/dx**2
        ax=np.where(uv>=0,a,b) if self.advection=='upwind' else .5*(a+b)
        ay=np.where(v>=0,c,d) if self.advection=='upwind' else .5*(c+d)
        vs=v+dt*(-uv*ax-v*ay+self.nu*lap)
        us[~self.um]=0.; vs[~self.vm]=0.
        us[:,0]=self.inlet; us[:,-1]=us[:,-2]
        div=(us[:,1:]-us[:,:-1])/dx+(vs[1:]-vs[:-1])/dy
        self.p[:]=0.; self.p[self.fluid]=self.solve(-div[self.fluid]/dt)
        us[:,1:-1]-=dt*(self.p[:,1:]-self.p[:,:-1])/dx
        us[:,-1]+=dt*2*self.p[:,-1]/dx
        vs[1:-1]-=dt*(self.p[1:]-self.p[:-1])/dy
        us[~self.um]=0.; vs[~self.vm]=0.
        self.u,self.v=us,vs; self.t+=dt
        if not np.isfinite(us).all() or not np.isfinite(vs).all():
            raise FloatingPointError('Non-finite velocity; reduce CFL or refine the grid.')
        return dt

    def fields(self):
        u=.5*(self.u[:,1:]+self.u[:,:-1]); v=.5*(self.v[1:]+self.v[:-1])
        return dict(u=u,v=v,p=self.p.copy(),time=self.t,geometry=self.g)

    def diagnostics(self):
        g=self.g
        div=(self.u[:,1:]-self.u[:,:-1])/g['dx']+(self.v[1:]-self.v[:-1])/g['dy']
        return dict(time=self.t,divergence_max=float(abs(div[self.fluid]).max()),
                    flux_in=float(self.u[:,0].sum()*g['dy']),flux_out=float(self.u[:,-1].sum()*g['dy']))

    def run(self,duration=4.,save_every=50):
        frames=[]; k=0; target=self.t+duration
        while self.t<target:
            self.step(); k+=1
            if k%save_every==0:
                frames.append(self.fields()); self.history.append(self.diagnostics())
        frames.append(self.fields()); self.history.append(self.diagnostics())
        return frames
