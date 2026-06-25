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

Design, voicing, and **real-part validation are complete**. Next milestone: **KiCad**
schematic + PCB (translate the validated SPICE blocks to real footprints + switching).

| done | |
|---|---|
| ✅ | All blocks designed + integrated (input buffer → fuzz → octave → filter → volume) |
| ✅ | Voiced by ear on real guitar (MOTU M2), grid of Squeal×Anger×Quack rendered |
| ✅ | Real part models (TL072 + LM13700) — chain converges, voicing holds |
| ⬜ | KiCad schematic + PCB |

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
- `kicad/`        — schematic + PCB (next phase)

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
