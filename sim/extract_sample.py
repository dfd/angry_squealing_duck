#!/usr/bin/env python3
"""Extract a small, committable mono DI segment from a large source WAV.

The large source recordings live in raw_wavs/ (git-ignored). This produces the
repo-tracked audio/in/di_sample.wav that the render workflow uses by default, so
the project is reproducible from the committed files alone.

    uv run sim/extract_sample.py raw_wavs/"Dry Guitar.wav" --start 24 --dur 6
"""
from __future__ import annotations

import argparse
import pathlib
import warnings

import numpy as np
from scipy.io import wavfile

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--start", type=float, default=24.0)
    ap.add_argument("--dur", type=float, default=6.0)
    ap.add_argument("--out", default="audio/in/di_sample.wav")
    args = ap.parse_args()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sr, data = wavfile.read(args.wav)
    if data.ndim > 1:
        data = data.mean(axis=1)            # stereo -> mono
    seg = data[int(args.start * sr):int((args.start + args.dur) * sr)]
    # peak-normalize to -1 dBFS so the committed sample has consistent level
    seg = seg.astype(np.float64)
    seg /= (np.max(np.abs(seg)) or 1.0) / 0.89

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(out, sr, (seg * 32767).astype(np.int16))
    print(f"wrote {out}  ({len(seg)/sr:.2f}s mono @ {sr} Hz, "
          f"{out.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
