"""Krahasoni rezultatet origjinale pa nisur një simulim të ri.

python 08_krahasimi_cfd_lbm.py --re 20
python 08_krahasimi_cfd_lbm.py --re 100
Për rezultate të reja: --cfd-folder results/rasti_cfd --lbm-folder results/rasti_lbm
"""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fluidlab import channel_geometry
from fluidlab.plotting import vorticity

ROOT=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--re',type=int,choices=[20,100],default=20)
    parser.add_argument('--cfd-folder',type=Path)
    parser.add_argument('--lbm-folder',type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'results'/'comparison')
    a=parser.parse_args()
    if bool(a.cfd_folder)!=bool(a.lbm_folder):
        parser.error('Për rezultate të reja duhen dhënë të dyja dosjet.')
    fields=[];configs=[]
    for method,folder in [('cfd',a.cfd_folder),('lbm',a.lbm_folder)]:
        name=f'{method}20_cylinder.npz' if a.re==20 else f'{method}100_data.npz'
        path=folder/'fields.npz' if folder else ROOT/'precomputed'/name
        with np.load(path,allow_pickle=False) as z:
            f={k:z[k] for k in z.files}
        if folder:
            config=json.loads((folder/'config.json').read_text());configs.append(config)
            g=channel_geometry(nx=f['u'].shape[1],ny=f['u'].shape[0],shape=config['shape'],
                               diameter=config['diameter'],angle=config['angle'],gap=config['gap'])
        else:
            g=channel_geometry(nx=f['u'].shape[1],ny=f['u'].shape[0],shape='cylinder',diameter=.25)
        f['geometry']=g;fields.append(f)
    if configs:
        for key in ['shape','re','diameter','angle','gap','length','height','mean_inlet_speed']:
            if configs[0][key]!=configs[1][key]:
                parser.error(f'Rastet nuk përputhen për parametrin {key}.')
        if not np.array_equal(fields[0]['geometry']['solid'],fields[1]['geometry']['solid']):
            parser.error('Për krahasimin grafik të drejtpërdrejtë përdorni të njëjtën rrjetë.')
    speeds=[np.hypot(f['u'],f['v']) for f in fields];omegas=[vorticity(f) for f in fields]
    vmax=max(float(s[~f['geometry']['solid']].max()) for s,f in zip(speeds,fields))
    wmax=max(float(np.percentile(abs(w[~f['geometry']['solid']]),98)) for w,f in zip(omegas,fields))
    fig,axs=plt.subplots(2,2,figsize=(13,5),layout='constrained')
    for j,(f,s,w,method) in enumerate(zip(fields,speeds,omegas,['CFD','LBM'])):
        g=f['geometry'];mask=g['solid']
        for i,(data,cmap,limits,label) in enumerate([(s,'viridis',(0,vmax),'|u|'),(w,'RdBu_r',(-wmax,wmax),'ωz')]):
            ax=axs[i,j]
            im=ax.pcolormesh(g['x'],g['y'],np.ma.masked_where(mask,data),cmap=cmap,
                              vmin=limits[0],vmax=limits[1],shading='nearest')
            ax.contourf(g['X'],g['Y'],mask.astype(float),levels=[.5,1.5],colors=['#29313d'])
            ax.set(xlabel='x',ylabel='y',aspect='equal',title=f'{method}: {label}, t={float(f["time"]):.3f}')
            fig.colorbar(im,ax=ax,label=label)
    source='Rezultate të reja nga dosjet e zgjedhura' if configs else 'Rezultate origjinale të llogaritura më parë'
    fig.suptitle(source+' — shkallë të përbashkëta ngjyrash')
    a.output.mkdir(parents=True,exist_ok=True);dest=a.output/f'comparison_re{configs[0]["re"]:g}.png' if configs else a.output/f'comparison_re{a.re}.png'
    fig.savefig(dest,dpi=140);plt.close(fig)
    print(source);print(dest.resolve())
    print('Fazat e vorbullave dhe kushtet fillestare mund të ndryshojnë. Figura nuk është provë konvergjence.')


if __name__=='__main__':main()
