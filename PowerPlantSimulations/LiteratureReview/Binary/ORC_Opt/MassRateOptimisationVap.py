import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib
import math

colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

Tref = 298
Pref = 101325
rho0_wat = PropsSI("Dmolar", "T", Tref, "P", Pref, "water")
cp.CoolProp.set_reference_state("water", Tref, rho0_wat, 0, 0)

rho0_but = PropsSI("Dmolar", "T", Tref, "Q", 0, "butane")
cp.CoolProp.set_reference_state("butane", Tref, rho0_but, 0, 0)

water = cp.AbstractState("?", "water")
wf = cp.AbstractState("?", "butane")

T_geo_in0 = 160 + 273.15
Q_geo_in0 = 0
water.update(cp.QT_INPUTS, Q_geo_in0, T_geo_in0)
P_geo_in = water.p()
H_geo_in0 = water.hmass()

T_wf_cond = 315

pinchdT = 5
eta_pump_isen = 0.75
eta_turb_isen = 0.80

whps = np.logspace(math.log10(P_geo_in * 0.1), math.log10(P_geo_in), 50)
P_geo_SH = P_geo_in +1
mrate = [math.sqrt(1- (p/(P_geo_SH))**2) for p in whps]

fig, ax = plt.subplots(ncols=2)


def calc_ORC(T_wf_evap, plot=False):
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

    H_wf_turb_out = H_wf_PHE_out - eta_turb_isen*(H_wf_PHE_out - H_wf_turb_isen)
    wf.update(cp.HmassP_INPUTS, H_wf_turb_out, P_wf_cond)
    S_wf_turb_out = wf.smass()
    T_wf_turb_out = wf.T()
    P_wf_turb_out = wf.p()

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

    dH_wf_sat = H_wf_PHE_out - H_wf_PHE_sat
    water.update(cp.PT_INPUTS, P_geo_in, T_wf_PHE_sat + pinchdT)
    H_geo_PHE_sat = water.hmass()
    dH_wat_sat = H_geo_in - H_geo_PHE_sat

    if plot:
        wf.build_phase_envelope("TS")
        wf_tab = wf.get_phase_envelope_data()
        Mr = wf.molar_mass()

        t_env = wf_tab.T
        s_env = [s / Mr / 1000 for s in wf_tab.smolar_vap]
        p_env = wf_tab.p
        h_env = [h / Mr for h in wf_tab.hmolar_vap]

        # TS Diagram
        ss = [S_wf_in/1000, S_wf_pump_out/1000, S_wf_PHE_sat/1000, S_wf_PHE_out/1000, S_wf_turb_out/1000, S_wf_cond_sat/1000, S_wf_cond_out/1000]
        ts = [T_wf_in, T_wf_pump_out, T_wf_PHE_sat, T_wf_PHE_out, T_wf_turb_out, T_wf_cond_sat, T_wf_cond_out]

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

        qs_in = [0, (H_wf_PHE_sat-H_wf_pump_out)/R/1000, (H_wf_PHE_out - H_wf_pump_out)/R/1000]
        ts_in = [T_wf_pump_out, T_wf_PHE_sat, T_wf_PHE_out]

        qs_out = [0, (H_wf_cond_sat-H_wf_cond_out)/R/1000, (H_wf_turb_out-H_wf_cond_out)/R/1000]
        ts_out = [T_wf_cond_out, T_wf_cond_sat, T_wf_turb_out]


        dH_geo_sat = (H_geo_in0- PropsSI("H", "T", T_geo_in, "Q", 0, "water"))/1000
        qs_geo = [0, (H_wf_PHE_out-H_wf_pump_out)/R/1000 - dH_geo_sat, (H_wf_PHE_out-H_wf_pump_out)/R/1000]
        ts_geo = [T_geo_out, T_geo_in, T_geo_in]

        ax[1].plot(qs_geo, ts_geo, label="Geofluid", color="#ff7f0e")
        ax[1].plot(qs_in, ts_in, label="Working Fluid", color="#1f77b4")
        ax[1].plot(qs_out, ts_out, color="#1f77b4")
        ax[1].set_ylim(300, T_geo_in + 10)
        ax[1].set_xlim(0, 400)
        ax[1].get_yaxis().set_visible(False)
        ax[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt\\per\\kg\\s}")
        ax[1].legend()

        ax_twin = ax[1].twinx()
        ax_twin.set_ylim(300-273, T_geo_in + 10-273)
        # ax_twin.set_xlim(0, (H_wf_PHE_out - H_wf_pump_out)/R/1000)
        ax_twin.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

    R = dH_wf_sat / dH_wat_sat

    work = (H_wf_turb_out - H_wf_PHE_out) - (H_wf_pump_out - H_wf_in)

    return work, R


Rs = []
Hs = []
Power = []
Ts_geo = []
Ts_wf_evap = []
for i, whp in enumerate(whps):

    water.update(cp.HmassP_INPUTS, H_geo_in0, whp)
    T_geo_in = water.T()
    H_geo_in = water.hmass()
    Ts_geo.append(T_geo_in)

    T_wf_evaps = np.linspace(T_wf_cond + 5, T_geo_in - 10, 200)

    Rs_ = []
    Hs_ = []
    Power_ = []

    for j, T_evap in enumerate(T_wf_evaps):
        W, r = calc_ORC(T_evap)

        Hs_.append(-W / 1000)
        Rs_.append(1 / r)
        Power_.append(-W / 1000 / r)

    maxPower_ = max(Power_)
    ipwr_ = Power_.index(maxPower_)

    W, r = calc_ORC(T_wf_evaps[ipwr_])

    m = mrate[i]
    Hs.append(-W/r/1000)
    Rs.append(1/r)
    Power.append(-W/1000/r*m)
    Ts_wf_evap.append(T_wf_evaps[ipwr_])

maxPower = max(Power)
ipwr = Power.index(maxPower)
T_geo_in =Ts_geo[ipwr]


figb, axb = plt.subplots(ncols=2)

W, r = calc_ORC(Ts_wf_evap[ipwr], plot=True)

whps_bar = [whp*1e-5 for whp in whps]

axb[0].plot(whps_bar, mrate, label="mrate", color="#1f77b4")
axb[0].plot([1], [-1], label="Geofluid", color="#ff7f0e")
axb[0].plot([1], [-1], label="n-Butane", color="#2ca02c")

axb[0].set_xlabel("Wellhead Pressure/\\unit{\\bar}")
axb[0].set_ylabel("Mass Rate Ratio")
axb[0].set_ylim(0, 1)
axb[0].set_xlim(0, 6.5)

ax_twin2 = axb[0].twinx()
ax_twin2.plot(whps_bar, Ts_geo, color="#ff7f0e")
ax_twin2.plot(whps_bar, Ts_wf_evap, color="#2ca02c")

ax_twin2.set_ylabel("Fluid Temperature/\\unit{\\K}")
ax_twin2.set_ylim(300, 450)

axb[1].plot(whps_bar, Power, label="net power", color="#1f77b4")
axb[1].plot([whps_bar[ipwr]], [Power[ipwr]], "ko")
axb[1].plot([whps_bar[ipwr], whps_bar[ipwr]], [0, Power[ipwr]], "k--")
axb[1].plot(whps_bar, Hs, label="cycle power", color="#ff7f0e")

axb[1].set_xlabel("Wellhead Pressure/\\unit{\\bar}")
axb[1].set_ylabel("Power/\\unit{\\kilo\\watt\\per\\kg}")
axb[1].set_ylim(0, 50)
axb[1].set_xlim(0, 6.5)

ax[0].legend()
ax[1].legend()
axb[0].legend()
axb[1].legend()


tikzplotlib.save("Vap_Mrate_Opt.tex", figure=figb)
tikzplotlib.save("Vap_Mrate_Opt_TS.tex", figure=fig)


plt.show()