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
from pathlib import Path

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


def serve_http(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a, **k: None  # pa zhurmë në terminal
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()


def display_name(user) -> str:
    return (getattr(user, "nickname", None) or getattr(user, "unique_id", None) or "anonim").strip()


async def emit_join_once(name: str) -> None:
    """TikTok nuk dërgon gjithmonë JoinEvent; hyrja e parë e çdo përdoruesi shfaqet si 'join'."""
    if name not in seen_users:
        seen_users.add(name)
        await broadcast({"type": "join", "user": name})


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
        await broadcast({"type": "join", "user": name})

    @client.on(GiftEvent)
    async def on_gift(event):
        # dhuratat me seri numërohen vetëm kur seria mbaron
        if event.gift.streakable and event.streaking:
            return
        name = display_name(event.user)
        await emit_join_once(name)
        await broadcast({
            "type": "gift", "user": name, "gift": event.gift.name,
            "diamonds": event.gift.diamond_count or 1,
            "count": event.repeat_count if event.gift.streakable else 1,
        })

    @client.on(LikeEvent)
    async def on_like(event):
        name = display_name(event.user)
        await emit_join_once(name)
        await broadcast({"type": "like", "user": name, "count": getattr(event, "count", 1) or 1})

    @client.on(CommentEvent)
    async def on_comment(event):
        name = display_name(event.user)
        await emit_join_once(name)
        await broadcast({"type": "chat", "user": name, "text": event.comment})

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
    ap.add_argument("--ws-port", type=int, default=8765)
    ap.add_argument("--http-port", type=int, default=8000)
    args = ap.parse_args()
    if not args.user and not args.demo:
        ap.error("jep --user @llogaria ose përdor --demo")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    serve_http(args.http_port)
    log.info("Hap në shfletues:  http://localhost:%d", args.http_port)

    async with websockets.serve(ws_handler, "0.0.0.0", args.ws_port):
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
