"""D2Q9 BGK with link bounce-back; no fluid simulation framework."""
import numpy as np

# Rest, east, north, west, south, NE, NW, SW, SE.
C=np.array([[0,0],[1,0],[0,1],[-1,0],[0,-1],[1,1],[-1,1],[-1,-1],[1,-1]])
W=np.array([4/9]+[1/9]*4+[1/36]*4)
OPP=np.array([0,3,4,1,2,7,8,5,6])

def equilibrium(rho,u,v):
    cu=C[:,0,None,None]*u+C[:,1,None,None]*v
    return W[:,None,None]*rho*(1+3*cu+4.5*cu**2-1.5*(u*u+v*v))

def _stream_bounce(post,solid,rho,wall_speed=0.):
    out=np.empty_like(post)
    for q,(cx,cy) in enumerate(C):
        out[q]=np.roll(post[q],shift=(cy,cx),axis=(0,1))
        # An incoming population whose source is solid is reflected locally.
        source_solid=np.roll(solid,shift=(cy,cx),axis=(0,1))
        out[q,source_solid]=post[OPP[q],source_solid]
        if wall_speed and cy<0:
            j=-2  # Fluid node immediately below the moving top wall.
            out[q,j]+=6*W[q]*rho[j]*cx*wall_speed
    out[:,solid]=W[:,None]
    return out

def plate_lbm(kind='couette',n=32,nu=.1,height=1.,wall_speed=1.,
              acceleration=.1,duration=8.,nu_lattice=.1):
    """Periodic streamwise plates; Guo forcing for pressure-gradient equivalent.

    Wall positions are halfway between fluid nodes and solid nodes. Guo force
    includes the half-step correction in the macroscopic velocity.
    """
    if kind not in ('couette','poiseuille'): raise ValueError(kind)
    dx=height/n; dt=nu_lattice*dx**2/nu; tau=.5+3*nu_lattice
    shape=(n+2,8); solid=np.zeros(shape,bool); solid[[0,-1]]=True
    rho=np.ones(shape); u=np.zeros(shape); v=np.zeros(shape)
    f=equilibrium(rho,u,v)
    gx=acceleration*dt**2/dx if kind=='poiseuille' else 0.
    uw=wall_speed*dt/dx if kind=='couette' else 0.
    steps=int(np.ceil(duration/dt))
    for k in range(steps):
        rho=f.sum(axis=0)
        u=(np.einsum('q,qyx->yx',C[:,0],f)+.5*gx)/rho
        v=np.einsum('q,qyx->yx',C[:,1],f)/rho
        u[solid]=0.; v[solid]=0.
        eq=equilibrium(rho,u,v)
        cu=C[:,0,None,None]*u+C[:,1,None,None]*v
        forcing=W[:,None,None]*(1-.5/tau)*(3*(C[:,0,None,None]-u)+9*cu*C[:,0,None,None])*gx
        post=f-(f-eq)/tau+forcing
        f=_stream_bounce(post,solid,rho,uw)
    rho=f.sum(axis=0)
    u=((np.einsum('q,qyx->yx',C[:,0],f)+.5*gx)/rho)[1:-1].mean(axis=1)*dx/dt
    y=(np.arange(n)+.5)*dx
    exact=wall_speed*y/height if kind=='couette' else acceleration*y*(height-y)/(2*nu)
    return dict(y=y,u=u,exact=exact,error=np.linalg.norm(u-exact)/np.linalg.norm(exact),
                tau=tau,steps=steps,time=steps*dt)

class LatticeFlow:
    def __init__(self,geometry,re=20.,mean_speed=1.,lattice_speed=.035,
                 seed_perturbation=0.,ramp_time=.5):
        g=geometry; self.g=g; self.re=re; self.U=mean_speed; self.ulb=lattice_speed; self.ramp_time=ramp_time
        if re<=0 or mean_speed<=0 or not 0<lattice_speed<.1: raise ValueError('Invalid flow parameters.')
        self.dt=g['dx']*lattice_speed/mean_speed
        self.nu=mean_speed*g['diameter']/re
        self.nu_lb=self.nu*self.dt/g['dx']**2; self.tau=.5+3*self.nu_lb
        if self.tau<.505: raise ValueError('Relaxation too close to 0.5; increase resolution or reduce Re.')
        ny,nx=g['solid'].shape
        self.solid=np.zeros((ny+2,nx),bool); self.solid[[0,-1]]=True
        self.solid[1:-1]=g['solid']; self.fluid=~self.solid
        y=g['y']/g['height']; self.inlet=6*lattice_speed*y*(1-y)
        self.inlet*=lattice_speed/self.inlet.mean()
        rho=np.ones(self.solid.shape); u=np.zeros_like(rho); v=np.zeros_like(rho)
        # Start from rest and ramp the inlet; abrupt truncation at an obstacle
        # launches strong acoustic transients in a weakly compressible method.
        # A reproducible small disturbance seeds instability in symmetric cases.
        if seed_perturbation:
            v[1:-1]=seed_perturbation*lattice_speed*np.sin(2*np.pi*g['X']/g['length'])*np.sin(np.pi*g['Y']/g['height'])
        u[self.solid]=0.; v[self.solid]=0.
        self.f=equilibrium(rho,u,v); self.t=0.; self.history=[]

    def step(self):
        f=self.f; rho=f.sum(axis=0)
        u=np.einsum('q,qyx->yx',C[:,0],f)/rho
        v=np.einsum('q,qyx->yx',C[:,1],f)/rho
        u[self.solid]=0.; v[self.solid]=0.
        post=f-(f-equilibrium(rho,u,v))/self.tau
        f=_stream_bounce(post,self.solid,rho)
        # Equilibrium reservoir inlet: an intentionally simple first-order
        # boundary for teaching. Density is extrapolated from the next column.
        j=slice(1,-1)
        fraction=min((self.t+self.dt)/max(self.ramp_time,self.dt),1.)
        ux=self.inlet*(.5-.5*np.cos(np.pi*fraction))
        rin=f[:,j,1].sum(axis=0)
        f[:,j,0]=equilibrium(rin[:,None],ux[:,None],np.zeros((len(ux),1)))[:,:,0]
        # Fixed-density equilibrium reservoir at the outlet. Velocity is
        # extrapolated; a long downstream channel limits boundary influence.
        rout=f[:,j,-2].sum(axis=0)
        ux=np.einsum('q,qy->y',C[:,0],f[:,j,-2])/rout
        vy=np.einsum('q,qy->y',C[:,1],f[:,j,-2])/rout
        f[:,j,-1]=equilibrium(np.ones((len(ux),1)),ux[:,None],vy[:,None])[:,:,0]
        self.f=f; self.t+=self.dt
        if not np.isfinite(f).all() or rho[self.fluid].min()<=0:
            raise FloatingPointError('LBM instability: refine the grid, reduce speed/Re.')
        return self.dt

    def fields(self):
        rho=self.f.sum(axis=0)
        u=np.einsum('q,qyx->yx',C[:,0],self.f)/rho*self.g['dx']/self.dt
        v=np.einsum('q,qyx->yx',C[:,1],self.f)/rho*self.g['dx']/self.dt
        u[self.solid]=0.; v[self.solid]=0.
        # Pressure relative to outlet rho=1, physical density reference rho0=1.
        p=(rho-1)/3*(self.g['dx']/self.dt)**2
        return dict(u=u[1:-1],v=v[1:-1],p=p[1:-1],rho=rho[1:-1],time=self.t,geometry=self.g)

    def diagnostics(self):
        f=self.fields(); fluid=~self.g['solid']
        mach=np.sqrt(f['u']**2+f['v']**2)*self.dt/self.g['dx']*np.sqrt(3)
        return dict(time=self.t,tau=self.tau,mach_max=float(mach[fluid].max()),
                    density_deviation_max=float(abs(f['rho'][fluid]-1).max()),
                    flux_in=float(f['u'][:,0].sum()*self.g['dy']),
                    flux_out=float(f['u'][:,-1].sum()*self.g['dy']))

    def run(self,duration=4.,save_every=100):
        steps=int(np.ceil(duration/self.dt)); frames=[]
        for k in range(steps):
            self.step()
            if (k+1)%save_every==0:
                frames.append(self.fields()); self.history.append(self.diagnostics())
        frames.append(self.fields()); self.history.append(self.diagnostics())
        return frames
