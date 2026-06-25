# Angry Squealing Duck

A guitar pedal: an octave-fuzz feeding a dynamics-driven envelope band-pass filter.

- **Volume** — output level
- **Anger** — fuzz amount (op-amp gain + diode clipping)
- **Squeal** — level of the up-octave blended into the fuzz
- **Quack** — single control ganging the envelope filter's *drive* (sweep sensitivity)
  and *Q* (resonance), Q-Tron style band-pass

All knobs: fully CCW = effect off, fully CW = full blast. A true-bypass switch
wraps the whole circuit.

## Signal architecture

```
 IN -> Input buffer -> SPLIT -+- AUDIO:  Fuzz -> Octave-up[Squeal blend] -> VCF ->[Volume]-> OUT
                              |                                              ^
                              +- CONTROL: Envelope follower -----------------+  (cutoff CV)
```

The envelope follower taps the **raw** (pre-fuzz) signal so the filter responds to
picking dynamics — fuzz compresses dynamics away, so sensing post-fuzz would barely move.

The octave-up sits **after** the fuzz (Fender Blender / EQD Hoof Reaper pattern):
rectifying the already-distorted signal yields a prominent "ring" octave, and Squeal
blends plain-fuzz vs octave-fuzz independently of Anger. (Octave *before* fuzz buried
the octave ~30 dB under the fuzz's odd harmonics.)

## Design choices

- Single **9V** supply, **op-amp-buffered 4.5V** virtual ground (`vref`) — a passive
  divider sags under the high-gain fuzz. Every stage input is AC-coupled.
- **Fuzz** = two voices, selectable (`muff` param): a single-stage hard clipper
  (DOD-250 / Distortion+ / RAT family, `fuzz.cir`) and a thick Big-Muff-style
  cascaded soft-clipper with asymmetric stage 1 for warmth (`fuzz_muff.cir`).
- **Octave** = op-amp precision full-wave rectifier (frequency doubler), no transformer,
  placed *after* the fuzz with a Squeal blend.
- **Envelope follower** = precision rectifier + 2-pole averaging (not peak-detect, which
  hunted in a ~12 Hz limit cycle that re-triggered the filter on held notes).
- **VCF** = LM13700 OTA state-variable filter, band-pass tap (authentic Q-Tron topology);
  gm control is ground-referenced to avoid a virtual-ground latch.
- We design **behavioral-ideal first** to lock topology/voicing, then swap in real
  part models (TL072, LM13700, 1N4148) for build accuracy.

## Layout

- `spice/lib/`     — reusable subcircuits (op-amp macromodel, etc.)
- `spice/blocks/`  — one `.subckt` per pedal block
- `spice/tests/`   — one test bench per block (stimulus + analysis)
- `sim/`           — Python harness: run ngspice, parse, FFT, WAV render
- `audio/`         — recorded guitar WAVs in, rendered WAVs out
- `kicad/`         — schematic + PCB (later phase)

## Build stages

1. Input buffer + split + bias        <- current
2. Octave-up + Squeal blend
3. Fuzz (Anger)
4. Envelope follower
5. OTA band-pass VCF (Quack)
6. Integrate audio path -> VCF, CV from envelope
7. Volume + output buffer + bypass
8. Real-audio render + listen (MOTU M2)
9. KiCad schematic + PCB

## Running sims

All sims are run from the project root via the harness:

```
uv run sim/run.py spice/tests/tb_input_buffer.cir
```

The harness invokes ngspice in batch mode, echoes `.meas` results, and leaves
waveform CSVs in `sim/out/`.
