"""Meaningful numerical checks, reproducible without a CFD framework."""
import json,time
from pathlib import Path
import numpy as np
from fluidlab import plate_fd,plate_lbm,channel_geometry,ProjectionFlow,LatticeFlow

def main():
    report={}; start=time.time()
    for kind in ['couette','poiseuille']:
        for name,fn in [('fd',plate_fd),('lbm',plate_lbm)]:
            r=fn(kind); error=float(r['error'])
            assert error<.005,(kind,name,error)
            report[f'{kind}_{name}_relative_error']=error
    # A real spatial refinement check for the LBM parabolic profile.
    errors=[float(plate_lbm('poiseuille',n=n,duration=12)['error']) for n in [16,32]]
    assert errors[1]<errors[0],errors
    report['poiseuille_lbm_refinement_errors_n16_n32']=errors
    for shape in ['none','rectangle','cylinder','ellipse','two_cylinders']:
        g=channel_geometry(nx=144,ny=24,diameter=.25,shape=shape,angle=20)
        c=ProjectionFlow(g,re=20); c.run(duration=.25)
        d=c.diagnostics(); assert d['divergence_max']<1e-9
        assert abs(d['flux_in']-d['flux_out'])<1e-9
        f=c.fields(); assert (f['u'][g['solid']]==0).all() and (f['v'][g['solid']]==0).all()
        report[f'{shape}_cfd']=d
        l=LatticeFlow(g,re=20); l.run(duration=.6,save_every=1000)
        d=l.diagnostics(); assert d['mach_max']<.3 and d['density_deviation_max']<.15
        report[f'{shape}_lbm']=d
    report['elapsed_seconds']=time.time()-start
    Path('results').mkdir(exist_ok=True)
    Path('results/validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2)); print('ALL CHECKS PASSED')

if __name__=='__main__': main()
