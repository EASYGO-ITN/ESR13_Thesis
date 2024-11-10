import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

Tref = 298
Pref = 101325
rho0_wat = PropsSI("Dmolar", "T", Tref, "P", Pref, "water")
cp.CoolProp.set_reference_state("water", Tref, rho0_wat, 0, 0)

rho0_but = PropsSI("Dmolar", "T", Tref, "Q", 0, "butane")
cp.CoolProp.set_reference_state("butane", Tref, rho0_but, 0, 0)

water = cp.AbstractState("?", "water")
wf = cp.AbstractState("?", "water")

T_geo_in = 160 + 273.15
Q_geo_in = 0
water.update(cp.QT_INPUTS, Q_geo_in, T_geo_in)
P_geo_in = water.p()
H_geo_in = water.hmass()

T_wf_cond = 315
T_wf_evap = 76.73+273.15                # 70.00 60.00 75.00 76.73
DT_superheat = 155 +273.15 -T_wf_evap   # 63.40 41.10 74.50 78.27
# Net power                             # 25.36 18.40 28.07 28.79

pinchdT = 5
eta_pump_isen = 0.75
eta_turb_isen = 0.80

# pump inlet
wf.update(cp.QT_INPUTS, 0, T_wf_cond)
H_wf_in = wf.hmass()
S_wf_in = wf.smass()
T_wf_in = wf.T()
P_wf_in = wf.p()

P_wf_cond = wf.p()

# pump outlet
wf.update(cp.QT_INPUTS, 0, T_wf_evap)
P_wf_evap = wf.p()
print("Pevap", P_wf_evap/1e5)

wf.update(cp.PSmass_INPUTS, P_wf_evap, S_wf_in)
H_wf_pump_isen = wf.hmass()
H_wf_pump_out = H_wf_in + (H_wf_pump_isen - H_wf_in)/eta_pump_isen

wf.update(cp.HmassP_INPUTS, H_wf_pump_out, P_wf_evap)
S_wf_pump_out = wf.smass()
T_wf_pump_out = wf.T()
P_wf_pump_out = wf.p()

# PHE outlet
wf.update(cp.PQ_INPUTS, P_wf_evap, 0)
S_wf_PHE_sat = wf.smass()
T_wf_PHE_sat = wf.T()
H_wf_PHE_sat = wf.hmass()
P_wf_PHE_sat = wf.p()

wf.update(cp.PQ_INPUTS, P_wf_evap, 1)
S_wf_PHE_vap = wf.smass()
T_wf_PHE_vap = wf.T()
H_wf_PHE_vap = wf.hmass()
P_wf_PHE_vap = wf.p()

wf.update(cp.PT_INPUTS, P_wf_evap, T_wf_PHE_vap + DT_superheat)
S_wf_PHE_out = wf.smass()
T_wf_PHE_out = wf.T()
H_wf_PHE_out = wf.hmass()
P_wf_PHE_out = wf.p()

# turbine outlet
wf.update(cp.PSmass_INPUTS, P_wf_cond, S_wf_PHE_out)
H_wf_turb_isen = wf.hmass()
S_wf_turb_isen = wf.smass()
T_wf_turb_isen = wf.T()
P_wf_turb_isen = wf.p()

H_wf_turb_out_ = H_wf_PHE_out - eta_turb_isen*(H_wf_PHE_out - H_wf_turb_isen)
wf.update(cp.HmassP_INPUTS, H_wf_turb_out_, P_wf_cond)
S_wf_turb_out_ = wf.smass()
T_wf_turb_out_ = wf.T()
P_wf_turb_out_ = wf.p()

# turbine outlet
wf.update(cp.PQ_INPUTS, P_wf_cond, 1)
S_wf_turb_out = wf.smass()
T_wf_turb_out = wf.T()
H_wf_turb_out = wf.hmass()
P_wf_turb_out = wf.p()

# turbine inlet
wf.update(cp.PSmass_INPUTS, P_wf_evap, S_wf_turb_out)
T_wf_turb_in = wf.T()
DT = T_wf_turb_in - T_wf_PHE_vap

print(H_wf_turb_out-H_wf_turb_out_, H_wf_PHE_out, H_wf_turb_out_,)
print(DT)

# cond outlet
wf.update(cp.PQ_INPUTS, P_wf_cond, 0)
S_wf_cond_out = wf.smass()
T_wf_cond_out = wf.T()
H_wf_cond_out = wf.hmass()
P_wf_cond_out = wf.p()

wf.build_phase_envelope("TS")
wf_tab = wf.get_phase_envelope_data()
Mr = wf.molar_mass()

t_env = wf_tab.T
s_env = [s/Mr/1000 for s in wf_tab.smolar_vap]
p_env = wf_tab.p
h_env = [h/Mr for h in wf_tab.hmolar_vap]

fig, ax = plt.subplots(ncols=2)

# TS Diagram
ss = [S_wf_in/1000, S_wf_pump_out/1000, S_wf_PHE_sat/1000, S_wf_PHE_vap/1000, S_wf_PHE_out/1000, S_wf_turb_out/1000, S_wf_cond_out/1000]
ts = [T_wf_in, T_wf_pump_out, T_wf_PHE_sat, T_wf_PHE_vap, T_wf_PHE_out, T_wf_turb_out, T_wf_cond_out]

ax[0].plot(ss, ts, "o-", color="#1f77b4")
ax[0].plot([S_wf_turb_isen/1000, S_wf_turb_isen/1000], [T_wf_PHE_out, T_wf_turb_isen], "--")
ax[0].plot(s_env, t_env, "k:")
ax[0].set_ylim(300, T_geo_in + 10)
ax[0].set_xlim(0, S_wf_turb_out/1000*1.1)
ax[0].set_xlabel("Entropy/\\unit{\\kilo\\joule\\per\\kg}")
ax[0].set_ylabel("Temperature/\\unit{\\K}")

# TQ diagram
dH_wf_sat = H_wf_PHE_out - H_wf_PHE_sat
water.update(cp.PT_INPUTS, P_geo_in, T_wf_PHE_sat + pinchdT)
H_geo_PHE_sat = water.hmass()
dH_wat_sat = H_geo_in - H_geo_PHE_sat

R = dH_wf_sat / dH_wat_sat
dH_wf_tot = H_wf_PHE_out - H_wf_in
dH_geo_tot = dH_wf_tot / R
water.update(cp.HmassP_INPUTS, H_geo_in - dH_geo_tot, P_geo_in)
T_geo_out = water.T()

qs_in = [0, (H_wf_PHE_sat-H_wf_pump_out)/R/1000, (H_wf_PHE_vap-H_wf_pump_out)/R/1000, (H_wf_PHE_out - H_wf_pump_out)/R/1000]
ts_in = [T_wf_in, T_wf_PHE_sat, T_wf_PHE_vap, T_wf_PHE_out]

qs_out = [0, (H_wf_turb_out-H_wf_cond_out)/R/1000]
ts_out = [T_wf_cond_out, T_wf_turb_out]

ax[1].plot([0, (H_wf_PHE_out-H_wf_pump_out)/R/1000], [T_geo_out, T_geo_in], label="Geofluid", color="#ff7f0e")
ax[1].plot(qs_in, ts_in, label="Working Fluid", color="#1f77b4")
ax[1].plot(qs_out, ts_out, color="#1f77b4")
ax[1].set_ylim(300, T_geo_in + 10)
ax[1].set_xlim(0, 375)
ax[1].get_yaxis().set_visible(False)
ax[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt\\per\\kg\\s}")
ax[1].legend()


ax_twin = ax[1].twinx()
ax_twin.set_ylim(300-273, T_geo_in + 10-273)
# ax_twin.set_xlim(0, (H_wf_PHE_out - H_wf_pump_out)/R/1000)
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

# # PH diagram
# hs = [H_wf_in, H_wf_pump_out, H_wf_PHE_sat, H_wf_PHE_out, H_wf_turb_out, H_wf_cond_sat, H_wf_cond_out]
# ps = [P_wf_in, P_wf_pump_out, P_wf_PHE_sat, P_wf_PHE_out, P_wf_turb_out, P_wf_cond_sat, P_wf_cond_out]
#
# ax[2].plot(hs, ps, "o-", color="#1f77b4")
# ax[2].plot([H_wf_PHE_out, H_wf_turb_isen], [P_wf_PHE_out, P_wf_turb_isen], "--")
# ax[2].plot(h_env, p_env, "k:")

print(qs_in[-1] - qs_out[-1])

tikzplotlib.save("RankineSuperHeatPerf.tex")

plt.show()