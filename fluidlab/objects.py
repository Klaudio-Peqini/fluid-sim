"""Configurable 2-D obstacles on square cells; all bounds in consistent model units."""
import warnings
from pathlib import Path
import numpy as np
from matplotlib.path import Path as PolygonPath
from scipy.ndimage import label

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



def build_geometry(c):
    ny=int(c['ny']);H=float(c['height']);L=float(c['length'])
    nx=int(c['nx']) if c.get('nx') else int(round(L/H*ny))
    if min(nx,ny)<8 or not np.isclose(L/nx,H/ny,rtol=1e-10):
        raise ValueError('Use square cells: length/nx must equal height/ny; omit nx for automatic sizing.')
    x=(np.arange(nx)+.5)*L/nx;y=(np.arange(ny)+.5)*H/ny;X,Y=np.meshgrid(x,y)
    cx=c.get('center_x');cy=c.get('center_y');cx=L*.25 if cx is None else float(cx);cy=H*.5 if cy is None else float(cy)
    D=float(c['diameter']);angle=float(c['angle']);a=np.deg2rad(angle)
    xr=(X-cx)*np.cos(a)+(Y-cy)*np.sin(a);yr=-(X-cx)*np.sin(a)+(Y-cy)*np.cos(a)
    kind=c['case'];outline=None
    if kind=='none':solid=np.zeros(X.shape,bool)
    elif kind=='cylinder':solid=(X-cx)**2+(Y-cy)**2<=(D/2)**2
    elif kind=='rectangle':solid=(abs(xr)<=D/2)&(abs(yr)<=D/2)
    elif kind=='ellipse':solid=(xr/D)**2+(yr/(D/2))**2<=1
    elif kind=='two_cylinders':
        if c['gap']<=D:raise ValueError('gap is centre-to-centre spacing and must exceed diameter.')
        solid=((X-cx)**2+(Y-cy)**2<=(D/2)**2)|((X-cx-c['gap'])**2+(Y-cy)**2<=(D/2)**2)
    elif kind in ('airfoil','polygon'):
        if kind=='airfoil':
            points=(naca4_coordinates(c['naca'])-[.25,0])*D
            # Positive aerodynamic incidence is nose-up, clockwise in this drawing.
            rot=np.array([[np.cos(a),np.sin(a)],[-np.sin(a),np.cos(a)]])
            thickness=int(c['naca'][2:])/100*D/(H/ny)
            if thickness<8:raise ValueError(f'Airfoil thickness spans {thickness:.1f} cells; increase ny to give >=8.')
        else:
            path=Path(c['polygon']);points=np.genfromtxt(path,delimiter=',',skip_header=1)
            if points.ndim!=2 or points.shape[1]!=2 or len(points)<3 or not np.isfinite(points).all():
                raise ValueError('Polygon CSV needs x,y header and >=3 finite local-coordinate vertices.')
            if len(np.unique(points,axis=0))<3:raise ValueError('Polygon needs three distinct vertices.')
            if not np.array_equal(points[0],points[-1]):points=np.vstack((points,points[0]))
            rot=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]])
        outline=points@rot.T+[cx,cy]
        if np.any(outline.min(axis=0)<=0) or np.any(outline.max(axis=0)>=[L,H]):
            raise ValueError('Object outline intersects the channel boundary. Change centre, size or domain.')
        solid=PolygonPath(outline,closed=True).contains_points(np.c_[X.ravel(),Y.ravel()]).reshape(X.shape)
    else:raise ValueError('Unknown 2-D object: '+kind)
    if solid.any():
        if any((solid[:,0].any(),solid[:,-1].any(),solid[0].any(),solid[-1].any())):
            raise ValueError('Object touches a channel boundary. Enlarge domain or reduce/move the object.')
        if solid.sum()<4:raise ValueError('Object has fewer than four solid cells; refine the grid.')
    elif kind!='none':raise ValueError('Object is absent on this grid; check coordinates and resolution.')
    _,n=label(~solid)
    if n!=1:raise ValueError('Fluid must be connected; a closed cavity needs different pressure boundary treatment.')
    g=dict(x=x,y=y,X=X,Y=Y,solid=solid,nx=nx,ny=ny,length=L,height=H,
           dx=L/nx,dy=H/ny,diameter=D,shape=kind,angle=angle,center=[cx,cy])
    if outline is not None:g['outline']=outline
    return g
