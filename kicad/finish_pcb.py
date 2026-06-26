#!/usr/bin/env python3
"""
Angry Squealing Duck - PCB finishing pass (pcbnew, system python 3.14):
    /usr/bin/python3 kicad/finish_pcb.py

Operates on the already-ROUTED kicad/duck.kicad_pcb (preserves the routing):
  1. snaps the few non-E-series resistor values to nearest standard (silk only)
  2. adds a GND copper pour on both layers (lower noise / solid ground)
Then re-save. (DRC + gerber re-export are run separately.)
"""
import pcbnew
MM = pcbnew.FromMM
B = pcbnew.LoadBoard("/home/dave/dev/angry_squealing_duck/kicad/duck.kicad_pcb")

# 1. snap non-standard resistor values to nearest E-series
SNAP = {"5k": "4.7k", "7k": "6.8k", "23k": "22k", "40k": "39k", "49k": "47k", "70k": "68k"}
n = 0
for f in B.GetFootprints():
    v = f.GetValue()
    if v in SNAP:
        f.SetValue(SNAP[v]); n += 1
print(f"snapped {n} resistor values to E-series")

# 2. GND pour on both copper layers, inset 0.6mm from edge. Idempotent: drop any
#    existing zones first. Solid pad connection (no thermal relief) -> no starved
#    thermals, solid ground (fine for a hand-soldered THT board).
for z in list(B.Zones()):
    B.Remove(z)
gnd = B.FindNet("GND")
gcode = gnd.GetNetCode()
# remove the redundant GND traces/vias so the solid pour is the clean ground plane
removed = 0
for t in list(B.GetTracks()):
    if t.GetNetCode() == gcode:
        B.Remove(t); removed += 1
print(f"removed {removed} GND tracks/vias -> ground plane")
# force solid (no-thermal) connection on every GND pad -> no starved thermals
for f in B.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode() == gcode:
            p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
W, H = 175, 120
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(B)
    z.SetLayer(layer)
    z.SetNet(gnd)
    try: z.SetAssignedPriority(0)
    except Exception: z.SetPriority(0)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(MM(0.3))                     # narrow gap + spokes so
    z.SetThermalReliefSpokeWidth(MM(0.4))             # reliefs fit crowded pads
    z.SetMinThickness(MM(0.2))
    z.SetIsFilled(True)
    poly = z.Outline()
    poly.NewOutline()
    for (x, y) in [(0.6, 0.6), (W-0.6, 0.6), (W-0.6, H-0.6), (0.6, H-0.6)]:
        poly.Append(pcbnew.VECTOR2I(MM(x), MM(y)))
    B.Add(z)
pcbnew.ZONE_FILLER(B).Fill(B.Zones())
print(f"added + filled GND pour on F.Cu and B.Cu ({len(B.Zones())} zones)")

pcbnew.SaveBoard("/home/dave/dev/angry_squealing_duck/kicad/duck.kicad_pcb", B)
print("saved.")
