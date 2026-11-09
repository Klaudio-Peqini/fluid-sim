"""Command-line interface and JSON parameter loading."""
import argparse,json,sys,itertools,subprocess,time,os
from pathlib import Path
from .config import CASES,DEFAULTS,normalize


def run_options(p):
    p.add_argument('--config',type=Path,help='JSON parameters; command-line options override values in the file')
    def option(name,**kw):p.add_argument('--'+name.replace('_','-'),dest=name,default=argparse.SUPPRESS,**kw)
    option('case',choices=CASES,help='Case or object; run `flow.py objects` for the physical meaning')
    p.add_argument('--object',dest='case',choices=CASES,default=argparse.SUPPRESS,help='Alias for --case')
    option('method',choices=['cfd','lbm']);option('backend',choices=['auto','numpy','numba'])
    option('threads',help='Positive integer or auto; restricted to allocated CPU cores')
    floats=['duration','re','length','height','diameter','angle','gap','mean_speed','cfl','lattice_speed',
            'seed','ramp','nu','wall_speed','acceleration','center_x','center_y','radius','rpm','thrust','torque',
            'payload_mass','vehicle_mass','domain_scale','epsilon','air_density','air_viscosity','max_dt','blade_step','position']
    for name in floats:option(name,type=float)
    p.add_argument('--chord',dest='diameter',type=float,default=argparse.SUPPRESS,help='Alias for reference diameter; use chord for airfoil Reynolds number')
    for name in ['ny','nx','frames','fps','render_jobs','rotor_count','elements']:option(name,type=int)
    option('grid',type=int,nargs=3,metavar=('NX','NY','NZ'),help='3-D rotor grid')
    option('naca',help='Four-digit NACA code as text, e.g. 0012 or 2412')
    option('polygon',help='CSV with x,y header and local-coordinate polygon vertices')
    option('advection',choices=['upwind','central'])
    option('gif',nargs='*',choices=['all','velocity','pressure','vorticity'],help='GIF fields; --gif alone means all')
    p.add_argument('--no-gif',dest='gif',action='store_const',const=[],default=argparse.SUPPRESS)
    option('velocity_style',choices=['vectors','streamlines','both'])
    option('plane',choices=['xy','xz','yz'],help='3-D rotor visualization plane')
    option('output',help='Result folder; default creates a unique name')
    option('overwrite',action='store_true',help='Replace only a marked result folder created by this program')


def read_values(a,argv):
    values={}
    if getattr(a,'config',None):
        values=json.loads(a.config.read_text())
        if 'parameters' in values:values=values['parameters']
        if not isinstance(values,dict):raise ValueError('Configuration must be a JSON object.')
        if values.get('polygon'):
            path=Path(values['polygon'])
            if not path.is_absolute():values['polygon']=str((a.config.parent/path).resolve())
    explicit={k:v for k,v in vars(a).items() if k not in ['command','config']}
    if 'gif' in explicit and explicit['gif']==[]:
        last_gif=max([i for i,x in enumerate(argv) if x=='--gif'],default=-1)
        last_no=max([i for i,x in enumerate(argv) if x=='--no-gif'],default=-1)
        if last_gif>last_no:explicit['gif']=['all']
    values.update(explicit)
    return values


def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0]=='help':argv=argv[1:]+['--help']
    parser=argparse.ArgumentParser(description='Fluid flows: flexible 2-D teaching cases and 3-D prescribed-load rotors.',allow_abbrev=False)
    sub=parser.add_subparsers(dest='command')
    for name in ['run','plan']:
        p=sub.add_parser(name,help='Run a case' if name=='run' else 'Resolve settings, check geometry, and estimate memory',allow_abbrev=False)
        run_options(p)
    p=sub.add_parser('animate',help='Make GIFs from saved snapshots without re-running the flow')
    p.add_argument('folder',type=Path);p.add_argument('--fields',nargs='+',choices=['all','velocity','pressure','vorticity'],default=['all'])
    p.add_argument('--velocity-style',choices=['vectors','streamlines','both'],default='both')
    p.add_argument('--fps',type=int,default=12);p.add_argument('--jobs',type=int,default=1)
    p.add_argument('--plane',choices=['xy','xz','yz'],default='xz');p.add_argument('--position',type=float,default=0.)
    p.add_argument('--output',type=Path)
    p=sub.add_parser('sweep',help='Run independent parameter combinations concurrently')
    p.add_argument('--config',type=Path,required=True);p.add_argument('--jobs',default='auto');p.add_argument('--threads',type=int,default=1)
    p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('benchmark',help='Measure warmed-up NumPy / Numba timings and numerical parity')
    p.add_argument('--ny',type=int,default=64);p.add_argument('--steps',type=int,default=100)
    p.add_argument('--threads',nargs='+',type=int,default=[1,2]);p.add_argument('--output',type=Path,default=Path('benchmark.json'))
    sub.add_parser('hardware',help='Show usable cores, allocation and optional acceleration support')
    sub.add_parser('objects',help='List supported geometries and model dimensionality')
    if not argv:parser.print_help();return 0
    a=parser.parse_args(argv)
    try:
        from .runtime import hardware
        if a.command=='hardware':print(json.dumps(hardware(),indent=2));return 0
        if a.command=='objects':
            print('2-D: none (channel), rectangle, cylinder, ellipse, two_cylinders, airfoil (NACA), polygon (CSV).')
            print('1-D equations visualized in 2-D: couette, poiseuille.')
            print('3-D: rotor, one or four horizontal prescribed-load actuator-line rotors in initially still air.')
            print('Rotor thrust/torque are inputs; this is not moving solid-blade or finite-wing CFD.')
            return 0
        if a.command in ('run','plan'):
            values=read_values(a,argv)
            if a.command=='plan':
                c=normalize(values);h=hardware()
                from .runtime import configure
                backend,n,_=configure(c['backend'],c['threads'],c['ny'])
                if backend=='numpy' and c['case']!='rotor':n=1
                c.update(backend=backend,threads=n)
                if c['case']=='rotor':
                    from .runner import rotor_specs
                    from .rotor3d.grid import Grid
                    from .rotor3d.rotor import Rotor
                    bounds,specs=rotor_specs(c);g=Grid(c['grid'],bounds)
                    for r in specs:
                        rotor=Rotor(g,**r)
                        if rotor.omega*rotor.R/343>.3:raise ValueError('Rotor tip Mach exceeds .3.')
                    cells=g.shape[0]*g.shape[1]*g.shape[2]
                elif c['case'] in ('couette','poiseuille'):cells=c['ny']*max(16,int(c['length']/c['height']*c['ny']))
                else:
                    from .objects import build_geometry
                    g=build_geometry(c);cells=g['nx']*g['ny']
                if c['payload_mass'] is not None:c['thrust']=None
                print(json.dumps({'parameters':c,'hardware':h,'estimated_array_memory_MiB':cells*(32*8+c['frames']*4*4)/2**20,
                                  'memory_note':'Rough array estimate; sparse LU factors, JIT and render workers add memory.'},indent=2));return 0
            from .runner import run
            run(values);return 0
        if a.command=='animate':
            if not 1<=a.fps<=60 or not 1<=a.jobs<=hardware()['usable_cpus']:raise ValueError('fps=1..60; jobs must fit allocated cores.')
            fields=['velocity','pressure','vorticity'] if 'all' in a.fields else a.fields
            from .render import render_all
            for p in render_all(a.folder,fields,a.velocity_style,a.fps,a.jobs,a.plane,a.position,a.output):print(p)
            return 0
        if a.command=='sweep':sweep(a);return 0
        if a.command=='benchmark':
            from .benchmark import benchmark
            print(json.dumps(benchmark(a.ny,a.steps,a.threads,a.output),indent=2));return 0
    except (ValueError,KeyError,FileNotFoundError,TypeError,json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


def sweep(a):
    from .runtime import hardware
    spec=json.loads(a.config.read_text());base=spec.get('base',{});vary=spec.get('vary',{})
    if not isinstance(base,dict) or not isinstance(vary,dict) or any(not isinstance(v,list) or not v for v in vary.values()):raise ValueError('Sweep JSON needs base object and nonempty vary lists.')
    cases=[{**base,**dict(zip(vary,combo))} for combo in itertools.product(*vary.values())]
    if not 1<=len(cases)<=256:raise ValueError('Sweep must contain 1..256 cases.')
    available=hardware()['usable_cpus'];jobs=min(4,available,len(cases)) if a.jobs=='auto' else int(a.jobs)
    if min(jobs,a.threads)<1 or jobs*a.threads>available:raise ValueError('jobs * threads must fit allocated CPU cores.')
    if a.output.exists() and any(a.output.iterdir()):raise ValueError('Sweep output must be new or empty.')
    for c in cases:normalize(c)
    a.output.mkdir(parents=True,exist_ok=True);queue=[]
    for i,c in enumerate(cases):
        if c.get('polygon') and not Path(c['polygon']).is_absolute():c['polygon']=str((a.config.parent/c['polygon']).resolve())
        c.update(output=str((a.output/f'case_{i:03d}').resolve()),threads=a.threads,overwrite=False,render_jobs=1)
        config=a.output/f'case_{i:03d}.json';config.write_text(json.dumps(c,indent=2)+'\n');queue.append((i,config))
    start=time.perf_counter();active={};finished=[]
    launcher=Path(__file__).resolve().parents[1]/'flow.py'
    try:
        while queue or active:
            while queue and len(active)<jobs:
                i,config=queue.pop(0);log=(a.output/f'case_{i:03d}.log').open('w')
                process=subprocess.Popen([sys.executable,str(launcher),'run','--config',str(config.resolve())],stdout=log,stderr=subprocess.STDOUT)
                active[i]=(process,log)
            for i,(process,log) in list(active.items()):
                status=process.poll()
                if status is not None:
                    log.close();finished.append(dict(case=i,exit_code=status));del active[i]
            if active:time.sleep(.05)
    finally:
        for process,log in active.values():process.terminate();process.wait();log.close()
    report=dict(status='PASS' if all(x['exit_code']==0 for x in finished) else 'FAIL',jobs=jobs,threads_per_job=a.threads,
                wall_seconds=time.perf_counter()-start,runs=sorted(finished,key=lambda x:x['case']))
    (a.output/'sweep_summary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if report['status']!='PASS':raise ValueError('Some sweep jobs failed; inspect their logs.')
