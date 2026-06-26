# Breadboard parts list — Angry Squealing Duck

A clean shopping list for the breadboard build. **Every component here rolls forward into the
PCB build** (pull from the breadboard, socket the ICs, re-solder the passives) — you do NOT buy
the electronics twice. Build + wiring instructions: **`BUILD_GUIDE.md`**; per-stage wiring
tables: **`CONNECTIONS.md`**; cost: **`COST.md`**.

## Reusable lab kit (one-time, not pedal-specific — keep for every project)
- 3–4 full-size (830-point) solderless breadboards
- jumper-wire kit (assorted lengths)
- 9 V supply (battery + clip, or a regulated adapter)
- a multimeter (and a scope/amp to listen, if you have one)
- a few alligator/clip leads (use instead of jacks while testing)

## ICs
Op-amps are spread **one stage per chip** on the breadboard (so each stage tests on its own);
on the PCB they pack into 6× TL074. Buying all TL074 covers both (a TL074 stands in anywhere
a dual would go) — get a couple spares.
| part | qty (incl spares) | notes |
|---|---|---|
| TL074 (quad op-amp, DIP-14) | 7 | the workhorse; PCB uses 6 |
| LM13700 (dual OTA, DIP-16) | 2 | the filter — priciest/rarest part, 1 spare |
| DIP IC sockets (14- and 16-pin) | for the PCB later | socket the LM13700 at least |

## Diodes (14)
| value | qty |
|---|---|
| 1N4148 | 13 |
| 1N5817 | 1 |
- 1N4148 = the fuzz clippers + the two precision rectifiers. 1N5817 = reverse-polarity protection.

## Resistors (52)  — 1/4 W, any tolerance (5% fine)
| value | qty |
|---|---|
| 10k | 16 |
| 100k | 6 |
| 22k | 5 |
| 1M | 4 |
| 12k | 2 |
| 68k | 2 |
| 2.2k | 2 |
| 4.7k | 2 |
| 15k | 2 |
| 1.5k | 2 |
| 110k | 2 |
| 47k | 2 |
| 1k | 2 |
| 3.3k | 1 |
| 6.8k | 1 |
| 39k | 1 |

## Capacitors (25)
| value | qty | type |
|---|---|---|
| 100n | 11 |
| 1.5n | 3 |
| 220n | 2 |
| 10n | 2 |
| 100u | 1 |
| 27n | 1 |
| 47n | 1 |
| 12n | 1 |
| 1u | 1 |
| 22n | 1 |
| 47u | 1 |
- **100 µF, 47 µF, 220 n** → electrolytic.  **1.5 n / 10 n / 12 n / 22 n / 27 n / 47 n / 100 n / 1 µF** → film or ceramic.
- The **7× of the 100 n** are per-IC decoupling (one 0.1 µF at each chip's V+ pin) — don't skip them.

## Pots (4 × 100 kΩ)
| control | part |
|---|---|
| Volume | 100k single (audio/log taper) |
| Anger | 100k single (any taper; reverse-log ideal) |
| Squeal | 100k single (audio/log taper) |
| **Quack** | 100k **dual-gang** (one knob, two ganged sections) — *or* two 100k singles turned together for testing |
- Add 4 knobs when you build the PCB/enclosure.

## NOT needed for the breadboard (buy at PCB time — see COST.md)
PCB, IC sockets, 2× 3PDT footswitches, enclosure, knobs, 1/4" jacks + DC jack.
