"""Read-only GIF generation from saved snapshots, with fixed temporal colour scales."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation,PillowWriter


def load_plane(folder,plane='xz',position=0.):
    with np.load(Path(folder)/'snapshots.npz',allow_pickle=False) as z:d={k:z[k] for k in z.files}
    if d['u'].ndim==3:
        return dict(x=d['x'],y=d['y'],u=d['u'],v=d['v'],speed=np.hypot(d['u'],d['v']),p=d['p'],
                    mask=d['solid'],times=d['times'],labels=('x','y'),scope='2D',rotors=[])
    # Every 3-D slice interpolates at the requested physical plane.
    axes={'xy':(0,1,2),'xz':(0,2,1),'yz':(1,2,0)}
    a,b,fixed=axes[plane];coords=[d[k] for k in 'xyz'];q=coords[fixed]
    if not q[0]<=position<=q[-1]:raise ValueError('Slice position is outside saved cell centres.')
    k=int(np.clip(np.searchsorted(q,position)-1,0,len(q)-2));f=(position-q[k])/(q[k+1]-q[k])
    def cut(v):return (1-f)*np.take(v,k,axis=fixed+1)+f*np.take(v,k+1,axis=fixed+1)
    vel=[cut(d[k]).swapaxes(1,2) for k in ['u','v','w']]
    config=json.loads((Path(folder)/'config.json').read_text())
    return dict(x=coords[a],y=coords[b],u=vel[a],v=vel[b],speed=np.sqrt(sum(v*v for v in vel)),
                p=cut(d['p']).swapaxes(1,2),mask=np.zeros(vel[0].shape[1:],bool),times=d['times'],
                labels=('xyz'[a],'xyz'[b]),scope=f'3D {plane} slice at {"xyz"[fixed]}={position:g}',
                rotors=config.get('rotors',[]),plane=plane,position=position)


def render_one(folder,field='vorticity',style='vectors',fps=12,plane='xz',position=0.,out=None):
    d=load_plane(folder,plane,position);x,y=d['x'],d['y'];mask=d['mask']
    if field=='vorticity':
        values=np.gradient(d['v'],x,axis=2)-np.gradient(d['u'],y,axis=1)
        label='ωz' if d['scope']=='2D' else 'In-plane curl component (not |ω|)'
        lim=max(float(np.percentile(abs(values[:,~mask]),98)),1e-10);lo,hi=-lim,lim;cmap='RdBu_r'
    elif field=='pressure':
        values=d['p'];label='Pressure relative to outlet/open boundaries';cmap='coolwarm'
        lo=float(values[:,~mask].min());hi=float(values[:,~mask].max())
    else:
        values=d['speed'];label='Speed |u| (magnitude of 3-D velocity for rotor slices)';cmap='viridis'
        lo=0.;hi=float(values[:,~mask].max())
    if hi<=lo:hi=lo+1e-9
    folder=Path(folder);out=Path(out) if out else folder/'animations';out.mkdir(parents=True,exist_ok=True)
    suffix=('_'+style) if field=='velocity' else ''
    name=field+suffix+('' if d['scope']=='2D' else '_'+plane+f'_{position:g}')
    fig,ax=plt.subplots(figsize=(9,4 if d['scope']!='2D' else 3),layout='constrained')
    im=ax.pcolormesh(x,y,np.ma.masked_where(mask,values[0]),
                     cmap=cmap,vmin=lo,vmax=hi,shading='nearest')
    fig.colorbar(im,ax=ax,label=label);ax.set(xlabel=d['labels'][0],ylabel=d['labels'][1],aspect='equal')
    if mask.any():ax.contourf(x,y,mask.astype(float),levels=[.5,1.5],colors=['#29313d'])
    for r in d['rotors']:
        centre=r['center'];radius=r['radius']
        if plane=='xy':
            theta=np.linspace(0,2*np.pi,100)
            ax.plot(centre[0]+radius*np.cos(theta),centre[1]+radius*np.sin(theta),'k--',lw=.8)
        else:
            cross=1 if plane=='xz' else 0;horizontal=0 if plane=='xz' else 1
            offset=abs(centre[cross]-position)
            if offset<=radius:
                reach=np.sqrt(radius**2-offset**2)
                ax.plot([centre[horizontal]-reach,centre[horizontal]+reach],[centre[2],centre[2]],'k--',lw=1)
    arrows=None;stream=None;step=max(1,len(x)//22)
    if field=='velocity' and style=='vectors':
        X,Y=np.meshgrid(x[::step],y[::step])
        scale=max(float(np.hypot(d['u'],d['v']).max()),1e-9)*15
        arrows=ax.quiver(X,Y,np.ma.masked_where(mask,d['u'][0])[::step,::step],
                         np.ma.masked_where(mask,d['v'][0])[::step,::step],color='white',scale=scale)
    title=ax.set_title('')
    def update(k):
        nonlocal stream
        im.set_array(np.ma.masked_where(mask,values[k]))
        if arrows is not None:
            arrows.set_UVC(np.ma.masked_where(mask,d['u'][k])[::step,::step],np.ma.masked_where(mask,d['v'][k])[::step,::step])
        if field=='velocity' and style=='streamlines':
            if stream is not None:
                stream.lines.remove()
                for patch in list(ax.patches):patch.remove()
            u=np.ma.masked_where(mask,d['u'][k]);v=np.ma.masked_where(mask,d['v'][k])
            # streamplot needs a nonzero field; still-air frames legitimately show no lines.
            if np.hypot(u.filled(0),v.filled(0)).max()>1e-12:
                stream=ax.streamplot(x,y,u,v,color='white',density=.8,linewidth=.7,arrowsize=.7)
            else:stream=None
        title.set_text(f'{field.capitalize()} | t={d["times"][k]:.4g} | {d["scope"]}')
        return im,title
    anim=FuncAnimation(fig,update,frames=len(d['times']),interval=1000/fps,blit=False)
    path=out/(name+'.gif');anim.save(path,writer=PillowWriter(fps=fps))
    update(len(d['times'])-1);fig.savefig(out/(name+'.png'),dpi=130);plt.close(fig)
    return str(path)


def render_all(folder,fields=('velocity','pressure','vorticity'),style='both',fps=12,jobs=1,plane='xz',position=0.,out=None):
    tasks=[]
    for field in dict.fromkeys(fields):
        for form in (['vectors','streamlines'] if field=='velocity' and style=='both' else [style if field=='velocity' else 'vectors']):
            tasks.append((str(folder),field,form,fps,plane,position,str(out) if out else None))
    if jobs>1 and len(tasks)>1:
        from concurrent.futures import ProcessPoolExecutor
        import multiprocessing as mp
        with ProcessPoolExecutor(max_workers=min(jobs,len(tasks)),mp_context=mp.get_context('spawn')) as pool:
            results=list(pool.map(_render_task,tasks))
    else:results=[_render_task(t) for t in tasks]
    target=Path(out) if out else Path(folder)/'animations';target.mkdir(parents=True,exist_ok=True)
    (target/'animations.json').write_text(json.dumps({'files':results,'fields':list(fields),'velocity_style':style,
        'meaning':'Streamlines and vectors are instantaneous; they are not particle paths. Colour scales are fixed across time.',
        'plane':plane,'position':position,'fps':fps},indent=2)+'\n')
    return results


def _render_task(task):return render_one(*task)


def static_rotor(folder,plane='xz',position=0.):
    d=load_plane(folder,plane,position);fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    for ax,val,label,cmap in zip(axs,[d['speed'][-1],d['p'][-1],d['v'][-1]],
        ['3-D speed magnitude','Pressure (Pa)','Velocity component '+d['labels'][1]],['viridis','coolwarm','RdBu_r']):
        im=ax.pcolormesh(d['x'],d['y'],val,cmap=cmap,shading='nearest');fig.colorbar(im,ax=ax,label=label)
        ax.set(xlabel=d['labels'][0],ylabel=d['labels'][1],aspect='equal')
    fig.suptitle(d['scope']+f' | t={d["times"][-1]:.3f} | prescribed-load rotor')
    fig.savefig(Path(folder)/'overview.png',dpi=130);plt.close(fig)
