# Fizika dhe algoritmet

Përshtatur nga shpjegimet e notebook-ut origjinal. Kodi përkatës ndodhet në dosjen `fluidlab/`.

## 1. Çfarë presim nga një fluid?

Imagjinoni dy pllaka me fluid mes tyre. Nëse lëviz pllaka e sipërme, fluidi pranë saj fillon të lëvizë; pas një kohe, lëvizja transmetohet edhe në shtresat më të largëta. Ky transmetim i impulsit lidhet me viskozitetin. Kushti i mosrrëshqitjes thotë se shpejtësia e fluidit në një sipërfaqe të ngurtë është shpejtësia e vetë sipërfaqes.

Në një kanal me një pengesë, ruajtja e masës kërkon që fluidi të devijojë. Presioni ndryshon për të mbështetur këtë devijim; viskoziteti dhe inercia përcaktojnë strukturën e gjurmës së rrjedhjes pas trupit. Para çdo figure, parashikoni ku shpejtësia do të jetë më e madhe dhe ku mund të krijohet kthim lokal i rrjedhjes.

Përdorim dendësinë $\rho$, viskozitetin dinamik $\mu$ dhe viskozitetin kinematik $\nu=\mu/\rho$. Numri Reynolds është
$$\mathrm{Re}=\frac{UD}{\nu}.$$
Ai krahason efektet inerciale me efektet viskoze. Për shembujt me trupa, $U$ është shpejtësia **mesatare** në hyrje dhe $D$ diametri ose gjerësia e referencës; për elipsin përdorim boshtin e vogël $D$, të deklaruar qartë. Shpejtësia maksimale e profilit parabolik është afërsisht $1.5U$.

Koha karakteristike e kalimit pranë trupit është $D/U$ dhe koha pa përmasa është $t^*=tU/D$. Koha e simulimit nuk është koha e pritjes në kompjuter. Në kanalet tona $H=1$, $L=6$, $U=1$ dhe zakonisht $D=0.25$ në njësi të zgjedhura në mënyrë konsistente. Nëse doni njësi SI, caktoni të gjitha gjatësitë në metra dhe $U$ në m/s; presioni jepet për dendësi reference $\rho_0=1$.

## 2. Couette dhe Poiseuille: fillojmë me një problem që e kontrollojmë

Për një rrjedhje të zhvilluar plotësisht midis pllakave, $\mathbf{u}=(u(y,t),0)$. Termi konvektiv zhduket sepse $\partial_xu=0$. Ekuacioni i impulsit reduktohet në
$$\partial_tu=\nu\partial_{yy}u+g,$$
ku $g=-\rho^{-1}\partial_xp$ është përshpejtimi nga gradienti i presionit. Në Couette kemi $g=0$, $u(0)=0$ dhe $u(H)=U_w$; në Poiseuille kemi $g>0$ dhe të dyja pllakat të palëvizshme.

Në gjendjen e qëndrueshme, integrimi i dytë dhe kushtet në kufi japin
$$u_C(y)=U_w\frac yH,\qquad u_P(y)=\frac{g}{2\nu}y(H-y).$$
Profili linear nuk do të thotë se viskoziteti mungon: viskoziteti përcakton sa shpejt arrihet kjo gjendje. Në Poiseuille, ndryshimi i $\nu$ ndryshon edhe amplitudën e profilit për të njëjtin $g$.

Zëvendësojmë derivatin e dytë me diferencën qendrore dhe derivatin kohor me Euler-in përpara:
$$u_j^{n+1}=u_j^n+\Delta t\left[\nu\frac{u_{j+1}^n-2u_j^n+u_{j-1}^n}{\Delta y^2}+g\right].$$
Ky është një algoritëm i plotë, jo thirrje e një biblioteke fluidesh. Për problemin e difuzionit kërkohet $\nu\Delta t/\Delta y^2\leq1/2$; zgjedhim 0.45. Nëse përgjysmojmë hapin hapësinor, duhet afërsisht ta ndajmë hapin kohor me katër.

Funksioni `plate_fd` ndodhet në `fluidlab/conventional.py`. Lexoni kushtet në kufi, ndryshimin e `u[1:-1]` dhe zgjedhjen e `dt`.

**Si lexohet figura?** Në Couette, pjesa pranë pllakës lëvizëse përgjigjet e para. Në Poiseuille, forca vepron në vëllim, por pllakat e mbajnë fluidin pranë sipërfaqeve të palëvizshëm. Koha karakteristike e difuzionit është e rendit $H^2/\nu$; afrimi i plotë drejt profilit analitik varet nga toleranca që kërkojmë.

Gabimi i raportuar është $\|u_{num}-u_{anal}\|_2/\|u_{anal}\|_2$. Ai përmban edhe gabimin nga koha e fundme e simulimit. Një krahasim hapësinor duhet bërë kur efekti i startup-it është bërë mjaft i vogël.

**Provoni:** përgjysmoni $\nu$ në Couette. A ndryshon profili përfundimtar apo vetëm ritmi i afrimit? Pastaj përgjysmoni $\nu$ në Poiseuille duke mbajtur $g$ të pandryshuar. Shpjegoni ndryshimin para se të ekzekutoni kodin.

## 3. Nga profili njëdimensional te Navier–Stokes

Për një fluid me dendësi konstante, ruajtja e masës jep $\nabla\cdot\mathbf{u}=0$. Ekuacioni i impulsit është
$$\partial_t\mathbf{u}+(\mathbf{u}\cdot\nabla)\mathbf{u}=-\frac1\rho\nabla p+\nu\nabla^2\mathbf{u}.$$
Termi konvektiv transporton impulsin, gradienti i presionit përshpejton fluidin dhe termi viskoz shpërndan dallimet e shpejtësisë. Presioni në problemin inkompresibël është një madhësi që siguron përputhjen e shpejtësisë me ruajtjen e masës.

Në rrjetën MAC, $p$ ndodhet në qendrat e qelizave, $u$ në faqet vertikale dhe $v$ në faqet horizontale. Fluksi që del nga një qelizë është shuma e flukseve në faqet e saj. Ky vendosim ndihmon që gradienti dhe divergjenca diskrete të përputhen.

**Projektimi i presionit** realizohet në tri hapa:
$$\mathbf{u}^*=\mathbf{u}^n+\Delta t[-(\mathbf{u}\cdot\nabla)\mathbf{u}+\nu\nabla^2\mathbf{u}],$$
$$\nabla^2p^{n+1}=\frac{\rho}{\Delta t}\nabla\cdot\mathbf{u}^*,$$
$$\mathbf{u}^{n+1}=\mathbf{u}^*-\frac{\Delta t}{\rho}\nabla p^{n+1}.$$
Duke marrë divergjencën e hapit të fundit dhe përdorur ekuacionin e Poisson-it, marrim divergjencë zero në rrjetën diskrete deri në saktësinë e zgjidhësit linear.

Kodi ndërton ekuacionin e Poisson-it **vetëm në fluid**, mbyll faqet që prekin trupin dhe fikson presionin në daljen e kanalit. Në kufijtë e ngurtë zbatohen kushtet normale dhe vlera fantazmë për komponentët tangjencialë. Konturi i lakuar mbetet një afrim me shkallëzime. Thjesht zerimi i shpejtësisë brenda trupit pas një hapi nuk do të mjaftonte për këtë përputhje.

Për transportin përdorim fillimisht upwind të rendit të parë. Kjo zgjedhje është e thjeshtë, por shton difuzion numerik. Hapi kohor kontrollohet nga transporti dhe difuzioni. Për shembullin me vorbulla përdorim edhe variantin central, me një kufizim shtesë të hapit kohor që varet nga viskoziteti. Më pak difuzion numerik nuk nënkupton automatikisht më shumë qëndrueshmëri.

## 4. Gjeometria: një maskë e përbashkët për të dyja metodat

Një maskë logjike identifikon qelizat e trupit. Ndryshojmë gjeometrinë pa ndryshuar ekuacionet e fluidit. Drejtkëndëshi, cilindri, elipsi i rrotulluar dhe dy cilindrat përfaqësohen nga pabarazi të thjeshta në koordinata.

Për krahasimin me D2Q9 kërkojmë qeliza katrore: $L/N_x=H/N_y$. Cilindri vendoset në $(L/4,H/2)$, larg daljes. Ky konfigurim është mësimor dhe **nuk është konfigurimi identik i benchmark-ut DFG**. Vlerat e forcave nga ai benchmark nuk vlejnë si referencë për këtë kanal.

## 5. Lattice Boltzmann: i njëjti fluid, ndryshore të tjera

Në një nyje ruajmë nëntë popullata $f_i$. Ato janë një model i shpërndarjes në shpejtësi diskrete, jo nëntë molekula të veçanta. D2Q9 do të thotë dy përmasa dhe nëntë drejtime: pushim, katër drejtime boshtore dhe katër diagonale. Në një hap kohor, një popullatë lëviz drejt një nyjeje fqinje përgjatë drejtimit të saj.

Momentet e popullatave japin
$$\rho=\sum_i f_i,\qquad \rho\mathbf{u}=\sum_i f_i\mathbf{c}_i.$$
Kur përdorim forcë, shpejtësia përfshin edhe korrigjimin gjysmë-hap; kjo zbatohet në shembullin Poiseuille me forcimin Guo.

Për D2Q9, peshat janë $w_0=4/9$, $w_{1\ldots4}=1/9$ dhe $w_{5\ldots8}=1/36$. Ekuilibri i rendit të dytë në shpejtësi është
$$f_i^{eq}=w_i\rho[1+3\mathbf{c}_i\cdot\mathbf{u}+\tfrac92(\mathbf{c}_i\cdot\mathbf{u})^2-\tfrac32u^2].$$
Collision BGK relakson popullatat drejt këtij ekuilibri:
$$f_i^*=f_i-\frac1\tau(f_i-f_i^{eq}).$$
Streaming i zhvendos: $f_i(\mathbf{x}+\mathbf{c}_i,t+1)=f_i^*(\mathbf{x},t)$. Në kushte të përshtatshme, momentet e kësaj dinamike riprodhojnë ekuacionet e rrjedhjes në kufirin hidrodinamik me Mach të vogël. Kjo nuk e bën fluidin saktësisht inkompresibël në çdo hap.

Në lidhjet që prekin një sipërfaqe të ngurtë, bounce-back pasqyron popullatën në drejtimin e kundërt. Në këtë kod, sipërfaqja efektive qëndron në mes të lidhjes mes nyjes së fluidit dhe nyjes së ngurtë. Për pllakën lëvizëse shtojmë korrigjimin e impulsit që përputhet me shpejtësinë e saj.

**Njësitë janë pjesë e algoritmit.** Në rrjetën standarde vendosim $\Delta x_{LB}=\Delta t_{LB}=1$ dhe $c_s^2=1/3$:
$$\nu_{LB}=\frac13(\tau-\tfrac12),\quad u_{LB}=u_{phys}\frac{\Delta t_{phys}}{\Delta x_{phys}},\quad \nu_{LB}=\nu_{phys}\frac{\Delta t_{phys}}{\Delta x_{phys}^2}.$$
Zgjedhim $U_{LB}=0.035$, pastaj $\Delta t_{phys}=\Delta x_{phys}U_{LB}/U_{phys}$ dhe nxjerrim $\tau$. Pra $\tau$ nuk është një rregullues i pavarur nëse duam të ruajmë Re.

Presioni relativ llogaritet si
$$p_{phys}-p_{out}=\frac{\rho_{LB}-1}{3}\left(\frac{\Delta x_{phys}}{\Delta t_{phys}}\right)^2$$
për $\rho_0=1$. Mach-u lokal është $\sqrt3\,|\mathbf{u}_{LB}|$. Vlera $\tau>1/2$ siguron viskozitet pozitiv, por nuk garanton qëndrueshmëri.

Në shembujt e hapur përdorim **rezervuarë ekuilibri të rendit të parë** në hyrje/dalje, me hyrje që rritet gradualisht. Në hyrje ekstrapolojmë dendësinë dhe imponojmë shpejtësinë; në dalje fiksojmë dendësinë në 1 dhe ekstrapolojmë shpejtësinë. Kjo zgjedhje është e thjeshtë për mësim, por mund të reflektojë valë. Nuk është kufiri Zou–He dhe nuk pretendojmë se ka të njëjtën saktësi. Shembujt e pllakave përdorin periodicitet përgjatë rrjedhjes dhe nuk kanë këtë kufi të hapur.

Tani e kontrollojmë LBM me **të njëjtat zgjidhje analitike**. Solver-i i pllakave zgjedh hapin kohor për të pasur të njëjtin viskozitet fizik dhe të njëjtën kohë fizike. Në LBM, nyjet e fluidit janë në qendrat e shtresave; në diferencat fundore të profilit 1D, pikat përfshijnë edhe kufijtë. Prandaj nuk krahasojmë indekset verbërisht, por koordinatat fizike.

## 6. Grafikët: çfarë na tregon secila madhësi?

Moduli i shpejtësisë është $|\mathbf{u}|=\sqrt{u^2+v^2}$. Vijat e rrjedhjes janë tangjente me fushën **e çastit** të shpejtësisë. Në rrjedhje të ndryshueshme në kohë, ato nuk përputhen në përgjithësi me trajektoret e grimcave gjurmuese.

Vorticiteti në plan është $\omega_z=\partial_xv-\partial_yu$. Shenja dallon drejtimet e kundërta të rrotullimit lokal. Nuk duhet të identifikojmë çdo zonë me vorticitet të madh si një vorbull të shkëputur: edhe shtresa e prerjes pranë një muri ka vorticitet.

Në figurat e veçanta shkallët e ngjyrave mund të përshtaten me rastin; krahasimet në skriptin `08_krahasimi_cfd_lbm.py` përdorin një shkallë të përbashkët. Presioni në të dyja metodat referohet ndaj daljes. Vorticiteti pranë konturit me shkallëzime është veçanërisht i ndjeshëm ndaj rrjetës.
