# The World Today — 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/KuroriShizuri/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/KuroriShizuri/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

Entry for make.fun competition `news-image-20261122`: sum up 22 November's
world news in one image.

`main.py` (Python 3.13, stdlib only, no network) copies the bundled
cover artwork `entry.png` (1024×1024 JPEG, 263,980 bytes — under the
1 MiB limit) to `<MAKEFUN_OUTPUT_DIR>/entry.png` (`/output` by default).
Before copying it checks the JPEG magic bytes and validates the dimensions
are exactly 1024×1024 (read from the SOF marker), and after copying it
verifies the copy by file size and SHA-256 digest, then prints the byte
count. The copy is byte-identical on every run.

## What the cover shows

A broadsheet front page, "THE WORLD TODAY — Sunday 22 November 2026":
one hero story across the top and six more in a 2×3 grid below, each with
a flat illustration and a short bold headline. Every headline is spelled
exactly as reported that day.

Researched from the day's reporting (22 November 2026):

1. **Russian missiles land in Poland** — missiles and a drone landed in
   Poland (NATO territory) during a massive strike on Ukraine; Poland
   calls it a deliberate provocation, NATO calls it a grave violation.
   Shown as missile trails over a night city skyline — the hero panel
   across the top.
2. **Wall Street in correction** — the S&P 500 down 3.7%, the Nasdaq down
   5.3% erasing all 2026 gains, as AI stocks sell off. Shown as a falling
   red chart arrow.
3. **Iran strikes a US base in Kuwait** — Iran hits a US air base in
   Kuwait and targets Bahrain amid wider Gulf attacks; tankers hit off
   the Oman coast. Shown as a fighter jet over a desert air base.
4. **Missile hits Kryvyi Rih** — 2 killed, about 60 wounded in
   Zelenskyy's hometown. Shown as a damaged apartment block with smoke.
5. **Quake shakes Peru** — a magnitude 6.9 earthquake in the Andes.
   Shown as cracked earth with a seismograph line.
6. **Court: Myanmar genocide** — the World Court (ICJ) finds Myanmar
   committed genocide against the Rohingya. Shown as a gavel over the
   scales of justice.
7. **Cyclone Akvan hits India** — crosses the Odisha coast, about
   300,000 people evacuated. Shown as a red cyclone spiral over a
   coastline.

## Verification

- JPEG exactly 1024×1024, 263,980 bytes (limit 1,048,576).
- Deterministic: `main.py` copies the bundled file byte-for-byte, so
  repeated runs write identical bytes (SHA-256
  `abb482084610e77e43aea9b19c2902c0055e03c4498f4f67e9738b41fc4830dc`).
- `python3 entry/main.py` run twice with `MAKEFUN_OUTPUT_DIR` set to a
  scratch directory produces byte-identical output both times.
- Image checked visually at full size: masthead, date line and all
  seven headlines legible, no garbled text, no spelling errors.
