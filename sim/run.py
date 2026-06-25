#!/usr/bin/env python3
"""Run an ngspice test bench from the project root and surface its results.

Usage:
    uv run sim/run.py spice/tests/tb_input_buffer.cir

ngspice is invoked in batch mode with the project root as CWD, so all
`.include` and `wrdata` paths in the netlists are relative to the root.
"""
import pathlib
import subprocess
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: run.py <netlist.cir>", file=sys.stderr)
        return 2

    root = pathlib.Path(__file__).resolve().parent.parent
    netlist = sys.argv[1]
    (root / "sim" / "out").mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(
        ["ngspice", "-b", netlist],
        cwd=root,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(proc.stdout)
    if proc.stderr.strip():
        sys.stderr.write("\n--- ngspice stderr ---\n" + proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
