from SP2009 import SpycherPruss2009
import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import tikzplotlib
import numpy as np
import scipy

fig, ax = plt.subplots()

Pmin = SpycherPruss2009.Pmin*1e-5
Pmax = SpycherPruss2009.Pmax*1e-5
Tmin = SpycherPruss2009.Tmin_low
Tmax = SpycherPruss2009.Tmax_high

# Water saturation curve
water = cp.AbstractState("HEOS", "water")
water.build_phase_envelope("PT")
tab_water = water.get_phase_envelope_data()

Tsat_wat_cp =np.array(tab_water.T)
Psat_wat_cp = np.array(tab_water.p)*1e-5

iTmax = np.argmax(Tsat_wat_cp)
Tsat_wat_cp = Tsat_wat_cp[:iTmax]
Psat_wat_cp = Psat_wat_cp[:iTmax]

# CO2 saturation curve
co2 = cp.AbstractState("HEOS", "CO2")
co2.build_phase_envelope("PT")
tab_co2 = co2.get_phase_envelope_data()

Tsat_co2_cp = np.array(tab_co2.T)
Psat_co2_cp = np.array(tab_co2.p)*1e-5

# cropped water saturation curve
boundary_T = Tsat_wat_cp[Psat_wat_cp>Pmin]
boundary_P = Psat_wat_cp[Psat_wat_cp>Pmin]

boundary_P = boundary_P[boundary_T<Tmax]
boundary_T = boundary_T[boundary_T<Tmax]

boundary_P = [Pmin] + list(boundary_P) + [PropsSI("P", "T", Tmax, "Q", 0, "Water")*1e-5]
boundary_T = [PropsSI("T", "P", Pmin*1e5, "Q", 0, "Water")] + list(boundary_T) + [Tmax]

# SP2009 region
SP2009_T = [Tmin] + boundary_T + [Tmax, Tmin, Tmin]
SP2009_P = [Pmin] + boundary_P + [Pmax, Pmax, Pmin]

SP2009_lower_T = [Tmin] + boundary_T
SP2009_lower_P = [Pmin] + boundary_P
SP2009_upper_P = [Pmax for i in SP2009_lower_T]

# Trivial region
trivial_upper_T = boundary_T
trivial_upper_P = boundary_P
trivial_lower_P = [Pmin for j in trivial_upper_T]

trivial_T = trivial_upper_T + [Tmax, Tmin]
trivial_P = trivial_upper_P + [Pmin, Pmin]

# CoolProp region
upper_boundary_P = [Pmin, Pmin]
lower_boundary_T = [Tmin, Tmax]
lower_boundary_P = [0.001, 0.001]


colors = {"steelblue":"#1f77b4", "orange":"#ff7f0e", "green":"#2ca02c", "red":"#d62728", 60: "#9467bd",31: "#8c564b", 20: "#e377c2"}
ax.plot(Tsat_wat_cp, Psat_wat_cp, label="Pure Water", color=colors["steelblue"])
ax.plot(Tsat_co2_cp, np.array(Psat_co2_cp), label="Pure CO2", color=colors["red"])

ax.fill_between(SP2009_lower_T, SP2009_upper_P, SP2009_lower_P, color=colors["steelblue"], alpha=0.3, label="SP2009")
ax.fill_between(trivial_upper_T, trivial_upper_P, trivial_lower_P, color=colors["orange"], alpha=0.3, label="\"Trivial\"")
ax.fill_between(lower_boundary_T, upper_boundary_P, lower_boundary_P, color=colors["green"], alpha=0.3, label="CoolProp")


def phase_env(zH2O, n_SP=30, colour="r"):
    def liq_serach_p(p):

        yH2O, xCO2, xSalt = SpycherPruss2009().calcSP2009(p, T, 0, 0, 0, 0, 0, 0)

        xH2O = (1 - xCO2 - xSalt)

        obj_func = (zH2O - xH2O) / zH2O

        return obj_func

    def vap_serach_p(p):

        yH2O, xCO2, xSalt = SpycherPruss2009().calcSP2009(p, T, 0, 0, 0, 0, 0, 0)

        yCO2 = (1 - yH2O)

        obj_func = (zCO2 - yCO2) / zCO2

        return obj_func

    Tsat_SP_liq = np.linspace(Tmin, Tmax, n_SP)
    Psat_SP_liq = np.zeros(n_SP)
    liq_flag = False
    Psat_SP_vap = np.zeros(n_SP)
    Tsat_SP_vap = Tsat_SP_liq*1
    vap_flag = False

    zCO2 = 1 - zH2O

    Pmin_ = Pmin * 1e5
    Pmax_ = Pmax * 1e5

    water = cp.AbstractState("?", "Water")
    for i, T in enumerate(Tsat_SP_liq):
        water.update(cp.QT_INPUTS, 0.5, T)
        Psat = water.p()

        if Psat < Pmin_:
            P_lower = Pmin_
        else:
            P_lower = Psat

        try:
            P_vap = scipy.optimize.bisect(vap_serach_p, P_lower, Pmax_)
            Psat_SP_vap[i] = P_vap
            vap_flag = True
        except ValueError:
            Psat_SP_vap[i] = np.NaN

        try:
            P_liq = scipy.optimize.bisect(liq_serach_p, P_lower, Pmax_)
            Psat_SP_liq[i] = P_liq
            liq_flag = True
        except ValueError:
            Psat_SP_liq[i] = np.NaN

    Tsat_SP_vap = list(Tsat_SP_vap)
    Tsat_SP_vap.reverse()
    Psat_SP_vap = list(Psat_SP_vap*1e-5)
    Psat_SP_vap.reverse()

    Tsat = list(Tsat_SP_liq) + [np.NAN] + Tsat_SP_vap
    Psat = list(Psat_SP_liq*1e-5) + [np.NAN] + Psat_SP_vap

    label = "\\(z_{CO_2}=" + str(int((1-zH2O)*100)) + "\\unit{\\percent}\\)"
    ax.plot(Tsat, Psat, color=colour, label=label)

phase_env(0.98, colour="#9467bd")
phase_env(0.97, colour="#8c564b")
phase_env(0.95, colour="#e377c2")
# phase_env(0.93)
# phase_env(0.9)

ax.set_xlabel("Temperature/\\unit{\\K}")
ax.set_ylabel("Pressure/\\unit{\\bar}")
ax.set_yscale("log")
ax.set_xlim((273, 600))
ax.set_ylim((0.005, 1000))
ax.legend()
# plt.show()

tikzplotlib.save("PhaseEnvelope.tex")


