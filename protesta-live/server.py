#!/usr/bin/env python3
"""Serveri i lojës "Protesta Live" (pa TikTok brenda).

Shërben faqen e lojës dhe është "qendra" ku lidhen:
  - dritaret e lojës (dëgjojnë ngjarje),
  - ura e TikTok-ut (tiktok_bridge.py) që dërgon ngjarjet kur live-i hapet.
Kështu loja hapet kur të duash, dhe TikTok mund të lidhet më vonë ose të rilidhet.

    python server.py                 # loja, pa TikTok
    python server.py --demo          # loja me ngjarje të simuluara
"""
import argparse
import asyncio
import functools
import http.server
import json
import logging
import random
import os
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import websockets

log = logging.getLogger("loja")
ROOT = Path(__file__).resolve().parent
clients: set = set()
APP_ID = "protesta-live"
ALLOWED_AVATAR_HOSTS = ("tiktokcdn", "ibyteimg", "byteimg", "tiktokv", "byteoversea", "muscdn", "ibytedtos", "bytedance")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Shërben skedarët e lojës + /avatar?u=<url> (proxy për fotot e profilit të TikTok)."""

    def log_message(self, *a, **k):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")  # gjithmonë versioni i fundit i lojës
        super().end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/__id":  # për të njohur nëse porta mbahet nga një instancë e kësaj loje
            body = json.dumps({"app": APP_ID, "root": str(ROOT)}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if url.path != "/avatar":
            return super().do_GET()
        target = (parse_qs(url.query).get("u") or [""])[0]
        host = urlparse(target).hostname or ""
        if urlparse(target).scheme != "https" or not any(h in host for h in ALLOWED_AVATAR_HOSTS):
            self.send_error(400, "host i palejuar")
            return
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.tiktok.com/"})
            with urllib.request.urlopen(req, timeout=8) as r:
                body, ctype = r.read(3_000_000), r.headers.get("Content-Type", "image/jpeg")
        except Exception as e:
            log.warning("Foto e profilit nuk u shkarkua: %s", e)
            self.send_error(502, "foto e padisponueshme")
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


    def do_POST(self):
        if urlparse(self.path).path == "/__shutdown":  # instanca e re mbyll të vjetrën
            self.send_response(200)
            self.end_headers()
            threading.Timer(0.3, lambda: os._exit(0)).start()
            return
        self.send_error(404)


def stop_old_instance(port: int) -> bool:
    """Nëse porta mbahet nga një instancë e vjetër e kësaj loje, e mbyll."""
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/__id", timeout=2) as r:
            if json.loads(r.read()).get("app") != APP_ID:
                return False
        urllib.request.urlopen(urllib.request.Request(f"http://localhost:{port}/__shutdown", method="POST"), timeout=2)
        time.sleep(1.2)
        return True
    except Exception:
        return False


def find_edge():
    """Gjen msedge.exe (ose Chrome) në Windows."""
    bases = [os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")]
    for b in filter(None, bases):
        for rel in (r"Microsoft\Edge\Application\msedge.exe", r"Google\Chrome\Application\chrome.exe"):
            p = Path(b) / rel
            if p.exists():
                return str(p)
    return None


def open_window(http_port: int, ws_port: int, page: str = "") -> None:
    """Hap lojën si dritare pa shirit adresash. Përdor profil të veçantë të shfletuesit, që zëri të lejohet vetvetiu
    (--autoplay-policy) dhe të mos mbetet versioni i vjetër në cache."""
    url = f"http://localhost:{http_port}/{page}?ws=ws://localhost:{ws_port}&v={int(time.time())}"
    try:
        if sys.platform == "win32":
            exe = find_edge()
            profile = str(ROOT / ".shfletues-profil")
            args = [f"--app={url}", "--window-size=540,960", "--autoplay-policy=no-user-gesture-required",
                    "--disable-features=CalculateNativeWinOcclusion", "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding", "--disable-background-timer-throttling",
                    f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check"]
            if exe:
                subprocess.Popen([exe, *args])
            else:
                subprocess.Popen(["cmd", "/c", "start", "", "msedge", *args])
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception:
        log.info("Hape vetë në shfletues: %s", url)


def serve_http(port: int) -> None:
    handler = functools.partial(Handler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


async def broadcast(msg: dict, skip=None) -> None:
    data = json.dumps(msg, ensure_ascii=False)
    await asyncio.gather(*(c.send(data) for c in list(clients) if c is not skip), return_exceptions=True)


async def ws_handler(ws, *_):
    clients.add(ws)
    log.info("U lidh një klient (%d gjithsej)", len(clients))
    try:
        async for raw in ws:  # çdo gjë që dërgon ura e TikTok-ut u përcillet dritareve të lojës
            try:
                msg = json.loads(raw)
            except ValueError:
                continue
            await broadcast(msg, skip=ws)
    finally:
        clients.discard(ws)
        log.info("Një klient u shkëput (%d mbeten)", len(clients))


async def demo_events() -> None:
    names = ["Arbër", "Elira", "Dritan", "Blerta", "Gent", "Sara", "Kristi", "Ola"]
    while True:
        await asyncio.sleep(random.uniform(0.4, 1.6))
        n = random.choice(names) + str(random.randint(1, 99))
        r = random.random()
        if r < 0.4:
            await broadcast({"type": "join", "user": n})
        elif r < 0.8:
            d = random.choice([1, 1, 5, 10, 30, 30, 100, 500])
            await broadcast({"type": "gift", "user": n, "gift": "Demo", "diamonds": d, "count": random.randint(1, 3)})
        else:
            await broadcast({"type": "like", "user": n, "count": 3})


async def main() -> None:
    ap = argparse.ArgumentParser(description="Serveri i lojës Protesta Live")
    ap.add_argument("--demo", action="store_true", help="ngjarje të simuluara, pa TikTok")
    ap.add_argument("--ws-port", type=int, default=8124)
    ap.add_argument("--http-port", type=int, default=8123)
    ap.add_argument("--open", action="store_true", help="hap dritaren e lojës pasi serveri niset")
    ap.add_argument("--page", default="", help="faqja për të hapur, p.sh. klubi.html (parazgjedhje: protesta)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    try:
        try:
            serve_http(args.http_port)
        except OSError:
            if not stop_old_instance(args.http_port):
                raise
            log.info("U mbyll një instancë e vjetër e lojës në portën %d.", args.http_port)
            serve_http(args.http_port)
    except OSError:
        raise SystemExit(f"Porta {args.http_port} eshte e zene nga nje aplikacion tjeter. Provo: python server.py --http-port 9123")
    try:
        for attempt in range(3):  # porta e lidhjes mund të çlirohet pak më vonë nga instanca e vjetër
            try:
                ws_server = await websockets.serve(ws_handler, "0.0.0.0", args.ws_port)
                break
            except OSError:
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
    except OSError:
        raise SystemExit(f"Porta {args.ws_port} eshte e zene. Provo: python server.py --ws-port 9124")
    log.info("Folderi i lojës: %s", ROOT)
    if args.open:
        open_window(args.http_port, args.ws_port, args.page)
    log.info("LOJA GATI: hap http://localhost:%d   (TikTok lidhet më vonë me tiktok_bridge.py)", args.http_port)
    async with ws_server:
        if args.demo:
            await demo_events()
        else:
            await asyncio.Future()  # punon pafund


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
