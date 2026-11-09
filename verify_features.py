"""Verify parallel/reference equivalence, geometries, rotor forces and slice coordinates."""
from pathlib import Path
import json,tempfile,warnings
import numpy as np
from scipy.fft import set_workers
from fluidlab.runtime import hardware,configure
from fluidlab.objects import build_geometry,naca4_coordinates
from fluidlab.config import normalize
from fluidlab import ProjectionFlow,LatticeFlow
from fluidlab.rotor3d.grid import Grid,divergence
from fluidlab.rotor3d.flow import Flow
from fluidlab.rotor3d.rotor import Rotor


def checks():
    metrics={}
    for case in ['none','rectangle','cylinder','ellipse','two_cylinders','airfoil']:
        c=normalize(dict(case=case,ny=96 if case=='airfoil' else 32))
        g=build_geometry(c);assert (~g['solid']).any();metrics['geometry_'+case]=int(g['solid'].sum())
    symmetric=build_geometry(normalize(dict(case='airfoil',naca='0012',angle=0,ny=96)))
    assert np.array_equal(symmetric['solid'],symmetric['solid'][::-1])
    for values in [dict(case='airfoil',ny=16),dict(case='cylinder',diameter=2),dict(case='rotor',rpm=0),dict(frames=1)]:
        try:
            c=normalize(values)
            if c['case']!='rotor':build_geometry(c)
        except ValueError:pass
        else:raise AssertionError('Invalid input accepted: '+str(values))
    if hardware()['numba_available']:
        n=min(2,hardware()['usable_cpus']);configure('numba',n)
        from fluidlab.fast import FastProjectionFlow,FastLatticeFlow
        for name,plain,fast in [('cfd',ProjectionFlow,FastProjectionFlow),('lbm',LatticeFlow,FastLatticeFlow)]:
            for kind in ['none','cylinder','ellipse','airfoil']:
                g=build_geometry(normalize(dict(case=kind,ny=96 if kind=='airfoil' else 24)))
                for scheme in (['upwind','central'] if name=='cfd' else ['lbm']):
                    kw=dict(re=20.,seed_perturbation=.01)
                    if name=='cfd':kw['advection']=scheme
                    a=plain(g,**kw);b=fast(g,threads=n,**kw)
                    for _ in range(12):a.step();b.step()
                    error=max(float(abs(a.fields()[k]-b.fields()[k]).max()) for k in ['u','v','p'])
                    assert error<1e-8,(name,kind,scheme,error)
                    metrics[f'{name}_{kind}_{scheme}_parallel_error']=error
    else:metrics['numba_checks']='SKIPPED: optional dependency unavailable'
    g=Grid((24,24,32),[[-.4,.4],[-.4,.4],[-.6,.4]])
    f=Flow(g);rng=np.random.default_rng(13);vel=[rng.normal(size=q.shape) for q in f.vel]
    with set_workers(1):a=f.project([q.copy() for q in vel],.001)
    with set_workers(min(2,hardware()['usable_cpus'])):b=f.project([q.copy() for q in vel],.001)
    error=max(float(abs(x-y).max()) for x,y in zip(a,b))
    assert error<1e-10;assert abs(divergence(g,b)).max()<1e-9
    metrics['rotor_fft_worker_difference']=error
    for direction in [-1,1]:
        r=Rotor(g,epsilon_m=.06,direction=direction)
        force=r.acceleration(.1,f.rho)
        assert abs(r.last['applied_thrust_N']-.5)<1e-12
        assert abs(r.last['applied_torque_Nm']-direction*.008)<1e-12
        f0=Flow(g);f0.step(.0001,force)
        assert abs(divergence(g,f0.vel)).max()<1e-9
    metrics['rotor_force_torque_projection']='PASS'
    # Nontrivial linear fields test interpolation, velocity component selection and transposition.
    from fluidlab.render import load_plane
    x=np.linspace(-1,1,5);y=np.linspace(-1,1,6);z=np.linspace(-1,1,7)
    X,Y,Z=np.meshgrid(x,y,z,indexing='ij');u=X+2*Y+3*Z;v=4*X+5*Y+6*Z;w=7*X+8*Y+9*Z
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);(p/'config.json').write_text('{"rotors":[]}')
        np.savez_compressed(p/'snapshots.npz',x=x,y=y,z=z,times=[0,1],u=[u,u],v=[v,v],w=[w,w],p=[u,u])
        d=load_plane(p,'xz',.1)
        expected=(x[:,None]+.2+3*z[None,:]).T
        np.testing.assert_allclose(d['u'][0],expected,atol=1e-14)
        assert d['u'].shape==(2,7,5)
    metrics['rotor_slice_coordinates']='PASS'
    return metrics


if __name__=='__main__':
    result=dict(status='PASS',metrics=checks())
    out=Path('verification/features.json');out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
