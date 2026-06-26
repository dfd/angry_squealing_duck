# Angry Squealing Duck — breadboard build guide

Prototype the pedal on solderless breadboards **one stage at a time**, testing each before
moving on, so a problem is caught in a 5-part block instead of a 100-part haystack. The
circuit is identical to the PCB; only the physical build differs.

- **Wiring detail:** [`CONNECTIONS.md`](CONNECTIONS.md) — per stage, every net is one
  breadboard row; put the listed pins in that row. IC pins are annotated (e.g. `U1.2 (IN1-)`).
- **Drawn schematics** (the simple stages SKiDL could auto-draw): `01_supply.png`,
  `02_input_buffer.png`, `05_envelope.png`, `06_quack_vtoi.png`. The dense stages (fuzz,
  octave, filter) are table-only — SKiDL's schematic auto-router can't handle them; the
  validated topology lives in `spice/blocks/*.cir` and the tables are generated from it.
- **Reference sound:** `audio/out/build_grid/` has the real-parts renders at every
  Squeal/Anger/Quack = 0/0.5/1.0 — listen to know what each stage *should* do.

> Op-amps here are allocated **per stage** (a fresh TL072/TL074 per block) — NOT the PCB's
> tight 6×TL074 packing — so each stage is independent and testable on its own.

## What you need
- Breadboards: 3–4 full-size (this is a big circuit).
- ICs: TL072 (DIP-8) and TL074 (DIP-14) op-amps, **1× LM13700** (DIP-16, the filter).
- 1N4148 diodes (~13), resistors + caps per `CONNECTIONS.md` (film for signal, electrolytic
  for the big supply/envelope caps), 4 pots (100k): **Volume, Anger, Squeal, Quack**.
- **9 V supply** (battery or regulated adapter), a DMM, and ideally a scope or an amp to listen.
- **One 0.1 µF ceramic from each IC's V+ pin to GND**, right at the chip (breadboard
  decoupling — skip it and the high-gain fuzz/filter may oscillate).

## Power & ground (build this rail discipline first)
- **VCC = +9 V**, **GND = 0 V** rails down both sides of every breadboard, linked together.
- **VREF = +4.5 V** is the "virtual ground" the whole pedal biases around — it is built by
  **Stage 1** and then distributed as a third rail to every other stage. Nearly every stage
  references VREF; run a wire for it everywhere.
- All inter-stage audio is AC-coupled and rides on VREF.

## The two pot wrinkles
- **Quack is a DUAL-GANG pot** (one knob, two ganged 100 k sections): section **A** lives in
  Stage 6 (the V-to-I "sweep" crossfade), section **B** lives in Stage 7 (the filter "Q").
  Use a real dual-gang 100 k pot (6 lugs), **or** two separate 100 k pots you turn together
  while testing.
- **Skip the true-bypass footswitch** while prototyping — just wire the input jack tip → Stage 2
  input, and Stage 8 output → output jack tip. Add switching later on the PCB.

## Inter-stage wiring (the wires between breadboard sections)
```
        IN ─► [2 Input buf] ─SIG─┬─► [3 Fuzz/Anger] ─FZ─┬─► [4 Octave/Squeal] ─OCTF─┐
                                 │                       └─► [7 Filter] ─BODYF───────┤
                                 └─► [5 Envelope] ─CV─► [6 V-to-I] ─VBIAS─► [7 Filter bias]
        [8 Output mix + Volume] ◄── BODYF + OCTF ──►  OUT ─► output jack
```
- **SIG** fans out to BOTH the fuzz (audio) and the envelope follower (control).
- **FZ** (fuzz output) fans out to BOTH the octave and the filter.
- **VBIAS** from Stage 6 biases the LM13700 in Stage 7 (this is what makes it quack).
- **BODYF** (filter) + **OCTF** (octave) meet at the Stage 8 mixer.

---

## Staged bring-up (build + test in this order)

### 1 — Supply / 4.5 V Vref   (table: `CONNECTIONS.md` §supply · schematic `01_supply.png`)
Build the reverse-protection diode, the 100 µF bulk cap, the 100k/100k divider + 47 µF, and
the TL072 buffer. **Test:** DMM — VCC = 9 V, **VREF = 4.5 V** (within ~0.1 V). Nothing else
works until this is solid.

### 2 — Input buffer   (§input_buffer · `02_input_buffer.png`)
Cin (100 n) + Rin (1 M to VREF) + unity buffer. **Test:** inject a signal (or plug a guitar)
at IN; on a scope, **SIG** is the same signal now centered on 4.5 V. Unity gain, no distortion.

### 3 — Fuzz (Anger)   (§fuzz_anger — table only, dense 3-stage Muff)
Three cascaded soft-clip stages (each: AC-couple, 1 M bias, gain op-amp, 100k/68k feedback +
1.5 n, asymmetric 1N4148 clippers), then a 2.2k/27n output low-pass → **FZ**. Anger (RV1) sets
stage-1 gain. **Test:** temporarily route SIG→FZ→an amp. Thick sustaining fuzz; Anger CCW =
cleaner/shorter, CW = maximum fuzz/sustain. If it squeals/oscillates, add the 0.1 µF decoupling.

### 4 — Octave (Squeal)   (§octave_squeal — table only)
HP into a precision full-wave rectifier (frequency doubler), gentle LP, AC-couple, ×8 makeup,
Squeal level pot, fixed ~330 Hz HP → **OCTF**. **Test:** FZ→octave→amp; you'll hear the
up-octave "ring" over the fuzz. Squeal CCW = none, noon = ring on top, CW = octave-dominant
blast. Most obvious on single notes / upper frets.

### 5 — Envelope follower   (§envelope · `05_envelope.png`)
Full-wave rectifier + 2-pole averaging + buffer → **CV**. This is a *control* voltage, not
audio. **Test:** DMM/scope on CV — sits at 4.5 V when quiet, **rises above 4.5 V when you
play** and tracks your picking dynamics (the rise is small, tens of mV — that's expected and
why Stage 6 has high gain).

### 6 — Quack control / V-to-I   (§quack_vtoi · `06_quack_vtoi.png`)
Vpark divider + buffer, a ×73 difference amp (1.5k/110k — high gain because CV is tiny), the
Quack-**sweep** crossfade pot (gang A), and a buffer → **VBIAS**. **Test:** DMM on VBIAS —
~1.6 V parked, climbing toward several volts on hard attacks. Quack-sweep CCW = VBIAS stays
parked (no sweep); CW = full swing.

### 7 — LM13700 band-pass filter (Quack)   (§filter_lm13700 — table only)
The heart of the quack: op-amp inverter + summer feeding two LM13700 OTA-C integrators; **VBIAS
sets the cutoff** (via the 10k bias resistors into pins 1 & 16). Quack-**Q** pot (gang B) sets
resonance. Input = FZ, output = **BODYF**. **Test:** FZ→filter→amp with VBIAS connected — the
body now *quacks*: bright on the pick attack, darkening as the note decays. Quack-Q CCW = gentle,
CW = vocal/resonant. **Quack is most audible with Squeal low** (at full Squeal the octave sits on top).

### 8 — Output (mix + Volume)   (§output — table only)
Op-amp mixer sums **BODYF + OCTF** (22k each), then a Volume pot + buffer → **OUT** → output
jack. **Test:** the whole pedal. Volume sets level; compare against `audio/out/build_grid/`.

---

### Once it all works
Wire SIG→(fuzz + envelope), FZ→(octave + filter), VBIAS→filter, BODYF+OCTF→output. Sweep all
four knobs and A/B against the grid renders. Then graduate to the PCB (`kicad/duck.kicad_pcb`)
— same circuit, soldered.
