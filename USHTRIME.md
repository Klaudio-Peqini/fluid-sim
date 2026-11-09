# Eksperimente të vogla për studentët

Për çdo eksperiment shkruani parashikimin fizik përpara ekzekutimit.
Ndryshoni vetëm një parametër dhe përdorni një dosje të re për rezultatet.

1. **Couette:** përgjysmoni viskozitetin me `--nu 0.05`. A ndryshon profili
   i qëndrueshëm apo koha e afrimit? Krahasoni të njëjtën kohë dhe më pas
   një kohë më të gjatë me `--duration 16`.
2. **Poiseuille:** dyfishoni `--acceleration`. Kontrolloni amplitudën e
   shpejtësisë në qendër dhe krahasojeni me $u_{max}=gH^2/(8\nu)$.
3. **Rrjeta:** përdorni `--n 16` dhe `--n 32` në Poiseuille me të njëjtën
   kohë të gjatë. Llogaritni raportin e gabimeve L2. Një gabim i vogël
   në këtë rast nuk verifikon automatikisht cilindrin.
4. **Cilindri:** krahasoni `--method cfd` dhe `--method lbm` për Re=20.
   Lexoni `diagnostics.json`: pse Mach/dendësia janë diagnostika të LBM,
   ndërsa divergjenca e shpejtësisë është diagnostikë e projektimit MAC?
5. **Elipsi:** krahasoni këndet 0°, 25° dhe 45°. Para grafikëve,
   parashikoni nëse gjurma pritet të jetë simetrike ndaj mesit të kanalit.
6. **Dy cilindrat:** ndryshoni `--gap` nga 0.6 në 0.8. Kjo madhësi matet
   midis qendrave. Si ndryshon rrjedhja që arrin te cilindri i dytë?
7. **Vorbullat:** shikoni fillimisht GIF-et në `precomputed/`. Pastaj
   rillogaritni Re=100. Studioni `probe.png`: nisja dhe regjimi i zhvilluar
   nuk duhen trajtuar si e njëjta gjendje. Mos nxirrni frekuencë nga një
   provë e shkurtër e komandës.

Në dorëzim përfshini komandën ose parametrat e përdorur, figurën,
diagnostikat dhe disa fjali interpretimi. Vijat e rrjedhjes në një çast
nuk janë trajektore grimcash në rrjedhje të ndryshueshme në kohë.
