#!/usr/bin/env python3
"""Ura mes TikTok LIVE dhe lojës "Protesta Live".

Lexon ngjarjet e live-it (hyrje, dhurata, like, komente) me bibliotekën
TikTokLive dhe i dërgon te faqja e lojës përmes WebSocket. Gjithashtu shërben
vetë index.html, kështu që mjafton një komandë:

    python server.py --user @emri_i_llogarise

Pa TikTok (vetëm provë):  python server.py --demo
"""
import argparse
import asyncio
import functools
import http.server
import json
import logging
import random
import threading
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import websockets

log = logging.getLogger("protesta")
ROOT = Path(__file__).resolve().parent
clients: set = set()
seen_users: set = set()


async def broadcast(msg: dict) -> None:
    if not clients:
        return
    data = json.dumps(msg, ensure_ascii=False)
    await asyncio.gather(*(c.send(data) for c in list(clients)), return_exceptions=True)


async def ws_handler(ws, *_):
    clients.add(ws)
    log.info("Loja u lidh (%d klientë)", len(clients))
    try:
        async for _ in ws:  # nuk presim mesazhe nga loja
            pass
    finally:
        clients.discard(ws)


ALLOWED_AVATAR_HOSTS = ("tiktokcdn", "ibyteimg", "byteimg", "tiktokv", "byteoversea")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Shërben skedarët e lojës + /avatar?u=<url> (proxy për fotot e profilit të TikTok)."""

    def log_message(self, *a, **k):
        pass

    def do_GET(self):
        url = urlparse(self.path)
        if url.path != "/avatar":
            return super().do_GET()
        target = (parse_qs(url.query).get("u") or [""])[0]
        host = urlparse(target).hostname or ""
        if urlparse(target).scheme != "https" or not any(h in host for h in ALLOWED_AVATAR_HOSTS):
            self.send_error(400, "host i palejuar")
            return
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                body, ctype = r.read(3_000_000), r.headers.get("Content-Type", "image/jpeg")
        except Exception:
            self.send_error(502, "foto e padisponueshme")
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def avatar_url(user) -> str:
    """Zgjedh një URL fotoje që shfletuesi e shfaq (jo HEIC) dhe e kalon nga proxy lokal."""
    for attr in ("avatar_large", "avatar_medium", "avatar_thumb"):
        img = getattr(user, attr, None)
        urls = getattr(img, "url_list", None) or getattr(img, "urls", None) or []
        for u in urls:
            if u.startswith("https://") and ".heic" not in u:
                return "/avatar?u=" + quote(u, safe="")
    return ""


def serve_http(port: int) -> None:
    handler = functools.partial(Handler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def display_name(user) -> str:
    return (getattr(user, "nickname", None) or getattr(user, "unique_id", None) or "anonim").strip()


async def emit_join_once(name: str, avatar: str = "") -> None:
    """TikTok nuk dërgon gjithmonë JoinEvent; hyrja e parë e çdo përdoruesi shfaqet si 'join'."""
    if name not in seen_users:
        seen_users.add(name)
        await broadcast({"type": "join", "user": name, "avatar": avatar})


def run_tiktok(unique_id: str):
    from TikTokLive import TikTokLiveClient
    from TikTokLive.events import CommentEvent, ConnectEvent, GiftEvent, JoinEvent, LikeEvent

    client = TikTokLiveClient(unique_id=unique_id)

    @client.on(ConnectEvent)
    async def on_connect(event):
        log.info("Lidhur me live-in e @%s", event.unique_id)

    @client.on(JoinEvent)
    async def on_join(event):
        name = display_name(event.user)
        seen_users.add(name)
        await broadcast({"type": "join", "user": name, "avatar": avatar_url(event.user)})

    @client.on(GiftEvent)
    async def on_gift(event):
        # dhuratat me seri numërohen vetëm kur seria mbaron
        if event.gift.streakable and event.streaking:
            return
        name = display_name(event.user)
        await emit_join_once(name, avatar_url(event.user))
        await broadcast({
            "type": "gift", "user": name, "avatar": avatar_url(event.user), "gift": event.gift.name,
            "diamonds": event.gift.diamond_count or 1,
            "count": event.repeat_count if event.gift.streakable else 1,
        })

    @client.on(LikeEvent)
    async def on_like(event):
        name = display_name(event.user)
        await emit_join_once(name, avatar_url(event.user))
        await broadcast({"type": "like", "user": name, "avatar": avatar_url(event.user), "count": getattr(event, "count", 1) or 1})

    @client.on(CommentEvent)
    async def on_comment(event):
        name = display_name(event.user)
        await emit_join_once(name, avatar_url(event.user))
        await broadcast({"type": "chat", "user": name, "avatar": avatar_url(event.user), "text": event.comment})

    return client


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
    ap = argparse.ArgumentParser(description="Ura TikTok LIVE -> Protesta Live")
    ap.add_argument("--user", help="@emri i llogarisë që është LIVE")
    ap.add_argument("--demo", action="store_true", help="ngjarje të simuluara, pa TikTok")
    ap.add_argument("--ws-port", type=int, default=8124)
    ap.add_argument("--http-port", type=int, default=8123)
    args = ap.parse_args()
    if not args.user and not args.demo:
        ap.error("jep --user @llogaria ose përdor --demo")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    try:
        serve_http(args.http_port)
    except OSError:
        raise SystemExit(f"Porta {args.http_port} eshte e zene nga nje aplikacion tjeter. Provo: python server.py --user @emri --http-port 9123")
    log.info("Hap në shfletues:  http://localhost:%d", args.http_port)

    try:
        ws_server = await websockets.serve(ws_handler, "0.0.0.0", args.ws_port)
    except OSError:
        raise SystemExit(f"Porta {args.ws_port} eshte e zene. Provo: python server.py --user @emri --ws-port 9124")
    async with ws_server:
        if args.demo:
            await demo_events()
        else:
            client = run_tiktok(args.user.lstrip("@"))
            await client.connect()  # bllokon derisa mbaron live-i


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
