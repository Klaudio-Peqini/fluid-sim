import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def vorticity(fields):
    g=fields['geometry']
    return np.gradient(fields['v'],g['dx'],axis=1)-np.gradient(fields['u'],g['dy'],axis=0)

def plot_flow(fields,title='',save=None):
    g=fields['geometry']; mask=g['solid']; u=fields['u']; v=fields['v']
    speed=np.hypot(u,v); omega=vorticity(fields)
    fig,axes=plt.subplots(3,1,figsize=(11,6.8),constrained_layout=True)
    for ax,z,name,cmap in zip(axes,[speed,fields['p'],omega],
                            ['Shpejtësia |u|','Presioni relativ (ρ₀=1)','Vorticiteti ωz'],['viridis','coolwarm','RdBu_r']):
        arr=np.ma.masked_where(mask,z)
        opts={}
        if name.startswith('Vorticiteti'):
            lim=max(float(np.percentile(abs(z[~mask]),98)),1e-6); opts=dict(vmin=-lim,vmax=lim)
        im=ax.pcolormesh(g['x'],g['y'],arr,shading='nearest',cmap=cmap,**opts)
        ax.contourf(g['X'],g['Y'],mask.astype(float),levels=[.5,1.5],colors=['#29313d']) if mask.any() else None
        fig.colorbar(im,ax=ax,pad=.012,label=name)
        ax.set_aspect('equal'); ax.set_ylabel('y'); ax.set_xlim(0,g['length']); ax.set_ylim(0,g['height'])
    axes[0].streamplot(g['x'],g['y'],np.ma.masked_where(mask,u),np.ma.masked_where(mask,v),
                       color='white',density=.8,linewidth=.55,arrowsize=.6)
    axes[-1].set_xlabel('x'); fig.suptitle(f'{title} — t={fields["time"]:.2f}')
    if save: fig.savefig(save,dpi=140)
    return fig

def animate_flow(frames,path=None,interval=80):
    g=frames[0]['geometry']; mask=g['solid']
    fig,ax=plt.subplots(figsize=(10,2.5),constrained_layout=True)
    lim=max(np.percentile(abs(vorticity(f)[~mask]),98) for f in frames)
    im=ax.imshow(np.ma.masked_where(mask,vorticity(frames[0])),origin='lower',
                 extent=[0,g['length'],0,g['height']],cmap='RdBu_r',vmin=-lim,vmax=lim,aspect='equal')
    ax.set_xlabel('x'); ax.set_ylabel('y'); fig.colorbar(im,ax=ax,label='ωz')
    def update(k):
        im.set_data(np.ma.masked_where(mask,vorticity(frames[k])))
        ax.set_title(f'Vorticiteti — t={frames[k]["time"]:.2f}'); return (im,)
    animation=FuncAnimation(fig,update,frames=len(frames),interval=interval,blit=False)
    if path: animation.save(path,writer=PillowWriter(fps=max(1,int(1000/interval))))
    return animation
