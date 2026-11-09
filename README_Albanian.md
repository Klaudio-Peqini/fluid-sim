# Fluid Flows Framework — udhëzues i plotë për instalimin dhe përdorimin

**Versioni në shqip.** Versioni përkatës në anglisht është [README.md](README.md).

Kjo paketë shërben për mësimin e simulimit të rrjedhjes së ajrit dhe të fluideve viskoze: rrjedhje Couette dhe Poiseuille, pengesa në kanal, profile krahu NACA dhe një model rotori me ngarkesë të imponuar. Ekzekutohet si kod i zakonshëm Python. Nuk kërkon Jupyter, ndërfaqe grafike ose një program të jashtëm CFD.

**Rruga e rekomanduar:** ndiqni fillimisht seksionet 1–6. Ato ju çojnë nga dosja e saposhpaketuar deri te një ekzekutim i vogël dhe kontrollet e para. Më pas zgjidhni eksperimentet dhe animacionet që ju duhen. Komandat shkruhen në terminal, jo brenda interpretuesit python3 te shenja `>>>`. Mos kopjoni shenja të terminalit si `$`.

## 1. Shpaketoni arkivin dhe gjeni dosjen e saktë

Shpaketoni **të gjithë arkivin ZIP**. Mos provoni të ekzekutoni vetëm një skedar pa e nxjerrë nga arkivi. Hapni dosjen `Fluid_Flows_Framework`; brenda saj duhet të jenë `flow.py`, dy skedarët e kërkesave dhe dosjet `fluidlab` e `configs`.

| Skedari ose dosja | Për çfarë shërben |
|---|---|
| `flow.py` | Ndërfaqja e rekomanduar për simulime, ndihmë, animacione dhe studime paralele |
| `fluidlab/` | Algoritmet numerike dhe modulet ndihmëse; duhet të qëndrojë pranë `flow.py` |
| `configs/` | Shembuj konfigurimi JSON dhe një poligon CSV |
| `01_*.py` deri te `09_*.py` | Skriptet e mësimeve të mëparshme, me opsionet e tyre origjinale |
| `requirements.txt` | Bibliotekat bazë numerike dhe grafike |
| `requirements-parallel.txt` | Bibliotekat bazë dhe përshpejtimi opsional me Numba |
| `examples/v2/` | Shembuj të llogaritur, fusha të ruajtura dhe GIF-e për t'u parë menjëherë |
| `verification/` | Raportet e kontrolleve dhe matjet e kohës |
| `TESTED_V2.md` | Çfarë është testuar dhe cilët janë kufijtë e këtyre provave |
| `LESSONS.md`, `FIZIKA_DHE_ALGORITMET.md`, `AIRFOIL.md` | Shpjegimet e mëparshme mësimore dhe shënimet për profilin e krahut |

Hapni terminalin brenda kësaj dosjeje. Në Linux/macOS, nëse e keni shpaketuar drejtpërdrejt te Downloads:

```bash
cd ~/Downloads/Fluid_Flows_Framework
```

Vendndodhja në kompjuterin tuaj mund të jetë tjetër. Në Windows hapni Command Prompt ose PowerShell brenda dosjes së shpaketuar, ose shkruani `cd "C:\your\actual\path\Fluid_Flows_Framework"`, duke zëvendësuar rrugën me atë reale. Rrugët që përmbajnë hapësira vendosini brenda thonjëzave.

Kontrolloni dosjen aktive:

```bash
python3 -c "from pathlib import Path; print(Path.cwd()); print(Path('flow.py').is_file())"
```

Përpara krijimit të mjedisit, në disa sisteme komanda quhet `python3`, prandaj përdoreni atë në vend të `python`. Rreshti i fundit duhet të japë `True`. Nëse jep `False`, kaloni në dosjen e saktë përpara se të vazhdoni.

## 2. Kontrolloni Python-in dhe krijoni mjedisin virtual

Paketa synon python3 3.10 ose më të ri; **python3 3.12 është zgjedhja e rekomanduar për fillim, sepse me të është testuar paketa**. Mundësia e instalimit të Numba-s varet nga versioni i Python-it dhe sistemi operativ. Nëse përshpejtimi nuk instalohet, mund të përdorni versionin bazë me NumPy.

Mjedisi virtual ndan bibliotekat e këtij projekti nga projektet e tjera Python. Krijohet një herë dhe aktivizohet sa herë hapni një terminal të ri për këtë projekt. Në udhëzimet më poshtë emri i tij është `.venv`.

### Linux dhe macOS — bash ose zsh

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
```

Nëse keni disa versione të Python-it dhe doni posaçërisht 3.12, komanda e krijimit mund të jetë `python3.12 -m venv .venv`.

### Windows — Command Prompt

Kur janë instaluar python3 launcher dhe python3 3.12:

```bat
py -3.12 --version
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

Nëse përdorni një instalim tjetër të mbështetur, zgjidhni interpretuesin përkatës gjatë krijimit të mjedisit. Mos vendosni një numër versioni që nuk është instaluar.

### Windows — PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nëse PowerShell bllokon skriptin e aktivizimit, mund të përdorni drejtpërdrejt interpretuesin e mjedisit, pa ndryshuar politikën e ekzekutimit:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-parallel.txt
.\.venv\Scripts\python.exe flow.py --help
```

Në këtë mënyrë përdorimi, në komandat e tjera zëvendësoni `python` me `.\.venv\Scripts\python.exe`.

### Verifikoni interpretuesin që po përdoret

Pas aktivizimit:

```bash
python3 -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
python3 -m pip --version
```

Rrugët e Python-it dhe pip-it duhet të përmbajnë `.venv`; kontrolli logjik duhet të japë `True`. Shfaqja e `(.venv)` në terminal është e dobishme, por kontrolli i interpretuesit është më i sigurt.

Mos ruani kodin e projektit brenda `.venv` dhe mos e zhvendosni këtë mjedis bashkë me ZIP-in në një kompjuter tjetër. Atje krijoni një mjedis të ri. Rezultatet e simulimeve ruhen në `results/`.

## 3. Instaloni bibliotekat

Për instalimin e rekomanduar me përshpejtim:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-parallel.txt
```

Skedari `requirements-parallel.txt` përfshin automatikisht edhe kërkesat bazë. Nuk është e nevojshme t'i instaloni të dy skedarët veçmas.

Për instalimin bazë pa Numba:

```bash
python3 -m pip install -r requirements.txt
```

Në këtë rast përdorni `--backend numpy`, ose lejoni që `auto` të zgjedhë implementimin e disponueshëm. Instalimi i `requirements.txt` nuk e çinstalon Numba-n nëse ajo ishte instaluar më parë.

Kontrolloni instalimin:

```bash
python3 -m pip check
python3 -c "import numpy, scipy, matplotlib, PIL, threadpoolctl; print('Core imports OK')"
```

Për një instalim me varësi të përputhshme duhet të shfaqen `No broken requirements found.` dhe `Core imports OK`. Për instalimin e përshpejtuar kontrolloni edhe:

```bash
python3 -c "import numba; print('Numba version:', numba.__version__)"
```

Përdorimi i `python3 -m pip` bën që instalimi të kryhet nga i njëjti interpretues që ekzekuton simulimet. Instalimi zakonisht kërkon internet; simulimet e zakonshme dhe krijimi lokal i GIF-eve nuk e kërkojnë atë.

## 4. Kontrollet e para: komandat, CPU-ja dhe plani

Komandat më poshtë nuk avancojnë një simulim:

```bash
python3 flow.py --help
python3 flow.py help run
python3 flow.py help animate
python3 flow.py objects
python3 flow.py hardware
```

`hardware` raporton CPU-të logjike, kufijtë e afinitetit/kuotës dhe nëse gjendet një instalim Numba. Ky është kontroll i konfigurimit, jo matje e performancës.

Përgatitni një plan të vogël:

```bash
python3 flow.py plan --case couette --duration 0.2 --backend numpy --threads 1
```

Dalja tregon parametrat përfundimtarë dhe një vlerësim të memories për vargjet numerike. Faktorët e presionit, kompilimi dhe renderimi mund të kërkojnë memorie shtesë. `plan` kontrollon parametrat dhe gjeometrinë; nuk provon qëndrueshmërinë ose konvergjencën e një llogaritjeje të plotë.

## 5. Simulimi dhe GIF-i juaj i parë

Përdorni një dosje të re rezultatesh:

```bash
python3 flow.py run --case couette --backend numpy --duration 0.2 --frames 6 --gif velocity --velocity-style vectors --fps 4 --output results/first_check
```

Ky ekzekutim është qëllimisht i shkurtër: kontrollon nisjen dhe krijimin e skedarëve. **Nuk synon arritjen e rrjedhjes Couette të qëndrueshme.** Në fund duhet të shfaqet një mesazh që fillon me `Completed:`.

Kontrolloni skedarët:

| Skedari në `results/first_check/` | Çfarë duhet të verifikoni |
|---|---|
| `summary.json` | `status` duhet të jetë `PASS` pasi përfundon me sukses i gjithë procesi |
| `config.json` | Parametrat duhet të përputhen me komandën tuaj |
| `overview.png` | Duhet të ketë një figurë të ruajtur; nuk pritet domosdoshmërisht një dritare grafike |
| `animations/velocity_vectors.gif` | Hapeni me shfletues ose shikues figurash që mbështet GIF-e |
| `snapshots.npz` | Evolucioni i ruajtur për GIF-e të tjera pa rillogaritje të rrjedhjes |
| `history.csv` | Kohët e modelit dhe diagnostikat e regjistruara |

Statusin mund ta lexoni edhe nga terminali:

```bash
python3 -c "import json; print(json.load(open('results/first_check/summary.json'))['status'])"
```

Nëse përsëritni të njëjtën komandë, dosja ekzistuese jo bosh mbrohet nga mbishkrimi. Zgjidhni një emër të ri, p.sh. `results/first_check_2`. Përdorni `--overwrite` vetëm kur dëshironi me vetëdije të zëvendësoni një dosje rezultatesh të krijuar nga programi; përmbajtja e saj hiqet. Dosjet e zakonshme pa shenjën përkatëse refuzohen.

## 6. Kryeni kontrollet numerike

```bash
python3 validate.py
python3 verify_features.py
```

`validate.py` përsërit krahasimet e rrjedhjeve midis pllakave me zgjidhjet analitike, një shembull rafinimi dhe prova të shkurtra rreth pengesave. Përfundimi i suksesshëm jep `ALL CHECKS PASSED` dhe shkruan `results/validation.json`.

`verify_features.py` kontrollon gjeometritë, përputhjen NumPy/Numba kur Numba është instaluar, normalizimin e forcës/momentit të rotorit, projektimin e presionit 3D dhe koordinatat e prerjeve. Shkruan `verification/features.json` dhe jep një raport JSON me `status: PASS`. Në mungesë të Numba-s, kontrollet e implementimit të përshpejtuar shënohen qartë si të anashkaluara.

Ekzekutojini normalisht, pa opsionin python3 `-O`, sepse kontrollet përdorin `assert`. Ato mund të zgjasin më shumë se prova fillestare e vogël, sidomos gjatë kompilimit të parë JIT. Kalimi i kontrolleve numerike nuk është validim eksperimental i një krahu ose rotori. `TESTED_V2.md` përshkruan se çfarë provojnë rezultatet e regjistruara.

## 7. Rikthimi në punë, ndalimi dhe përdorimi i një IDE-je

Pas instalimit fillestar, zakonisht mjafton të kaloni te dosja e projektit dhe të riaktivizoni mjedisin. Në Linux/macOS:

```bash
cd ~/Downloads/Fluid_Flows_Framework
source .venv/bin/activate
python3 flow.py --help
```

Në Windows përdorni komandën e aktivizimit nga seksioni 2. Bibliotekat zakonisht riinstalohen vetëm kur krijoni mjedis të ri ose ndryshoni varësitë.

Me `deactivate` dilni nga mjedisi virtual. Kjo nuk fshin kodin ose rezultatet. Për të ndërprerë një ekzekutim të gjatë përdorni Ctrl+C në terminal; mund të mbeten skedarë të pjesshëm, të cilët nuk duhen trajtuar si një ekzekutim i përfunduar me sukses.

Në VS Code, Spyder ose PyCharm zgjidhni interpretuesin e `.venv` dhe dosjen e projektit si dosje pune. Nëse terminali përdor një interpretues dhe IDE-ja një tjetër, importet mund të sillen ndryshe. Shfaqja e `sys.executable` ndihmon për ta gjetur këtë mospërputhje.

## 8. Komandat fleksibël dhe objektet e disponueshme

Struktura e rekomanduar është:

```text
python3 flow.py SUBCOMMAND OPTIONS
```

| Nënkomanda | Funksioni |
|---|---|
| `run` | Llogarit një simulim dhe, sipas zgjedhjes, krijon GIF-et |
| `plan` | Zgjidh parametrat dhe kontrollon gjeometrinë/vlerësimin e memories |
| `animate` | Krijon GIF-e nga fushat e ruajtura |
| `sweep` | Ekzekuton kombinime të pavarura parametrash në paralel |
| `benchmark` | Mat kohën NumPy/Numba dhe diferencat numerike |
| `hardware` | Kontrollon alokimin CPU dhe praninë e përshpejtimit opsional |
| `objects` | Liston rastet dhe përmasat e modeleve |

Si `python3 flow.py help run`, ashtu edhe `python3 flow.py run --help` japin ndihmë. Opsionet pas nënkomandës mund t'i ndryshoni në rend. Emrat `run --gif ...` dhe `animate --fields ...` janë qëllimisht të ndryshëm.

Rastet janë `couette`, `poiseuille`, `none`, `rectangle`, `cylinder`, `ellipse`, `two_cylinders`, `airfoil`, `polygon` dhe `rotor`. `none` do të thotë kanal pa pengesë. `--object` është sinonim i `--case`.

Shembuj të zakonshëm:

```bash
python3 flow.py run --case cylinder --method lbm --re 20 --ny 64 --duration 4 --threads auto --gif all
python3 flow.py run --case rectangle --method cfd --re 20 --gif velocity pressure
python3 flow.py run --case ellipse --angle 30 --method cfd --duration 3
python3 flow.py run --case two_cylinders --gap 0.8 --duration 3
python3 flow.py run --case none --method cfd --duration 2
python3 flow.py run --case couette --nu 0.05 --duration 8 --gif all --fps 4
python3 flow.py run --case poiseuille --acceleration 0.2 --duration 8 --gif all
```

Pa `--output`, çdo simulim merr automatikisht një dosje të re brenda `results/`. Evolucioni i pllakave në ndërfaqen e përbashkët përdor `--method cfd` dhe ekuacionin e vogël serial 1D; skriptet e mëparshme të pllakave ruajnë edhe krahasimet përfundimtare me LBM.

## 9. Parametrat, rrjeta dhe interpretimi fizik

| Opsioni | Kuptimi |
|---|---|
| `--duration` | Koha e synuar e simulimit, jo koha e pritjes në kompjuter |
| `--frames` | Mostrimi i kërkuar i gjendjeve; 2–300; ruhen kohët reale |
| `--fps` | Ritmi i GIF-it; 1–60 kuadro/s; vlera fillestare 12 |
| `--ny`, `--nx` | Numrat e qelizave 2D; Nx mund të zgjidhet automatikisht |
| `--length`, `--height` | Përmasat e kanalit 2D |
| `--diameter` / `--chord` | Gjatësia e referencës D; korda për profilin e krahut |
| `--mean-speed` | Shpejtësia mesatare U në hyrjen e kanalit |
| `--re` | Numri Reynolds U D / nu për objektet në kanal |
| `--nu` | Viskoziteti kinematik për ekuacionin e reduktuar të pllakave |
| `--angle` | Këndi në gradë; konventa e profilit të krahut shpjegohet më poshtë |
| `--gap` | Largësia midis qendrave për dy cilindra |
| `--center-x`, `--center-y` | Pozicioni i objektit; pika e çerekut të kordës për profilin |
| `--advection` | Transporti në CFD: `upwind` ose `central` |
| `--lattice-speed` | Shpejtësia e referencës LBM në njësi të rrjetës |
| `--backend` | `auto`, `numpy` ose `numba` |
| `--threads` | Numri i kërkuar i threads CPU ose `auto` |

Qelizat 2D duhet të jenë katrore: `length/nx = height/ny`. Nëse Nx i zgjedhur automatikisht nuk përputhet me përmasat, vendosni një raport të përshtatshëm ose Nx eksplicit. Në shembujt e kanalit hyrja është parabolike, me shpejtësi në qendër afërsisht 1.5 herë mesataren. Numri Reynolds përdor **shpejtësinë mesatare**. Për elipsin, D është gjatësia e boshtit të vogël.

Ndryshimi i D, duke mbajtur Re dhe U të pandryshuar, ndryshon edhe nu = U D / Re. Te pllakat përdoret drejtpërdrejt `--nu`. Parametrat varen nga rasti: p.sh. `--grid` përcakton rrjetën 3D të rotorit, ndërsa `--ny` përcakton rrjetën e kanalit ose të pllakave. Lexoni daljen e `plan` përpara një llogaritjeje të madhe.

Rastet mësimore 2D përdorin njësi reference të përputhshme; përmasat e parazgjedhura nuk përfaqësojnë domosdoshmërisht një tub ose krah real. Përcaktoni shkallët e gjatësisë, shpejtësisë dhe kohës përpara krahasimit me matjet. Parametrat e rotorit përdorin njësitë SI: metra, sekonda, kilogramë, njutonë dhe paskalë; RPM tregon rrotullime në minutë.

Hapi i fundit 2D mund ta kalojë pak kohën e synuar. Një kohë shumë e shkurtër mund të japë më pak gjendje se numri i kërkuar, sepse solver-i nuk ruan gjendje të ndërmjetme që nuk i ka llogaritur. Titujt e GIF-it përdorin kohët reale. Shtimi i `--frames` nuk rafinon rrjetën ose hapin kohor numerik.

## 10. Llojet e GIF-eve, ngadalësimi dhe rigjenerimi

Krijoni të gjitha animacionet gjatë një ekzekutimi:

```bash
python3 flow.py run --case airfoil --gif all --velocity-style both --fps 4
```

Emrat standardë 2D brenda `animations/` janë:

| Skedari | Çfarë paraqet |
|---|---|
| `velocity_vectors.gif` | Modulin e shpejtësisë dhe vektorët |
| `velocity_streamlines.gif` | Modulin e shpejtësisë dhe vijat e çastit të rrjedhjes |
| `pressure.gif` | Presionin relativ ndaj referencës |
| `vorticity.gif` | Vorticitetin 2D |

Stilet e shpejtësisë janë `vectors`, `streamlines` dhe `both`. `--no-gif` shmang krijimin e GIF-eve, por ruan fushat numerike. Shkalla e ngjyrave mbetet e njëjtë gjatë të gjitha kuadrove të një animacioni.

**Për animacion më të ngadaltë, ulni FPS.** Me 12 kuadro/s, 60 kuadro shfaqen për afërsisht 5 sekonda; me 4 kuadro/s, për afërsisht 15 sekonda. Shikuesi mund ta rrumbullakosë kohën e GIF-it. Ndryshimi i FPS ndryshon shfaqjen, jo fizikën e llogaritur.

Rigjeneroni GIF-et ekzistuese me ritëm më të ngadaltë:

```bash
python3 flow.py animate results/first_check --fields all --velocity-style both --fps 4
python3 flow.py animate examples/v2/airfoil --fields all --fps 4
```

Në dosjen përkatëse duhen `snapshots.npz` dhe `config.json`. Këto komanda **nuk e rillogarisin rrjedhjen**. Ato zëvendësojnë eksportet përkatëse GIF/PNG në dosjen e animacioneve. Për të mbajtur dy variante të ritmit të shfaqjes, zgjidhni një dosje tjetër eksporti:

```bash
python3 flow.py animate examples/v2/airfoil --fields all --fps 4 --output results/airfoil_slow_gifs
```

`results/first_check` ka vetëm një nisje të shkurtër. Shembulli i përfshirë i profilit ka evolucion më të gjatë. `animate` nuk krijon histori fizike më të gjatë se ajo që është ruajtur.

Vijat e rrjedhjes janë tangjente me fushën e shpejtësisë në atë çast; në rrjedhje të ndryshueshme nuk janë trajektore grimcash. Në modelin e reduktuar Couette presioni është konstant. Te Poiseuille, gradienti i imponuar është konstant në kohë. Prandaj mungesa e ndryshimeve të fushës në GIF-in e presionit për këto raste është e pritshme.

## 11. Profile krahu dhe objekte të personalizuara

```bash
python3 flow.py run --case airfoil --naca 2412 --angle 8 --gif all
python3 flow.py run --case airfoil --naca 0012 --angle 0 --output results/symmetric_wing
python3 flow.py run --case airfoil --ny 192 --output results/finer_wing
python3 flow.py run --config configs/polygon.json --gif all
```

Këndi pozitiv i profilit do të thotë buza hyrëse më lart se buza dalëse: korda nga buza hyrëse te dalësja rrotullohet në drejtim orar në këtë figurë. Pika e rrotullimit është në çerekun e kordës. Kodet NACA janë tekst; në JSON përdorni `"0012"` për të ruajtur zerot në fillim.

Ky është një **profil 2D në kanal**, jo një krah i fundëm 3D. Rrjeta e shpejtë e parazgjedhur ka vetëm rreth nëntë qeliza përgjatë trashësisë maksimale. Për rezultate sasiore nevojiten rafinim dhe studim i kufijve. Nuk llogariten koeficientët e ngritjes ose rezistencës.

Për një poligon, jepni CSV me tituj `x,y` dhe të paktën tre kulme në koordinata lokale. Kodi e rrotullon dhe e zhvendos te qendra e zgjedhur. `configs/triangle.csv` është një shembull funksional. Zgjidhni `--diameter` si gjatësinë e referencës për Reynolds-in e objektit tuaj. Rezultatet e ruajtura përfshijnë një kopje të poligonit burim, që konfigurimi të mund të ripërdoret.

## 12. Rotori i dronit: fusha 3D dhe prerje të dobishme

```bash
python3 flow.py run --case rotor --threads auto --gif all --output results/my_rotor
```

Parametrat ilustrues fillestarë janë: një rotor horizontal, R=0.1 m, RPM=1800, shtytje 0.5 N dhe moment 0.008 N m. Ajri fillon në qetësi; z është lart, ndërsa forca mbi ajrin është poshtë. Paraqitja fillestare është prerja xz në y=0.

| Opsioni i rotorit | Kuptimi |
|---|---|
| `--grid 40 40 48` | Numri i qelizave 3D |
| `--radius`, `--rpm` | Rrezja dhe shpejtësia e rrotullimit |
| `--thrust`, `--torque` | Shtytja dhe momenti i imponuar për secilin rotor |
| `--rotor-count 1` / `4` | Konfigurimet e mbështetura: një rotor ose katër rotorë |
| `--payload-mass`, `--vehicle-mass` | Ngarkesa dhe masa e dronit me bateri; jepini të dyja |
| `--epsilon` | Gjerësia e rregullarizimit të forcës; duhet të zgjidhet nga rrjeta dhe të përshtatet në domain |
| `--domain-scale` | Shkallëzimi i kutisë së jashtme të llogaritjes |
| `--max-dt`, `--blade-step` | Kufizime shtesë të hapit kohor dhe lëvizjes së tehut |

Solver-i përdor **vija forcash rrotulluese 3D me ngarkesa të imponuara**, jo sipërfaqe të zgjidhura të teheve. RPM përcakton rrotullimin e vijave; shtytja dhe momenti janë hyrje të pavarura. Nuk përfshihen model turbulence, fuselazh, tokë ose parashikim i forcës nga aerodinamika e tehut. Mach i majës së tehut mbi 0.3 refuzohet.

Pasi të jetë llogaritur `results/my_rotor`, paraqitni prerje horizontale mbi dhe poshtë rotorit të parazgjedhur:

```bash
python3 flow.py animate results/my_rotor --fields velocity pressure --plane xy --position 0.1 --fps 4
python3 flow.py animate results/my_rotor --fields velocity pressure --plane xy --position -0.1 --fps 4
```

Për `xy`, `position` është z; për `xz`, është y; për `yz`, është x. Pozicioni duhet të ndodhet brenda koordinatave të qendrave të qelizave të ruajtura. Emrat e GIF-eve 3D përfshijnë planin dhe pozicionin. Ngjyra e shpejtësisë tregon modulin e plotë 3D, ndërsa vektorët/vijat përdorin komponentët në plan. Curl-i i paraqitur është një komponent i orientuar i prerjes, jo moduli i plotë i vorticitetit. Konturet e ndërprera tregojnë pozicionet ose projeksionet e disqeve të rotorëve.

Konfigurimi opsional me katër rotorë është:

```bash
python3 flow.py plan --config configs/quad_4kg_payload.json
python3 flow.py run --config configs/quad_4kg_payload.json --no-gif
```

Ai përdor **4 kg ngarkesë dhe 3 kg masë të supozuar të dronit me bateri**, katër rotorë, R=0.2811 m, RPM=2640 dhe moment ilustrues 0.429 N m për rotor. Shtytja totale e nevojshme në gjendje të qëndrueshme është 7 × 9.80665 = 68.64655 N dhe ndahet midis katër rotorëve. Ngarkesat rriten gradualisht gjatë nisjes, prandaj në fillim janë më të vogla. Jepni masën reale dhe matjet e punës së dronit tuaj. Ky konfigurim nuk është identifikim ose validim i tij. Kur jepni të dyja masat, mos jepni njëkohësisht edhe shtytjen.

## 13. Ekzekutimi paralel dhe performanca e matur

Për rastet 2D në kanal, `auto` përdor Numba kur ajo është instaluar. Disponueshmëria e CPU-së merr parasysh afinitetin dhe informacionin e mbështetur të kuotës cgroup. `auto` zgjedh deri në katër threads; kërkesa mbi alokimin refuzohet.

| Puna | Zbatimi paralel dhe kufijtë |
|---|---|
| LBM | Bërthama të kompilueshme paralele për përplasjen, transportin dhe rezervuarët |
| CFD 2D | Parashikim paralel i impulsit; presioni sparse LU mbetet serial |
| Rotori 3D | Transformime paralele SciPy për presionin; impuls/forca me NumPy |
| Rrjedhja 1D midis pllakave | Zgjidhje e vogël seriale; përdorni raste të pavarura për studime paralele |
| GIF-et | Procese të veçanta për eksporte të pavarura |
| Studimet me parametra | Procese të veçanta për simulime të pavarura |

Për implementimin referencë NumPy 1D/2D, threads efektivë të solver-it raportohen si një. Shtimi i threads nuk i bën paralelë këta operatorë me vargje. Nuk ka backend GPU ose ndarje të domain-it me MPI midis nyjeve të cluster-it.

Për eksporte paralele GIF përdorni `--render-jobs 2` gjatë simulimit ose `animate --jobs 2`. Kjo përshpejton eksportet e pavarura, jo avancimin e fluidit. Përdorini këto vlera vetëm nëse janë të disponueshme të paktën dy CPU.

Matni performancën në makinën tuaj:

```bash
python3 flow.py benchmark --ny 96 --steps 200 --threads 1 2 4 --output benchmark_my_machine.json
```

Nëse alokimi ka më pak CPU, shkurtoni listën, p.sh. `--threads 1 2` ose `--threads 1`. Matja e përgatitjes dha rreth 5.6× përshpejtim LBM dhe 1.4× CFD kundrejt NumPy me katër threads Numba. Këto përfshijnë përfitimin nga kompilimi dhe paralelizimi së bashku; kalimi vetëm nga një në katër threads Numba dha afërsisht 2.2× dhe 1.07×. Kompilimi i parë, përgatitja dhe vizatimi përjashtohen. Rezultatet varen nga makina.

Për një studim me disa kënde:

```bash
python3 flow.py sweep --config configs/sweep_angles.json --jobs 2 --threads 2 --output results/angle_study
```

Kërkohen të paktën katër CPU të alokuara, sepse `jobs × threads` duhet të përshtatet me kufirin e CPU-së. Një provë seriale që punon edhe me një CPU është:

```bash
python3 flow.py sweep --config configs/sweep_quick.json --jobs 1 --threads 1 --output results/quick_study
```

JSON-i i studimit ka parametrat `base` dhe lista nën `vary`; kombinimet karteziane janë raste të veçanta. Çdo rast ka dosjen dhe log-un e vet. `sweep_summary.json` regjistron suksesin e proceseve. Renderimi brenda çdo rasti përdor një proces për të shmangur mbingarkimin me procese.

## 14. Konfigurimi JSON dhe riprodhueshmëria

```bash
python3 flow.py plan --config configs/airfoil.json
python3 flow.py run --config configs/airfoil.json --angle 12 --output results/wing12
python3 flow.py run --config results/wing12/config.json --angle 0 --output results/wing0
```

Opsionet eksplicite të terminalit kanë përparësi ndaj JSON-it; JSON-i ka përparësi ndaj parametrave të parazgjedhur të rastit. Çelësat JSON përdorin nënvizim, si `mean_speed` ose `velocity_style`, ndërsa opsionet e terminalit përdorin vizë, si `--mean-speed` ose `--velocity-style`. Përdorni JSON standard: tekst në thonjëza dyshe, pa komente dhe me `true`/`false` me shkronja të vogla.

`config.json` ruan si `parameters` të ripërdorshëm, ashtu edhe metadata të ekzekutimit. Përsëritja e rastit lexon seksionin e parametrave. Për një eksperiment të ri zgjidhni dosje tjetër rezultatesh. Për interpretim fizik ndryshoni nga një parametër në herë. Me `python3 -m pip freeze > environment_installed.txt` mund të regjistroni mjedisin e instaluar; rikrijoni mjediset nga skedarët përkatës të varësive, duke shmangur kopjimin e `.venv`.

## 15. A vlejnë ende skriptet e mëparshme me numra?

**Po, me opsionet e tyre origjinale.** Ndërfaqja e tyre e komandave është e ndarë nga `flow.py`.

| Skripti | Mësimi |
|---|---|
| `01_couette.py` | Nisja Couette dhe krahasimi përfundimtar FD/LBM |
| `02_poiseuille.py` | Poiseuille dhe krahasimi analitik |
| `03_pengesa_drejtkendore.py` | Pengesë drejtkëndore |
| `04_cilindri_re20.py` | Cilindër me Re=20 |
| `05_cilindri_re100.py` | Ekzekutim më i gjatë për Re=100 |
| `06_elipsa.py` | Elips i rrotulluar |
| `07_dy_cilindra.py` | Ndërveprimi i dy cilindrave |
| `08_krahasimi_cfd_lbm.py` | Krahasime grafike nga të dhënat origjinale ose të zgjedhura |
| `09_profili_i_krahut.py` | Mësimi origjinal për profilin NACA 2D |

```bash
python3 01_couette.py --help
python3 01_couette.py --gif --frames 100 --output results/legacy_couette
python3 04_cilindri_re20.py --method lbm --gif --output results/legacy_cylinder
```

Skriptet origjinale të kanalit prodhojnë GIF vorticiteti; skriptet e pllakave prodhojnë `velocity.gif`. Ato nuk pranojnë çdo opsion të ri të `flow.py`. Për GIF presioni, stile shpejtësie, FPS, implementime paralele dhe rotorë, përdorni ndërfaqen e përbashkët. Në veçanti, `run_case.py` i mëparshëm është i ndryshëm nga `flow.py run`. Për ndërfaqen e vjetër lexoni `LESSONS.md`.

## 16. Leximi i rezultateve dhe kufijtë e modelit

`summary.json` regjistron përfundimin, implementimin e zgjedhur, threads efektivë, kohët, ekstremet e diagnostikave kur regjistrohen dhe madhësitë përfundimtare. `PASS` do të thotë që kaluan procesi i implementuar dhe kufijtë numerikë të kontrolluar. Nuk është certifikatë e saktësisë fizike.

`snapshots.npz` ruan kohët dhe evolucionin e fushave; `fields.npz` ruan fushat përfundimtare. Llogaritja kryhet me float64, ndërsa fushat ruhen me float32. Për 2D presioni jepet për dendësi reference 1, në thelb p/rho0. Presioni i rotorit është në paskal. `history.csv` mund të hapet me mjete të zakonshme tabelore ose grafike.

Modelet 2D janë laminare dhe përdorin mure karteziane me shkallëzime. Adveksioni upwind shton difuzion numerik; central kërkon kufizim më të fortë kohor. LBM është dobët i kompresueshëm dhe përdor rezervuarë të thjeshtë ekuilibri në hyrje/dalje, jo Zou–He. Gjeometria e cilindrit nuk është benchmark-u identik DFG. Për pretendime sasiore të projektit duhen pavarësi nga rrjeta/koha/domain-i dhe krahasim me matjet laboratorike.

## 17. Zgjidhja e problemeve të zakonshme

| Shenja e problemit | Çfarë të bëni |
|---|---|
| `can't open file flow.py` | Kaloni në dosjen e shpaketuar `Fluid_Flows_Framework`; kontrolloni `Path('flow.py').is_file()` |
| `No module named ...` | Kontrolloni `sys.executable`, aktivizoni mjedisin e duhur dhe instaloni me `python3 -m pip` të atij mjedisi |
| Mungon `venv` / `ensurepip` | Kontrolloni që instalimi i zgjedhur python3 ka mbështetje për mjedise virtuale; në makina të administruara kërkojani administratorit |
| Dështon instalimi/importi Numba | Përdorni interpretues të përputhshëm, mundësisht python3 3.12 të testuar, ose kërkesat bazë me `--backend numpy` |
| `unrecognized arguments` | Lexoni `--help` të komandës përkatëse; skriptet e vjetra dhe ndërfaqja e re kanë opsione të ndryshme |
| Dosja e rezultateve nuk është bosh | Përdorni `--output` me emër të ri; zëvendësoni me `--overwrite` vetëm kur e dëshironi me vetëdije |
| Nuk hapet dritare grafike | Hapni PNG/GIF-et e krijuara; vizatimi ruhet në disk |
| GIF-i ecën shumë shpejt | Rigjenerojeni me `animate ... --fps 4` ose `--fps 2` |
| GIF-i tregon vetëm nisje të shkurtër | Simulimi i ruajtur ishte i shkurtër; rritni `--duration` nëse nevojitet histori fizike më e gjatë |
| GIF-i i presionit të pllakave duket konstant | Kjo është e pritshme për fushën e presionit të modelit të reduktuar |
| Rrjetë e papërshtatshme / profil shumë i hollë | Përdorni qeliza katrore dhe rritni rezolucionin e trupit |
| Numër tepër i madh threads/jobs | Lexoni `hardware` dhe qëndroni brenda alokimit |
| Dështon kufiri Mach/dendësi ose projektimi | Trajtojeni si ekzekutim të dështuar; shqyrtoni parametrat, kufizimet kohore, rezolucionin dhe regjimin fizik |
| Ekzekutimi i parë i përshpejtuar është i ngadaltë | Numba kompilon në përdorimin e parë; krahasoni ekzekutime pas kompilimit ose përdorni `benchmark` |

Në një nyje llogaritëse të largët, transferoni figurat/GIF-et që ju duhen në kompjuterin lokal për t'i parë. Nuk kërkohet desktop grafik në nyjen llogaritëse. Mos kërkoni threads mbi alokimin e scheduler-it.

## 18. Rruga e sugjeruar për takimin e parë me studentët

Konfirmoni mjedisin, ekzekutoni provën e vogël Couette dhe shikoni GIF-in. Më pas kryeni `validate.py`. Inspektoni animacionet e profilit të llogaritura më parë, përpara se të nisni një llogaritje të re më të gjatë. Në fund ndryshoni një parametër, ruani konfigurimin dhe diagnostikat dhe shkruani disa fjali interpretimi fizik.

Referenca zyrtare për mjedisin: [python3 venv](https://docs.python.org/3/library/venv.html), [udhëzuesi python3 Packaging](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) dhe [pip check](https://pip.pypa.io/en/stable/cli/pip_check/). Komandat e projektit dhe përshkrimet e modeleve janë kontrolluar kundrejt kodit të përfshirë. Një mjedis i ri Linux/python3 3.12 kaloi instalimin e bibliotekave, ekzekutimin e parë Couette, rigjenerimin e GIF-eve dhe të dy skriptet e kontrolleve numerike. Versionet dhe kontrollet gjenden te `verification/readme_installation.json`. Shembujt e aktivizimit Windows/macOS ndjekin sintaksën e dokumentuar të shell-it përkatës dhe nuk janë ekzekutuar këtu.
