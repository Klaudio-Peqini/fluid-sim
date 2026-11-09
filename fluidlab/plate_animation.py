"""Animacion i fushës u(y,t), uniforme përgjatë x; të dhëna FD të llogaritura."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def animate_plate(result, kind, path, frames=100, wall_speed=1., fps=12):
    """Sample the computed FD histories at uniform model times.

    The channel field repeats the same 1-D velocity along x. Arrows show
    instantaneous velocity, not particle trajectories. The dashed curve is
    the analytical steady solution, not an analytical transient solution.
    """
    y=result['y'];times=result['times'];profiles=result['profiles']
    display_times=np.linspace(times[0],times[-1],frames)
    values=np.column_stack([np.interp(display_times,times,profiles[:,j]) for j in range(len(y))])
    # The wall starts impulsively. Correct only the displayed boundary point
    # of the t=0 sample: the original FD history stores zero before the first step.
    if kind=='couette':values[:,-1]=wall_speed
    lo=min(0.,float(values.min()),float(result['exact'].min()))
    hi=max(0.,float(values.max()),float(result['exact'].max()))
    span=max(hi-lo,1e-12);limit=max(abs(lo),abs(hi),1e-12)
    fig,(ax,profile)=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
    xx=np.linspace(0,2,9);yy=np.linspace(y[0],y[-1],13)
    X,Y=np.meshgrid(xx,yy)
    im=ax.imshow(np.repeat(values[0,:,None],32,axis=1),origin='lower',
                 extent=[0,2,y[0],y[-1]],aspect='auto',cmap='viridis',vmin=lo,vmax=hi)
    initial=np.interp(yy,y,values[0])
    arrows=ax.quiver(X,Y,np.broadcast_to(initial[:,None],X.shape),np.zeros_like(X),
                     color='white',angles='xy',scale_units='xy',scale=limit/.3,width=.006)
    ax.plot([0,2],[y[0],y[0]],'k',lw=3);ax.plot([0,2],[y[-1],y[-1]],'k',lw=3)
    ax.set(xlabel='x (rrjedhje uniforme përgjatë x)',ylabel='y',title='Fusha e shpejtësisë; shigjetat tregojnë u')
    fig.colorbar(im,ax=ax,label='u(y,t)')
    line,=profile.plot(values[0],y,color='#17649b',lw=2,label='Profili numerik FD')
    profile.plot(result['exact'],y,'k--',label='Gjendja e qëndrueshme analitike')
    profile.set(xlabel='u',ylabel='y',xlim=(lo-.05*span,hi+.1*span),ylim=(y[0],y[-1]))
    profile.grid(alpha=.2);profile.legend(fontsize=8,loc='lower right')
    title=fig.suptitle('')

    def update(k):
        im.set_data(np.repeat(values[k,:,None],32,axis=1))
        velocity=np.interp(yy,y,values[k])
        arrows.set_UVC(np.broadcast_to(velocity[:,None],X.shape),np.zeros_like(X))
        line.set_xdata(values[k])
        title.set_text(f'{kind.capitalize()} — t={display_times[k]:.3f} — diferenca të fundme')
        return im,arrows,line,title

    anim=FuncAnimation(fig,update,frames=frames,interval=1000/fps,blit=False)
    anim.save(path,writer=PillowWriter(fps=fps));plt.close(fig)
    return display_times,values
