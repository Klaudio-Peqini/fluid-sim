"""Unified execution with conservation gates, saved snapshots and provenance."""
import json,csv,time,shutil,uuid
from pathlib import Path
from datetime import datetime
import numpy as np
from .config import normalize,DEFAULTS
from .runtime import configure


def output_directory(c):
    p=Path(c['output']) if c['output'] else Path('results')/(c['case']+'_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:5])
    if p.exists() and any(p.iterdir()):
        if not c['overwrite']:raise ValueError(f'{p} is not empty; choose --output NEW or pass --overwrite.')
        # Only a marked result directory created by this runner may be overwritten.
        if not (p/'.flow_result').is_file():raise ValueError('Refusing to overwrite an unmarked directory.')
        shutil.rmtree(p)
    p.mkdir(parents=True,exist_ok=True);(p/'.flow_result').write_text('Generated simulation results\n')
    return p


def json_file(path,data):Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def save_history(p,rows):
    with (p/'history.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)


def run(values):
    c=normalize(values);backend,threads,hw=configure(c['backend'],c['threads'],c['ny'])
    if backend=='numpy' and c['case']!='rotor':threads=1
    if c['render_jobs']>hw['usable_cpus']:raise ValueError('render_jobs exceeds allocated CPU cores.')
    c.update(backend=backend,threads=threads)
    parameters={k:c[k] for k in DEFAULTS}
    parameters['backend']=values.get('backend','auto')
    parameters['threads']=values.get('threads','auto')
    if parameters['payload_mass'] is not None:parameters['thrust']=None
    parameters['overwrite']=False
    c['parameters']=parameters
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        if c['case']=='rotor':data,rows,extra=run_rotor(c)
        elif c['case'] in ('couette','poiseuille'):data,rows,extra=run_plate(c)
        else:data,rows,extra=run_channel(c)
    p=extra.pop('output');c.update(extra);json_file(p/'config.json',c)
    np.savez_compressed(p/'snapshots.npz',**data)
    arrays={k:data[k][-1] for k in ['u','v','p']}
    if 'w' in data:arrays['w']=data['w'][-1]
    arrays.update({k:data[k] for k in ['x','y','z','solid'] if k in data});arrays['time']=data['times'][-1]
    np.savez_compressed(p/'fields.npz',**arrays);save_history(p,rows)
    summary=dict(status='PASS',case=c['case'],backend=backend,threads=threads,hardware=hw,**extra,
                 physical_validation='Not experimentally validated; numerical checks are not aerodynamic validation.',final=rows[-1])
    if c['gif']:
        from .render import render_all
        render_all(p,c['gif'],c['velocity_style'],c['fps'],c['render_jobs'],c['plane'],c['position'])
    # A static overview is always produced, even with --no-gif.
    import matplotlib
    matplotlib.use('Agg')
    if data['u'].ndim==3:
        from .plotting import plot_flow
        import matplotlib.pyplot as plt
        x,y=data['x'],data['y'];g=dict(x=x,y=y,X=np.meshgrid(x,y)[0],Y=np.meshgrid(x,y)[1],
             dx=x[1]-x[0],dy=y[1]-y[0],solid=data['solid'],length=c['length'],height=c['height'])
        f=dict(u=data['u'][-1],v=data['v'][-1],p=data['p'][-1],time=float(data['times'][-1]),geometry=g)
        fig=plot_flow(f,c['case']+' | '+backend,save=p/'overview.png');plt.close(fig)
    else:
        from .render import static_rotor
        static_rotor(p,c['plane'],c['position'])
    json_file(p/'summary.json',summary)
    print('Completed:',p.resolve(),flush=True)
    return str(p)


def run_channel(c):
    from .objects import build_geometry
    from .conventional import ProjectionFlow
    from .lbm import LatticeFlow
    g=build_geometry(c)
    cls=ProjectionFlow if c['method']=='cfd' else LatticeFlow
    opts=dict(re=c['re'],mean_speed=c['mean_speed'],seed_perturbation=c['seed'])
    if c['method']=='cfd':opts.update(cfl=c['cfl'],advection=c['advection'])
    else:opts.update(lattice_speed=c['lattice_speed'],ramp_time=c['ramp'])
    if c['backend']=='numba':
        from .fast import FastProjectionFlow,FastLatticeFlow
        cls=FastProjectionFlow if c['method']=='cfd' else FastLatticeFlow;opts['threads']=c['threads']
    solver=cls(g,**opts);p=output_directory(c);json_file(p/'config.json',c)
    if 'outline' in g:np.savetxt(p/'object_outline.csv',g['outline'],delimiter=',',header='x,y',comments='')
    if c['case']=='polygon':
        shutil.copyfile(c['polygon'],p/'source_polygon.csv')
        c['parameters']['polygon']='source_polygon.csv'
    start=time.perf_counter();frames=[solver.fields()];rows=[];dtout=c['duration']/(c['frames']-1);next_save=dtout;steps=0
    maxima=dict(max_divergence=0.,max_mach=0.,max_density_deviation=0.,max_flux_imbalance=0.)
    while solver.t<c['duration']:
        dt=solver.step();steps+=1
        if solver.t>=next_save or solver.t>=c['duration'] or steps%50==0:
            d=solver.diagnostics();d['step']=steps
            if c['method']=='cfd':
                maxima['max_divergence']=max(maxima['max_divergence'],d['divergence_max'])
                imbalance=abs(d['flux_in']-d['flux_out'])
                maxima['max_flux_imbalance']=max(maxima['max_flux_imbalance'],imbalance)
                if d['divergence_max']*dt>1e-8 or imbalance>1e-8*max(c['mean_speed']*c['height'],1.):raise FloatingPointError('Projection conservation gate failed.')
            else:
                maxima['max_mach']=max(maxima['max_mach'],d['mach_max'])
                maxima['max_density_deviation']=max(maxima['max_density_deviation'],d['density_deviation_max'])
                if d['mach_max']>=.3 or d['density_deviation_max']>=.15:raise FloatingPointError('LBM Mach/density gate failed; refine grid or lower lattice speed/Re.')
            if solver.t>=next_save or solver.t>=c['duration']:
                frames.append(solver.fields());rows.append(d)
                print(f'{c["case"]}/{c["method"]}: t={solver.t:.4g}/{c["duration"]:g}',flush=True)
                while next_save<=solver.t:next_save+=dtout
    data={k:np.array([f[k] for f in frames],dtype=np.float32) for k in ['u','v','p']}
    data.update(times=np.array([f['time'] for f in frames]),x=g['x'],y=g['y'],solid=g['solid'])
    return data,rows,dict(output=p,steps=steps,solve_seconds=time.perf_counter()-start,**maxima,
          nx=g['nx'],length=g['length'],height=g['height'],kinematic_viscosity=solver.nu,
          pressure_units='p/rho0; reference density 1',initial_condition='CFD inlet profile / LBM still air with inlet ramp',
          parallel_scope='Numba parallel cell kernels; 2-D sparse pressure LU remains serial' if c['backend']=='numba' else 'NumPy reference backend')


def run_plate(c):
    from .conventional import plate_fd
    if c['method']!='cfd':raise ValueError('Unified plate evolution currently uses --method cfd; the legacy scripts also compare final LBM profiles.')
    start=time.perf_counter();n=c['ny'];H=c['height'];nu=c['nu'];duration=c['duration']
    result=plate_fd(c['case'],n=n,nu=nu,height=H,wall_speed=c['wall_speed'],acceleration=c['acceleration'],duration=duration,
                    sample_every=max(1,int(np.ceil(duration/(.45*(H/n)**2/nu)))//(c['frames']-1)))
    times=np.linspace(0,duration,c['frames']);profiles=np.column_stack([np.interp(times,result['times'],result['profiles'][:,j]) for j in range(n+1)])
    if c['case']=='couette':profiles[:,-1]=c['wall_speed']
    # Nonzero pressure gradient exactly corresponds to the imposed acceleration.
    x=np.linspace(0,c['length'],max(16,int(round(c['length']/H*n))))
    u=np.broadcast_to(profiles[:,:,None],(len(times),n+1,len(x))).copy()
    v=np.zeros_like(u);pressure=np.zeros_like(u)
    if c['case']=='poiseuille':pressure[:]=c['acceleration']*(c['length']-x)[None,None,:]
    data=dict(times=times,x=x,y=result['y'],u=u.astype('float32'),v=v.astype('float32'),p=pressure.astype('float32'),solid=np.zeros(u.shape[1:],bool))
    rows=[dict(time=float(t),relative_final_steady_error=float(result['error'])) for t in times]
    p=output_directory(c);np.savez_compressed(p/'plate_profiles.npz',**result)
    return data,rows,dict(output=p,solve_seconds=time.perf_counter()-start,
       scope='1-D fully developed plate equation, shown uniformly in x; no inlet/outlet channel development',
       parallel_scope='Small 1-D plate solve remains serial; use parallel sweeps for multiple runs.',pressure_units='p/rho0',
       pressure_interpretation='Poiseuille p(x)=g*(L-x), constant in time under prescribed acceleration; Couette p=0.',
       relative_L2_error=float(result['error']))


def rotor_specs(c):
    R=c['radius'];n=c['rotor_count'];s=1.5*R
    centres=[[0,0,0]] if n==1 else [[-s,-s,0],[s,-s,0],[s,s,0],[-s,s,0]]
    scale=c['domain_scale'];extent=(4 if n==1 else 6)*R*scale
    bounds=[[-extent,extent],[-extent,extent],[-6*R*scale,4*R*scale]]
    h=max((b[1]-b[0])/k for b,k in zip(bounds,c['grid']))
    eps=c['epsilon'] if c['epsilon'] is not None else 1.75*h
    rotors=[dict(center=centre,radius=R,hub_radius=.2*R,blades=2,rpm=c['rpm'],thrust_N=c['thrust'],torque_Nm=c['torque'],
                 direction=1 if i%2==0 else -1,epsilon_m=eps,elements=c['elements'],ramp_s=c['ramp'],phase_deg=i*45)
            for i,centre in enumerate(centres)]
    return bounds,rotors


def run_rotor(c):
    from scipy.fft import set_workers
    from .rotor3d.grid import Grid,cell_velocity
    from .rotor3d.flow import Flow
    from .rotor3d.rotor import Rotor
    bounds,specs=rotor_specs(c);g=Grid(c['grid'],bounds)
    if c['rpm']*2*np.pi/60*c['radius']/343>.3:raise ValueError('Rotor tip Mach exceeds .3; incompressible model rejected.')
    f=Flow(g,nu=c['air_viscosity'],rho=c['air_density'],cfl=c['cfl']);rotors=[Rotor(g,**r) for r in specs]
    p=output_directory(c);c['rotors']=specs;json_file(p/'config.json',c)
    dtmax=min(c['max_dt'],np.deg2rad(c['blade_step'])/max(r.omega for r in rotors),.5*min(g.h)/max(r.omega*r.R for r in rotors))
    start=time.perf_counter();frames=[];rows=[];steps=0;next_save=0.;spacing=c['duration']/(c['frames']-1);maxdiv=0.;maxload=0.
    def record():
        frames.append(dict(time=f.time,**{k:q.astype('float32') for k,q in zip(['u','v','w'],cell_velocity(f.vel))},p=f.p.astype('float32')))
    record();next_save=spacing
    with set_workers(c['threads']):
        while f.time<c['duration']-1e-13:
            bound=min(dtmax,c['duration']-f.time);acc=g.faces()
            for r in rotors:
                force=r.acceleration(f.time+.5*bound,f.rho)
                for k in range(3):acc[k]+=force[k]
            dt=f.stable_dt(bound,acc)
            if dt<1e-12:raise FloatingPointError('Rotor time step collapsed.')
            if dt<bound*.999:
                acc=g.faces()
                for r in rotors:
                    force=r.acceleration(f.time+.5*dt,f.rho)
                    for k in range(3):acc[k]+=force[k]
            f.step(dt,acc);steps+=1;d=f.diagnostics();maxdiv=max(maxdiv,d['max_divergence_1_s'])
            for r in rotors:maxload=max(maxload,abs(r.last['requested_thrust_N']-r.last['applied_thrust_N']))
            if d['max_divergence_1_s']*dt>1e-8:raise FloatingPointError('Rotor projection gate failed.')
            if f.time>=next_save or f.time>=c['duration']-1e-13:
                record();row=dict(time=f.time,max_divergence=d['max_divergence_1_s'],step=steps,
                                 applied_thrust_N=sum(r.last['applied_thrust_N'] for r in rotors))
                w=cell_velocity(f.vel)[2]
                for i,r in enumerate(rotors):
                    for label,height in [('above',r.R),('plane',0),('below',-r.R)]:row[f'rotor{i}_{label}_w']=r.disk_mean(w,height)
                rows.append(row);print(f'rotor: t={f.time:.4g}/{c["duration"]:g}',flush=True)
                while next_save<=f.time:next_save+=spacing
    data={k:np.array([fr[k] for fr in frames]) for k in ['u','v','w','p']}
    data.update(times=np.array([fr['time'] for fr in frames]),**{key:g.axes[i] for i,key in enumerate('xyz')})
    return data,rows,dict(output=p,steps=steps,solve_seconds=time.perf_counter()-start,rotors=specs,
       max_divergence=maxdiv,max_thrust_absolute_error_N=maxload,pressure_units='Pa',
       scope='3-D prescribed-load rotating actuator lines in initially still air; no blade surfaces, turbulence closure, fuselage or ground.',
       parallel_scope='CPU-parallel 3-D pressure DST transforms; momentum and actuator deposition use NumPy.',
       rpm_interpretation='RPM rotates force lines; thrust and torque are independent prescribed inputs, not aerodynamic predictions.')
