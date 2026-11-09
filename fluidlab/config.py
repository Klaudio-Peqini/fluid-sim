"""Shared flat JSON / command-line schema. Explicit CLI values override JSON."""
from pathlib import Path
import math
CASES=('couette','poiseuille','none','rectangle','cylinder','ellipse','two_cylinders','airfoil','polygon','rotor')
DEFAULTS=dict(case='cylinder',method='lbm',backend='auto',threads='auto',duration=2.,frames=40,
              re=20.,ny=48,nx=None,length=6.,height=1.,diameter=.25,angle=0.,gap=.6,naca='2412',
              center_x=None,center_y=None,polygon=None,mean_speed=1.,cfl=.35,advection='upwind',
              lattice_speed=.035,seed=.01,ramp=.5,nu=.1,wall_speed=1.,acceleration=.1,
              gif=[],velocity_style='both',fps=12,render_jobs=1,plane='xz',position=0.,output=None,
              overwrite=False,radius=.1,rpm=1800.,thrust=None,torque=.008,rotor_count=1,
              payload_mass=None,vehicle_mass=None,grid=[40,40,48],domain_scale=1.,epsilon=None,
              air_density=1.204,air_viscosity=1.5e-5,max_dt=.002,blade_step=6.,elements=10)
PRESETS={
 'airfoil':dict(ny=96,diameter=.8,re=50.,angle=6.,duration=4.,method='cfd'),
 'rotor':dict(duration=.2,ramp=.04,method='cfd'),
 'couette':dict(duration=8.,ny=32,method='cfd',backend='numpy',threads=1), 'poiseuille':dict(duration=8.,ny=32,method='cfd',backend='numpy',threads=1),
}


def normalize(values):
    unknown=set(values)-set(DEFAULTS)
    if unknown:raise ValueError('Unknown configuration keys: '+', '.join(sorted(unknown)))
    case=values.get('case','cylinder')
    if case not in CASES:raise ValueError('Unknown case. Use `python flow.py objects`.')
    c={**DEFAULTS,**PRESETS.get(case,{}),**values}
    if c['method'] not in ('cfd','lbm') or c['backend'] not in ('auto','numpy','numba'):
        raise ValueError('method is cfd/lbm; backend is auto/numpy/numba.')
    if c['advection'] not in ('upwind','central'):raise ValueError('advection must be upwind or central.')
    if c['velocity_style'] not in ('vectors','streamlines','both'):raise ValueError('velocity_style must be vectors, streamlines or both.')
    if c['plane'] not in ('xy','xz','yz'):raise ValueError('plane must be xy, xz or yz.')
    for key in ['duration','re','length','height','diameter','mean_speed','nu','radius','rpm','air_density','air_viscosity','max_dt','domain_scale']:
        c[key]=float(c[key])
        if not math.isfinite(c[key]) or c[key]<=0:raise ValueError(key+' must be positive and finite.')
    for key in ['angle','gap','seed','ramp','wall_speed','acceleration','torque','cfl','lattice_speed','position','blade_step']:
        c[key]=float(c[key])
        if not math.isfinite(c[key]):raise ValueError(key+' must be finite.')
    for key in ['ny','frames','fps','render_jobs','rotor_count','elements']:
        value=c[key]
        if isinstance(value,bool) or int(value)!=value:raise ValueError(key+' must be an integer.')
        c[key]=int(value)
    if c['nx'] is not None:
        if int(c['nx'])!=c['nx']:raise ValueError('nx must be an integer.')
        c['nx']=int(c['nx'])
    if not 8<=c['ny']<=4096 or not 2<=c['frames']<=300 or not 1<=c['fps']<=60 or c['render_jobs']<1:
        raise ValueError('Require ny=8..4096, frames=2..300, fps=1..60, render_jobs>=1.')
    if not 0<c['cfl']<=.5 or not 0<c['lattice_speed']<.1 or min(c['ramp'],c['torque'],c['seed'])<0:
        raise ValueError('Require 0<cfl<=0.5, 0<lattice_speed<0.1; ramp/torque/seed nonnegative.')
    if c['threads']!='auto' and (int(c['threads'])!=float(c['threads']) or int(c['threads'])<1):raise ValueError('threads must be auto or a positive integer.')
    fields=c['gif']
    if isinstance(fields,str):fields=fields.replace(',',' ').split()
    if 'all' in fields:fields=['velocity','pressure','vorticity']
    if any(f not in ['velocity','pressure','vorticity'] for f in fields):raise ValueError('GIF fields: velocity, pressure, vorticity, all.')
    c['gif']=list(dict.fromkeys(fields))
    if case=='polygon' and not c['polygon']:raise ValueError('polygon case requires --polygon vertices.csv.')
    if case in ('couette','poiseuille'):
        if c['backend']=='auto':c['backend']='numpy'
        if c['backend']=='numba':raise ValueError('The small 1-D plate solve is serial; choose numpy and use sweeps for independent runs.')
        if c['method']!='cfd':raise ValueError('Plate time histories use --method cfd; legacy plate lessons retain final LBM comparisons.')
        if (case=='couette' and c['wall_speed']==0) or (case=='poiseuille' and c['acceleration']==0):raise ValueError('Use a nonzero drive for the plate relative-error comparison.')
    if case=='rotor':
        if c['backend']=='auto':c['backend']='numpy'
        if c['backend']=='numba':raise ValueError('Rotor parallelism uses SciPy FFT; select --backend numpy or auto with --threads N.')
        if c['method']!='cfd':raise ValueError('The 3-D rotor uses the projection solver; select --method cfd.')
        if c['rotor_count'] not in (1,4):raise ValueError('This rotor layout supports 1 or 4 rotors.')
        if len(c['grid'])!=3 or any(int(n)!=n or n<16 for n in c['grid']):raise ValueError('grid needs three integers >=16.')
        c['grid']=[int(n) for n in c['grid']]
        if not 0<c['blade_step']<=15 or c['elements']<2:raise ValueError('Require blade_step in (0,15] and elements>=2.')
        if (c['payload_mass'] is None)!=(c['vehicle_mass'] is None):raise ValueError('Supply both payload_mass and vehicle_mass.')
        if c['payload_mass'] is not None:
            if c['thrust'] is not None:raise ValueError('Specify masses OR per-rotor thrust, not both.')
            if not math.isfinite(c['payload_mass']+c['vehicle_mass']) or c['payload_mass']<0 or c['vehicle_mass']<=0:
                raise ValueError('Payload must be >=0; aircraft+battery mass must be >0.')
            c['thrust']=(c['payload_mass']+c['vehicle_mass'])*9.80665/c['rotor_count']
        elif c['thrust'] is None:c['thrust']=.5
        if not math.isfinite(c['thrust']) or c['thrust']<=0:raise ValueError('Per-rotor thrust must be positive and finite.')
    return c
