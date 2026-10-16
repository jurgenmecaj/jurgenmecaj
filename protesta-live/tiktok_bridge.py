#!/usr/bin/env python3
"""Ura e TikTok-ut për "Protesta Live" — punon VEÇ nga loja.

Mund ta nisësh para ose pas hapjes së lojës, dhe para ose pas nisjes së live-it:
provon vetë çdo disa sekonda derisa live-i të hapet, dhe rilidhet nëse ndërpritet.

    python tiktok_bridge.py --user @partiamegrada
"""
import argparse
import asyncio
import json
import logging

import websockets

log = logging.getLogger("tiktok")
seen_users: set = set()


class Hub:
    """Lidhja me serverin e lojës; rilidhet vetë nëse loja mbyllet dhe hapet përsëri."""

    def __init__(self, url: str):
        self.url, self.ws = url, None

    async def keep_connected(self):
        while True:
            try:
                async with websockets.connect(self.url) as ws:
                    self.ws = ws
                    log.info("U lidha me lojën (%s)", self.url)
                    await self.send({"type": "status", "state": self.state})
                    await ws.wait_closed()
            except Exception:
                pass
            if self.ws is not None:
                log.info("Loja nuk është e hapur. Po pres…")
            self.ws = None
            await asyncio.sleep(3)

    state = "waiting"

    async def send(self, msg: dict):
        if self.ws is None:
            return
        try:
            await self.ws.send(json.dumps(msg, ensure_ascii=False))
        except Exception:
            self.ws = None


def display_name(user) -> str:
    return (getattr(user, "nickname", None) or getattr(user, "unique_id", None) or "anonim").strip()


def avatar_url(user) -> str:
    """URL e fotos që shfletuesi e shfaq (jo HEIC); loja e merr përmes /avatar të serverit."""
    from urllib.parse import quote
    for attr in ("avatar_jpg", "avatar_large", "avatar_medium", "avatar_thumb"):
        img = getattr(user, attr, None)
        urls = getattr(img, "url_list", None) or getattr(img, "urls", None) or []
        for u in urls:
            if u.startswith("https://") and ".heic" not in u:
                return "/avatar?u=" + quote(u, safe="")
    return ""


def make_client(unique_id: str, hub: Hub):
    from TikTokLive import TikTokLiveClient
    from TikTokLive.events import CommentEvent, ConnectEvent, GiftEvent, JoinEvent, LikeEvent

    client = TikTokLiveClient(unique_id=unique_id)

    async def join_once(name, user):
        if name not in seen_users:  # TikTok nuk dërgon gjithmonë JoinEvent
            seen_users.add(name)
            await hub.send({"type": "join", "user": name, "avatar": avatar_url(user)})

    @client.on(ConnectEvent)
    async def on_connect(event):
        hub.state = "connected"
        log.info("✅ LIDHUR me live-in e @%s", event.unique_id)
        await hub.send({"type": "status", "state": "connected"})

    @client.on(JoinEvent)
    async def on_join(event):
        name = display_name(event.user)
        seen_users.add(name)
        await hub.send({"type": "join", "user": name, "avatar": avatar_url(event.user)})

    @client.on(GiftEvent)
    async def on_gift(event):
        if event.gift.streakable and event.streaking:  # numërohet kur seria mbaron
            return
        name = display_name(event.user)
        await join_once(name, event.user)
        await hub.send({"type": "gift", "user": name, "avatar": avatar_url(event.user), "gift": event.gift.name,
                        "diamonds": event.gift.diamond_count or 1, "count": event.repeat_count if event.gift.streakable else 1})

    @client.on(LikeEvent)
    async def on_like(event):
        name = display_name(event.user)
        await join_once(name, event.user)
        await hub.send({"type": "like", "user": name, "avatar": avatar_url(event.user), "count": getattr(event, "count", 1) or 1})

    @client.on(CommentEvent)
    async def on_comment(event):
        name = display_name(event.user)
        await join_once(name, event.user)
        await hub.send({"type": "chat", "user": name, "avatar": avatar_url(event.user), "text": event.comment})

    return client


async def run(user: str, ws_url: str, retry: int) -> None:
    hub = Hub(ws_url)
    asyncio.create_task(hub.keep_connected())
    while True:
        hub.state = "waiting"
        try:
            log.info("Po provoj të lidhem me live-in e @%s …", user)
            await make_client(user, hub).connect()  # bllokon derisa live-i mbaron
            log.info("Live-i u ndërpre. Po provoj përsëri…")
        except Exception as e:
            kind = type(e).__name__
            if "Offline" in kind or "offline" in str(e).lower():
                log.info("Live-i nuk është hapur ende. Provoj përsëri pas %ds…", retry)
            else:
                log.warning("Nuk u lidh (%s: %s). Provoj përsëri pas %ds…", kind, str(e)[:120], retry)
        await hub.send({"type": "status", "state": "waiting"})
        await asyncio.sleep(retry)


def main() -> None:
    ap = argparse.ArgumentParser(description="Ura TikTok LIVE -> Protesta Live")
    ap.add_argument("--user", required=True, help="@emri i llogarisë që bën LIVE")
    ap.add_argument("--ws-port", type=int, default=8124, help="porta e lidhjes së lojës")
    ap.add_argument("--retry", type=int, default=5, help="sekonda mes provave të lidhjes")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    try:
        asyncio.run(run(args.user.lstrip("@"), f"ws://localhost:{args.ws_port}", args.retry))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
