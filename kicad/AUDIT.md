# Netlist audit + gap-fixes (Tier-1 de-risk)

Virtual pass before breadboarding/fab: cross-checked the hand-written `duck.py` netlist
against the validated SPICE (`spice/blocks/*`) + part datasheets, and closed the physical gaps
the simulation can't model. ERC only proves the copper matches `duck.py` — it can't catch a
wrong translation, so this was done by hand.

## 🔴 Bug found + fixed — 10 of 14 diodes were reversed

The biggest risk in any hand-translated netlist: diode orientation. ERC and simulation both
pass regardless (the SPICE blocks are a *separate*, correct source). Found:

| where | count | was | now |
|---|---|---|---|
| Fuzz clipper `dba`/`dbb` (the 2-diode side of each asymmetric soft-clipper), ×3 stages | 6 | reversed | matches `fuzz_muff.cir` (`Da1`/`Db1a`/`Db1b`) |
| Precision rectifier `d1`/`d2`, ×2 instances (octave + envelope) | 4 | reversed (even contradicted their own comments) | matches `fwr.cir` (`D1 a1o n1`, `D2 hw a1o`) |

`1N4148` symbol pinout is **pin 1 = K (cathode), pin 2 = A (anode)** — verified from the
library, not assumed. **Built as-was, this board would have had a broken octave + envelope
(no quack) and a wrong-sounding fuzz.** This alone justified the audit.

## ✅ Verified correct (no change needed)

- **TL074** section pinout — out/−/+ = (1,2,3)(7,6,5)(8,9,10)(14,13,12), V+ 4 / V− 11.
- **LM13700** — Iabc 1/16, +in 3/14, −in 4/13, out 5/12, V+ 11 / V− 6; non-inverting
  integrators match `vcf_build.cir`.
- All op-amp stage wiring (input buffer, 3 fuzz gain stages, both rectifiers, envelope,
  octave makeup, V-to-I diff amp ×73, SVF summer/inverter, output summer + buffers).
- **Pots** — Volume/Squeal (dividers), Anger (rheostat), **Quack dual-gang**
  (`R_Potentiometer_Dual_Separate`: 1-3 = sweep crossfade, 4-6 = filter-Q). All correct.
- **Jacks** (AudioJack2 T/S, Barrel_Jack), the Vref buffer + divider, and the unused
  LM13700 buffer/diode-bias pins (tied/NC).

## 🟢 Physical gaps closed

1. **Per-IC decoupling** — added **7× 0.1 µF** from V+ → GND, one at each IC, **placed
   beside the chip** on the board. Was missing entirely (only a 100 µF bulk + 47 µF Vref cap
   existed) — a real oscillation/noise risk on a high-gain 7-IC design that SPICE can't show.
2. **Reverse-protection diode** — 1N4148 → **1N5817 Schottky** (handles supply current, low
   drop), placed by the DC jack.
3. **DC polarity pinned to center-negative** (Boss/standard: center pin = GND, sleeve = +9 V).
   ⚠️ **Verify against your barrel jack's actual pinout** — the Schottky blocks damage if a
   reversed/center-positive supply is plugged in, but get the convention right for it to power on.

## Breadboard generator independently verified (second translation)

The breadboard docs (`kicad/breadboard/CONNECTIONS.md`, schematics) come from a *separate*
hand-written generator — `kicad/breadboard/gen_blocks.py` — not `duck.py`. It was audited
against the SPICE on its own:

- **All 14 diodes correct.** gen_blocks uses a clean `diode(part, anode, cathode)` helper
  (`part[2]=A, part[1]=K`); the fuzz clippers (`Da1/Db1a/Db1b`) and both rectifiers
  (`D1 a1o n1`, `D2 hw a1o`) match the SPICE in `CONNECTIONS.md`. **The `duck.py` diode bug
  did NOT exist here** — it was specific to duck.py's direct K/A pin assignment.
- TL072/TL074 section maps + power pins, the **LM13700** pinout (Iabc 1/16, +in 3/14, −in 4/13,
  out 5/12, V+ 11 / V− 6), and key values (V-to-I ×73, octave makeup, filter attenuator) all
  match the design.

So the audit covers **both** outputs: the PCB netlist (`duck.py`, diodes fixed) and the
breadboard docs (`gen_blocks.py`, already correct). No breadboard changes needed.

## Still untested by simulation (real-silicon, for the breadboard to confirm)
- Noise floor and real oscillation behavior (no noise analysis exists; layout-dependent).
- The LM13700 filter with the **/50 input attenuation** hack instead of the on-chip
  linearizing diodes (diode-bias pins left open) — distortion/headroom, and behavior near the
  ~1 mA Iabc ceiling at full sweep. These are exactly what the Tier-2 breadboard checks.

Bottom line: the **logic/translation bugs are now scrubbed out** (diodes) and the **known
physical gaps closed** (decoupling, power). What remains is genuine real-silicon behavior —
the stuff worth breadboarding the filter + fuzz for.
