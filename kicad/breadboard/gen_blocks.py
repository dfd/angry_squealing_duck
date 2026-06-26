#!/usr/bin/env python3
"""
Per-block breadboard schematics for the Angry Squealing Duck.

    KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols uv run kicad/breadboard/gen_blocks.py

Each stage from spice/blocks/* is rebuilt as a small, standalone SKiDL circuit with its
OWN op-amp IC(s) (NOT the PCB's shared 6x-TL074 packing) so you can breadboard + test one
stage at a time. SKiDL generate_schematic() writes ./skidl.kicad_sch; we move it per block.
Values match the locked design (pedal_build.cir, V-to-I gain x73).
"""
import os, shutil
os.environ.setdefault("KICAD8_SYMBOL_DIR", "/usr/share/kicad/symbols")
from skidl import Part, Net, generate_schematic, generate_netlist, set_default_tool, KICAD8, reset

set_default_tool(KICAD8)
OUT = "kicad/breadboard"
DIP8, DIP14, DIP16 = "Package_DIP:DIP-8_W7.62mm", "Package_DIP:DIP-14_W7.62mm", "Package_DIP:DIP-16_W7.62mm"
FR  = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
FC  = "Capacitor_THT:C_Rect_L7.0mm_W2.5mm_P5.00mm"
FCP = "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm"
FD  = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"

def R(v):   return Part("Device","R", value=v, footprint=FR)
def C(v):   return Part("Device","C", value=v, footprint=FC)
def CP(v):  return Part("Device","C_Polarized", value=v, footprint=FCP)
def D():    return Part("Diode","1N4148", footprint=FD)
def POT(v): return Part("Device","R_Potentiometer", value=v)
def TL072(ref): return Part("Amplifier_Operational","TL072", value="TL072", ref=ref, footprint=DIP8)
def TL074(ref): return Part("Amplifier_Operational","TL074", value="TL074", ref=ref, footprint=DIP14)
def LM13700(ref): return Part("Amplifier_Operational","LM13700", value="LM13700", ref=ref, footprint=DIP16)

# op-amp section pin maps (out, in-, in+)
S072 = [(1,2,3),(7,6,5)]
S074 = [(1,2,3),(7,6,5),(8,9,10),(14,13,12)]
def diode(part, anode, cathode):   # 1N4148: pin1=K, pin2=A
    part[2]+=anode; part[1]+=cathode

def gen(name):
    import glob
    os.makedirs(f"{OUT}/nets", exist_ok=True)
    # netlist = the reliable connection record (no flaky router) -> drives the build tables
    generate_netlist(file_=f"{OUT}/nets/{name}.net")
    # drawn schematic = best-effort (SKiDL's router fails on dense analog blocks)
    for net in VREF.circuit.nets:
        if net.name in ("VCC","GND","VREF") or len(net.pins) < 2:
            net.stub = True
    try:
        generate_schematic()
        produced = glob.glob("*.kicad_sch")
        shutil.move(produced[0], f"{OUT}/{name}.kicad_sch")
        print(f"  -> {name}  (schematic + netlist)")
    except Exception as e:
        print(f"  -> {name}  (netlist only - router failed: {type(e).__name__})")
    for junk in glob.glob("*-erc.rpt") + glob.glob("*.kicad_sch"): os.remove(junk)
    reset()

VCC = GND = VREF = None
def rails():
    global VCC,GND,VREF
    VCC,GND,VREF = Net("VCC"),Net("GND"),Net("VREF")

# ============================================================ 1. SUPPLY
rails()
U = TL072("U1")
U[8]+=VCC; U[4]+=GND
dpr=D(); diode(dpr, Net("V9"), VCC)                   # reverse protection 9V->VCC
cbulk=CP("100u"); cbulk[1]+=VCC; cbulk[2]+=GND
r1,r2,cref = R("100k"),R("100k"),CP("47u")
NREF=Net("NREF")
r1[1]+=VCC; r1[2]+=NREF; r2[1]+=NREF; r2[2]+=GND; cref[1]+=NREF; cref[2]+=GND
o,m,p=[U[x] for x in S072[0]]; p+=NREF; o+=VREF; m+=VREF   # vref buffer
gen("01_supply")

# ============================================================ 2. INPUT BUFFER
rails(); U=TL072("U1"); U[8]+=VCC; U[4]+=GND
cin=C("100n"); rin=R("1M"); IN=Net("IN"); NP=Net("NP"); SIG=Net("SIG")
cin[1]+=IN; cin[2]+=NP; rin[1]+=NP; rin[2]+=VREF
o,m,p=[U[x] for x in S072[0]]; p+=NP; o+=SIG; m+=SIG
gen("02_input_buffer")

# ============================================================ 3. FUZZ (Anger) - 3-stage Muff
rails(); U=TL074("U1"); U[4]+=VCC; U[11]+=GND
SIG=Net("SIG"); FZ=Net("FZ"); ANGER=POT("100k")
def muff(n_in, n_out, sec, ri_builder, rf):
    o,m,p=[U[x] for x in S074[sec]]; p+=VREF
    n1=Net(); cc=C("100n"); rb=R("1M")
    cc[1]+=n_in; cc[2]+=n1; rb[1]+=n1; rb[2]+=VREF
    ri_builder(n1,m)
    rfp=R(rf); cf=C("1.5n"); rfp[1]+=m; rfp[2]+=o; cf[1]+=m; cf[2]+=o
    da,dba,dbb=D(),D(),D(); x=Net()
    diode(da, m, o); diode(dba, o, x); diode(dbb, x, m)
    o+=n_out
def ri1(n1,m):
    rf=R("2.2k"); rf[1]+=n1; rf[2]+=ANGER[1]; ANGER[2]+=m; ANGER[3]+=ANGER[2]
def ri2(n1,m):
    r=R("12k"); r[1]+=n1; r[2]+=m
N1,N2=Net("FZ1"),Net("FZ2")
N3=Net("FZ3")
muff(SIG,N1,0,ri1,"100k"); muff(N1,N2,1,ri2,"100k"); muff(N2,N3,2,ri2,"68k")
# stage-3 output node is FZ3; output LP
rlp=R("2.2k"); clp=C("27n"); rlp[1]+=N3; rlp[2]+=FZ; clp[1]+=FZ; clp[2]+=VREF
gen("03_fuzz_anger")

# ============================================================ 4. OCTAVE (Squeal)
rails(); U=TL074("U1"); U[4]+=VCC; U[11]+=GND
FZ=Net("FZ"); OCTF=Net("OCTF"); SQUEAL=POT("100k")
chp=C("47n"); OIN=Net(); chp[1]+=FZ; chp[2]+=OIN
# full-wave rectifier (sections 0,1)
def fwr(rin, out, s_a, s_b):
    o1,m1,p1=[U[x] for x in S074[s_a]]; p1+=VREF
    o2,m2,p2=[U[x] for x in S074[s_b]]; p2+=VREF
    n1,n2,hw=Net(),Net(),Net()
    a=R("10k"); a[1]+=rin; a[2]+=n1; rf1=R("10k"); rf1[1]+=n1; rf1[2]+=hw
    diode(D(), o1, n1); diode(D(), hw, o1); m1+=n1
    r3=R("10k"); r3[1]+=rin; r3[2]+=n2; r4=R("4.7k"); r4[1]+=hw; r4[2]+=n2
    rf2=R("10k"); rf2[1]+=n2; rf2[2]+=out; m2+=n2; o2+=out
RABS=Net()
fwr(OIN, RABS, 0, 1)
rlp=R("3.3k"); clp=C("12n"); NLP=Net(); rlp[1]+=RABS; rlp[2]+=NLP; clp[1]+=NLP; clp[2]+=VREF
cc=C("1u"); rb=R("100k"); OAC=Net(); cc[1]+=NLP; cc[2]+=OAC; rb[1]+=OAC; rb[2]+=VREF
# makeup x8 (section 2): ocg = vref + 8*(oac-vref)
o,m,p=[U[x] for x in S074[2]]; OCG=Net(); MFB=Net()
p+=OAC; o+=OCG; rmf=R("68k"); rmg=R("10k"); rmf[1]+=OCG; rmf[2]+=MFB; rmg[1]+=MFB; rmg[2]+=VREF; m+=MFB
# Squeal pot + fixed HP (section 3 buffer)
SW=Net(); SQUEAL[1]+=OCG; SQUEAL[2]+=SW; SQUEAL[3]+=VREF
chf=C("22n"); rhf=R("22k"); NHF=Net(); chf[1]+=SW; chf[2]+=NHF; rhf[1]+=NHF; rhf[2]+=VREF
o,m,p=[U[x] for x in S074[3]]; p+=NHF; o+=OCTF; m+=OCTF
gen("04_octave_squeal")

# ============================================================ 5. ENVELOPE FOLLOWER
rails(); U=TL074("U1"); U[4]+=VCC; U[11]+=GND
SIG=Net("SIG"); CV=Net("CV"); RABS=Net()
fwr(SIG, RABS, 0, 1)   # reuse fwr (sections 0,1)
ra=R("15k"); ca=CP("220n"); rb=R("15k"); cb=CP("220n"); N1=Net(); N2=Net()
ra[1]+=RABS; ra[2]+=N1; ca[1]+=N1; ca[2]+=VREF; rb[1]+=N1; rb[2]+=N2; cb[1]+=N2; cb[2]+=VREF
o,m,p=[U[x] for x in S074[2]]; p+=N2; o+=CV; m+=CV
gen("05_envelope")

# ============================================================ 6. QUACK CONTROL (V-to-I)
rails(); U=TL074("U1"); U[4]+=VCC; U[11]+=GND
CV=Net("CV"); VBIAS=Net("VBIAS"); VOFF=Net("VOFF"); ECTL=Net("ECTL"); QSWEEP=POT("100k")
rvo1=R("100k"); rvo2=R("22k"); NVOFF=Net(); rvo1[1]+=VCC; rvo1[2]+=NVOFF; rvo2[1]+=NVOFF; rvo2[2]+=GND
o,m,p=[U[x] for x in S074[0]]; p+=NVOFF; o+=VOFF; m+=VOFF                 # Vpark buffer
rdi=R("1.5k"); rdf=R("110k"); rdj=R("1.5k"); rdk=R("110k"); NI=Net(); PI=Net()
rdi[1]+=VREF; rdi[2]+=NI; rdf[1]+=NI; rdf[2]+=ECTL; rdj[1]+=CV; rdj[2]+=PI; rdk[1]+=PI; rdk[2]+=VOFF
o,m,p=[U[x] for x in S074[1]]; p+=PI; m+=NI; o+=ECTL                      # diff amp (gain ~73)
VBP=Net(); QSWEEP[1]+=VOFF; QSWEEP[2]+=VBP; QSWEEP[3]+=ECTL              # crossfade pot
o,m,p=[U[x] for x in S074[2]]; p+=VBP; o+=VBIAS; m+=VBIAS                # wiper buffer
gen("06_quack_vtoi")

# ============================================================ 7. LM13700 BAND-PASS FILTER
rails(); U=TL074("U1"); U[4]+=VCC; U[11]+=GND
U2=TL072("U2"); U2[8]+=VCC; U2[4]+=GND
OTA=LM13700("U3"); OTA[11]+=VCC; OTA[6]+=GND
FZ=Net("FZ"); VBIAS=Net("VBIAS"); BODYF=Net("BODYF"); QQ=POT("100k")
HP,BP,LP,NS=Net("HP"),Net("BP"),Net("LP"),Net()
rab1=R("10k"); rab2=R("10k"); IAB1=Net(); IAB2=Net()
rab1[1]+=VBIAS; rab1[2]+=OTA[1]; rab2[1]+=VBIAS; rab2[2]+=OTA[16]        # bias -> Iabc A/B
# inverter (U1 sec0): iinv = 2*vref - fz
ri1=R("10k"); ri2=R("10k"); NII=Net(); IINV=Net()
ri1[1]+=FZ; ri1[2]+=NII; ri2[1]+=NII; ri2[2]+=IINV
o,m,p=[U[x] for x in S074[0]]; p+=VREF; m+=NII; o+=IINV
# summer (U1 sec1): hp = vref + (fz) - (lp) - d*(bp), Quack-Q on bp
rsin=R("10k"); rslp=R("10k"); rsf=R("10k"); rqf=R("6.8k"); rqp=R("39k"); NQ=Net()
rsin[1]+=IINV; rsin[2]+=NS; rslp[1]+=LP; rslp[2]+=NS; rsf[1]+=NS; rsf[2]+=HP
rqf[1]+=BP; rqf[2]+=NQ; QQ[1]+=NQ; QQ[2]+=NS; QQ[3]+=QQ[2]; rqp[1]+=NQ; rqp[2]+=NS
o,m,p=[U[x] for x in S074[1]]; p+=VREF; m+=NS; o+=HP
# integrator 1 (OTA A -> BP), buffer U1 sec2
ra1=R("47k"); rb1=R("1k"); A1=Net(); cc1=C("10n")
ra1[1]+=HP; ra1[2]+=A1; rb1[1]+=A1; rb1[2]+=VREF
OTA[3]+=A1; OTA[4]+=VREF; cc1[1]+=OTA[5]; cc1[2]+=VREF
o,m,p=[U[x] for x in S074[2]]; p+=OTA[5]; o+=BP; m+=BP
# integrator 2 (OTA B -> LP), buffer U1 sec3
ra2=R("47k"); rb2=R("1k"); A2=Net(); cc2=C("10n")
ra2[1]+=BP; ra2[2]+=A2; rb2[1]+=A2; rb2[2]+=VREF
OTA[14]+=A2; OTA[13]+=VREF; cc2[1]+=OTA[12]; cc2[2]+=VREF
o,m,p=[U[x] for x in S074[3]]; p+=OTA[12]; o+=LP; m+=LP
# output buffer (U2 sec0): bp -> bodyf
o,m,p=[U2[x] for x in S072[0]]; p+=BP; o+=BODYF; m+=BODYF
gen("07_filter_lm13700")

# ============================================================ 8. OUTPUT (summer + volume)
rails(); U=TL072("U1"); U[8]+=VCC; U[4]+=GND
BODYF=Net("BODYF"); OCTF=Net("OCTF"); OUT=Net("OUT"); VOL=POT("100k")
rua=R("22k"); rub=R("22k"); ruf=R("22k"); NSUM=Net(); OPRE=Net()
rua[1]+=BODYF; rua[2]+=NSUM; rub[1]+=OCTF; rub[2]+=NSUM; ruf[1]+=NSUM; ruf[2]+=OPRE
o,m,p=[U[x] for x in S072[0]]; p+=VREF; m+=NSUM; o+=OPRE               # summer
VW=Net(); VOL[1]+=OPRE; VOL[2]+=VW; VOL[3]+=VREF
o,m,p=[U[x] for x in S072[1]]; p+=VW; o+=OUT; m+=OUT                   # volume buffer
gen("08_output")

# SKiDL doesn't flush the very last block's netlist -> a throwaway trailing block
rails(); rr=R("1k"); rr[1]+=VCC; rr[2]+=GND; gen("99_flush")

print("done - block netlists in", OUT, "/nets")
