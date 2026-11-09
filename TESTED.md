> Regjistër historik i mësimeve. Për veçoritë e reja lexoni TESTED_V2.md.

# Kontrollet e këtij versioni — 6 nëntor 2026

Ky është një konvertim i materialit mësimor në skripte Python. Të pesë
modulet origjinale në `fluidlab/` janë identike me skedarët e paketës origjinale.
Nuk u ndryshuan ekuacionet, diskretizimi ose kushtet në kufi.

## Ekzekutime reale

- Mësimet 01–04, 06 dhe 07: ekzekutim me parametrat e parazgjedhur.
- Mësimi 05: CFD, Re=100, rrjeta 360×60, deri në t=18.000222,
  me figurat, sondën dhe animacionin GIF të krijuar nga ky ekzekutim.
- LBM Re=20: cilindër deri në t≈4; LBM Re=100: provë e shkurtër deri në t≈0.3.
- LBM me elips të rrotulluar, parametrat e terminalit dhe krijimi i GIF-it.
- Krahasimi 08 për të dhënat origjinale Re=20 dhe Re=100, si dhe për dy
  dosje rezultatesh të llogaritura rishtas me Re=20.
- Parametra të pavlefshëm dhe dosje jo bosh: komandat ndalojnë me gabim.
- Të gjithë skedarët Python u kontrolluan me kompilim; figurat e profileve
  dhe krahasimit u inspektuan vizualisht.

Ekzekutimi i plotë CFD Re=100 zgjati **322.5 s** në mjedisin
e përgatitjes. Kohët varen nga kompjuteri. Divergjenca maksimale në hapin
përfundimtar ishte 1.42e-14; flukset hyrës/dalës ishin
1 / 1.

## Verifikimi analitik i përsëritur

`python validate.py` përfundoi me `ALL CHECKS PASSED`. Për pllakat në t≈8:

| Rasti | Metoda | Gabimi relativ L2 |
|---|---|---|
| couette | FD | 0.0002836597 |
| couette | LBM | 0.00028914393 |
| poiseuille | FD | 0.00036951692 |
| poiseuille | LBM | 0.0010412405 |

Rafinimi Poiseuille/LBM, në t≈12, dha gabimet
0.0027876768 (N=16) dhe
0.00070177767 (N=32).
Për pesë maskat gjeometrike u përsëritën provat e shkurtra CFD/LBM:
mosrrjedhja brenda trupit, divergjenca/fluksi në CFD dhe Mach/dendësia në LBM.

Provat e shkurtra nuk janë prova të konvergjencës së gjurmës së cilindrit.
Ekzekutimi i gjatë LBM Re=100 i përfshirë në `precomputed/` vjen nga paketa
origjinale; gjatë këtij konvertimi u riekzekutua vetëm prova e tij e shkurtër.

`verification/` ruan raportet JSON dhe versionet e bibliotekave.
`examples/` ka disa figura të krijuara gjatë provave të këtij versioni.
`precomputed/` ruan veçmas rezultatet historike të notebook-ut.
Dosja e punës `results/` krijohet kur studentët ekzekutojnë skriptet.

## Përditësim: animacionet e pllakave — 8 nëntor 2026

U ekzekutuan realisht Couette me 100 kuadro dhe Poiseuille me 20 kuadro,
me opsionin `--gif`. GIF-et u rihapën dhe u kontrolluan numrat e kuadrove;
profilet ishin të fundme dhe kohët rriteshin. Profili i fundit i animacionit
përputhet saktësisht me profilin FD përfundimtar. Zgjidhjet përfundimtare FD
janë identike me ato të versionit pa animacion. U inspektuan vizualisht
kuadro gjatë nisjes dhe pranë gjendjes së qëndrueshme.

Animacioni interpolon në kohë historinë numerike FD të ruajtur me frekuencë
më të madhe. Në Couette, pika e murit në kuadrin t=0 shfaqet menjëherë me
shpejtësinë e murit, në përputhje me nisjen impulsive. Zgjidhësi numerik
nuk ndryshoi. Këto animacione nuk përdorin fusha kalimtare LBM.

## Mësimi 09: profili NACA — 8 nëntor 2026

CFD, NACA 2412, Re=50, kënd 6°, kordë 0.8, rrjetë 576×96:
ekzekutim i plotë deri në t≈4 me 40 kuadro dhe GIF. Divergjenca përfundimtare
ishte rreth 2.74e-13 dhe flukset 1 / 1 deri në gabimet e rrumbullakimit.
LBM me të njëjtën gjeometri: provë e shkurtër deri në t≈0.6, me Mach<0.10
dhe ndryshim maksimal dendësie<0.076. Diferenca e flukseve gjatë nisjes
LBM është e pranishme; kjo provë nuk tregon një gjendje të zhvilluar.

Për NACA 0012 u kontrollua sipërfaqja e poligonit kundrejt integralit analitik
të trashësisë, simetria e maskës dhe ruajtja e simetrisë së fushave në një
provë të shkurtër CFD pa perturbim. U kontrolluan maskat në disa kënde,
ndalimi i parametrave të pavlefshëm/rrjetës tepër të trashë, skedarët e
fushave, mosrrjedhja në qelizat e trupit dhe numri i kuadrove të GIF-it.
U ekzekutua edhe një shembull ekzistues cilindri si provë regresioni për
mjetet e përbashkëta. U inspektuan vizualisht pamjet e plota dhe të zmadhuara.

Këto janë prova numerike dhe gjeometrike, jo validim i forcave aerodinamike,
konvergjencë e zgjidhjes së profilit ose validim eksperimental i një krahu.
Raporti është `verification/wing_checks.json`.
