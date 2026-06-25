#!/usr/bin/env python3
"""Render a WAV through the pedal with ngspice: wav -> PWL -> .tran -> wav.

Usage:
    uv run sim/render.py raw_wavs/"Dry Guitar.wav" --start 10 --dur 2.0 \
        --squeal 1 --anger 0.6 --quack 1 --volume 0.7 [--bypass]

Pulls a short mono segment, scales it to a guitar-ish input level, builds a
netlist with an inline PWL source feeding the `pedal` block, runs ngspice, and
writes the processed output to audio/out/.
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import time

import numpy as np
from scipy.io import wavfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

NETLIST_HEAD = """* Auto-generated render netlist - Angry Squealing Duck
.include spice/lib/opamp.sub
.include spice/lib/diode.mod
.include spice/lib/supply.cir
.include spice/blocks/input_buffer.cir
.include spice/blocks/fwr.cir
.include spice/blocks/octave_rect.cir
.include spice/blocks/octave_gen.cir
.include spice/blocks/hpf.cir
.include spice/blocks/fuzz.cir
.include spice/blocks/fuzz_muff.cir
.include spice/blocks/gmint.cir
.include spice/blocks/vcf.cir
.include spice/blocks/envfollow.cir
.include spice/blocks/duck.cir
.include spice/blocks/duck_split.cir
.include spice/blocks/pedal.cir
"""


def load_segment(path: str, start: float, dur: float) -> tuple[int, np.ndarray]:
    sr, data = wavfile.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)        # stereo -> mono
    data = data.astype(np.float64)
    peak = np.max(np.abs(data)) or 1.0
    data /= peak                        # normalize to [-1, 1]
    i0 = int(start * sr)
    i1 = i0 + int(dur * sr)
    return sr, data[i0:i1]


def write_pwl_source(seg: np.ndarray, sr: int, vpeak: float) -> str:
    """Inline PWL voltage source `Vin in 0 PWL(...)`, 6 points per line."""
    t = np.arange(len(seg)) / sr
    v = seg * vpeak                     # scale to guitar-ish input volts
    parts = ["Vin in 0 PWL"]
    line = "+"
    for k, (tt, vv) in enumerate(zip(t, v)):
        line += f" {tt:.7g} {vv:.6g}"
        if (k + 1) % 6 == 0:
            parts.append(line)
            line = "+"
    if line != "+":
        parts.append(line)
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav", nargs="?", default="audio/in/di_sample.wav",
                    help="input WAV (default: the committed DI sample)")
    ap.add_argument("--start", type=float, default=0.0, help="segment start (s)")
    ap.add_argument("--dur", type=float, default=6.0, help="segment length (s)")
    ap.add_argument("--vpeak", type=float, default=0.25, help="input peak volts")
    ap.add_argument("--squeal", type=float, default=1.0)
    ap.add_argument("--anger", type=float, default=0.6)
    ap.add_argument("--quack", type=float, default=1.0)
    ap.add_argument("--volume", type=float, default=0.7)
    ap.add_argument("--fuzz", choices=["hard", "muff"], default="muff",
                    help="fuzz voice: Muff (thick, default) or hard-clip (DOD-style)")
    ap.add_argument("--mode", choices=["lp", "bp", "hp", "mixed"], default="bp",
                    help="filter mode (Q-Tron style): low/band/high pass or BP+HP mixed")
    ap.add_argument("--route", choices=["mixed", "hybrid", "parallel"], default=None,
                    help="octave routing experiment (instantiates the duck-level block "
                         "directly): mixed=1 filter (BP+HP taps); hybrid=body BP + octave "
                         "fixed HP; parallel=body BP + octave swept HP")
    ap.add_argument("--goct", type=float, default=2.5, help="octave makeup level (split routes)")
    ap.add_argument("--bypass", action="store_true")
    ap.add_argument("--tag", default="out", help="output filename tag")
    args = ap.parse_args()

    sr, seg = load_segment(args.wav, args.start, args.dur)
    print(f"segment: {len(seg)} samples @ {sr} Hz = {len(seg)/sr:.2f}s")

    bypass = 1 if args.bypass else 0
    muff = 1 if args.fuzz == "muff" else 0
    wlp, wbp, whp = {"lp": (1, 0, 0), "bp": (0, 1, 0),
                     "hp": (0, 0, 1), "mixed": (0, 0.7, 0.7)}[args.mode]
    common = (f"squeal={args.squeal} anger={args.anger} quack={args.quack} muff={muff}")
    if args.route is None:                       # normal: full pedal (volume + bypass)
        xline = (f"Xp in out vref vcc 0 pedal {common} volume={args.volume}"
                 f" bypass={bypass} wlp={wlp} wbp={wbp} whp={whp}")
    elif args.route == "mixed":                  # one filter, BP+HP tap blend
        xline = f"Xp in out vref vcc 0 duck {common} wlp=0 wbp=0.7 whp=0.7"
    else:                                        # split: hybrid / parallel
        octsweep = 1 if args.route == "parallel" else 0
        xline = f"Xp in out vref vcc 0 duck_split {common} goct={args.goct} octsweep={octsweep}"
    netlist = (
        NETLIST_HEAD
        + write_pwl_source(seg, sr, args.vpeak)
        + "\n" + xline + "\n"
        + ".control\n"
        + f"tran {1/sr:.10g} {len(seg)/sr:.6g}\n"
        + f"linearize\n"
        + "wrdata sim/out/render.csv v(out)\n"
        + ".endc\n.end\n"
    )
    nl_path = ROOT / "sim" / "out" / "render.cir"
    (ROOT / "sim" / "out").mkdir(parents=True, exist_ok=True)
    nl_path.write_text(netlist)

    print("running ngspice...")
    t0 = time.time()
    proc = subprocess.run(["ngspice", "-b", str(nl_path)], cwd=ROOT,
                          capture_output=True, text=True)
    print(f"ngspice done in {time.time()-t0:.1f}s")
    if "error" in proc.stderr.lower() or proc.returncode != 0:
        sys.stderr.write(proc.stderr[-2000:])
        return 1

    d = np.loadtxt(ROOT / "sim" / "out" / "render.csv")
    t, out = d[:, 0], d[:, 1]
    out = out - np.mean(out)            # remove vref DC
    out /= (np.max(np.abs(out)) or 1.0) * 1.05   # normalize, small headroom
    # resample onto a uniform sr grid (linearize already uniform, but be safe)
    n = int(round((t[-1] - t[0]) * sr))
    tu = t[0] + np.arange(n) / sr
    outu = np.interp(tu, t, out)
    (ROOT / "audio" / "out").mkdir(parents=True, exist_ok=True)
    if args.bypass:
        name = f"duck_{args.tag}_BYPASS.wav"          # effect params don't apply
    elif args.route is not None:
        name = (f"duck_{args.tag}_{args.route}_{args.fuzz}"
                f"_sq{args.squeal}_an{args.anger}_qk{args.quack}.wav")
    else:
        name = (f"duck_{args.tag}_{args.fuzz}_{args.mode}_sq{args.squeal}"
                f"_an{args.anger}_qk{args.quack}.wav")
    op = ROOT / "audio" / "out" / name
    wavfile.write(op, sr, (outu * 32767).astype(np.int16))
    print(f"wrote {op}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
