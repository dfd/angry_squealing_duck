#!/usr/bin/env python3
"""Measure the clean octave-vs-body level (dB) on a real DI clip.

Probes duck_split's internal `octave` and `bodyf` nodes (the two paths *before*
they're summed) and reports 20*log10(rms(octave)/rms(body)) over the whole clip --
the actual "how much louder is the octave than the body" in real playing.

    uv run sim/octave_balance.py --wav audio/in/di_sample.wav --squeal 1.0 --goct 3.5
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess

import numpy as np

# reuse the renderer's helpers
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from render import NETLIST_HEAD, ROOT, load_segment, write_pwl_source


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", default="audio/in/di_sample.wav")
    ap.add_argument("--squeal", type=float, default=1.0)
    ap.add_argument("--goct", type=float, default=3.5)
    ap.add_argument("--anger", type=float, default=0.8)
    ap.add_argument("--quack", type=float, default=0.6)
    ap.add_argument("--dur", type=float, default=6.0)
    args = ap.parse_args()

    sr, seg = load_segment(args.wav, 0.0, args.dur)
    stem = (f"obal_{pathlib.Path(args.wav).stem}_sq{args.squeal}"
            f"_g{args.goct}_q{args.quack}")
    xline = (f"Xp in out vref vcc 0 duck_split squeal={args.squeal} anger={args.anger}"
             f" quack={args.quack} muff=1 goct={args.goct} octsweep=0")
    netlist = (
        NETLIST_HEAD + write_pwl_source(seg, sr, 0.25) + "\n" + xline + "\n"
        + ".control\n" + f"tran {1/sr:.10g} {len(seg)/sr:.6g}\n" + "linearize\n"
        + f"wrdata sim/out/{stem}.csv v(xp.octave) v(xp.bodyf)\n" + ".endc\n.end\n"
    )
    nl = ROOT / "sim" / "out" / f"{stem}.cir"
    csv = ROOT / "sim" / "out" / f"{stem}.csv"
    (ROOT / "sim" / "out").mkdir(parents=True, exist_ok=True)
    nl.write_text(netlist)
    subprocess.run(["ngspice", "-b", str(nl)], cwd=ROOT, capture_output=True, text=True)
    d = np.loadtxt(csv)
    octv = d[:, 1] - d[:, 1].mean()
    body = d[:, 3] - d[:, 3].mean()
    db = 20 * np.log10(np.sqrt((octv**2).mean()) / (np.sqrt((body**2).mean()) + 1e-12))
    nl.unlink(missing_ok=True)
    csv.unlink(missing_ok=True)
    print(f"{pathlib.Path(args.wav).stem:18s} squeal={args.squeal:<4} goct={args.goct:<4} "
          f"quack={args.quack} -> octave-vs-body = {db:+.1f} dB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
