#!/usr/bin/env python3
"""Turn the per-block netlists (kicad/breadboard/nets/*.net) into readable breadboard
connection tables -> kicad/breadboard/CONNECTIONS.md. Each net = one breadboard row."""
import re, glob, os

# IC pin-function annotations (so 'U1 pin 2' reads as 'U1.2 (IN1-)')
PINFN = {
 "TL072": {1:"OUT1",2:"IN1-",3:"IN1+",4:"V- (GND)",5:"IN2+",6:"IN2-",7:"OUT2",8:"V+ (VCC)"},
 "TL074": {1:"OUT1",2:"IN1-",3:"IN1+",4:"V+ (VCC)",5:"IN2+",6:"IN2-",7:"OUT2",8:"OUT3",
           9:"IN3-",10:"IN3+",11:"V- (GND)",12:"IN4+",13:"IN4-",14:"OUT4"},
 "LM13700": {1:"Iabc-A",2:"Vd-A",3:"IN+A",4:"IN-A",5:"OUT-A",6:"V-",7:"Bin-A",8:"Bout-A",
             9:"Bout-B",10:"Bin-B",11:"V+",12:"OUT-B",13:"IN-B",14:"IN+B",15:"Vd-B",16:"Iabc-B"},
 "1N4148": {1:"K (band)",2:"A"},
 "R_Potentiometer": {1:"end1",2:"wiper",3:"end3"},
}
def lib_of(val):
    if val in ("TL072","TL074","LM13700"): return val
    if val=="1N4148": return "1N4148"
    return None

def parse_sexp(s):
    toks=re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s); it=iter(toks)
    def rd(tok):
        if tok=='(':
            lst=[]
            for t in it:
                if t==')': return lst
                lst.append(rd(t))
            return lst
        return tok[1:-1] if tok.startswith('"') else tok
    return rd(next(it))
def _all(node,key): return [c for c in node if isinstance(c,list) and c and c[0]==key]
def _first(node,key):
    for c in node:
        if isinstance(c,list) and c and c[0]==key: return c
def _val(node,key):
    c=_first(node,key); return c[1] if c and len(c)>1 else None

def parse(net_file):
    tree=parse_sexp(open(net_file).read())
    comps={_val(c,"ref"):_val(c,"value") for c in _all(_first(tree,"components"),"comp")}
    nets={}
    for n in _all(_first(tree,"nets"),"net"):
        nets[_val(n,"name").lstrip('/')] = [(_val(nd,"ref"),_val(nd,"pin")) for nd in _all(n,"node")]
    return comps, nets

def pinlabel(ref, pin, comps):
    val=comps.get(ref,"")
    lib=lib_of(val)
    fn=PINFN.get(lib or val,{})
    try: fn=PINFN.get(lib or val,{}).get(int(pin))
    except ValueError: fn=PINFN.get(lib or val,{}).get(pin)
    return f"{ref}.{pin}" + (f" ({fn})" if fn else "")

TITLES={"01_supply":"Supply / 4.5 V Vref","02_input_buffer":"Input buffer",
 "03_fuzz_anger":"Fuzz (Anger) - 3-stage Muff","04_octave_squeal":"Octave (Squeal)",
 "05_envelope":"Envelope follower","06_quack_vtoi":"Quack control (envelope -> V-to-I)",
 "07_filter_lm13700":"LM13700 band-pass filter","08_output":"Output (mix + Volume)"}

out=["# Angry Squealing Duck - breadboard connection tables\n",
     "Each **net = one breadboard row**: put every listed pin in that row. IC pins are\n"
     "annotated with their function. Build in numbered order (see BUILD_GUIDE.md).\n"]
for nf in sorted(glob.glob("kicad/breadboard/nets/*.net")):
    name=os.path.basename(nf)[:-4]
    comps,nets=parse(nf)
    out.append(f"\n## {name.split('_',1)[1] if '_' in name else name} - {TITLES.get(name,name)}\n")
    ics=[f"{r} ({v})" for r,v in sorted(comps.items()) if lib_of(v) in ("TL072","TL074","LM13700")]
    pots=[f"{r} ({v})" for r,v in sorted(comps.items()) if v=="R_Potentiometer" or r.startswith("RV")]
    out.append(f"**ICs:** {', '.join(ics) or 'none'}  |  **Pots:** {', '.join(pots) or 'none'}\n")
    out.append("\n| net (breadboard row) | connect these pins |\n|---|---|")
    for net,nodes in sorted(nets.items()):
        pins=", ".join(pinlabel(r,p,comps) for r,p in nodes)
        out.append(f"| **{net}** | {pins} |")
    out.append("")
# 08_output: hardcoded (SKiDL won't emit its netlist; trivial mixer + Volume)
out.append("\n## output - Output (mix + Volume)\n")
out.append("**ICs:** U1 (TL072)  |  **Pots:** RV1 Volume (100k, audio taper)\n")
out.append("\n| net (breadboard row) | connect these pins |\n|---|---|")
out += [
 "| **BODYF** | R1.1  (from filter stage BODYF) |",
 "| **OCTF** | R2.1  (from octave stage OCTF) |",
 "| **NSUM** | R1.2, R2.2, R3.1, U1.2 (IN1-) |",
 "| **OPRE** | R3.2, U1.1 (OUT1), RV1.1 (end) |",
 "| **VW** | RV1.2 (wiper), U1.5 (IN2+) |",
 "| **OUT** | U1.7 (OUT2), U1.6 (IN2-)  -> output jack tip |",
 "| **VREF** | U1.3 (IN1+), RV1.3 (end) |",
 "| **VCC** | U1.8 (V+) |",
 "| **GND** | U1.4 (V-) |", "",
 "_R1=R2=R3 = 22k (mixer). Body + octave sum here, then Volume sets output level._\n"]
open("kicad/breadboard/CONNECTIONS.md","w").write("\n".join(out))
print("wrote kicad/breadboard/CONNECTIONS.md for", len(glob.glob('kicad/breadboard/nets/*.net')), "blocks")
