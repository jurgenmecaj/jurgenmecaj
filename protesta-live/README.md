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

## Provë e shpejtë (pa TikTok)
Hape `index.html` në shfletues me `?demo=1` (simulim automatik), ose pa parametra dhe shtyp:
`J` hyrje · `1`–`5` dhurata (nivelet) · `L` like · `M` zë on/off.

## Lidhja me live-in real (Python)
```bash
cd protesta-live
pip install -r requirements.txt
python server.py --user @llogaria_jote      # duhet të jesh LIVE
# hap http://localhost:8000
```
`python server.py --demo` nis serverin me ngjarje të simuluara. Porte: `--http-port`, `--ws-port`.

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
