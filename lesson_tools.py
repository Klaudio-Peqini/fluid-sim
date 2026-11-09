"""Mjete të përbashkëta për skriptet mësimore; nuk kërkohet Jupyter."""
import argparse
import csv
import json
import time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fluidlab import plate_fd, plate_lbm, channel_geometry, ProjectionFlow, LatticeFlow, plot_flow, animate_flow

ROOT = Path(__file__).resolve().parent


def write_csv(path, rows):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plate_lesson(kind, argv=None):
    parser = argparse.ArgumentParser(description=f'{kind}: diferenca të fundme dhe LBM kundrejt zgjidhjes analitike')
    parser.add_argument('--n', type=int, default=32, help='Numri i intervaleve FD / qelizave fluide LBM')
    parser.add_argument('--nu', type=float, default=.1)
    parser.add_argument('--duration', type=float, default=8.)
    parser.add_argument('--wall-speed', type=float, default=1.)
    parser.add_argument('--acceleration', type=float, default=.1)
    parser.add_argument('--gif', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--frames', type=int, default=100, help='Numri i kuadrove në animacion (2–300)')
    parser.add_argument('--output', type=Path, default=ROOT/'results'/kind)
    a = parser.parse_args(argv)
    if not 2 <= a.frames <= 300:
        parser.error('Numri i kuadrove --frames duhet të jetë midis 2 dhe 300.')
    if a.n < 8 or not np.isfinite([a.nu, a.duration, a.wall_speed, a.acceleration]).all() or a.nu <= 0 or a.duration <= 0:
        parser.error('Kërkohen n>=8, nu>0, duration>0 dhe parametra të fundëm.')
    drive = a.wall_speed if kind == 'couette' else a.acceleration
    if drive == 0:
        parser.error('Zgjidhni një shpejtësi/forcë jo zero për krahasimin relativ.')
    # LBM: u_LB = u * dt/dx. Shmangim një test me Mach të madh.
    scale = abs(a.wall_speed) if kind == 'couette' else abs(a.acceleration)/(8*a.nu)
    if scale * .1/(a.n*a.nu) * np.sqrt(3) >= .3:
        parser.error('Mach i profilit LBM do të ishte >=0.3. Rritni n ose ulni forcën/shpejtësinë.')
    opts = dict(n=a.n, nu=a.nu, duration=a.duration, wall_speed=a.wall_speed, acceleration=a.acceleration)
    # Ruajmë mjaft profile numerike për animacionin, jo thjesht profilin final.
    fd_steps=int(np.ceil(a.duration/(.45/(a.n*a.n*a.nu))))
    fd = plate_fd(kind, sample_every=max(1,fd_steps//(a.frames-1)) if a.gif else 100, **opts)
    lb = plate_lbm(kind, **opts)
    a.output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout='constrained')
    for k in np.unique(np.linspace(0, len(fd['times'])-1, 5, dtype=int)):
        axes[0].plot(fd['profiles'][k], fd['y'], label=f't={fd["times"][k]:.2f}')
    axes[0].plot(fd['exact'], fd['y'], 'k--', label='Gjendja e qëndrueshme analitike')
    axes[0].set_title('Zhvillimi në kohë — diferenca të fundme')
    axes[1].plot(fd['u'], fd['y'], 'o-', ms=3, label='Diferenca të fundme')
    axes[1].plot(lb['u'], lb['y'], 's', ms=3, label='LBM D2Q9')
    axes[1].plot(fd['exact'], fd['y'], 'k--', label='Analitike')
    axes[1].set_title('Profilet përfundimtare')
    for ax in axes:
        ax.set(xlabel='u', ylabel='y'); ax.legend(fontsize=8); ax.grid(alpha=.2)
    fig.suptitle(kind.capitalize())
    fig.savefig(a.output/'profiles.png', dpi=140); plt.close(fig)
    if a.gif:
        from fluidlab.plate_animation import animate_plate
        display_times,profiles=animate_plate(fd,kind,a.output/'velocity.gif',frames=a.frames,wall_speed=a.wall_speed)
        np.savez_compressed(a.output/'animation_profiles.npz',times=display_times,y=fd['y'],profiles=profiles)
    for method, result in [('fd', fd), ('lbm', lb)]:
        np.savez_compressed(a.output/f'{method}.npz', **result)
        write_csv(a.output/f'{method}_profile.csv', [dict(y=float(y),u=float(u),analytic_steady=float(ex))
                  for y,u,ex in zip(result['y'],result['u'],result['exact'])])
    metrics = dict(fd_relative_L2_error=float(fd['error']), lbm_relative_L2_error=float(lb['error']),
                   requested_time=a.duration, lbm_actual_time=lb['time'], lbm_tau=lb['tau'],
                   note='Gabimi kundrejt gjendjes së qëndrueshme përmban edhe efektin e kohës së fundme.')
    (a.output/'diagnostics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    print(json.dumps(metrics, indent=2)); print('Rezultatet:', a.output.resolve())


def flow_lesson(shape='cylinder', re=20., method='cfd', ny=40, duration=4.,
                angle=0., gap=.6, advection='upwind', gif=False, argv=None,
                reference_length=.25, geometry_builder=None, add_arguments=None):
    parser = argparse.ArgumentParser(description='Rrjedhje 2D në kanal; kodi i solver-it ndodhet në fluidlab/')
    parser.add_argument('--method', choices=['cfd','lbm'], default=method)
    parser.add_argument('--shape', choices=[shape] if geometry_builder else ['none','rectangle','cylinder','ellipse','two_cylinders'], default=shape)
    parser.add_argument('--re', type=float, default=re)
    parser.add_argument('--ny', type=int, default=ny)
    parser.add_argument('--diameter','--chord',dest='diameter',type=float,default=reference_length,
                        help='Gjatësia e referencës për Re; korda për profilin e krahut')
    parser.add_argument('--duration', type=float, default=duration, help='Koha e modelit; nuk është koha e pritjes në kompjuter')
    parser.add_argument('--angle', type=float, default=angle)
    parser.add_argument('--gap', type=float, default=gap)
    parser.add_argument('--advection', choices=['upwind','central'], default=advection)
    parser.add_argument('--lattice-speed', type=float, default=.035)
    parser.add_argument('--frames', type=int, default=50)
    parser.add_argument('--gif', action=argparse.BooleanOptionalAction, default=gif)
    parser.add_argument('--output', type=Path)
    if add_arguments is not None:add_arguments(parser)
    a=parser.parse_args(argv)
    vals=[a.re,a.diameter,a.duration,a.angle,a.gap,a.lattice_speed]
    if not np.isfinite(vals).all() or min(a.re,a.diameter,a.duration)<=0 or a.ny<16 or not 2<=a.frames<=300:
        parser.error('Parametra të fundëm e pozitivë; ny>=16; frames midis 2 dhe 300.')
    if a.re>=100 and a.ny<60:
        parser.error('Për shembullin Re>=100 përdorni --ny 60 ose më shumë.')
    if a.shape=='two_cylinders' and a.gap<=a.diameter:
        parser.error('--gap është largësia midis qendrave; duhet të jetë më e madhe se diametri.')
    out=a.output or ROOT/'results'/f'{a.method}_{a.shape}_re{a.re:g}'
    # Një dosje e re shmang mbishkrimin e rezultateve të eksperimentit të mëparshëm.
    if out.exists() and any(out.iterdir()):
        parser.error(f'Dosja {out} nuk është bosh. Përdorni --output me një emër të ri.')
    try:
        g=(geometry_builder(a) if geometry_builder else
           channel_geometry(nx=6*a.ny,ny=a.ny,shape=a.shape,diameter=a.diameter,angle=a.angle,gap=a.gap))
    except ValueError as exc:
        parser.error(str(exc))
    if a.shape!='none' and g['solid'].sum()<4:
        parser.error('Pengesa është shumë e vogël për këtë rrjetë. Rritni --ny.')
    kw=(dict(advection=a.advection,seed_perturbation=.01) if a.method=='cfd' else
        dict(lattice_speed=a.lattice_speed,seed_perturbation=.01,ramp_time=2. if a.re>=100 else .5))
    solver=(ProjectionFlow if a.method=='cfd' else LatticeFlow)(g,re=a.re,**kw)
    out.mkdir(parents=True,exist_ok=True)
    config=vars(a).copy();config['output']=str(out)
    config.update(length=6.,height=1.,mean_inlet_speed=1.,kinematic_viscosity=solver.nu,
                  seed_perturbation=.01,initial_condition='CFD: profile inlet; LBM: rest with inlet ramp',
                  output_sampling='Approximately uniform model times; actual times saved; last step may overshoot duration')
    config.update(g.get('metadata',{}))
    if 'outline' in g:
        np.savetxt(out/'airfoil_outline.csv',g['outline'],delimiter=',',header='x,y',comments='')
    # Matja v bëhet në një pikë të deklaruar prapa trupit, në qelizën më të afërt.
    probe_x=1.5+2*a.diameter;probe_y=.5+.25*a.diameter
    j=int(np.argmin(abs(g['y']-probe_y)));i=int(np.argmin(abs(g['x']-probe_x)))
    if g['solid'][j,i]:
        # Dy cilindrat mund të mbulojnë pikën e parë; zhvendosemi pas të dytit.
        i=int(np.argmin(abs(g['x']-(1.5+a.gap+2*a.diameter))))
    config.update(probe_x=float(g['x'][i]),probe_y=float(g['y'][j]))
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    frames=[];rows=[];next_save=a.duration/(a.frames-1);interval=next_save
    start=time.perf_counter();next_print=0.;steps=0
    # Gjendja fillestare ruhet në arrays, por diagnostikat maten pas projektimit të parë.
    frames.append(solver.fields())
    while solver.t<a.duration:
        solver.step();steps+=1
        if steps%50==0 or solver.t>=next_save or solver.t>=a.duration:
            d=solver.diagnostics()
            if a.method=='cfd':
                if d['divergence_max']>1e-8 or abs(d['flux_in']-d['flux_out'])>1e-8:
                    raise FloatingPointError('Kontrolli i inkompresibilitetit dështoi.')
            elif d['mach_max']>=.3 or d['density_deviation_max']>=.15:
                raise FloatingPointError('Mach/dendësia tejkalojnë kufirin mësimor. Ulni shpejtësinë ose rafinoni rrjetën.')
        if solver.t>=next_save or solver.t>=a.duration:
            f=solver.fields();frames.append(f)
            d.update(probe_v=float(f['v'][j,i]));rows.append(d)
            while next_save<=solver.t:next_save+=interval
        if solver.t>=next_print:
            print(f'{a.method.upper()} | Re={a.re:g} | t={solver.t:.3f}/{a.duration:g}',flush=True)
            next_print+=a.duration/10
    last=frames[-1]
    fig=plot_flow(last,f'{a.method.upper()} — {a.shape} — Re={a.re:g}',save=out/'fields.png');plt.close(fig)
    np.savez_compressed(out/'fields.npz',u=last['u'],v=last['v'],p=last['p'],
                        x=g['x'],y=g['y'],solid=g['solid'],time=last['time'])
    np.savez_compressed(out/'snapshots.npz',times=[f['time'] for f in frames],
                        u=np.array([f['u'] for f in frames],dtype='float32'),
                        v=np.array([f['v'] for f in frames],dtype='float32'),
                        p=np.array([f['p'] for f in frames],dtype='float32'),x=g['x'],y=g['y'],solid=g['solid'])
    write_csv(out/'history.csv',rows)
    fig,ax=plt.subplots(figsize=(8,3),layout='constrained')
    ax.plot([d['time'] for d in rows],[d['probe_v'] for d in rows])
    ax.set(xlabel='Koha t',ylabel='Shpejtësia tërthore v',title=f'Sonda: x={g["x"][i]:.3f}, y={g["y"][j]:.3f}')
    ax.grid(alpha=.2);fig.savefig(out/'probe.png',dpi=140);plt.close(fig)
    if a.gif:
        anim=animate_flow(frames,path=out/'vorticity.gif');plt.close(anim._fig)
    metrics=solver.diagnostics();metrics.update(steps=steps,wall_seconds=time.perf_counter()-start,
        status='completed',source='freshly computed',saved_frames=len(frames))
    (out/'diagnostics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps(metrics,indent=2));print('Rezultatet:',out.resolve())
    return out
