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

rho0_pen = PropsSI("Dmolar", "T", Tref, "Q", 0, "Pentane")
cp.CoolProp.set_reference_state("Pentane", Tref, rho0_but, 0, 0)

water = cp.AbstractState("?", "water")
wfa = cp.AbstractState("?", "butane")
wfb = cp.AbstractState("?", "Pentane")

T_geo_in = 160 + 273.15
Q_geo_in = 0
water.update(cp.QT_INPUTS, Q_geo_in, T_geo_in)
P_geo_in = water.p()
H_geo_in = water.hmass()

T_wfa_cond = 315
T_wfa_evap = 110+273.15

T_wfb_cond = T_wfa_evap
T_wfb_evap = 140+273.15

pinchdT = 5
eta_pump_isen = 0.75
eta_turb_isen = 0.80
ratio = 0.6


## Fluid A

# pump inlet
wfa.update(cp.QT_INPUTS, 0, T_wfa_cond)
H_wfa_in = wfa.hmass()
S_wfa_in = wfa.smass()
T_wfa_in = wfa.T()
P_wfa_in = wfa.p()

P_wfa_cond = wfa.p()

# pump outlet
wfa.update(cp.QT_INPUTS, 0, T_wfa_evap)
P_wfa_evap = wfa.p()

wfa.update(cp.PSmass_INPUTS, P_wfa_evap, S_wfa_in)
H_wfa_pump_isen = wfa.hmass()
H_wfa_pump_out = H_wfa_in + (H_wfa_pump_isen - H_wfa_in)/eta_pump_isen

wfa.update(cp.HmassP_INPUTS, H_wfa_pump_out, P_wfa_evap)
S_wfa_pump_out = wfa.smass()
T_wfa_pump_out = wfa.T()
P_wfa_pump_out = wfa.p()

# PHE outlet
wfa.update(cp.PQ_INPUTS, P_wfa_evap, 0)
S_wfa_PHE_sat = wfa.smass()
T_wfa_PHE_sat = wfa.T()
H_wfa_PHE_sat = wfa.hmass()
P_wfa_PHE_sat = wfa.p()

wfa.update(cp.PQ_INPUTS, P_wfa_evap, 1)
S_wfa_PHE_out = wfa.smass()
T_wfa_PHE_out = wfa.T()
H_wfa_PHE_out = wfa.hmass()
P_wfa_PHE_out = wfa.p()

# turbine outlet
wfa.update(cp.PSmass_INPUTS, P_wfa_cond, S_wfa_PHE_out)
H_wfa_turb_isen = wfa.hmass()
S_wfa_turb_isen = wfa.smass()
T_wfa_turb_isen = wfa.T()
P_wfa_turb_isen = wfa.p()

H_wfa_turb_out = H_wfa_PHE_out - eta_turb_isen*(H_wfa_PHE_out - H_wfa_turb_isen)
wfa.update(cp.HmassP_INPUTS, H_wfa_turb_out, P_wfa_cond)
S_wfa_turb_out = wfa.smass()
T_wfa_turb_out = wfa.T()
P_wfa_turb_out = wfa.p()

# cond outlet
wfa.update(cp.PQ_INPUTS, P_wfa_cond, 1)
S_wfa_cond_sat = wfa.smass()
T_wfa_cond_sat = wfa.T()
H_wfa_cond_sat = wfa.hmass()
P_wfa_cond_sat = wfa.p()

wfa.update(cp.PQ_INPUTS, P_wfa_cond, 0)
S_wfa_cond_out = wfa.smass()
T_wfa_cond_out = wfa.T()
H_wfa_cond_out = wfa.hmass()
P_wfa_cond_out = wfa.p()

### Fluid B
# pump inlet
wfb.update(cp.QT_INPUTS, 0, T_wfb_cond)
H_wfb_in = wfb.hmass()
S_wfb_in = wfb.smass()
T_wfb_in = wfb.T()
P_wfb_in = wfb.p()

P_wfb_cond = wfb.p()

# pump outlet
wfb.update(cp.QT_INPUTS, 0, T_wfb_evap)
P_wfb_evap = wfb.p()

wfb.update(cp.PSmass_INPUTS, P_wfb_evap, S_wfb_in)
H_wfb_pump_isen = wfb.hmass()
H_wfb_pump_out = H_wfb_in + (H_wfb_pump_isen - H_wfb_in)/eta_pump_isen

wfb.update(cp.HmassP_INPUTS, H_wfb_pump_out, P_wfb_evap)
S_wfb_pump_out = wfb.smass()
T_wfb_pump_out = wfb.T()
P_wfb_pump_out = wfb.p()

# PHE outlet
wfb.update(cp.PQ_INPUTS, P_wfb_evap, 0)
S_wfb_PHE_sat = wfb.smass()
T_wfb_PHE_sat = wfb.T()
H_wfb_PHE_sat = wfb.hmass()
P_wfb_PHE_sat = wfb.p()

wfb.update(cp.PQ_INPUTS, P_wfb_evap, 1)
S_wfb_PHE_out = wfb.smass()
T_wfb_PHE_out = wfb.T()
H_wfb_PHE_out = wfb.hmass()
P_wfb_PHE_out = wfb.p()

# turbine outlet
wfb.update(cp.PSmass_INPUTS, P_wfb_cond, S_wfb_PHE_out)
H_wfb_turb_isen = wfb.hmass()
S_wfb_turb_isen = wfb.smass()
T_wfb_turb_isen = wfb.T()
P_wfb_turb_isen = wfb.p()

H_wfb_turb_out = H_wfb_PHE_out - eta_turb_isen*(H_wfb_PHE_out - H_wfb_turb_isen)
wfb.update(cp.HmassP_INPUTS, H_wfb_turb_out, P_wfb_cond)
S_wfb_turb_out = wfb.smass()
T_wfb_turb_out = wfb.T()
P_wfb_turb_out = wfb.p()

# cond outlet
wfb.update(cp.PQ_INPUTS, P_wfb_cond, 1)
S_wfb_cond_sat = wfb.smass()
T_wfb_cond_sat = wfb.T()
H_wfb_cond_sat = wfb.hmass()
P_wfb_cond_sat = wfb.p()

wfb.update(cp.PQ_INPUTS, P_wfb_cond, 0)
S_wfb_cond_out = wfb.smass()
T_wfb_cond_out = wfb.T()
H_wfb_cond_out = wfb.hmass()
P_wfb_cond_out = wfb.p()


# butane phase envelope
wfa.build_phase_envelope("TS")
wfa_tab = wfa.get_phase_envelope_data()
Mr = wfa.molar_mass()

wfa_t_env = wfa_tab.T
wfa_s_env = [s/Mr/1000 for s in wfa_tab.smolar_vap]
wfa_p_env = wfa_tab.p
wfa_h_env = [h/Mr for h in wfa_tab.hmolar_vap]

# pentane phase envelope
wfb.build_phase_envelope("TS")
wfb_tab = wfb.get_phase_envelope_data()
Mr = wfb.molar_mass()

wfb_t_env = wfb_tab.T
wfb_s_env = [s/Mr/1000 for s in wfb_tab.smolar_vap]
wfb_p_env = wfb_tab.p
wfb_h_env = [h/Mr for h in wfb_tab.hmolar_vap]


fig, ax = plt.subplots(ncols=2)

# TS Diagram
ssa = [S_wfa_in,
       S_wfa_pump_out,
       S_wfa_PHE_sat,
       S_wfa_PHE_out,
       S_wfa_turb_out,
       S_wfa_cond_sat,
       S_wfa_cond_out]
ssa = [s/1000 for s in ssa]
tsa = [T_wfa_in,
       T_wfa_pump_out,
       T_wfa_PHE_sat,
       T_wfa_PHE_out,
       T_wfa_turb_out,
       T_wfa_cond_sat,
       T_wfa_cond_out]

ssb = [S_wfb_in,
       S_wfb_pump_out,
       S_wfb_PHE_sat,
       S_wfb_PHE_out,
       S_wfb_turb_out,
       S_wfb_cond_sat,
       S_wfb_cond_out]
ssb = [s/1000 for s in ssb]
tsb = [T_wfb_in,
       T_wfb_pump_out,
       T_wfb_PHE_sat,
       T_wfb_PHE_out,
       T_wfb_turb_out,
       T_wfb_cond_sat,
       T_wfb_cond_out]

ax[0].plot(ssa, tsa, "o-", color="#1f77b4", label="Fluid A")
ax[0].plot(ssb, tsb, "o-", color="#ff7f0e", label="Fluid B")

ax[0].plot([S_wfa_turb_isen/1000, S_wfa_turb_isen/1000], [T_wfa_PHE_out, T_wfa_turb_isen], "--", color="#1f77b4")
ax[0].plot([S_wfb_turb_isen/1000, S_wfb_turb_isen/1000], [T_wfb_PHE_out, T_wfb_turb_isen], "--", color="#ff7f0e")

ax[0].plot(wfa_s_env, wfa_t_env, "k:")
ax[0].plot(wfb_s_env, wfb_t_env, "k-.")

ax[0].set_ylim(300, T_geo_in + 10)
ax[0].set_xlim(0, 2)
ax[0].set_xlabel("Entropy/\\unit{\\kilo\\joule\\per\\kg}")
ax[0].set_ylabel("Temperature/\\unit{\\K}")
ax[0].legend()

# TQ diagram
dH_wfa_sat = ratio*(H_wfa_PHE_out - H_wfa_PHE_sat) + (1-ratio)*(H_wfb_PHE_out-H_wfb_pump_out)
water.update(cp.PT_INPUTS, P_geo_in, T_wfa_PHE_sat + pinchdT)
H_geo_PHE_sat = water.hmass()
dH_wat_sat = H_geo_in - H_geo_PHE_sat

R = dH_wfa_sat / dH_wat_sat
dH_wf_tot = ratio*(H_wfa_PHE_out - H_wfa_pump_out) + (1-ratio)*(H_wfb_PHE_out-H_wfb_pump_out)
dH_geo_tot = dH_wf_tot / R
water.update(cp.HmassP_INPUTS, H_geo_in - dH_geo_tot, P_geo_in)
T_geo_out = water.T()

qsa_in = [0,
          (H_wfa_PHE_sat-H_wfa_pump_out)*ratio,
          (H_wfa_PHE_out - H_wfa_pump_out)*ratio]
qsa_in = [q/1000/R for q in qsa_in]
tsa_in = [T_wfa_in,
          T_wfa_PHE_sat,
          T_wfa_PHE_out]

qsb_in = [0,
          (H_wfb_PHE_sat-H_wfb_pump_out)*(1-ratio),
          (H_wfb_PHE_out - H_wfb_pump_out)*(1-ratio)]
tsb_in = [T_wfb_in,
          T_wfb_PHE_sat,
          T_wfb_PHE_out]
qsb_in = [q/1000/R + qsa_in[-1] for q in qsb_in]

qs_out = [0, (H_wfa_cond_sat-H_wfa_pump_out)/R/1000, (H_wfa_turb_out-H_wfa_pump_out)/R/1000]
ts_out = [T_wfa_in, T_wfa_cond_sat, T_wfa_turb_out]

ax[1].plot([0, qsb_in[-1]], [T_geo_out, T_geo_in], label="Geofluid", color="red")

ax[1].plot(qsa_in, tsa_in, label="Fluid A", color="#1f77b4")
ax[1].plot(qsb_in, tsb_in, label="Fluid B", color="#ff7f0e")

# ax[1].plot(qs_out, ts_out, color="#1f77b4")
ax[1].set_ylim(300, T_geo_in + 10)
ax[1].set_xlim(0, 300)
ax[1].get_yaxis().set_visible(False)
ax[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt\\per\\kg\\s}")
ax[1].legend()


ax_twin = ax[1].twinx()
ax_twin.set_ylim(300-273, T_geo_in + 10-273)
ax_twin.set_xlim(0, 300)
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

# # PH diagram
# hs = [H_wfa_in, H_wfa_pump_out, H_wfa_PHE_sat, H_wfa_PHE_out, H_wfa_turb_out, H_wfa_cond_sat, H_wfa_cond_out]
# ps = [P_wfa_in, P_wfa_pump_out, P_wfa_PHE_sat, P_wfa_PHE_out, P_wfa_turb_out, P_wfa_cond_sat, P_wfa_cond_out]
#
# ax[2].plot(hs, ps, "o-", color="#1f77b4")
# ax[2].plot([H_wfa_PHE_out, H_wfa_turb_isen], [P_wfa_PHE_out, P_wfa_turb_isen], "--")
# ax[2].plot(h_env, p_env, "k:")

tikzplotlib.save("ORC_dualFluidPerf.tex")

plt.show()