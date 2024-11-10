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
Qin = 1
water.update(cp.QT_INPUTS, Qin, Tin)
Sin = water.smass()
Hin = water.hmass()

Pout = 0.1e5
water.update(cp.PSmass_INPUTS, Pout, Sin)
Tout_isen = water.T()
Hout_isen = water.hmass()

eta_isen = 0.85
Hout = Hin - eta_isen*(Hin - Hout_isen)
water.update(cp.HmassP_INPUTS, Hout, Pout)
Tout = water.T()
Sout = water.smass()

ts_exp = list(np.linspace(Tin, Tout, 20))
ps_exp = [PropsSI("P", "T", t, "Q", 1, "water") for t in ts_exp]
ss_exp = []
for p in ps_exp:
    water.update(cp.PSmass_INPUTS, p, Sin)
    Hout_isen_ = water.hmass()

    Hout_ = Hin - eta_isen * (Hin - Hout_isen_)
    water.update(cp.HmassP_INPUTS, Hout_, p)
    ss_exp.append(water.smass())

water.update(cp.PQ_INPUTS, Pout, 0)
Treinj = water.T()
Sreinj = water.smass()

ts = [Tin] + ts_exp + [Tout, Treinj]
ss = [Sin] + ss_exp + [Sout, Sreinj]


ax.plot(smass, tab_water.T, "k:")
ax.plot([Sin, Sin], [Tin, Tout], "--", color="#1f77b4")
ax.plot(ss, ts, color="#1f77b4")
ax.plot([Sin, Sout, Sreinj], [Tin, Tout, Treinj], "o", color="#1f77b4")

ax_twin.set_ylim([t-273 for t in ax.get_ylim()])

ax.set_ylabel("Temperature/\\unit{\\K}")
ax.set_xlabel("Entropy/\\unit{\\joule\\per\\kg\\per\\K}")
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

tikzplotlib.save("DrySteam_TS_Diagram.tex")