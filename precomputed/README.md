# Rezultate të llogaritura më parë

Këta skedarë vijnë nga paketa origjinale `Fluid_Flows_CFD_LBM_Python_Package.zip`
e datës 14 tetor 2026. Nuk janë rezultate të rillogaritura gjatë konvertimit në skripte.
Grafikët PNG dhe animacionet GIF mund të hapen drejtpërdrejt.

- `cfd20_*` dhe `lbm20_*`: rastet Re=20 për katër gjeometri; Ny=40.
- `cfd100_data.npz`, `lbm100_data.npz`: gjendja përfundimtare dhe sonda për cilindrin Re=100; Ny=60.
- `*_vorticity.gif`: animacione të vorbullave të llogaritura me secilën metodë.
- `validation.json`: verifikimi origjinal, jo prova e re e skripteve.

Në këto raste H=1, L=6, U=1, D=0.25. Për 20 përdoret upwind në CFD;
për 100 përdoret central. Presioni përdor dendësi reference 1.
Gjendjet fillestare dhe rritja e hyrjes ndryshojnë midis metodave;
fazat e vorbullave nuk duhet të përputhen.
