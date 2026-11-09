# Burimi i algoritmeve

Pesë modulet origjinale Python në `fluidlab/` janë identike me ato në paketën origjinale
`Fluid_Flows_CFD_LBM_Python_Package.zip`, të përgatitur për studentët e vitit
të dytë të Fizikës. Ato janë kontrolluar me krahasim të drejtpërdrejtë të skedarëve.

Ky version shton skripte të veçanta për mësimet, hyrje nga terminali, ruajtje
CSV/NPZ/PNG/GIF, kontroll parametrash dhe shpjegime që nuk varen nga Jupyter.
Ndryshimet nuk përfshijnë një model të ri fizik ose një solver të ri fluidesh.

`precomputed/` përmban rezultatet historike të paketës origjinale.
`verification/` dokumenton verifikimet e përsëritura gjatë kësaj përshtatjeje.

Përditësimi i 8 nëntorit shton `fluidlab/plate_animation.py`, që vizualizon historinë FD të rrjedhjeve midis pllakave.

Mësimi 09 shton poligonin NACA me katër shifra në `09_profili_i_krahut.py`.
Zgjidhësit origjinalë CFD/LBM nuk ndryshuan. `lesson_tools.py` pranon edhe një
ndërtues gjeometrie të jashtëm për këtë mësim. Formulat dhe kufijtë e modelit
dokumentohen në `AIRFOIL.md`.

Përditësimi me ndërfaqe të përbashkët:

- `fluidlab/fast.py` ka ekuacione ekuivalente me implementimet NumPy, të
  kompilueshme dhe paralelizueshme me Numba; krahasohen në `verify_features.py`.
- `fluidlab/rotor3d/` ripërdor solver-in MAC 3D dhe vijat e forcave nga paketa
  e mëparshme e këtij projekti `Drone_Pollutant_Flow_Python_Package.zip`.
- `flow.py`, `fluidlab/cli.py`, `config.py`, `runner.py` dhe `render.py`
  shtojnë komandat, JSON, ekzekutimin, studimet paralele dhe eksportin e fushave.
- Numba CPU parallelism: https://numba.readthedocs.io/en/stable/user/parallel.html
- SciPy FFT workers: https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dstn.html

Modelet kufizohen siç përshkruhet në README; nuk shtohet një model turbulence,
 një model force nga aerodinamika e tehut ose një validim eksperimental.
