#!/usr/bin/env python3
"""Gjeneron klipet e zërit shqip (assets/voice/*.mp3) nga voice_lines.json me zërat nervorë shqip të Microsoft
(sq-AL-AnilaNeural dhe sq-AL-IlirNeural). Kërkon internet. Nise një herë:   python make_voices.py
Përdor --force për t'i gjeneruar përsëri të gjitha."""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent
VOICES = {"anila": "sq-AL-AnilaNeural", "ilir": "sq-AL-IlirNeural"}


async def one(key: str, line: dict, out: Path, force: bool) -> bool:
    f = out / f"{key}.mp3"
    if f.exists() and f.stat().st_size > 1000 and not force:
        return True
    for attempt in range(3):
        try:
            comm = edge_tts.Communicate(line["text"], VOICES[line.get("voice", "anila")], rate=line.get("rate", "+0%"))
            await comm.save(str(f))
            return True
        except Exception as e:  # rrjeti, kufizim i përkohshëm etj.
            print(f"   provë {attempt + 1}/3 për {key}: {type(e).__name__}")
            await asyncio.sleep(2)
    return False


async def main() -> None:
    force = "--force" in sys.argv
    lines = json.loads((ROOT / "voice_lines.json").read_text(encoding="utf-8"))
    out = ROOT / "assets" / "voice"
    out.mkdir(parents=True, exist_ok=True)
    ok = 0
    for key, line in lines.items():
        good = await one(key, line, out, force)
        ok += good
        print(("✔ " if good else "✘ ") + f"{key}: {line['text']}")
    print(f"\nU bënë {ok}/{len(lines)} klipe te {out}")
    if ok < len(lines):
        print("Disa dështuan (kontrollo internetin) — nise përsëri; ato që u bënë nuk gjenerohen sërish.")


if __name__ == "__main__":
    asyncio.run(main())
