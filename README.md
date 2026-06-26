# Angry Squealing Duck

A guitar pedal: a thick octave-fuzz feeding a dynamics-driven envelope band-pass
("Q-Tron") filter. Designed and voiced entirely in **ngspice**, validated against
real-part models, ready for KiCad.

**Controls (4 knobs + 2 footswitches):**
- **Volume** — output level
- **Anger** — fuzz amount / sustain (Big-Muff-style)
- **Squeal** — up-octave level: CCW = none, ~noon = "ring on top", CW = octave-dominant blast
- **Quack** — envelope band-pass intensity (ganged sweep depth + resonance Q)
- **Master** true-bypass footswitch, and a dedicated **Squeal (octave) footswitch**
  (kick the octave in/out, Hoof-Reaper style)

All knobs CCW = that effect off.

## Signal architecture

```
 IN ─► Input buffer ─► SPLIT ─┬─ AUDIO: Fuzz(Anger) ─┬─► BP envelope filter(Quack) ──┐
                              │                       └─► Octave-up(Squeal) ─► fixed HP┤─►[Volume]─► OUT
                              └─ CONTROL: Envelope follower (raw) ─► Iabc (cutoff) ─────┘
```

Key voicing decisions (each one earned the hard way — see `git log` / memory):
- **Octave AFTER the fuzz** (Octavia / Fender-Blender pattern): rectifying the distorted
  signal yields a prominent ring. Octave *before* the fuzz buried it ~30 dB under the
  fuzz's odd harmonics.
- **Body and octave on separate filter paths** ("hybrid" route): the fuzz body goes
  through the **band-pass** envelope filter (it quacks); the octave goes through a
  **fixed high-pass** (stays clear/bright instead of being swept under). A single shared
  filter ("mixed") muffled the octave.
- **Envelope tapped from the RAW split** (pre-fuzz) so the filter tracks picking dynamics
  — fuzz compresses dynamics away.

## Design choices

- Single **9 V** supply, **op-amp-buffered 4.5 V** virtual ground (`vref`) — a passive
  divider sags under the high-gain fuzz. Every stage input is AC-coupled.
- **Fuzz** = 3-stage cascaded **Big-Muff-style soft-clipper** with asymmetric stages for
  warmth (`fuzz_muff.cir`, default). A single-stage hard clipper (`fuzz.cir`, DOD-250
  family) is kept selectable via the `muff` param.
- **Octave** = op-amp **precision full-wave rectifier** (`fwr.cir`), no transformer.
  `octave_gen.cir` produces octave-only; Squeal level is **quadratic** so noon = ring,
  full = blast (`goct=8`, ~+9 dB octave-over-body, calibrated on real DI clips).
- **Envelope follower** = precision rectifier + **2-pole averaging** (not peak-detect,
  which hunted in a ~12 Hz limit cycle that re-triggered the filter on held notes).
- **Filter** = **LM13700 OTA state-variable** filter (`vcf.cir` behavioral / `vcf_real.cir`
  real). Has LP/BP/HP/mixed taps (Q-Tron-style mode); the hybrid route uses BP for the
  body. Quack maps to a **linear Q (0.7→3.5)** and an envelope-swept cutoff (gm = Iabc).
  gm control is ground-referenced to avoid a virtual-ground latch.
- **Behavioral-ideal first** to lock topology/voicing, then **real part models** for build
  accuracy (`opamp_real.sub` = TL072, `lm13700.sub` = OTA) — validated: voicing essentially
  unchanged on real silicon. See `memory` / `real-parts-and-build-notes`.

## Status

Design, voicing, real-part validation, **and a routed KiCad PCB are complete.**

| done | |
|---|---|
| ✅ | All blocks designed + integrated (input buffer → fuzz → octave → filter → volume) |
| ✅ | Voiced by ear on real guitar (MOTU M2), grid of Squeal×Anger×Quack rendered |
| ✅ | Real part models (TL072 + LM13700) — chain converges, voicing holds |
| ✅ | All-real buildable netlist (`pedal_build.cir`, no B-sources) — re-validated |
| ✅ | Quack sweep restored: V-to-I gain ×73 → body cutoff ~280 Hz→2.1 kHz, auditioned-good |
| ✅ | KiCad PCB: placed, auto-routed, **DRC-clean**, gerbers exported |

**Quack note:** the real envelope is tiny (~0.04 V peak), so the V-to-I needs high gain
(`Rdi`/`Rdj` = 1.5k, `Rdf`/`Rdk` = 110k → ×73) for the filter to sweep. Quack is most
audible at lower Squeal — at full Squeal the octave sits on top by design.

**Known residual:** 4 benign `starved_thermal` DRC advisories on crowded GND pads
(fully connected to the pour; clear them with a solid-connection click in pcbnew if desired).

## Layout

- `spice/lib/`    — models: `opamp.sub` (ideal), `opamp_real.sub` (TL072),
  `lm13700.sub` (OTA), `diode.mod` (1N4148), `supply.cir` (buffered vref)
- `spice/blocks/` — one `.subckt` per block: `input_buffer`, `fuzz`, `fuzz_muff`, `fwr`,
  `octave_rect`/`octave_gen`, `hpf`, `gmint`+`vcf`/`vcf_real`, `envfollow`,
  `duck`(mixed)/`duck_split`(hybrid/parallel), `pedal`
- `spice/tests/`  — per-block test benches
- `sim/`          — Python harness: `run.py`, `render.py`, `octave_balance.py`,
  `fft_report.py`, `spicelib.py`, `extract_sample.py`
- `audio/in/`     — committed DI samples; `audio/out/` — rendered WAVs (git-ignored)
- `raw_wavs/`     — large source recordings (git-ignored)
- `kicad/`        — the board, generated programmatically:
  - `duck.py` (SKiDL netlist generator) → `duck.net` (ERC-clean) + `BOM.md`
  - `build_pcb.py` (pcbnew: parse netlist → place → board) ; `finish_pcb.py` (values + GND pour)
  - `duck.kicad_pcb` (routed, DRC-clean) ; `gerbers/` + `duck.drl` + `duck-pos.csv` (fab-ready)
  - `pedal_build.cir` in `spice/blocks/` is the all-real buildable schematic-of-record

## KiCad / PCB workflow

The board is generated entirely by script (no GUI), bridging two Pythons because
`pcbnew` is built for system Python 3.14 while the sim harness uses uv's 3.13:
```
# 1. netlist (uv / 3.13)
KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols uv run kicad/duck.py     # -> duck.net (+ ERC)
# 2. place + board (system python 3.14, needs pcbnew)
/usr/bin/python3 kicad/build_pcb.py                                 # -> duck.kicad_pcb
# 3. route: export DSN, run freerouting (needs a display, e.g. :0), import SES
/usr/bin/python3 -c "import pcbnew,sys; b=pcbnew.LoadBoard('kicad/duck.kicad_pcb'); pcbnew.ExportSpecctraDSN(b,'/tmp/duck.dsn')"
DISPLAY=:0 java -jar freerouting.jar -de /tmp/duck.dsn -do /tmp/duck.ses -mp 14
/usr/bin/python3 -c "import pcbnew; b=pcbnew.LoadBoard('kicad/duck.kicad_pcb'); pcbnew.ImportSpecctraSES(b,'/tmp/duck.ses'); pcbnew.SaveBoard('kicad/duck.kicad_pcb',b)"
# 4. finishing pass (snap values + GND pour) + checks + fab outputs
/usr/bin/python3 kicad/finish_pcb.py
kicad-cli pcb drc kicad/duck.kicad_pcb
kicad-cli pcb export gerbers --output kicad/gerbers/ kicad/duck.kicad_pcb
```
Board: 2-layer, 175×120 mm (1590DD-class), 6× TL074 + 1× LM13700 + 14× 1N4148,
4 knobs (Volume / Anger / Squeal / Quack-dual-gang). No graphical schematic
(eeschema has no scripting API) — `pedal_build.cir` + `duck.py` are the design-of-record.

## Workflow

Run a block test bench:
```
uv run sim/run.py spice/tests/tb_input_buffer.cir
```
Render guitar through the pedal (→ `audio/out/`):
```
uv run sim/render.py [wav] --route hybrid --squeal 1 --anger 0.8 --quack 0.6 \
    [--real] [--subdir name] [--fuzz muff|hard] [--mode bp|hp|mixed]
```
- `--real` = TL072 + LM13700 real-part chain (else fast ideal models)
- `--route` = mixed | hybrid | parallel  · `--goct` = octave makeup
- Scratch files are unique per render, so render the grid in parallel on many cores:
  `... | xargs -P 24 -I A sh -c 'uv run sim/render.py A'`

Measure octave-vs-body level on real clips (don't trust single-note benches — they
over-read the octave ~6 dB):
```
uv run sim/octave_balance.py --wav audio/in/di_sample.wav --squeal 1.0 --goct 8
```
