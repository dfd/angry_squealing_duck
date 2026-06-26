#!/usr/bin/env python3
"""
Angry Squealing Duck - KiCad netlist generator (SKiDL).

1:1 translation of spice/blocks/pedal_build.cir (the all-real, no-B-source buildable
design: Muff fuzz + hybrid route, dual-gang Quack). Run under the uv venv:

    KICAD8_SYMBOL_DIR=/usr/share/kicad/symbols uv run kicad/duck.py

Emits kicad/duck.net (KiCad netlist) for the pcbnew layout step (system python 3.14).

Packaging: 23 op-amp sections -> 6x TL074 (U1..U6, 1 spare); 2 OTAs -> 1x LM13700 (U7).
Single 9V supply; op-amps run V+=VCC / V-=GND, all audio biased around the buffered
4.5V VREF. Pots: Volume/Anger/Squeal single, Quack dual-gang (RV4A sweep + RV4B Q).
"""
import os
os.environ.setdefault("KICAD8_SYMBOL_DIR", "/usr/share/kicad/symbols")
from skidl import Part, Net, generate_netlist, set_default_tool, KICAD8, TEMPLATE, ERC

set_default_tool(KICAD8)

# ---------------- footprints (through-hole) ----------------
FP_DIP14 = "Package_DIP:DIP-14_W7.62mm"
FP_DIP16 = "Package_DIP:DIP-16_W7.62mm"
FP_R     = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical"
FP_Cf    = "Capacitor_THT:C_Rect_L7.0mm_W2.5mm_P5.00mm"      # film
FP_Ce    = "Capacitor_THT:CP_Radial_D5.0mm_P2.50mm"          # electrolytic
FP_D     = "Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_AnodeUp"   # compact vertical mount
FP_POT   = "Potentiometer_THT:Potentiometer_Alps_RK097_Single_Horizontal"
FP_POT2  = "Potentiometer_THT:Potentiometer_Alps_RK097_Dual_Horizontal"   # dual-gang
FP_JACK  = "Connector_Audio:Jack_6.35mm_Neutrik_NJ3FD-V_Vertical"
FP_DC    = "Connector_BarrelJack:BarrelJack_Horizontal"
FP_SW    = "Button_Switch_THT:SW_PUSH_3PDT_Horizontal"
FP_LED   = "LED_THT:LED_D5.0mm"

# ---------------- part helpers ----------------
def R(val):  return Part("Device", "R", value=val, footprint=FP_R)
def Cf(val): return Part("Device", "C", value=val, footprint=FP_Cf)
def Ce(val): return Part("Device", "C_Polarized", value=val, footprint=FP_Ce)
def Di():    return Part("Diode", "1N4148", footprint=FP_D)
def Pot(val, ref=None):
    return Part("Device", "R_Potentiometer", value=val, footprint=FP_POT, ref=ref)

# ---------------- power nets ----------------
VCC = Net("VCC"); GND = Net("GND"); VREF = Net("VREF")
VCC.drive = GND.drive = 7  # POWER

# ---------------- TL074 pool: 6 quads, dispense op-amp sections ----------------
TL = [Part("Amplifier_Operational", "TL074", footprint=FP_DIP14, ref=f"U{i+1}")
      for i in range(6)]
for U in TL:
    U[4] += VCC      # V+
    U[11] += GND     # V-
# (out, inverting, non-inverting) pin numbers for the 4 sections of a TL074 (DIP-14)
_SEC = [(1, 2, 3), (7, 6, 5), (8, 9, 10), (14, 13, 12)]
_seq = [(U, k) for U in TL for k in range(4)]
_n = [0]
def amp():
    """Return (out, in_minus, in_plus) pins of the next free op-amp section."""
    U, k = _seq[_n[0]]; _n[0] += 1
    o, m, p = _SEC[k]
    return U[o], U[m], U[p]

def buf(in_net, out_net):
    """Unity follower: +=in, output tied back to -."""
    o, m, p = amp()
    p += in_net; o += out_net; m += out_net

# ============================================================
#  POWER SUPPLY  (supply.cir)  - 9V in, buffered 4.5V VREF
# ============================================================
DC = Part("Connector", "Barrel_Jack", footprint=FP_DC, ref="J3")
Dpr = Di()                                   # reverse-polarity protection (upgrade to 1N5817)
NRAW = Net("VRAW")
DC[1] += NRAW; DC[2] += GND                   # 1=center, 2=sleeve (set polarity by jack)
Dpr[1] += VCC; Dpr[2] += NRAW                 # A->K : VRAW -> VCC (blocks reverse)
Cps = Ce("100u"); Cps[1] += VCC; Cps[2] += GND
r1 = R("100k"); r2 = R("100k"); cref = Ce("47u")
NREF = Net("NREF")
r1[1] += VCC;  r1[2] += NREF
r2[1] += NREF; r2[2] += GND
cref[1] += NREF; cref[2] += GND
buf(NREF, VREF)                               # vref unity buffer

# ============================================================
#  INPUT  (jack + true-bypass master footswitch) + input_buffer
# ============================================================
JIN = Part("Connector_Audio", "AudioJack2", footprint=FP_JACK, ref="J1")
SIN = Net("SIN")                              # raw guitar in (tip)
JIN["T"] += SIN; JIN["S"] += GND
cin = Cf("100n"); rin = R("1M")
NP = Net("NP"); SIG = Net("SIG")
cin[1] += SIN; cin[2] += NP
rin[1] += NP;  rin[2] += VREF
buf(NP, SIG)                                  # input buffer -> SIG (split node)

# ============================================================
#  FUZZ  (fuzz_muff.cir) - 3 cascaded asymmetric soft-clip stages
# ============================================================
RV_ANGER = Pot("100k", ref="RV2")             # Anger (gain) - reverse-log ideal
def muff_stage(n_in, n_out, ri_part, rf_val):
    o, m, p = amp(); p += VREF
    n1 = Net(); rb = R("1M")
    cc = Cf("100n"); cc[1] += n_in; cc[2] += n1   # AC-couple in
    rb[1] += n1; rb[2] += VREF
    # input resistor (ri_part already a 2-pin net path n1->m)
    ri_part(n1, m)
    rf = R(rf_val); cf = Cf("1.5n")
    rf[1] += m; rf[2] += o
    cf[1] += m; cf[2] += o
    da = Di(); dba = Di(); dbb = Di(); x = Net()
    da[2] += m;  da[1] += o            # + side ~0.6V (A=o? Da m s -> anode m,cath s) : m->o
    dba[1] += o; dba[2] += x           # - side: s->x->m (two series)
    dbb[1] += x; dbb[2] += m
    o += n_out                          # stage output = o (== s)
# stage 1: Ri1 = 2.2k + Anger pot (rheostat)
N1 = Net("FZ1")
def ri1(n1, m):
    rfix = R("2.2k")
    rfix[1] += n1; rfix[2] += RV_ANGER[1]
    RV_ANGER[2] += m                    # wiper -> m (rheostat: term1..wiper)
    RV_ANGER[3] += RV_ANGER[2]          # tie other end to wiper (rheostat)
muff_stage(SIG, N1, ri1, "100k")
# stage 2: Ri2 = 12k
N2 = Net("FZ2")
def ri2(n1, m):
    r = R("12k"); r[1] += n1; r[2] += m
muff_stage(N1, N2, ri2, "100k")
# stage 3: Ri3 = 12k, Rf3 = 68k
N3 = Net("FZ3")
def ri3(n1, m):
    r = R("12k"); r[1] += n1; r[2] += m
muff_stage(N2, N3, ri3, "68k")
# output LP  Rlp 2.2k / Clp 27n
FZ = Net("FZ")
rlp = R("2.2k"); clp = Cf("27n")
rlp[1] += N3; rlp[2] += FZ
clp[1] += FZ; clp[2] += VREF

# ============================================================
#  full-wave rectifier helper (fwr.cir)
# ============================================================
def fwr(rin_net, out_net):
    o1, m1, p1 = amp(); p1 += VREF
    o2, m2, p2 = amp(); p2 += VREF
    n1 = Net(); n2 = Net(); hw = Net()
    a = R("10k"); a[1] += rin_net; a[2] += n1
    rf1 = R("10k"); rf1[1] += n1; rf1[2] += hw
    d1 = Di(); d1[1] += o1; d1[2] += n1        # feedback clamp (A=o1->K=n1)
    d2 = Di(); d2[1] += hw; d2[2] += o1        # steering (A=hw->K=o1)
    m1 += n1
    r3 = R("10k"); r3[1] += rin_net; r3[2] += n2
    r4 = R("4.7k");  r4[1] += hw; r4[2] += n2
    rf2 = R("10k"); rf2[1] += n2; rf2[2] += out_net
    m2 += n2; o2 += out_net

# ============================================================
#  ENVELOPE FOLLOWER (envfollow.cir): fwr -> 2-pole average -> buffer
# ============================================================
RABS_E = Net("RABS_E"); CV = Net("CV")
fwr(SIG, RABS_E)
ra = R("15k"); ca = Ce("220n"); rb = R("15k"); cb = Ce("220n")
ne1 = Net(); ne2 = Net()
ra[1] += RABS_E; ra[2] += ne1; ca[1] += ne1; ca[2] += VREF
rb[1] += ne1; rb[2] += ne2; cb[1] += ne2; cb[2] += VREF
buf(ne2, CV)

# ============================================================
#  OCTAVE GENERATOR (octave_gen.cir, full octave - Squeal pot is external)
# ============================================================
OCTV = Net("OCTV")
chp = Cf("47n"); oin = Net(); rabs_o = Net()
chp[1] += FZ; chp[2] += oin
fwr(oin, rabs_o)
rlp_o = R("3.3k"); clp_o = Cf("12n"); nlp = Net()
rlp_o[1] += rabs_o; rlp_o[2] += nlp; clp_o[1] += nlp; clp_o[2] += VREF
cc_o = Cf("1u"); rb_o = R("100k"); oac = Net()
cc_o[1] += nlp; cc_o[2] += oac; rb_o[1] += oac; rb_o[2] += VREF
buf(oac, OCTV)

# ============================================================
#  V-to-I  (crossfade Quack-sweep, dual-gang section A)
# ============================================================
# Quack = ONE dual-gang pot (RV4): section A (pins 1-3) = sweep, section B (4-6) = Q
RV_QK = Part("Device", "R_Potentiometer_Dual_Separate", value="100k", ref="RV4",
             footprint=FP_POT2)
VOFF = Net("VOFF"); ECTL = Net("ECTL"); VBIAS = Net("VBIAS")
rvo1 = R("100k"); rvo2 = R("22k"); nvoff = Net()
rvo1[1] += VCC; rvo1[2] += nvoff; rvo2[1] += nvoff; rvo2[2] += GND
buf(nvoff, VOFF)                              # buffer Vpark
# difference amp: ECTL = VOFF + 11*(CV-VREF)
od, md, pd = amp()
rdi = R("10k"); rdf = R("110k"); rdj = R("10k"); rdk = R("110k")
ni = Net(); pi_ = Net()
rdi[1] += VREF; rdi[2] += ni; rdf[1] += ni; rdf[2] += ECTL
rdj[1] += CV;   rdj[2] += pi_; rdk[1] += pi_; rdk[2] += VOFF
md += ni; pd += pi_; od += ECTL
# crossfade pot: VOFF (term1) - wiper VBP - ECTL (term3)
VBP = Net("VBP")
RV_QK[1] += VOFF; RV_QK[2] += VBP; RV_QK[3] += ECTL   # gang A: sweep crossfade
buf(VBP, VBIAS)                               # buffer wiper -> VBIAS

# ============================================================
#  BODY BAND-PASS FILTER (vcf_build.cir) - LM13700 OTA SVF
# ============================================================
U7 = Part("Amplifier_Operational", "LM13700", footprint=FP_DIP16, ref="U7")
U7[11] += VCC; U7[6] += GND                   # V+ / V-
BODYF = Net("BODYF")
# bias resistors  vbias -> each OTA Iabc pin (1 = Iabc A, 16 = Iabc B)
rab1 = R("10k"); rab2 = R("10k")
rab1[1] += VBIAS; rab1[2] += U7[1]
rab2[1] += VBIAS; rab2[2] += U7[16]
# inverter:  IINV = 2*VREF - FZ
oi, mi, pii = amp(); pii += VREF
rinv1 = R("10k"); rinv2 = R("10k"); IINV = Net(); nii = Net()
rinv1[1] += FZ; rinv1[2] += nii; rinv2[1] += nii; rinv2[2] += IINV
mi += nii; oi += IINV
# summer: HP = VREF + (FZ-VREF) - (LP-VREF) - d*(BP-VREF)
osu, msu, psu = amp(); psu += VREF
HP = Net("HP"); BP = Net("BP"); LP = Net("LP"); NS = Net()
rs_in = R("10k"); rs_lp = R("10k"); rs_f = R("10k")
rs_in[1] += IINV; rs_in[2] += NS
rs_lp[1] += LP;   rs_lp[2] += NS
rs_f[1] += NS;    rs_f[2] += HP
msu += NS; osu += HP
# Quack-Q network:  Rq = 7k + (RV5 || 40k)  from BP to NS
rqfix = R("6.8k"); rqpar = R("39k"); nq = Net()
rqfix[1] += BP; rqfix[2] += nq
RV_QK[4] += nq; RV_QK[5] += NS; RV_QK[6] += nq                  # gang B: Q rheostat
rqpar[1] += nq; rqpar[2] += NS                                  # 40k parallel
# integrator 1 -> BP   (atten 49k:1k into OTA A +in, cap on out, buffer)
ra1 = R("47k"); rb1 = R("1k"); a1 = Net(); i1 = Net()
ra1[1] += HP; ra1[2] += a1; rb1[1] += a1; rb1[2] += VREF
U7[3] += a1; U7[4] += VREF                    # OTA A  +in=3, -in=4
cc1 = Cf("10n"); cc1[1] += U7[5]; cc1[2] += VREF    # OTA A out=5
i1 += U7[5]; buf(i1, BP)
# integrator 2 -> LP   (OTA B: +in=14, -in=13, out=12)
ra2 = R("47k"); rb2 = R("1k"); a2 = Net()
ra2[1] += BP; ra2[2] += a2; rb2[1] += a2; rb2[2] += VREF
U7[14] += a2; U7[13] += VREF
cc2 = Cf("10n"); cc2[1] += U7[12]; cc2[2] += VREF
buf(U7[12], LP)
# band-pass output buffer
buf(BP, BODYF)

# ============================================================
#  OCTAVE makeup (x8) -> Squeal pot -> fixed HP
# ============================================================
RV_SQ = Pot("100k", ref="RV3")                # Squeal (audio taper)
OCTF = Net("OCTF")
om, mm, pm = amp()                            # non-inverting x8
rmf = R("68k"); rmg = R("10k"); OCG = Net(); mfb = Net()
pm += OCTV; mm += mfb; om += OCG
rmf[1] += OCG; rmf[2] += mfb; rmg[1] += mfb; rmg[2] += VREF
# Squeal pot divider: OCG (term1) - wiper SW - VREF (term3)
SW = Net()
RV_SQ[1] += OCG; RV_SQ[2] += SW; RV_SQ[3] += VREF
# fixed HP ~329Hz (22n / 22k) -> buffer
chf = Cf("22n"); rhf = R("22k"); nhf = Net()
chf[1] += SW; chf[2] += nhf; rhf[1] += nhf; rhf[2] += VREF
buf(nhf, OCTF)

# ============================================================
#  SUMMER (body + octave, inverting unity) + Volume + output buffer
# ============================================================
osm, msm, psm = amp(); psm += VREF
rua = R("22k"); rub = R("22k"); ruf = R("22k"); OPRE = Net("OPRE"); nsum = Net()
rua[1] += BODYF; rua[2] += nsum
rub[1] += OCTF;  rub[2] += nsum
ruf[1] += nsum;  ruf[2] += OPRE
msm += nsum; osm += OPRE
# Volume pot: OPRE (term1) - wiper VW - VREF (term3)
RV_VOL = Pot("100k", ref="RV1")               # Volume (audio taper)
VW = Net(); OUT = Net("OUT")
RV_VOL[1] += OPRE; RV_VOL[2] += VW; RV_VOL[3] += VREF
buf(VW, OUT)

# ---------------- output jack ----------------
JOUT = Part("Connector_Audio", "AudioJack2", footprint=FP_JACK, ref="J2")
JOUT["T"] += OUT; JOUT["S"] += GND

# ============================================================
#  tie off spares / unused pins  (clean ERC)
# ============================================================
# mark the supply rails as driven (power comes in via the DC jack -> ERC clean)
from skidl import POWER
VCC.drive = POWER
GND.drive = POWER
# spare op-amp section (U6 unit D): unity follower of VREF
U6 = TL[5]; U6[12] += VREF; U6[13] += U6[14]
# LM13700 unused: buffer inputs -> GND; buffer outputs + diode-bias left open
#   (sim used /50 input attenuation; linearizing diodes are a future board option)
U7[7] += GND; U7[10] += GND
for _pin in (U7[8], U7[9], U7[2], U7[15]):
    _pin.do_erc = False

ERC()
generate_netlist(file_="kicad/duck.net")
print("netlist -> kicad/duck.net  | op-amp sections used:", _n[0], "/ 24")
