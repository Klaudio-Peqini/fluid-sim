"""Optional compiled CPU-parallel kernels; float64, no fastmath.

The NumPy implementations remain the reference. Pressure LU for 2-D CFD is
serial; only the independent momentum cells are threaded in that solver.
"""
import numpy as np
from numba import njit, prange, set_num_threads
from .lbm import LatticeFlow, C, W, OPP
from .conventional import ProjectionFlow


@njit(parallel=True,cache=True)
def collide(f,solid,tau,post):
    ny,nx=solid.shape;bad=0
    for j in prange(ny):
        for i in range(nx):
            rho=0.;ux=0.;vy=0.
            for q in range(9):
                value=f[q,j,i];rho+=value;ux+=C[q,0]*value;vy+=C[q,1]*value
            if rho<=0:bad+=1
            if solid[j,i]:ux=0.;vy=0.
            else:ux/=rho;vy/=rho
            for q in range(9):
                cu=C[q,0]*ux+C[q,1]*vy
                eq=W[q]*rho*(1+3*cu+4.5*cu*cu-1.5*(ux*ux+vy*vy))
                post[q,j,i]=f[q,j,i]-(f[q,j,i]-eq)/tau
    return bad


@njit(parallel=True,cache=True)
def stream(post,solid,out):
    ny,nx=solid.shape
    for j in prange(ny):
        for i in range(nx):
            for q in range(9):
                sj=(j-C[q,1])%ny;si=(i-C[q,0])%nx
                if solid[j,i]:out[q,j,i]=W[q]
                elif solid[sj,si]:out[q,j,i]=post[OPP[q],j,i]
                else:out[q,j,i]=post[q,sj,si]


@njit(parallel=True,cache=True)
def reservoirs(f,inlet,fraction):
    ny,nx=f.shape[1:]
    for j in prange(1,ny-1):
        rin=0.;rout=0.;ux=0.;vy=0.
        for q in range(9):
            rin+=f[q,j,1];rout+=f[q,j,nx-2]
            ux+=C[q,0]*f[q,j,nx-2];vy+=C[q,1]*f[q,j,nx-2]
        ux/=rout;vy/=rout;ui=inlet[j-1]*(.5-.5*np.cos(np.pi*fraction))
        for q in range(9):
            cu=C[q,0]*ui
            f[q,j,0]=W[q]*rin*(1+3*cu+4.5*cu*cu-1.5*ui*ui)
            cu=C[q,0]*ux+C[q,1]*vy
            f[q,j,nx-1]=W[q]*(1+3*cu+4.5*cu*cu-1.5*(ux*ux+vy*vy))


class FastLatticeFlow(LatticeFlow):
    def __init__(self,*args,threads=1,**kw):
        set_num_threads(threads);super().__init__(*args,**kw)
        self.post=np.empty_like(self.f);self.other=np.empty_like(self.f)
    def step(self):
        bad=collide(self.f,self.solid,self.tau,self.post)
        if bad:raise FloatingPointError('Nonpositive LBM density.')
        stream(self.post,self.solid,self.other)
        fraction=min((self.t+self.dt)/max(self.ramp_time,self.dt),1.)
        reservoirs(self.other,self.inlet,fraction)
        self.f,self.other=self.other,self.f;self.t+=self.dt
        if not np.isfinite(self.f).all():raise FloatingPointError('Nonfinite LBM population.')
        return self.dt


@njit(parallel=True,cache=True)
def predictor(u,v,um,vm,nu,dx,dy,dt,central):
    ny=u.shape[0];nx=v.shape[1]
    us=np.empty_like(u);vs=np.empty_like(v)
    for j in prange(ny):
        for i in range(nx+1):
            q=u[j,i];west=u[j,max(i-1,0)];east=u[j,min(i+1,nx)]
            south=u[max(j-1,0),i];north=u[min(j+1,ny-1),i]
            lap=(east-2*q+west)/dx**2+(north-2*q+south)/dy**2
            if j==0 or j==ny-1:lap-=2*q/dy**2
            if j>0 and not um[j-1,i]:lap-=q/dy**2
            if j<ny-1 and not um[j+1,i]:lap-=q/dy**2
            vu=0.
            if 0<i<nx:vu=.25*(v[j,i-1]+v[j+1,i-1]+v[j,i]+v[j+1,i])
            ax=(east-west)/(2*dx) if central else ((q-west)/dx if q>=0 else (east-q)/dx)
            ay=(north-south)/(2*dy) if central else ((q-south)/dy if vu>=0 else (north-q)/dy)
            us[j,i]=q+dt*(-q*ax-vu*ay+nu*lap) if um[j,i] else 0.
    for j in prange(ny+1):
        for i in range(nx):
            q=v[j,i];west=v[j,max(i-1,0)];east=v[j,min(i+1,nx-1)]
            south=v[max(j-1,0),i];north=v[min(j+1,ny),i]
            lap=(east-2*q+west)/dx**2+(north-2*q+south)/dy**2
            if i>0 and not vm[j,i-1]:lap-=q/dx**2
            if i<nx-1 and not vm[j,i+1]:lap-=q/dx**2
            uv=0.
            if 0<j<ny:uv=.25*(u[j-1,i]+u[j-1,i+1]+u[j,i]+u[j,i+1])
            ax=(east-west)/(2*dx) if central else ((q-west)/dx if uv>=0 else (east-q)/dx)
            ay=(north-south)/(2*dy) if central else ((q-south)/dy if q>=0 else (north-q)/dy)
            vs[j,i]=q+dt*(-uv*ax-q*ay+nu*lap) if vm[j,i] else 0.
    return us,vs


class FastProjectionFlow(ProjectionFlow):
    def __init__(self,*args,threads=1,**kw):
        set_num_threads(threads);super().__init__(*args,**kw)
    def step(self):
        g=self.g;dx,dy=g['dx'],g['dy'];u,v=self.u,self.v
        rate=np.max(abs(u))/dx+np.max(abs(v))/dy
        dt=min(self.cfl/max(rate,1e-12),.45/(self.nu*(1/dx**2+1/dy**2)))
        if self.advection=='central':dt=min(dt,.5*self.nu/max(np.max(u*u)+np.max(v*v),1e-12))
        us,vs=predictor(u,v,self.um,self.vm,self.nu,dx,dy,dt,self.advection=='central')
        us[:,0]=self.inlet;us[:,-1]=us[:,-2]
        div=(us[:,1:]-us[:,:-1])/dx+(vs[1:]-vs[:-1])/dy
        self.p[:]=0.;self.p[self.fluid]=self.solve(-div[self.fluid]/dt)
        us[:,1:-1]-=dt*(self.p[:,1:]-self.p[:,:-1])/dx
        us[:,-1]+=dt*2*self.p[:,-1]/dx
        vs[1:-1]-=dt*(self.p[1:]-self.p[:-1])/dy
        us[~self.um]=0.;vs[~self.vm]=0.
        self.u,self.v=us,vs;self.t+=dt
        if not np.isfinite(us).all() or not np.isfinite(vs).all():raise FloatingPointError('Nonfinite CFD velocity.')
        return dt
