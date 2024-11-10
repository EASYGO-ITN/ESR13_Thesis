import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

fig, ax = plt.subplots()
ax_twin = ax.twinx()

water = cp.AbstractState("?", "water")
water.build_phase_envelope("TS")
tab_water = water.get_phase_envelope_data()

Mr = 0.018
smass = [s/Mr for s in tab_water.smolar_vap]


Tin = 200 + 273
Qin = 0.1
water.update(cp.QT_INPUTS, Qin, Tin)
Sin = water.smass()
Hin = water.hmass()
Pin = water.p()

# Pflash = 0.8*Pin

Tflash1 = Tin - 0.25*(Tin - (273+50))
Pflash1 = PropsSI("P", "T", Tflash1, "Q", 1, "water")

Tflash2 = Tin - 0.75*(Tin - (273+50))
Pflash2 = PropsSI("P", "T", Tflash2, "Q", 1, "water")

# first flash
water.update(cp.HmassP_INPUTS, Hin, Pflash1)
x1 = water.Q()
Sflash1 = water.smass()

water.update(cp.QT_INPUTS, 0, Tflash1)
Hliq1 = water.hmass()
Sliq1 = water.smass()

water.update(cp.QT_INPUTS, 1, Tflash1)
Hvap1 = water.hmass()
Svap1 = water.smass()

# second flash
water.update(cp.HmassP_INPUTS, Hliq1, Pflash2)
x2 = water.Q()
Sflash2 = water.smass()

water.update(cp.QT_INPUTS, 0, Tflash2)
Hliq2 = water.hmass()
Sliq2 = water.smass()

water.update(cp.QT_INPUTS, 1, Tflash2)
Hvap2 = water.hmass()
Svap2 = water.smass()

# expansion1
water.update(cp.PSmass_INPUTS, Pflash2, Svap1)
Tout_isen1 = water.T()
Hout_isen1 = water.hmass()

eta_isen = 0.85
Hout = Hvap1 - eta_isen*(Hvap1 - Hout_isen1)
water.update(cp.HmassP_INPUTS, Hout, Pflash2)
Tout1 = water.T()
Sout1 = water.smass()
Hout1 = water.hmass()

ts_exp1 = list(np.linspace(Tflash1, Tflash2, 20))
ps_exp1 = [PropsSI("P", "T", t, "Q", 1, "water") for t in ts_exp1]
ss_exp1 = []
for p in ps_exp1:
    water.update(cp.PSmass_INPUTS, p, Svap1)
    Hout_isen_ = water.hmass()

    Hout_ = Hvap1 - eta_isen * (Hvap1 - Hout_isen_)
    water.update(cp.HmassP_INPUTS, Hout_, p)
    ss_exp1.append(water.smass())

# mix vapour

Smix = (x1*Sout1 + (1-x1)*x2*Svap2) / (x1 + (1-x1)*x2)
Hmix = (x1*Hout1 + (1-x1)*x2*Hvap2) / (x1 + (1-x1)*x2)

Pout = 0.1e5
# expansion2
water.update(cp.PSmass_INPUTS, Pout, Smix)
Tout_isen2 = water.T()
Hout_isen2 = water.hmass()

eta_isen = 0.85
Hout = Hmix - eta_isen*(Hmix - Hout_isen2)
water.update(cp.HmassP_INPUTS, Hout, Pout)
Tout2 = water.T()
Sout2 = water.smass()

ts_exp2 = list(np.linspace(Tflash2, Tout2, 20))
ps_exp2 = [PropsSI("P", "T", t, "Q", 1, "water") for t in ts_exp2]
ss_exp2 = []
for p in ps_exp2:
    water.update(cp.PSmass_INPUTS, p, Smix)
    Hout_isen_ = water.hmass()

    Hout_ = Hmix - eta_isen * (Hmix - Hout_isen_)
    water.update(cp.HmassP_INPUTS, Hout_, p)
    ss_exp2.append(water.smass())

water.update(cp.PQ_INPUTS, Pout, 0)
Treinj = water.T()
Sreinj = water.smass()

ts = [Tin, Tflash1, np.NAN, Tflash1, Tflash2, np.NAN] + ts_exp1 + [np.NAN, Tflash2] + ts_exp2 + [Tout2, Treinj]
ss = [Sin, Sflash1, np.NAN, Sliq1, Sflash2, np.NAN] + ss_exp1 + [np.NAN, Smix] + ss_exp2 + [Sout2, Sreinj]


ax.plot(smass, tab_water.T, "k:")  # the phase envelope
ax.plot([Svap1, Svap1, np.NAN, Smix, Smix], [Tflash1, Tflash2, np.NAN, Tflash2, Tout2], "--", color="#1f77b4")
ax.plot(ss, ts, color="#1f77b4")
ax.plot([Sin, Sliq1, Svap1, Sliq2, Svap2, Sout1, Smix, Sreinj], [Tin, Tflash1, Tflash1, Tflash2, Tflash2, Tout1, Tflash2, Treinj], "o", color="#1f77b4")
ax.plot([Sliq1, Svap1], [Tflash1, Tflash1], "-.", color="#1f77b4")
ax.plot([Sliq2, Svap2], [Tflash2, Tflash2], "-.", color="#1f77b4")

ax_twin.set_ylim([t-273 for t in ax.get_ylim()])

ax.set_ylabel("Temperature/\\unit{\\K}")
ax.set_xlabel("Entropy/\\unit{\\joule\\per\\kg\\per\\K}")
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

tikzplotlib.save("MultiFlash_TS_Diagram.tex")

plt.show()