"""Measured speedups, excluding JIT compilation and geometry/LU setup."""
from pathlib import Path
import json,time,statistics
import numpy as np
from .runtime import configure


def _benchmark(ny=64,steps=100,threads=(1,2),output=Path('benchmark.json')):
    if ny<16 or steps<1:raise ValueError('benchmark needs ny>=16 and steps>=1.')
    configure('numba',max(threads),ny)
    from .geometry import channel_geometry
    from .conventional import ProjectionFlow
    from .lbm import LatticeFlow
    from .fast import FastProjectionFlow,FastLatticeFlow
    g=channel_geometry(nx=6*ny,ny=ny,diameter=.25,shape='cylinder')
    report={'ny':ny,'nx':6*ny,'steps':steps,'timing_scope':'Median of 3 warmed-up complete step loops; excludes JIT compilation, geometry and pressure-factorization setup, and plotting.',
            'note':'Memory bandwidth and the serial 2-D pressure solve limit thread scaling. Results are hardware-specific.','methods':{}}
    for method,plain,fast in [('cfd',ProjectionFlow,FastProjectionFlow),('lbm',LatticeFlow,FastLatticeFlow)]:
        options=dict(re=20,seed_perturbation=.01)
        warm=fast(g,threads=1,**options);warm.step()
        measurements={};reference=None
        for label,cls,n in [('numpy',plain,1)]+[(f'numba_{n}',fast,n) for n in dict.fromkeys(threads)]:
            samples=[];fields=None
            for _ in range(3):
                f=cls(g,**options,**({'threads':n} if cls is fast else {}))
                start=time.perf_counter()
                for __ in range(steps):f.step()
                samples.append(time.perf_counter()-start);fields=f.fields()
            if reference is None:reference=fields
            error=max(float(abs(fields[k]-reference[k]).max()) for k in ['u','v','p'])
            if error>1e-8:raise AssertionError(f'Parallel backend mismatch: {method}, {error}')
            measurements[label]={'seconds':statistics.median(samples),'max_abs_field_difference':error,'threads':n}
        baseline=measurements['numpy']['seconds'];serial=measurements.get('numba_1',{}).get('seconds')
        for d in measurements.values():
            d['speedup_vs_numpy']=baseline/d['seconds']
            if serial is not None:d['speedup_vs_numba_1']=serial/d['seconds']
        report['methods'][method]=measurements
    Path(output).parent.mkdir(parents=True,exist_ok=True);Path(output).write_text(json.dumps(report,indent=2)+'\n')
    return report


def benchmark(ny=64,steps=100,threads=(1,2),output=Path('benchmark.json')):
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        return _benchmark(ny,steps,threads,output)
