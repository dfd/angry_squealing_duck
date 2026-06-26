# Angry Squealing Duck — build cost estimate

Rough estimates from `BOM.md`, **budget DIY sourcing** (Tayda / AliExpress). Mouser/DigiKey
run ~1.5–2× higher. USD, one unit. These are ballpark figures, **not live quotes**. The board
is large (175×120 mm), so fab + enclosure cost more than a typical compact pedal.

Parts in the BOM: 6× TL074 + 1× LM13700, 4× 100k pots (RV4 = dual-gang Quack), 14× 1N4148,
52 resistors, 18 caps. Build extras (not in BOM): 2× 3PDT footswitches (true-bypass + Squeal),
LEDs, knobs, IC sockets, enclosure.

## 🍞 Breadboard (prototype)

| item | est. |
|---|---|
| 3–4 full-size breadboards *(reusable)* | $20–30 |
| jumper wire kit *(reusable)* | $8–15 |
| 9 V supply (battery+clip or adapter) | $3–8 |
| ~8 TL07x op-amps + 1 LM13700 | $7–10 |
| 14× 1N4148 | ~$0.50 |
| ~55 resistors + 18 caps *(or assortment kits, reusable)* | $6–10 |
| 4 pots (3 single + 1 dual-gang 100k) | $8–14 |
| *no jacks / enclosure / footswitches needed* | — |
| **Total, buying fresh** | **≈ $55–85** |
| **Marginal** (if you already own breadboards/jumpers/supply/kits) | **≈ $25–40** |

Not giggable — it's a test rig. But it's the cheapest way to confirm the circuit before
committing to copper. See `BUILD_GUIDE.md` for the staged bring-up.

## 🟢 PCB (finished, giggable pedal)

| item | est. |
|---|---|
| PCB fab — 175×120 mm 2-layer, **5 pcs** + shipping (you keep 5 boards) | $35–55 |
| 6× TL074 + 1× LM13700 | $5–7 |
| 7× IC sockets | ~$2 |
| 14× 1N4148 | ~$0.50 |
| 52 resistors + 18 caps | $5–8 |
| 4 pots + 4 knobs | $11–20 |
| 2× ¼" jacks + DC jack | $4–7 |
| 2× 3PDT footswitches + 2 LEDs | $6–10 |
| enclosure (1590DD-class) | $12–18 |
| wire / solder / battery snap / standoffs | ~$5 |
| **First complete pedal** (incl the 5-board fab batch) | **≈ $85–130** |
| **Each additional build** (from the 4 spare boards) | **≈ $50–75** |

## Takeaways

- **Electronics are cheap (~$15–20).** The cost is the *mechanical* stuff — enclosure,
  footswitches, jacks, knobs — plus the board. The breadboard skips all of it.
- **The 175×120 mm board is the cost driver.** It's past the cheap ≤100×100 mm fab tier *and*
  needs a large (1590DD-class) enclosure. Going SMD or splitting the board would cut both.
- **LM13700** is the priciest / rarest active part (~$2) — order a spare.
- **Shipping** is often the single biggest line on a small order ($5–20+) — batch one cart.
- Budget sources (Tayda + AliExpress) hit the low end; Mouser/DigiKey ~1.5–2×.

**Bottom line:** prototype on breadboard for **~$25–40** (if you have the basics), then the
**first finished pedal is ~$85–130**, dropping to **~$50–75** for builds 2–5 off the same
board batch.
