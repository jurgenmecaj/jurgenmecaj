# 🎮 Protesta Live – lojë satirike për TikTok LIVE

Lojë animacioni (vertikale 9:16) ku shikuesit që hyjnë në live shfaqen si protestues të vizatuar dhe me dhurata
"gjuajnë" bojë, gurë etj. mbi tre godina: **Bashkia, Kryeministria, Ministria e Arsimit**.
Në krye ka gjithmonë shënimin: *"Kjo është vetëm një lojë · animacion satirik · pa dhunë reale"*.

## Çfarë ndodh në ekran
| Ngjarje në live | Efekti |
|---|---|
| Dikush hyn | Del figurë e animuar + banderola **"SAPO IU BASHKUA PROTESTËS: @emri"** |
| Dhuratë 💎1+ | 🎨 Bojë (balonë me bojë) |
| Dhuratë 💎10+ | 💥 Bombë me bojë (njolla të mëdha) |
| Dhuratë 💎30+ | 🪨 Gur (çarje në godinë) |
| Dhuratë 💎100+ | 🔥 Molotov (animacion: zjarr, tym, shkulm) |
| Dhuratë 💎500+ | 🎆 FINALE (të gjithë gjuajnë, fishekzjarre) |
| Like | Gjuajtje e vogël me bojë |
| Koment `!bashkia` `!kryeministria` `!arsimi` | Zgjedh objektivin e vet (përndryshe random) |

Çdo godinë ka shkallë **ZEMËRIMI**; kur arrin 100% mbulohet me ngjyra, pastrohet dhe fillon raundi i ri.
Ka edhe renditje (top 3 gjuajtësit), statistika dhe zë (mund ta çosh me `?mute=1`).

## Foto
- **Fotot e profilit të shikuesve**: fytyra e personazhit është fotoja e vërtetë e shikuesit (me rreth ngjyrë), dhe del edhe në
  banderolën "Sapo iu bashkua protestës". Serveri i shkarkon fotot nga TikTok përmes `/avatar` (vetëm host-e të TikTok).
  Pa foto, personazhi ka fytyrë të vizatuar me shirit protestuesi.
- **Foto reale të godinave**: janë në `assets/` si PNG me sfond transparent (`bashkia.png`, `kryeministria.png`, `arsimi.png`).
  Boja, çarjet dhe zjarri prehen saktësisht mbi formën e godinës. Për t'i ndërruar, zëvendëso skedarët me të njëjtat emra
  (PNG me sfond transparent, ~700–900px, nën 1 MB). Nëse mungojnë, loja përdor godinat e vizatuara.

## Të reja në lojë
- 👑 Kurorë dhe kornizë e artë për gjuajtësin #1 në renditje
- 🔥 **COMBO ×N** kur gjuajnë shumë njerëz njëkohësisht
- 📣 Çdo ~25 sekonda turma thërret **MJAFT! / DREJTËSI! / ARSIM PËR TË GJITHË!** dhe kërcen
- 🔦 Drita kërkuese në qiell, godinat me pamje nate, shkëlqim i kuq kur zemërimi kalon 50%

## 🚔 Policia (animacion satirik)
Rreth çdo 100 sekonda vjen policia me sirenë: hedh gaz tymi, i kap protestuesit dhe i largon nga skena (deri 16 për raund).
Të ndaluarit shfaqen në një shirit të kuq/blu. **LIKE i kthen**: kur një i ndaluar jep like kthehet vetë,
ndërsa like nga të tjerët kthejnë të ndaluarit një nga një. Një dhuratë e kthen gjithashtu.
- Shpeshtësia: `?police=60` (çdo 60 s), `?police=0` e fikë. Tasti `P` e nis menjëherë (provë).
- Nga serveri: dërgo `{"type": "police"}` te WebSocket për ta thirrur me dorë.

## Provë e shpejtë (pa TikTok)
Hape `index.html` në shfletues me `?demo=1` (simulim automatik), ose pa parametra dhe shtyp:
`J` hyrje · `P` policia · `1`–`5` dhurata (nivelet) · `L` like · `M` zë on/off.

## Windows: me një klik
Dyfisho **`start.bat`** (instalon bibliotekat, hap dritaren e lojës dhe lidhet me `@partiamegrada`).
`start.bat @emri` për llogari tjetër, `start.bat demo` për provë pa TikTok.

## Lidhja me live-in real (Python)
```bash
cd protesta-live
pip install -r requirements.txt
python server.py --user @llogaria_jote      # duhet të jesh LIVE
# hap http://localhost:8000
```
`python server.py --demo` nis serverin me ngjarje të simuluara. Porte: `--http-port`, `--ws-port`.

Nëse `pip install` dështon te `protobuf3-to-dict` (ndodh me Python shumë të ri ose setuptools të vjetër), provo:
```bash
pip install -U pip setuptools wheel
pip install -r requirements.txt
# nëse prapë dështon:
pip install --no-deps TikTokLive && pip install TikTokLiveProto==0.2.2 betterproto2==0.9.1 EulerApiSdk==0.1.0 websockets_proxy==0.1.3 "python-socks[asyncio]" httpx pyee==13.0.1 ffmpy websockets
```

## Si e shfaq në TikTok LIVE
1. **TikTok LIVE Studio / OBS**: shto *Browser Source* (ose Window Capture) me `http://localhost:8000`, madhësia **1080×1920**.
2. Nise live-in nga LIVE Studio/OBS (TikTok kërkon kushte llogarie për transmetim nga kompjuteri).
3. Telefoni ose kompjuteri duhet të jetë i njëjti ku vrapon `server.py`.

## Shënime
- Biblioteka `TikTokLive` është **jozyrtare**; ngjarja "join" nuk dërgohet gjithmonë nga TikTok. Prandaj serveri e shfaq si
  "join" edhe herën e parë që një përdorues bën like, koment ose dhuratë.
- Për të ndryshuar emra/pragje të dhuratave ose objektivat shih `TIERS` dhe `BUILD` në krye të `index.html`.
- **Kujdes me rregullat e TikTok**: imazhet me armë/zjarrvënie dhe sulme ndaj institucioneve mund të shënohen nga moderimi
  edhe si animacion. Nëse të kufizojnë live-in, riemërto "Molotov" në diçka si "Shishe me bojë" te `TIERS`.
