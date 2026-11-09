# Shembuj të llogaritur të versionit të ri

- `airfoil/`: NACA 2412, Re=50, CFD/Numba, rrjetë 576×96, t≈4, 16 kuadro.
- `rotor/`: një rotor 3D, R=0.1 m, RPM=1800, T=0.5 N, Q=0.008 N m,
  rrjetë 40×40×48, ajër fillimisht në qetësi, t=0.12 s, 12 kuadro.
- `couette_short/`: provë e nisjes deri në t=0.2, 6 kuadro; nuk është gjendja e qëndrueshme.

Në `animations/` ka GIF-et e shpejtësisë me vektorë, me vija rrjedhjeje,
të presionit dhe të vorticitetit. `snapshots.npz` mundëson rigjenerimin:

```bash
python flow.py animate examples/v2/rotor --fields velocity pressure --jobs 2
```

Konfigurimet përmbajnë edhe metadata nga makina e përgatitjes. Për simulim
të ri përdorni `--config examples/v2/rotor/config.json --output results/new_rotor`.
Kohët e rrjedhjes janë ato në `snapshots.npz`; shpejtësia e GIF-it nuk është
një orë fizike e laboratorit.
