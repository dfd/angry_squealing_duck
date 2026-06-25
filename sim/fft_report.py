#!/usr/bin/env python3
"""Report the harmonic content of ngspice waveform vectors.

Usage:
    uv run sim/fft_report.py <csv> --f0 220 v(name1) v(name2) ...

For each vector it prints the dominant peak and the amplitude at the first few
harmonics of f0, so we can see (e.g.) the octave-up energy at 2*f0.
"""
from __future__ import annotations

import argparse

from spicelib import amp_at, fft_mag, peak, read_wrdata


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("names", nargs="+", help="vector names in wrdata order")
    ap.add_argument("--f0", type=float, default=220.0, help="fundamental (Hz)")
    ap.add_argument("--harmonics", type=int, default=4)
    args = ap.parse_args()

    data = read_wrdata(args.csv, args.names)
    t = data["time"]
    print(f"f0 = {args.f0:.1f} Hz   (samples={len(t)}, "
          f"dt={1e6 * (t[1] - t[0]):.2f} us)\n")

    for name in args.names:
        f, m = fft_mag(t, data[name])
        pf, pa = peak(f, m)
        print(f"{name}:  peak {pf:7.1f} Hz @ {pa:.4f}")
        for h in range(1, args.harmonics + 1):
            fa = amp_at(f, m, h * args.f0)
            bar = "#" * int(40 * fa / (pa + 1e-12))
            print(f"    {h}x f0 = {h * args.f0:6.0f} Hz : {fa:.4f}  {bar}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
