"""Helpers for reading ngspice `wrdata` output and doing spectral analysis.

`wrdata file v(a) v(b) ...` writes interleaved (time, value) column pairs:
    col0=time col1=v(a) col2=time col3=v(b) ...
So vector k (0-based) lives in column 2*k+1, all sharing the col0 time base
(true once `linearize` has put everything on a uniform grid).
"""
from __future__ import annotations

import numpy as np


def read_wrdata(path: str, names: list[str]) -> dict[str, np.ndarray]:
    """Return {"time": t, name0: y0, ...} from an ngspice wrdata file.

    `names` lists the vectors in the same order passed to `wrdata`.
    """
    raw = np.loadtxt(path)
    if raw.ndim == 1:  # single row
        raw = raw.reshape(1, -1)
    out = {"time": raw[:, 0]}
    for k, name in enumerate(names):
        out[name] = raw[:, 2 * k + 1]
    return out


def fft_mag(t: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Single-sided amplitude spectrum of uniformly-sampled y(t).

    Returns (freqs_hz, amplitude) where amplitude is in the same units as y
    (peak amplitude of each sinusoidal component).
    """
    n = len(y)
    dt = float(np.mean(np.diff(t)))
    y = y - np.mean(y)  # drop DC so it doesn't dominate
    win = np.hanning(n)
    # coherent-gain correction for the Hann window (mean = 0.5)
    spec = np.fft.rfft(y * win) / (n * 0.5) * 2.0
    freqs = np.fft.rfftfreq(n, dt)
    return freqs, np.abs(spec)


def amp_at(freqs: np.ndarray, mag: np.ndarray, f0: float) -> float:
    """Amplitude in the bin nearest f0."""
    return float(mag[np.argmin(np.abs(freqs - f0))])


def peak(freqs: np.ndarray, mag: np.ndarray, fmin: float = 1.0) -> tuple[float, float]:
    """(freq, amplitude) of the largest spectral peak above fmin."""
    sel = freqs >= fmin
    i = np.argmax(mag[sel])
    return float(freqs[sel][i]), float(mag[sel][i])
