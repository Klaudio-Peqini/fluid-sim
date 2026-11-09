# Verifikimi i versionit me ndërfaqe të përbashkët

## Përputhja numerike e përshpejtimit

`verify_features.py` kontrolloi NumPy kundrejt Numba me disa threads për
kanalin bosh, cilindrin, elipsin dhe profilin NACA. U testuan upwind dhe
central në CFD. Pas 12 hapash, diferencat e fushave ishin zero ose të
rendit 1e-14; LBM përputhej në saktësinë e llogaritjes. Nuk përdoret
`fastmath`. Raporti i plotë: `verification/features.json`.

U testuan gjithashtu maskat, simetria NACA 0012, refuzimi i parametrave të
pavlefshëm, integrimi i forcës/momentit të rotorit, divergjenca pas
projektimit 3D, përputhja e DST me 1 dhe 2 workers, dhe interpolimi/transpozimi
i prerjeve 3D kundrejt fushave lineare analitike. Prova DST dha diferencë zero.

## Ekzekutime dhe eksporte reale

- Profil NACA 2412, Re=50, rrjetë 576×96, CFD/Numba, deri në t≈4.
  Divergjenca përfundimtare: 2.74e-13.
- Rotor 3D, rrjetë 40×40×48, deri në t=0.12 s, forcë 0.5 N.
  Divergjenca përfundimtare: 4.97e-14.
  Mesataret e w mbi/në/poshtë diskut ishin përkatësisht
  -0.8141, -2.8283,
  -3.8083 m/s; z është lart.
- Nisja Couette: t=0.2, me të katër llojet e GIF-eve.
- LBM me cilindër dhe poligon CSV; përsëritje nga konfigurimi i ruajtur.
- Një studim me dy procese u përfundua me dy raste të suksesshme.
- Ndërfaqja dhe daljet mbrohen nga komanda të pavlefshme dhe mbishkrimi
  i dosjeve të pashënuara; shihni `verification/cli.json`.

GIF-et e presionit, vorticitetit, shpejtësisë me vektorë dhe me vija
rrjedhjeje u krijuan realisht. Numri i kuadrove u kontrollua duke rihapur
GIF-et: 16 për profilin, 12 për rotorin dhe 6 për provën Couette.
U inspektuan vizualisht kuadrot përfundimtare të të katër eksporteve 3D.

## Matja e shpejtësisë

Rrjetë 576×96, 200 hapa, mediana e 3 matjeve, pa vizatim. Kompilimi i parë
JIT dhe ndërtimi i gjeometrisë/faktorëve LU përjashtohen. Matja u bë pa
simulime/renderime të tjera të këtij projekti në proces. Shpejtësitë
varen nga makina dhe ngarkesa e sistemit.

| Metoda | Backend | Sekonda | Kundrejt NumPy | Diferenca maksimale e fushave |
|---|---|---|---|---|
| CFD | numpy | 3.4267 | 1.00× | 0 |
| CFD | numba_1 | 2.6071 | 1.31× | 0 |
| CFD | numba_2 | 2.5548 | 1.34× | 0 |
| CFD | numba_4 | 2.4384 | 1.41× | 0 |
| LBM | numpy | 2.3733 | 1.00× | 0 |
| LBM | numba_1 | 0.9444 | 2.51× | 3.63e-13 |
| LBM | numba_2 | 0.6021 | 3.94× | 3.63e-13 |
| LBM | numba_4 | 0.4255 | 5.58× | 3.63e-13 |

Përshpejtimi kundrejt NumPy përfshin efektin e kompilimit dhe të threads.
Nga 1 në 4 threads Numba, LBM fitoi rreth 2.2× dhe CFD rreth 1.07×.
Presioni sparse mbetet kufizimi kryesor serial në CFD 2D. Benchmark-u nuk
përfshin kohën e GIF-eve ose kompilimin e parë të kodit në kompjuterin tuaj.

## Kufijtë e evidencës

Këto janë kontrolle gjeometrike, algjebrike, të qëndrueshmërisë dhe të
përputhjes së implementimeve. Nuk provojnë konvergjencë të përgjithshme,
validim të forcave të një krahu, turbulencë të zgjidhur ose validim
 eksperimental të rotorit. Forca/momenti i rotorit janë të imponuara.
Kontrolloni veçmas madhësinë e domain-it, rrjetën, hapin kohor, rregullarizimin
 dhe matjet laboratorike për një studim sasior. Të dhënat ruhen float32;
kufijtë e ruajtjes vlerësohen nga aritmetika float64 e solver-it.

Mësimet, provat analitike dhe raportet origjinale janë ruajtur veçmas.
