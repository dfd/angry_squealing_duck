# Angry Squealing Duck - breadboard connection tables

Each **net = one breadboard row**: put every listed pin in that row. IC pins are
annotated with their function. Build in numbered order (see BUILD_GUIDE.md).


## supply - Supply / 4.5 V Vref

**ICs:** U1 (TL072)  |  **Pots:** none


| net (breadboard row) | connect these pins |
|---|---|
| **GND** | C1.2, C2.2, R2.2, U1.4 (V- (GND)) |
| **NREF** | C2.1, R1.2, R2.1, U1.3 (IN1+) |
| **V9** | D1.2 (A) |
| **VCC** | C1.1, D1.1 (K (band)), R1.1, U1.8 (V+ (VCC)) |
| **VREF** | U1.1 (OUT1), U1.2 (IN1-) |


## input_buffer - Input buffer

**ICs:** U1 (TL072)  |  **Pots:** none


| net (breadboard row) | connect these pins |
|---|---|
| **GND** | U1.4 (V- (GND)) |
| **IN** | C1.1 |
| **NP** | C1.2, R1.1, U1.3 (IN1+) |
| **SIG** | U1.1 (OUT1), U1.2 (IN1-) |
| **VCC** | U1.8 (V+ (VCC)) |
| **VREF** | R1.2 |


## fuzz_anger - Fuzz (Anger) - 3-stage Muff

**ICs:** U1 (TL074)  |  **Pots:** RV1 (100k)


| net (breadboard row) | connect these pins |
|---|---|
| **FZ** | C7.1, R10.2 |
| **FZ1** | C2.2, C3.1, D1.1 (K (band)), D2.2 (A), R3.2, U1.1 (OUT1) |
| **FZ2** | C4.2, C5.1, D4.1 (K (band)), D5.2 (A), R6.2, U1.7 (OUT2) |
| **FZ3** | C6.2, D7.1 (K (band)), D8.2 (A), R10.1, R9.2, U1.8 (OUT3) |
| **GND** | U1.11 (V- (GND)) |
| **N$1** | C1.2, R1.1, R2.1 |
| **N$10** | C5.2, R7.1, R8.1 |
| **N$11** | C6.1, D7.2 (A), D9.1 (K (band)), R8.2, R9.1, U1.9 (IN3-) |
| **N$13** | D8.1 (K (band)), D9.2 (A) |
| **N$2** | R2.2, RV1.1 |
| **N$3** | C2.1, D1.2 (A), D3.1 (K (band)), R3.1, RV1.2, RV1.3, U1.2 (IN1-) |
| **N$5** | D2.1 (K (band)), D3.2 (A) |
| **N$6** | C3.2, R4.1, R5.1 |
| **N$7** | C4.1, D4.2 (A), D6.1 (K (band)), R5.2, R6.1, U1.6 (IN2-) |
| **N$9** | D5.1 (K (band)), D6.2 (A) |
| **SIG** | C1.1 |
| **VCC** | U1.4 (V+ (VCC)) |
| **VREF** | C7.2, R1.2, R4.2, R7.2, U1.10 (IN3+), U1.3 (IN1+), U1.5 (IN2+) |


## octave_squeal - Octave (Squeal)

**ICs:** U1 (TL074)  |  **Pots:** RV1 (100k)


| net (breadboard row) | connect these pins |
|---|---|
| **FZ** | C1.1 |
| **GND** | U1.11 (V- (GND)) |
| **N$1** | C1.2, R1.1, R3.1 |
| **N$10** | R8.2, R9.1, U1.9 (IN3-) |
| **N$11** | C4.1, RV1.2 |
| **N$12** | C4.2, R10.1, U1.12 (IN4+) |
| **N$2** | R5.2, R6.1, U1.7 (OUT2) |
| **N$3** | D1.1 (K (band)), R1.2, R2.1, U1.2 (IN1-) |
| **N$4** | R3.2, R4.2, R5.1, U1.6 (IN2-) |
| **N$5** | D2.2 (A), R2.2, R4.1 |
| **N$6** | D1.2 (A), D2.1 (K (band)), U1.1 (OUT1) |
| **N$7** | C2.1, C3.1, R6.2 |
| **N$8** | C3.2, R7.1, U1.10 (IN3+) |
| **N$9** | R8.1, RV1.1, U1.8 (OUT3) |
| **OCTF** | U1.13 (IN4-), U1.14 (OUT4) |
| **VCC** | U1.4 (V+ (VCC)) |
| **VREF** | C2.2, R10.2, R7.2, R9.2, RV1.3, U1.3 (IN1+), U1.5 (IN2+) |


## envelope - Envelope follower

**ICs:** U1 (TL074)  |  **Pots:** none


| net (breadboard row) | connect these pins |
|---|---|
| **CV** | U1.8 (OUT3), U1.9 (IN3-) |
| **GND** | U1.11 (V- (GND)) |
| **N$1** | R5.2, R6.1, U1.7 (OUT2) |
| **N$2** | D1.1 (K (band)), R1.2, R2.1, U1.2 (IN1-) |
| **N$3** | R3.2, R4.2, R5.1, U1.6 (IN2-) |
| **N$4** | D2.2 (A), R2.2, R4.1 |
| **N$5** | D1.2 (A), D2.1 (K (band)), U1.1 (OUT1) |
| **N$6** | C1.1, R6.2, R7.1 |
| **N$7** | C2.1, R7.2, U1.10 (IN3+) |
| **SIG** | R1.1, R3.1 |
| **VCC** | U1.4 (V+ (VCC)) |
| **VREF** | C1.2, C2.2, U1.3 (IN1+), U1.5 (IN2+) |


## quack_vtoi - Quack control (envelope -> V-to-I)

**ICs:** U1 (TL074)  |  **Pots:** RV1 (100k)


| net (breadboard row) | connect these pins |
|---|---|
| **CV** | R5.1 |
| **ECTL** | R4.2, RV1.3, U1.7 (OUT2) |
| **GND** | R2.2, U1.11 (V- (GND)) |
| **N$1** | R1.2, R2.1, U1.3 (IN1+) |
| **N$2** | R3.2, R4.1, U1.6 (IN2-) |
| **N$3** | R5.2, R6.1, U1.5 (IN2+) |
| **N$4** | RV1.2, U1.10 (IN3+) |
| **VBIAS** | U1.8 (OUT3), U1.9 (IN3-) |
| **VCC** | R1.1, U1.4 (V+ (VCC)) |
| **VOFF** | R6.2, RV1.1, U1.1 (OUT1), U1.2 (IN1-) |
| **VREF** | R3.1 |


## filter_lm13700 - LM13700 band-pass filter

**ICs:** U1 (TL074), U2 (TL072), U3 (LM13700)  |  **Pots:** RV1 (100k)


| net (breadboard row) | connect these pins |
|---|---|
| **BODYF** | U2.1 (OUT1), U2.2 (IN1-) |
| **BP** | R12.1, R8.1, U1.8 (OUT3), U1.9 (IN3-), U2.3 (IN1+) |
| **FZ** | R3.1 |
| **GND** | U1.11 (V- (GND)), U2.4 (V- (GND)), U3.6 (V-) |
| **HP** | R10.1, R7.2, U1.7 (OUT2) |
| **LP** | R6.1, U1.13 (IN4-), U1.14 (OUT4) |
| **N$1** | R5.2, R6.2, R7.1, R9.2, RV1.2, RV1.3, U1.6 (IN2-) |
| **N$10** | C1.1, U1.10 (IN3+), U3.5 (OUT-A) |
| **N$11** | R12.2, R13.1, U3.14 (IN+B) |
| **N$12** | C2.1, U1.12 (IN4+), U3.12 (OUT-B) |
| **N$4** | R1.2, U3.1 (Iabc-A) |
| **N$5** | R2.2, U3.16 (Iabc-B) |
| **N$6** | R3.2, R4.1, U1.2 (IN1-) |
| **N$7** | R4.2, R5.1, U1.1 (OUT1) |
| **N$8** | R8.2, R9.1, RV1.1 |
| **N$9** | R10.2, R11.1, U3.3 (IN+A) |
| **VBIAS** | R1.1, R2.1 |
| **VCC** | U1.4 (V+ (VCC)), U2.8 (V+ (VCC)), U3.11 (V+) |
| **VREF** | C1.2, C2.2, R11.2, R13.2, U1.3 (IN1+), U1.5 (IN2+), U3.13 (IN-B), U3.4 (IN-A) |


## output - Output (mix + Volume)

**ICs:** U1 (TL072)  |  **Pots:** RV1 Volume (100k, audio taper)


| net (breadboard row) | connect these pins |
|---|---|
| **BODYF** | R1.1  (from filter stage BODYF) |
| **OCTF** | R2.1  (from octave stage OCTF) |
| **NSUM** | R1.2, R2.2, R3.1, U1.2 (IN1-) |
| **OPRE** | R3.2, U1.1 (OUT1), RV1.1 (end) |
| **VW** | RV1.2 (wiper), U1.5 (IN2+) |
| **OUT** | U1.7 (OUT2), U1.6 (IN2-)  -> output jack tip |
| **VREF** | U1.3 (IN1+), RV1.3 (end) |
| **VCC** | U1.8 (V+) |
| **GND** | U1.4 (V-) |

_R1=R2=R3 = 22k (mixer). Body + octave sum here, then Volume sets output level._
