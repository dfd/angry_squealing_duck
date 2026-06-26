#!/usr/bin/env python3
"""
Angry Squealing Duck - PCB builder (pcbnew, run under SYSTEM python 3.14):

    /usr/bin/python3 kicad/build_pcb.py

Parses kicad/duck.net (SKiDL netlist), loads each footprint, assigns nets (so KiCad
shows the ratsnest), does a first functional-group placement, draws the board outline,
and saves kicad/duck.kicad_pcb.  NO routing yet - placement is for an eyeball pass.
"""
import sys, re, pcbnew

ROOT = "/home/dave/dev/angry_squealing_duck"
NET  = f"{ROOT}/kicad/duck.net"
OUT  = f"{ROOT}/kicad/duck.kicad_pcb"
FPLIB = "/usr/share/kicad/footprints"
MM = pcbnew.FromMM
def V(x, y): return pcbnew.VECTOR2I(MM(x), MM(y))

# ---------------- tiny s-expression parser ----------------
def parse_sexp(s):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s)
    it = iter(toks)
    def rd(tok):
        if tok == '(':
            lst = []
            for t in it:
                if t == ')': return lst
                lst.append(rd(t))
            return lst
        if tok.startswith('"'): return tok[1:-1]
        return tok
    return rd(next(it))

def find_all(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]
def first(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key: return c
    return None
def val(node, key):
    c = first(node, key)
    return c[1] if c and len(c) > 1 else None

# ---------------- read netlist ----------------
tree = parse_sexp(open(NET).read())
comps = {}   # ref -> (value, footprint)
for c in find_all(first(tree, "components"), "comp"):
    ref = val(c, "ref"); comps[ref] = (val(c, "value"), val(c, "footprint"))
nets = {}    # netname -> [(ref, pin)]
for n in find_all(first(tree, "nets"), "net"):
    name = val(n, "name")
    nets[name] = [(val(nd, "ref"), val(nd, "pin")) for nd in find_all(n, "node")]
print(f"parsed: {len(comps)} comps, {len(nets)} nets")

# ---------------- create board + load footprints ----------------
board = pcbnew.BOARD()
fp_objs = {}
missing = []
for ref, (value, fpid) in comps.items():
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", name)
    if fp is None:
        missing.append(fpid); continue
    fp.SetReference(ref); fp.SetValue(value)
    board.Add(fp); fp_objs[ref] = fp
if missing:
    print("MISSING FOOTPRINTS:", sorted(set(missing)));
print(f"loaded {len(fp_objs)} footprints")

# ---------------- assign nets to pads ----------------
netinfo = {}
unassigned = 0
for name, nodes in nets.items():
    ni = pcbnew.NETINFO_ITEM(board, name); board.Add(ni); netinfo[name] = ni
    for ref, pin in nodes:
        fp = fp_objs.get(ref)
        if not fp: continue
        pad = fp.FindPadByNumber(str(pin))
        if pad: pad.SetNet(ni)
        else: unassigned += 1
print(f"nets assigned; {unassigned} pads not matched by number")

# ---------------- first-pass placement (functional groups) ----------------
# signal flows U1->U6 left-to-right; cluster each passive near the IC it shares
# the most nets with. Pots top edge, jacks at edges.
ref_nets = {}
for name, nodes in nets.items():
    if name in ("VCC", "GND", "VREF"): continue        # skip globals for clustering
    for ref, _ in nodes: ref_nets.setdefault(ref, set()).add(name)

# decoupling caps = caps tied only across VCC<->GND -> placed beside their IC (not the grid)
ref_nets_full = {}
for name, nodes in nets.items():
    for ref, _ in nodes: ref_nets_full.setdefault(ref, set()).add(name)
decoup = sorted(r for r in comps if r[0] == "C" and comps[r][0] == "100n"
                and ref_nets_full.get(r, set()) == {"VCC", "GND"})   # exclude the 100u bulk
pdiode = [r for r in comps if comps[r][0] == "1N5817"]   # power diode -> near the DC jack

# ICs: one vertical-oriented row, inset from the side jacks
ICS = sorted([r for r in comps if r.startswith("U")], key=lambda s: int(s[1:]))
ic_x = {r: 30 + 18*i for i, r in enumerate(ICS)}         # U1..U7, 18mm spacing
IC_Y = 38
for r in ICS:
    if r in fp_objs:
        fp_objs[r].SetPosition(V(ic_x[r], IC_Y))   # default 0deg = long axis vertical (narrow)

# one decoupling cap just above each IC (gap between pots and IC row), near its V+ pin
for i, c in enumerate(decoup):
    ic = ICS[i % len(ICS)]
    if c in fp_objs: fp_objs[c].SetPosition(V(ic_x[ic], IC_Y - 14))

# group passives by the IC they share the most (signal) nets with, so each stage's
# parts stay contiguous in the grid below
clusters = {r: [] for r in ICS}
for ref in comps:
    if ref[0] not in "RCD" or ref in decoup or ref in pdiode: continue   # placed separately
    best, bn = ICS[0], -1
    for ic in ICS:
        sh = len(ref_nets.get(ref, set()) & ref_nets.get(ic, set()))
        if sh > bn: bn, best = sh, ic
    clusters[best].append(ref)
ordered = [ref for ic in ICS for ref in clusters[ic]]

# lay all passives in ONE clean, stage-ordered grid BELOW the IC row (nothing above
# the ICs -> the pot band stays clear). 6mm pitch = comfortable for hand-soldering.
NCOL, X0, Y0, DX, DY = 14, 26, 64, 9, 9          # inset from side jacks; clear the IC row
for idx, ref in enumerate(ordered):
    if ref in fp_objs:
        fp_objs[ref].SetPosition(V(X0 + (idx % NCOL)*DX, Y0 + (idx // NCOL)*DY))

# pots across the top edge (4 knobs), jacks on the side edges, DC top-right corner
for i, r in enumerate(sorted([r for r in comps if r.startswith("RV")], key=lambda s:int(s[2:]))):
    if r in fp_objs: fp_objs[r].SetPosition(V(30 + 35*i, 13))   # 30,65,100,135 (clear of J3)
edge = {"J1": V(12, 62), "J2": V(163, 62), "J3": V(163, 13)}
for r, p in edge.items():
    if r in fp_objs: fp_objs[r].SetPosition(p)
# power-protection diode by the DC jack (clear of the last pot + IC row)
for d in pdiode:
    if d in fp_objs: fp_objs[d].SetPosition(V(148, 24))

# strip stray Edge.Cuts graphics that some footprints (RV4 dual pot) carry, so the
# board outline is just our rectangle (a single closed shape)
for f in board.GetFootprints():
    for g in list(f.GraphicalItems()):
        if g.GetLayer() == pcbnew.Edge_Cuts:
            f.Remove(g)

# ---------------- board outline (175 x 120 mm, 1590DD-class enclosure) ----------------
W, H = 175, 120
rect = pcbnew.PCB_SHAPE(board); rect.SetShape(pcbnew.SHAPE_T_RECT)
rect.SetStart(V(0, 0)); rect.SetEnd(V(W, H))
rect.SetLayer(pcbnew.Edge_Cuts); rect.SetWidth(MM(0.15)); board.Add(rect)

board.BuildConnectivity()
pcbnew.SaveBoard(OUT, board)
rn = board.GetConnectivity().GetUnconnectedCount(False)
print(f"saved {OUT}  | footprints={len(board.GetFootprints())} ratsnest(unrouted)={rn}")
