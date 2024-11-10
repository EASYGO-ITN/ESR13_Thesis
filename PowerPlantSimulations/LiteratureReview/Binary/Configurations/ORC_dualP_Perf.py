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
wf = cp.AbstractState("?", "butane")

T_geo_in = 160 + 273.15
Q_geo_in = 0
water.update(cp.QT_INPUTS, Q_geo_in, T_geo_in)
P_geo_in = water.p()
H_geo_in = water.hmass()

T_wf_cond = 315
T_wf_evap_lp = 110+273.15
T_wf_evap_hp = 130+273.15

pinchdT = 5
eta_pump_isen = 0.75
eta_turb_isen = 0.80
ratio = 0.71  # how much goes to the HP system

# pump inlet
wf.update(cp.QT_INPUTS, 0, T_wf_cond)
H_wf_in = wf.hmass()
S_wf_in = wf.smass()
T_wf_in = wf.T()
P_wf_in = wf.p()

P_wf_cond = wf.p()

# pump outlet
wf.update(cp.QT_INPUTS, 0, T_wf_evap_lp)
P_wf_evap_lp = wf.p()

wf.update(cp.PSmass_INPUTS, P_wf_evap_lp, S_wf_in)
H_wf_pump_isen = wf.hmass()
H_wf_pump_out = H_wf_in + (H_wf_pump_isen - H_wf_in)/eta_pump_isen

wf.update(cp.HmassP_INPUTS, H_wf_pump_out, P_wf_evap_lp)
S_wf_pump_out = wf.smass()
T_wf_pump_out = wf.T()
P_wf_pump_out = wf.p()

# PreH Sat outlet
wf.update(cp.PQ_INPUTS, P_wf_evap_lp, 0)
S_wf_PreH_out = wf.smass()
T_wf_PreH_out = wf.T()
H_wf_PreH_out = wf.hmass()
P_wf_PreH_out = wf.p()

# Evap lp outlet
wf.update(cp.PQ_INPUTS, P_wf_evap_lp, 1)
S_wf_LPevap_out = wf.smass()
T_wf_LPevap_out = wf.T()
H_wf_LPevap_out = wf.hmass()
P_wf_LPevap_out = wf.p()

# HP pump outlet
wf.update(cp.QT_INPUTS, 0, T_wf_evap_hp)
P_wf_evap_hp = wf.p()

wf.update(cp.PSmass_INPUTS, P_wf_evap_hp, S_wf_PreH_out)
H_wf_HPpump_isen = wf.hmass()
H_wf_HPpump_out = H_wf_PreH_out + (H_wf_HPpump_isen - H_wf_PreH_out)/eta_pump_isen

wf.update(cp.HmassP_INPUTS, H_wf_HPpump_out, P_wf_evap_hp)
S_wf_HPpump_out = wf.smass()
T_wf_HPpump_out = wf.T()
P_wf_HPpump_out = wf.p()

# PreH HP outlet
wf.update(cp.PQ_INPUTS, P_wf_evap_hp, 0)
S_wf_HPPreH_out = wf.smass()
T_wf_HPPreH_out = wf.T()
H_wf_HPPreH_out = wf.hmass()
P_wf_HPPreH_out = wf.p()

wf.update(cp.PQ_INPUTS, P_wf_evap_hp, 1)
S_wf_HPevap_out = wf.smass()
T_wf_HPevap_out = wf.T()
H_wf_HPevap_out = wf.hmass()
P_wf_HPevap_out = wf.p()

# HP turbine outlet
wf.update(cp.PSmass_INPUTS, P_wf_evap_lp, S_wf_HPevap_out)
H_wf_HPturb_isen = wf.hmass()
S_wf_HPturb_isen = wf.smass()
T_wf_HPturb_isen = wf.T()
P_wf_HPturb_isen = wf.p()

H_wf_HPturb_out = H_wf_HPevap_out - eta_turb_isen*(H_wf_HPevap_out - H_wf_HPturb_isen)
wf.update(cp.HmassP_INPUTS, H_wf_HPturb_out, P_wf_evap_lp)
S_wf_HPturb_out = wf.smass()
T_wf_HPturb_out = wf.T()
P_wf_HPturb_out = wf.p()

# LP Turbine Inlet
S_wf_LPturb_in = ratio*(S_wf_HPturb_out) + (1-ratio)*(S_wf_LPevap_out)
wf.update(cp.PSmass_INPUTS, P_wf_evap_lp, S_wf_LPturb_in)
H_wf_LPturb_in = wf.hmass()
T_wf_LPturb_in = wf.T()

# LP turbine outlet
wf.update(cp.PSmass_INPUTS, P_wf_cond, S_wf_LPturb_in)
H_wf_LPturb_isen = wf.hmass()
S_wf_LPturb_isen = wf.smass()
T_wf_LPturb_isen = wf.T()
P_wf_LPturb_isen = wf.p()

H_wf_LPturb_out = H_wf_LPturb_in - eta_turb_isen*(H_wf_LPturb_in - H_wf_LPturb_isen)
wf.update(cp.HmassP_INPUTS, H_wf_LPturb_out, P_wf_cond)
S_wf_LPturb_out = wf.smass()
T_wf_LPturb_out = wf.T()
P_wf_LPturb_out = wf.p()

# cond outlet
wf.update(cp.PQ_INPUTS, P_wf_cond, 1)
S_wf_cond_sat = wf.smass()
T_wf_cond_sat = wf.T()
H_wf_cond_sat = wf.hmass()
P_wf_cond_sat = wf.p()

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
# ss = [S_wf_in/1000, S_wf_pump_out/1000, S_wf_PHE_sat/1000, S_wf_PHE_out/1000, S_wf_turb_out/1000, S_wf_cond_sat/1000, S_wf_cond_out/1000]
# ts = [T_wf_in, T_wf_pump_out, T_wf_PHE_sat, T_wf_PHE_out, T_wf_turb_out, T_wf_cond_sat, T_wf_cond_out]

ss = [S_wf_in,
      S_wf_pump_out,
      S_wf_PreH_out,
      S_wf_LPevap_out,
      S_wf_LPturb_in,
      S_wf_LPturb_out,
      S_wf_cond_sat,
      S_wf_cond_out,
      np.NAN,
      S_wf_HPpump_out,
      S_wf_HPPreH_out,
      S_wf_HPevap_out,
      S_wf_HPturb_out]
ss = [s/1000 for s in ss]
ts = [T_wf_in,
      T_wf_pump_out,
      T_wf_PreH_out,
      T_wf_LPevap_out,
      T_wf_LPturb_in,
      T_wf_LPturb_out,
      T_wf_cond_sat,
      T_wf_cond_out,
      np.NAN,
      T_wf_HPpump_out,
      T_wf_HPPreH_out,
      T_wf_HPevap_out,
      T_wf_HPturb_out
      ]
ss_isen = [S_wf_LPturb_isen, S_wf_LPturb_isen, np.NAN, S_wf_HPturb_isen, S_wf_HPturb_isen]
ss_isen = [s/1000 for s in ss_isen]
ts_isen = [T_wf_LPturb_in, T_wf_LPturb_isen, np.NAN, T_wf_evap_hp, T_wf_HPturb_isen]

ax[0].plot(ss, ts, "o-", color="#1f77b4")
ax[0].plot(ss_isen, ts_isen, "--")
ax[0].plot(s_env, t_env, "k:")
ax[0].set_ylim(300, T_geo_in + 10)
ax[0].set_xlim(0, 1.6)
ax[0].set_xlabel("Entropy/\\unit{\\kilo\\joule\\per\\kg}")
ax[0].set_ylabel("Temperature/\\unit{\\K}")

# # TQ diagram
R = 1
offset = H_wf_pump_out
qs_in = [H_wf_pump_out-offset,
         H_wf_PreH_out-offset,
         H_wf_PreH_out + (1-ratio)*(H_wf_LPevap_out-H_wf_PreH_out) - offset,
         np.NAN,
         H_wf_PreH_out + (1-ratio)*(H_wf_LPevap_out-H_wf_PreH_out) - offset,
         H_wf_PreH_out + (1-ratio)*(H_wf_LPevap_out-H_wf_PreH_out) + (ratio)*(H_wf_HPPreH_out-H_wf_HPpump_out) - offset,
         H_wf_PreH_out + (1-ratio)*(H_wf_LPevap_out-H_wf_PreH_out) + (ratio)*(H_wf_HPevap_out-H_wf_HPpump_out) - offset,]

ts_in = [T_wf_pump_out,
         T_wf_PreH_out,
         T_wf_LPevap_out,
         np.NAN,
         T_wf_HPpump_out,
         T_wf_HPPreH_out,
         T_wf_HPevap_out]

dH_wf_sat = qs_in[-1] - (H_wf_PreH_out-offset)
water.update(cp.PT_INPUTS, P_geo_in, T_wf_PreH_out + pinchdT)
H_geo_PHE_sat = water.hmass()
dH_wat_sat = H_geo_in - H_geo_PHE_sat
#
R = dH_wf_sat / dH_wat_sat
dH_wf_tot = qs_in[-1]
dH_geo_tot = dH_wf_tot / R
water.update(cp.HmassP_INPUTS, H_geo_in - dH_geo_tot, P_geo_in)
T_geo_out = water.T()

dH_wf_hpevap = qs_in[-1] - qs_in[-2]
dH_geo_hpevap = dH_wf_hpevap / R
water.update(cp.HmassP_INPUTS, H_geo_in - dH_geo_hpevap, P_geo_in)
T_geo_HPevap_out = water.T()

if T_geo_HPevap_out - T_wf_HPPreH_out < 5:
    raise ValueError
#
# qs_in = [0, (H_wf_PHE_sat-H_wf_pump_out)/R/1000, (H_wf_PHE_out - H_wf_pump_out)/R/1000]
# ts_in = [T_wf_in, T_wf_PHE_sat, T_wf_PHE_out]
#
qs_out = [0, (H_wf_cond_sat-H_wf_pump_out)/R/1000, (H_wf_LPturb_out-H_wf_pump_out)/R/1000]
ts_out = [T_wf_in, T_wf_cond_sat, T_wf_LPturb_out]

qs_in =[q/R/1000 for q in qs_in]
ax[1].plot([0, qs_in[-1]], [T_geo_out, T_geo_in], label="Geofluid", color="#ff7f0e")
ax[1].plot(qs_in, ts_in, label="Working Fluid", color="#1f77b4")
ax[1].plot(qs_out, ts_out, color="#1f77b4")
ax[1].set_ylim(300, T_geo_in + 10)
ax[1].set_xlim(0, 350)
ax[1].get_yaxis().set_visible(False)
ax[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt\\per\\kg\\s}")
ax[1].legend()

ax_twin = ax[1].twinx()
ax_twin.set_ylim(300-273, T_geo_in + 10-273)
ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

# # # PH diagram
# # hs = [H_wf_in, H_wf_pump_out, H_wf_PHE_sat, H_wf_PHE_out, H_wf_turb_out, H_wf_cond_sat, H_wf_cond_out]
# # ps = [P_wf_in, P_wf_pump_out, P_wf_PHE_sat, P_wf_PHE_out, P_wf_turb_out, P_wf_cond_sat, P_wf_cond_out]
# #
# # ax[2].plot(hs, ps, "o-", color="#1f77b4")
# # ax[2].plot([H_wf_PHE_out, H_wf_turb_isen], [P_wf_PHE_out, P_wf_turb_isen], "--")
# # ax[2].plot(h_env, p_env, "k:")
#
tikzplotlib.save("ORC_dualP_Perf.tex")

plt.show()