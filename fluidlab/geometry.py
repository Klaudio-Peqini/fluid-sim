import numpy as np

def channel_geometry(nx=180, ny=60, length=6., height=1., shape='cylinder',
                     diameter=.2, angle=0., gap=.5):
    """Cell-centred grid and a Boolean solid mask. Lengths share one unit.

    Shapes: none, rectangle, cylinder, ellipse, two_cylinders.
    The default cylinder is centred on the channel axis, unlike the DFG case.
    """
    if nx < 8 or ny < 8 or diameter <= 0 or length <= 0 or height <= 0:
        raise ValueError('Use positive dimensions and at least 8 cells per axis.')
    if not np.isclose(length/nx, height/ny):
        raise ValueError('D2Q9 comparison requires square cells: nx/ny = length/height.')
    x=(np.arange(nx)+.5)*length/nx
    y=(np.arange(ny)+.5)*height/ny
    X,Y=np.meshgrid(x,y)
    cx=length*.25; cy=height*.5
    a=np.deg2rad(angle)
    xr=(X-cx)*np.cos(a)+(Y-cy)*np.sin(a)
    yr=-(X-cx)*np.sin(a)+(Y-cy)*np.cos(a)
    if shape=='none': solid=np.zeros((ny,nx),bool)
    elif shape=='cylinder': solid=(X-cx)**2+(Y-cy)**2 <= (diameter/2)**2
    elif shape=='rectangle': solid=(abs(xr)<=diameter/2)&(abs(yr)<=diameter/2)
    elif shape=='ellipse': solid=(xr/diameter)**2+(yr/(diameter/2))**2<=1
    elif shape=='two_cylinders':
        solid=((X-cx)**2+(Y-cy)**2<=(diameter/2)**2)|((X-cx-gap)**2+(Y-cy)**2<=(diameter/2)**2)
    else: raise ValueError('Unknown shape: '+shape)
    if solid[:,0].any() or solid[:,-1].any() or solid[0].any() or solid[-1].any():
        raise ValueError('Object must remain separated from the inlet, outlet and walls.')
    return dict(x=x,y=y,X=X,Y=Y,solid=solid,nx=nx,ny=ny,
                length=length,height=height,dx=length/nx,dy=height/ny,
                diameter=diameter,shape=shape,angle=angle)
