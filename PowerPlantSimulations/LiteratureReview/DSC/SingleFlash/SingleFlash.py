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

Tflash = (Tin + 273+50)*0.52
Pflash = PropsSI("P", "T", Tflash, "Q", 1, "water")

water.update(cp.HmassP_INPUTS, Hin, Pflash)
x = water.Q()
Tflash = water.T()
Sflash = water.smass()

water.update(cp.QT_INPUTS, 0, Tflash)
Hliq = water.hmass()
Sliq = water.smass()

water.update(cp.QT_INPUTS, 1, Tflash)
Hvap = water.hmass()
Svap = water.smass()

Pout = 0.1e5
water.update(cp.PSmass_INPUTS, Pout, Svap)
Tout_isen = water.T()
Hout_isen = water.hmass()

eta_isen = 0.85
Hout = Hvap - eta_isen*(Hvap - Hout_isen)
water.update(cp.HmassP_INPUTS, Hout, Pout)
Tout = water.T()
Sout = water.smass()

ts_exp = list(np.linspace(Tflash, Tout, 20))
ps_exp = [PropsSI("P", "T", t, "Q", 1, "water") for t in ts_exp]
ss_exp = []
for p in ps_exp:
    water.update(cp.PSmass_INPUTS, p, Svap)
    Hout_isen_ = water.hmass()

    Hout_ = Hvap - eta_isen * (Hvap - Hout_isen_)
    water.update(cp.HmassP_INPUTS, Hout_, p)
    ss_exp.append(water.smass())

water.update(cp.PQ_INPUTS, Pout, 0)
Treinj = water.T()
Sreinj = water.smass()

ts = [Tin, Tflash, np.NAN, Tflash] + ts_exp + [Tout, Treinj]
ss = [Sin, Sflash, np.NAN, Svap] + ss_exp + [Sout, Sreinj]


ax.plot(smass, tab_water.T, "k:")  # the phase envelope
ax.plot([Svap, Svap], [Tflash, Tout], "--", color="#1f77b4")
ax.plot(ss, ts, color="#1f77b4")
ax.plot([Sin, Sliq, Svap, Sout, Sreinj], [Tin, Tflash, Tflash, Tout, Treinj], "o", color="#1f77b4")
ax.plot([Sliq, Svap], [Tflash, Tflash], "-.", color="#1f77b4")

ax_twin.set_ylim([t-273 for t in ax.get_ylim()])

ax.set_ylabel("Temperature/\\unit{\\K}")
ax.set_xlabel("Entropy/\\unit{\\joule\\per\\kg\\per\\K}")
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

tikzplotlib.save("SingleFlash_TS_Diagram.tex")

plt.show()