# Rrjedhja e fluideve — skripte Python për studentët e Fizikës

Versioni me skripte i materialit **Fluid_Flows_CFD_LBM**. Nuk nevojitet
Jupyter ose notebook. Algoritmet origjinale janë ruajtur në `fluidlab/`:
diferenca të fundme, projektim MAC për Navier–Stokes dhe LBM D2Q9/BGK.
Shpjegimet fizike gjenden në `FIZIKA_DHE_ALGORITMET.md`.

## Instalimi dhe shembulli i parë

Përdorni Python 3.10 ose më të ri. Shpaketoni **të gjithë dosjen** dhe hapni
terminalin brenda saj. Në Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python 01_couette.py
```

Në Windows, krijoni mjedisin me `py -m venv .venv`, pastaj aktivizojeni me
`.venv\Scripts\activate.bat` në Command Prompt. Komandat e tjera janë të njëjta.
Në VS Code, Spyder ose PyCharm mund të hapni dhe ekzekutoni një skript të vetëm;
zgjidhni interpretuesin ku instaluat paketat. Mbajeni dosjen `fluidlab/` pranë tij.

Hapni `results/couette/profiles.png`. Grafikët **ruhen në skedarë**;
nuk është e nevojshme të shfaqet një dritare grafike gjatë ekzekutimit.

## Animacioni Couette / Poiseuille

Për një GIF të shpejtësisë gjatë zhvillimit të rrjedhjes, përdorni:

```bash
python 01_couette.py --gif --frames 100 --output results/couette_animation
python 02_poiseuille.py --gif --frames 100 --output results/poiseuille_animation
```

Hapni `velocity.gif` në dosjen përkatëse. Paneli majtas tregon fushën u(y,t)
me ngjyra dhe shigjeta të shpejtësisë; paneli djathtas tregon profilin në kohë
kundrejt gjendjes së qëndrueshme analitike. Në Couette profili afrohet drejt
vijës së drejtë. Për të parë afrim më të ngadaltë, përdorni `--nu 0.05`.

Animacioni përdor historinë numerike **FD**; testi LBM i profilit përfundimtar
vazhdon të ruhet veçmas. Shigjetat nuk janë trajektore grimcash. Shpejtësia
është uniforme përgjatë x; fusha 2D vizualizon zgjidhjen 1D, jo vorbulla.
`--duration` ndryshon kohën e modelit; `--frames` ndryshon numrin e kuadrove.
Gjithashtu ruhet `animation_profiles.npz` me kohët dhe profilet e shfaqura.
Një shembull Couette i krijuar rishtas është te `examples/couette_velocity.gif`.

## Rendi i punës

| Skripti | Çfarë bën |
|---|---|
| `01_couette.py` | Pllaka lëvizëse; profile në kohë; FD dhe LBM kundrejt zgjidhjes analitike |
| `02_poiseuille.py` | Gradient presioni/forcë vëllimore; profili parabolik |
| `03_pengesa_drejtkendore.py` | Rrjedhje rreth një pengese drejtkëndore |
| `04_cilindri_re20.py` | Cilindër me Re=20 |
| `05_cilindri_re100.py` | Cilindër me Re=100; sondë dhe animacion GIF; ekzekutim më i gjatë |
| `06_elipsa.py` | Elips i rrotulluar |
| `07_dy_cilindra.py` | Ndërveprimi i dy cilindrave |
| `08_krahasimi_cfd_lbm.py` | Krahason rezultate me shkallë të njëjta ngjyrash; nuk nis simulim |
| `09_profili_i_krahut.py` | Profil krahu NACA 2D; kënd sulmi, fusha dhe animacion |
| `run_case.py` | Hyrje e përgjithshme me parametra nga terminali |
| `validate.py` | Verifikimet analitike dhe kontrollet numerike bazë |

Në skriptet 03–07 ndryshoni parametrat në krye të skedarit ose përdorni terminalin:

```bash
python 04_cilindri_re20.py --method lbm
python 06_elipsa.py --angle 40 --output results/elipsa40
python 07_dy_cilindra.py --gap 0.8 --output results/dy_cilindra08
python 05_cilindri_re100.py --method lbm
python 08_krahasimi_cfd_lbm.py --re 100
python validate.py
```

`--help` liston opsionet. Një dosje rezultatesh jo bosh mbrohet nga mbishkrimi
në simulimet e kanalit: përdorni një emër të ri me `--output`.
Skriptet e pllakave përditësojnë rezultatet në dosjen e tyre të zgjedhur.

## Rezultatet dhe koha e llogaritjes

Për simulimet e reja, `results/` përmban fushat në `fields.npz`, evolucionin në
`snapshots.npz`, figurat `fields.png` dhe `probe.png`, diagnostikat JSON,
parametrat `config.json` dhe tabelën `history.csv`. `--gif` aktivizon animacionin;
`--no-gif` e çaktivizon. Për pllakat ruhen edhe profile CSV.

`--duration` është koha e modelit; mund të kërkojë më shumë sekonda ose minuta
në kompjuter. Për një provë të shkurtër të komandës përdorni `--duration 0.2`;
ajo **nuk mjafton për zhvillimin e vorbullave**. Re=100 përdor Ny≥60 dhe, në CFD,
adveksion central me hap më të vogël kohor. Për të parë menjëherë rezultatet,
hapni figurat/animacionet origjinale në `precomputed/` ose ekzekutoni skriptin 08.
Këto të dhëna janë të shënuara qartë si të llogaritura më parë.

## Ku lexohet algoritmi?

- `fluidlab/conventional.py`: `plate_fd`, hapi i impulsit dhe projektimi i presionit.
- `fluidlab/lbm.py`: ekuilibri, përplasja BGK, transporti dhe bounce-back.
- `fluidlab/geometry.py`: maskat e trupave; `diameter` është diametri i cilindrit
  ose boshti i vogël i elipsit; `gap` është largësia midis qendrave.
- `lesson_tools.py`: hyrja nga terminali, ruajtja e rezultateve dhe grafikët.

Shembujt janë **2D, laminarë dhe mësimorë**. H=1, L=6, U=1, D=0.25 në njësi
konsistente; Re=UD/ν dhe koha pa përmasa është tU/D. Presioni përdor dendësi
reference 1. Pengesat kanë kontur të shkallëzuar nga rrjeta. Kushtet LBM në
hyrje/dalje janë rezervuarë ekuilibri, jo Zou–He. Dy metodat kanë nisje të
ndryshme; nuk pritet përputhje e fazës së vorbullave. Këto nuk janë simulime
të rotorëve 3D ose një riprodhim i benchmark-ut DFG.

Për kontrollet e ekzekutuara në këtë version shihni `TESTED.md`.
`VALIDATION_ORIGINAL.md` dokumenton provat dhe kufijtë e paketës origjinale.

## Shembulli i ri: profili i krahut

```bash
python 09_profili_i_krahut.py
python 09_profili_i_krahut.py --naca 0012 --angle 0 --output results/wing_symmetric
```

Lexoni `AIRFOIL.md` për gjeometrinë, konventën e këndit dhe kufijtë.
Ky është një profil 2D në kanal, jo një krah i fundëm 3D. Parametrat e
parazgjedhur janë NACA 2412, Re=50, kënd 6° dhe kordë 0.8; ruhet GIF-i.
Fushat e zmadhuara janë `wing_zoom.png`; animacioni është `vorticity.gif`.
Shembuj të llogaritur rishtas janë te `examples/wing_*.png` dhe `examples/wing_vorticity.gif`.
