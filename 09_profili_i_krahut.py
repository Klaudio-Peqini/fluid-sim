"""Rrjedhje 2D rreth një profili NACA me katër shifra në kanal.

    python 09_profili_i_krahut.py
    python 09_profili_i_krahut.py --naca 0012 --angle 0 --output results/naca0012
    python 09_profili_i_krahut.py --method lbm --output results/wing_lbm

Ky model përfaqëson një prerje të krahut, jo një krah të fundëm 3D.
Re=U_mean*c/nu përdor kordën c dhe shpejtësinë MESATARE të kanalit.
Kufijtë e kanalit janë mure; fusha hyrëse është parabolike. Nuk është
fluturim në atmosferë të pakufizuar. Nuk llogariten koeficientë ngritjeje
ose rezistence. Rrjeta me shkallëzime dhe upwind janë afrime mësimore.

Gjeometria: formulat standarde NACA me trashësi fundore të vogël, jo zero;
NASA TM X-3284, https://ntrs.nasa.gov/citations/19760003945
"""
# %% Parametrat që studentët mund të ndryshojnë.
NACA = '2412'       # '0012': simetrik; '2412': profil me vijë të mesme të lakuar
ANGLE = 6.0         # Gradë. Pozitiv: buza hyrëse më lart se buza dalëse (nose-up).
CHORD = 0.8        # Në të njëjtat njësi si kanali H=1, L=6
REYNOLDS = 50.0    # Re = U_mean * CHORD / nu; U_mean=1
NY = 96           # Nx=6*Ny; rreth 9 qeliza në trashësinë maksimale (shembull i trashë)
DURATION = 4.0    # Koha e modelit
METHOD = 'cfd'    # 'cfd' ose 'lbm'
SAVE_GIF = True

import warnings
import numpy as np
from matplotlib.path import Path as PolygonPath
from scipy.ndimage import label
from fluidlab.geometry import channel_geometry
from lesson_tools import flow_lesson


def naca4_coordinates(code='2412', points=401):
    """Kufiri i mbyllur, me kordë njësi; trashësia vendoset normalisht te vija e mesme.

    Kodi MPTT: m=M/100, p=P/10, t=TT/100. Pikat shpërndahen me kosinus
    që buza hyrëse e rrumbullakët të përfaqësohet me më shumë pika.
    """
    if not isinstance(code,str) or len(code)!=4 or not code.isascii() or not code.isdigit():
        raise ValueError('Kodi NACA duhet të ketë katër shifra, p.sh. 0012 ose 2412.')
    m=int(code[0])/100;p=int(code[1])/10;t=int(code[2:])/100
    if not .04<=t<=.30 or (m>0 and not 0<p<1) or (m==0 and p!=0):
        raise ValueError('Kërkohet trashësi 04–30%; për profil simetrik përdorni 00TT; për profil të lakuar p>0.')
    if not isinstance(points,int) or points<50:
        raise ValueError('Kërkohen të paktën 50 pika për faqe.')
    x=.5*(1-np.cos(np.linspace(0,np.pi,points)))
    # yt është GJYSMËTRASHËSIA. -0.1015 ruan fundin standard me trashësi jo zero.
    yt=5*t*(.2969*np.sqrt(x)-.1260*x-.3516*x*x+.2843*x**3-.1015*x**4)
    if m:
        yc=np.where(x<p,m/p**2*(2*p*x-x*x),m/(1-p)**2*((1-2*p)+2*p*x-x*x))
        slope=np.where(x<p,2*m/p**2*(p-x),2*m/(1-p)**2*(p-x))
    else:
        yc=np.zeros_like(x);slope=yc.copy()
    theta=np.arctan(slope)
    upper=np.c_[x-yt*np.sin(theta),yc+yt*np.cos(theta)]
    lower=np.c_[x+yt*np.sin(theta),yc-yt*np.cos(theta)]
    # TE sipër -> LE -> TE poshtë -> TE sipër: mbyllje eksplicite.
    return np.vstack((upper[::-1],lower[1:],upper[-1]))


def wing_geometry(naca='2412',chord=.8,angle=6.,ny=96):
    """Nominal NACA polygon and the actual binary wall used by both solvers."""
    if not np.isfinite([chord,angle]).all() or chord<=0 or abs(angle)>30:
        raise ValueError('Korda duhet të jetë pozitive; këndi për shembullin mësimor kufizohet në ±30°.')
    g=channel_geometry(nx=6*ny,ny=ny,shape='none',diameter=chord)
    original=naca4_coordinates(naca)
    local=(original-np.array([.25,0]))*chord
    alpha=np.deg2rad(angle)
    # Këndi pozitiv aerodinamik = rrotullim ORAR i kordës në rrjedhje drejt +x.
    rotation=np.array([[np.cos(alpha),np.sin(alpha)],[-np.sin(alpha),np.cos(alpha)]])
    outline=local@rotation.T+np.array([1.5,.5])
    margin=2*g['dx']
    if np.any(outline.min(axis=0)<margin) or np.any(outline.max(axis=0)>np.array([6.,1.])-margin):
        raise ValueError('Profili është shumë pranë kufirit. Ulni kordën/këndin.')
    cells_in_thickness=int(naca[2:])/100*chord/g['dy']
    if cells_in_thickness<8:
        raise ValueError(f'Vetëm {cells_in_thickness:.1f} qeliza në trashësi. Rritni --ny ose --chord (duhen >=8).')
    if cells_in_thickness<16:
        warnings.warn(f'Profil i përfaqësuar trashë: {cells_in_thickness:.1f} qeliza në trashësinë maksimale. Për saktësi duhen rafinim dhe prova konvergjence.')
    polygon=PolygonPath(outline,closed=True)
    solid=polygon.contains_points(np.c_[g['X'].ravel(),g['Y'].ravel()]).reshape(g['X'].shape)
    if label(solid)[1]!=1:
        raise ValueError('Maska e profilit nuk është një trup i vetëm i lidhur; rafinoni rrjetën.')
    g.update(solid=solid,shape='airfoil',angle=angle,outline=outline,
             metadata={'naca':naca,'chord':chord,'angle_of_attack_deg':angle,
                       'angle_convention':'positive nose-up: clockwise rotation of LE-to-TE chord',
                       'quarter_chord':[1.5,.5],'reference_length':'chord',
                       'cells_across_max_thickness':cells_in_thickness,
                       'scope':'2D low-Re airfoil in a no-slip channel with parabolic inlet; no finite-span effects or lift/drag prediction',
                       'geometry_reference':'https://ntrs.nasa.gov/citations/19760003945'})
    return g


def add_options(parser):
    parser.add_argument('--naca',default=NACA,help='Kodi si tekst: 0012, 2412, ...')


def save_closeups(output):
    """Show the smooth definition beside the actual stepped numerical wall."""
    import json
    import matplotlib.pyplot as plt
    from fluidlab.plotting import vorticity
    config=json.loads((output/'config.json').read_text())
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        g=wing_geometry(config['naca'],config['chord'],config['angle'],config['ny'])
    outline=g['outline'];chord=config['chord']
    xlim=(max(0,float(outline[:,0].min())-.35*chord),min(6,float(outline[:,0].max())+.6*chord))
    ylim=(max(0,float(outline[:,1].min())-.3*chord),min(1,float(outline[:,1].max())+.3*chord))
    fig,ax=plt.subplots(figsize=(9,3.5),layout='constrained')
    ax.pcolormesh(g['x'],g['y'],np.ma.masked_where(~g['solid'],g['solid']),cmap='Greys',vmin=0,vmax=1,shading='nearest')
    ax.plot(outline[:,0],outline[:,1],color='#c75a27',lw=1.4,label='Kufiri nominal NACA')
    ax.scatter([1.5],[.5],s=20,color='#1c7196',label='Pika 1/4 e kordës')
    ax.set(xlabel='x',ylabel='y',xlim=xlim,ylim=ylim,aspect='equal',
           title=f'NACA {config["naca"]}, α={config["angle"]:g}° — qelizat e zeza janë trupi numerik')
    ax.legend(fontsize=8);fig.savefig(output/'geometry.png',dpi=150);plt.close(fig)
    with np.load(output/'fields.npz',allow_pickle=False) as z:
        f={k:z[k] for k in ['u','v','p','time']}
    f['geometry']=g
    # Presim edhe të dhënat, jo vetëm kufijtë e akseve, që vijat e rrjedhjes
    # dhe llogaritja e faqosjes të mos mbeten të lidhura me kanalin e plotë.
    ix=(g['x']>=xlim[0])&(g['x']<=xlim[1]);iy=(g['y']>=ylim[0])&(g['y']<=ylim[1])
    crop=np.ix_(iy,ix);mask=g['solid'][crop];x=g['x'][ix];y=g['y'][iy]
    fig,axs=plt.subplots(3,1,figsize=(8,9.5),layout='constrained')
    for ax,data,cmap,title in zip(axs,[np.hypot(f['u'],f['v']),f['p'],vorticity(f)],
                                ['viridis','coolwarm','RdBu_r'],['|u|','p relativ (ρ₀=1)','ωz']):
        options={}
        if title=='ωz':
            limit=max(float(np.percentile(abs(data[crop][~mask]),98)),1e-9)
            options=dict(vmin=-limit,vmax=limit)
        im=ax.pcolormesh(x,y,np.ma.masked_where(mask,data[crop]),cmap=cmap,shading='nearest',**options)
        ax.contourf(x,y,mask.astype(float),levels=[.5,1.5],colors=['#29313d'])
        ax.plot(outline[:,0],outline[:,1],color='#101010',lw=.7)
        ax.set(xlabel='x',ylabel='y',aspect='equal')
        fig.colorbar(im,ax=ax,label=title,pad=.02,panchor=False)
    axs[0].streamplot(x,y,np.ma.masked_where(mask,f['u'][crop]),np.ma.masked_where(mask,f['v'][crop]),
                      color='white',density=.8,linewidth=.55,arrowsize=.6)
    fig.suptitle(f'Prerje krahu NACA {config["naca"]} — {config["method"].upper()}, Re={config["re"]:g}, t={float(f["time"]):.2f}')
    fig.savefig(output/'wing_zoom.png',dpi=150);plt.close(fig)


def main():
    print('Profil krahu 2D në kanal; për detajet lexoni AIRFOIL.md.',flush=True)
    output=flow_lesson(shape='airfoil',re=REYNOLDS,method=METHOD,ny=NY,duration=DURATION,
                angle=ANGLE,advection='upwind',gif=SAVE_GIF,reference_length=CHORD,
                add_arguments=add_options,
                geometry_builder=lambda args:wing_geometry(args.naca,args.diameter,args.angle,args.ny))
    save_closeups(output)


if __name__=='__main__':main()
