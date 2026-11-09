# Mësimi 09 — rrjedhja rreth profilit të krahut

```bash
python 09_profili_i_krahut.py
```

Shembulli i parazgjedhur përdor **NACA 2412**, kënd sulmi 6°, kordë c=0.8,
Re=50, rrjetë 576×96 dhe kohë t≈4. Ruhet edhe animacioni GIF.
Përdorni `--help` për opsionet, ose ndryshoni konstantet në krye të skedarit.

```bash
python 09_profili_i_krahut.py --naca 0012 --angle 0 --output results/naca0012_zero
python 09_profili_i_krahut.py --angle 12 --output results/wing_angle12
python 09_profili_i_krahut.py --method lbm --output results/wing_lbm
python 09_profili_i_krahut.py --ny 192 --output results/wing_finer
```

Këndi pozitiv nënkupton buzën hyrëse më lart se buza dalëse: në figurë,
korda nga hyrja te dalja rrotullohet në drejtim orar. Rrotullimi bëhet
rreth pikës së çerekut të kordës, (1.5,0.5). Një simetri gjeometrike mund
të testohet me NACA 0012 dhe kënd zero; hyrja dhe muret janë simetrike,
ndërsa perturbimi i vogël i përdorur nga skripti mund ta thyejë këtë simetri.

## Çfarë shohin studentët?

- `fields.png`: shpejtësia me vija rrjedhjeje, presioni relativ dhe vorticiteti.
- `wing_zoom.png`: të njëjtat fusha, të zmadhuara rreth krahut.
- `geometry.png`: forma nominale dhe qelizat e ngurta të solver-it.
- `vorticity.gif`: zhvillimi i vorticitetit; animacion me fusha të llogaritura.
- `airfoil_outline.csv`: koordinatat e kufirit nominal.
- `fields.npz`, `snapshots.npz`, `history.csv`, `config.json`,
  `diagnostics.json`: të dhënat numerike dhe parametrat e ekzekutimit.

Dosja e parazgjedhur është `results/cfd_airfoil_re50/`. Për eksperimente të
tjera përdorni emra të rinj me `--output`. Një dosje jo bosh mbrohet nga
mbishkrimi. `--no-gif` shmang ruajtjen e animacionit.

## Përshkrimi fizik dhe kufijtë

Ky është një **profil krahu 2D në kanal**, i ngjashëm me një eksperiment
në tunel: H=1, L=6, hyrje parabolike me shpejtësi mesatare U=1 dhe mure
pa rrëshqitje sipër/poshtë. Nuk është një krah i fundëm 3D në atmosferë të
pakufizuar. Nuk përfaqëson vorbullat në skajet e krahut, rezistencën e
induktuar, fluturimin turbulent ose gjendjen e zakonshme të një avioni.
Këto numra të vegjël Reynolds përdoren për mësim.

Re=Uc/ν përdor **kordën** dhe **shpejtësinë mesatare të hyrjes**, jo
trashësinë e profilit ose maksimumin e profilit parabolik. Në qendër të
hyrjes shpejtësia është afërsisht 1.5U. Ndryshimi i `--chord` me të njëjtin
Re ndryshon edhe viskozitetin ν=Uc/Re dhe bllokimin e kanalit; për një
eksperiment të thjeshtë ndryshoni fillimisht vetëm këndin ose kodin NACA.
Presioni përdor dendësi reference 1 dhe vlerë zero në dalje.

NACA 2412 ka vijë të mesme të lakuar dhe trashësi nominale 12% të kordës;
0012 është simetrik. Formulat janë shkruar drejtpërdrejt në këtë skedar;
nuk përdoret një program CFD ose një bibliotekë e jashtme profilesh.
Polinomi standard përdor koeficientin fundor -0.1015 dhe jep trashësi të
vogël, jo zero, në buzën dalëse. Poligoni mbyllet eksplicitisht atje.

Muri numerik ka shkallëzime: rrjeta e shpejtë e parazgjedhur ka vetëm rreth
9 qeliza përgjatë trashësisë maksimale. Ajo jep një demonstrim, jo një
zgjidhje të konvergjuar të shtresës kufitare. Për teste saktësie duhen
rafinim, studim i hapit kohor dhe i ndikimit të mureve/kufijve. Hyrja CFD
dhe rritja graduale e hyrjes LBM kanë kalime fillestare të ndryshme.

**Nuk llogariten C_L/C_D, ngritja ose rezistenca e krahut.** Mos i nxirrni
ato thjesht nga ngjyrat e presionit ose nga diferencat midis metodave.
Vijat e rrjedhjes janë të çastit; nuk janë trajektore në rrjedhje të
ndryshueshme në kohë. Shihni `verification/wing_checks.json` për provat
reale të këtij shembulli; ato nuk janë validim eksperimental aerodinamik.

Referenca e gjeometrisë: C. L. Ladson dhe C. W. Brooks Jr. (1975),
*Development of a computer program to obtain ordinates for NACA 4-digit,
4-digit modified, 5-digit, and 16 series airfoils*, NASA TM X-3284:
https://ntrs.nasa.gov/citations/19760003945
