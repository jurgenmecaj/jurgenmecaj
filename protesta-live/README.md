# 🎮 Protesta Live – lojë satirike për TikTok LIVE

Lojë animacioni (vertikale 9:16) ku shikuesit që hyjnë në live shfaqen si protestues të vizatuar dhe me dhurata
"gjuajnë" bojë, gurë etj. mbi tre godina: **Bashkia, Kryeministria, Ministria e Arsimit**.
Në krye ka gjithmonë shënimin: *"Kjo është vetëm një lojë · animacion satirik · pa dhunë reale"*.

## Çfarë ndodh në ekran
| Ngjarje në live | Efekti |
|---|---|
| Dikush hyn | Del figurë e animuar + banderola **"SAPO IU BASHKUA PROTESTËS: @emri"** |
| Dhuratë 💎1+ | 🪨 Guralec (çarje e vogël) |
| Dhuratë 💎10+ | 🪨 Gur (çarje e madhe, pluhur) |
| Dhuratë 💎30+ | ⛰️ Shkëmb (çarje shumë të mëdha, copa) |
| Dhuratë 💎100+ | 🔥 Molotov (animacion: zjarr, tym, shkulm) |
| Dhuratë 💎500+ | 🎆 FINALE (të gjithë gjuajnë, fishekzjarre) |
| Like | Guralec i vogël |
| Koment `!bashkia` `!kryeministria` `!arsimi` | Zgjedh objektivin e vet (përndryshe random) |

Çdo godinë ka shkallë **ZEMËRIMI**; kur arrin 100% është goditur plotësisht, riparohet dhe fillon raundi i ri.
Ka edhe renditje (top 3 gjuajtësit), statistika dhe zë (mund ta çosh me `?mute=1`).

## Foto
- **Fotot e profilit të shikuesve**: fytyra e personazhit është fotoja e vërtetë e shikuesit (me rreth ngjyrë), dhe del edhe në
  banderolën "Sapo iu bashkua protestës". Serveri i shkarkon fotot nga TikTok përmes `/avatar` (vetëm host-e të TikTok).
  Pa foto, personazhi ka fytyrë të vizatuar me shirit protestuesi.
- **Foto reale të godinave**: janë në `assets/` si PNG me sfond transparent (`bashkia.png`, `kryeministria.png`, `arsimi.png`).
  Çarjet dhe zjarri prehen saktësisht mbi formën e godinës. Për t'i ndërruar, zëvendëso skedarët me të njëjtat emra
  (PNG me sfond transparent, ~700–900px, nën 1 MB). Nëse mungojnë, loja përdor godinat e vizatuara.

## Të reja në lojë
- 👑 Kurorë dhe kornizë e artë për gjuajtësin #1 në renditje
- 🔥 **COMBO ×N** kur gjuajnë shumë njerëz njëkohësisht
- 📣 Çdo ~25 sekonda turma thërret **MJAFT! / DREJTËSI! / ARSIM PËR TË GJITHË!** dhe kërcen
- 🔦 Drita kërkuese në qiell, godinat me pamje nate, shkëlqim i kuq kur zemërimi kalon 50%

## Më shumë për t'i mbajtur shikuesit
- **Secili godet secilën godinë**: shkruaj `1`, `2` ose `3` në chat për të zgjedhur godinën (ose `!bashkia` etj.). Pa zgjedhje, çdo shikues
  gjuan radhazi në të tria godinat (jo vetëm random). Dhurata me shumë copë shpërndahet nëpër të tria.
- **Nivele** (⭐ pranë emrit): fitohen me dhurata, like dhe komente; ruhen edhe kur shikuesi kthehet ("MIRËSEARDHE PËRSËRI · NIVELI n").
- **Sfida çdo 40–70 s**: *Sondazh* (shkruaj 1/2/3 → të gjithë sulmojnë godinën fituese), *Like* (X like në 25 s) ose *Chat* (shkruaj MJAFT × X). Sukses = fishekzjarre.
- **FITORE E PËRBASHKËT** kur të tre godinat goditen plotësisht; numëruesi 🏆 në ekran.
- **Numërim mbrapsht për policinë** (10…1 me tik) dhe kohëmatës në shiritin e poshtëm.
- **Karta e HERO-it** në mes të ekranit për dhurata të mëdha (💎100+ në total).

## 🚔 Policia (animacion satirik)
Rreth çdo 100 sekonda vjen policia me sirenë: hedh gaz tymi, i kap protestuesit dhe i largon nga skena (deri 16 për raund).
Të ndaluarit shfaqen në një shirit të kuq/blu. **LIKE i kthen**: kur një i ndaluar jep like kthehet vetë,
ndërsa like nga të tjerët kthejnë të ndaluarit një nga një. Një dhuratë e kthen gjithashtu.

**Dhuratat godasin policinë** (vetëm gjatë ardhjes së saj dhe vetëm 💎10+, jo lulet; ndryshon me `?copmin=20`):
gur (💎10+) → policia mpaket 2 s; shkëmb/molotov (💎30+) → policia rrëzohet 5–7 s dhe **e lë të lirë** protestuesin që po merrte; sa e rrëzon 2 herë, tërhiqet.
💎500+ (FINALE) i largon të gjithë policët.
- Shpeshtësia: `?police=60` (çdo 60 s), `?police=0` e fikë. Tasti `P` e nis menjëherë (provë).
- Nga serveri: dërgo `{"type": "police"}` te WebSocket për ta thirrur me dorë.

## Provë e shpejtë (pa TikTok)
Hape `index.html` në shfletues me `?demo=1` (simulim automatik), ose pa parametra dhe shtyp:
`J` hyrje · `P` policia · `1`–`5` dhurata (nivelet) · `L` like · `M` zë on/off.

## Windows: dy skedarë të ndarë
1. **`1-LOJA.bat`** — hap lojën (server + dritare). Pa TikTok; mund ta hapësh kur të duash. `1-LOJA.bat demo` për provë.
2. **`2-TIKTOK.bat`** — lidhet me live-in e `@partiamegrada`. Mund ta nisësh para ose pas live-it: provon vetë çdo 5 s derisa
   live-i të hapet, dhe rilidhet nëse ndërpritet. `2-TIKTOK.bat @emri` për llogari tjetër.

Porta të tjera: `1-LOJA.bat 9123 9124` dhe `2-TIKTOK.bat @emri 9124`.
Diagnostikim: hap `http://localhost:8123/?debug=1` — në fund të majtë shfaq statusin e lidhjes, fotove të godinave dhe fotove të profilit.

## Lidhja me live-in real (Python)
```bash
cd protesta-live
pip install -r requirements.txt
python server.py                              # loja (http://localhost:8123)
python tiktok_bridge.py --user @llogaria_jote # në një terminal tjetër; pret derisa live-i të hapet
```
`python server.py --demo` nis lojën me ngjarje të simuluara. Porta: `--http-port`, `--ws-port` (dhe `--ws-port` te `tiktok_bridge.py`).

Nëse `pip install` dështon te `protobuf3-to-dict` (ndodh me Python shumë të ri ose setuptools të vjetër), provo:
```bash
pip install -U pip setuptools wheel
pip install -r requirements.txt
# nëse prapë dështon:
pip install --no-deps TikTokLive && pip install TikTokLiveProto==0.2.2 betterproto2==0.9.1 EulerApiSdk==0.1.0 websockets_proxy==0.1.3 "python-socks[asyncio]" httpx pyee==13.0.1 ffmpy websockets
```

## Si e shfaq në TikTok LIVE
1. **TikTok LIVE Studio / OBS**: shto *Browser Source* (ose Window Capture) me `http://localhost:8123`, madhësia **1080×1920**.
2. Nise live-in nga LIVE Studio/OBS (TikTok kërkon kushte llogarie për transmetim nga kompjuteri).
3. Telefoni ose kompjuteri duhet të jetë i njëjti ku vrapon `server.py`.

## Shënime
- Biblioteka `TikTokLive` është **jozyrtare**; ngjarja "join" nuk dërgohet gjithmonë nga TikTok. Prandaj serveri e shfaq si
  "join" edhe herën e parë që një përdorues bën like, koment ose dhuratë.
- Për të ndryshuar emra/pragje të dhuratave ose objektivat shih `TIERS` dhe `BUILD` në krye të `index.html`.
- **Kujdes me rregullat e TikTok**: imazhet me armë/zjarrvënie dhe sulme ndaj institucioneve mund të shënohen nga moderimi
  edhe si animacion. Nëse të kufizojnë live-in, riemërto "Molotov" në diçka si "Shishe me bojë" te `TIERS`.
