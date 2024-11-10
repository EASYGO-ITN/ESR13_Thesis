import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

Tref = 298
Pref = 101325

fluid = "water"
# rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, fluid)
# cp.CoolProp.set_reference_state(fluid, Tref, rho0, 0, 0)
water = cp.AbstractState("?", fluid)

water.build_phase_envelope("TS")
water_env = water.get_phase_envelope_data()
water_Mr = water.molar_mass()

# wat_ss = [s/water_Mr/1000 for s in water_env.smolar_vap]
wat_ss = water_env.smolar_vap
wat_ts = water_env.T

plt.plot(wat_ss, wat_ts, label="Wet - Water")


fluid = "Pentane"
# rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, fluid)
# cp.CoolProp.set_reference_state(fluid, Tref, rho0, 0, 0)
pentane = cp.AbstractState("?", fluid)

pentane.build_phase_envelope("TS")
pentane_env = pentane.get_phase_envelope_data()
pentane_Mr = pentane.molar_mass()

# pen_ss = [s/pentane_Mr/1000 for s in pentane_env.smolar_vap]
pen_ss = pentane_env.smolar_vap
pen_ts = pentane_env.T

plt.plot(pen_ss, pen_ts, label="Dry - Pentane")


fluid = "R11"
# rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, fluid)
# cp.CoolProp.set_reference_state(fluid, Tref, rho0, 0, 0)
R11 = cp.AbstractState("?", fluid)

R11.build_phase_envelope("TS")
R11_env = R11.get_phase_envelope_data()
R11_Mr = R11.molar_mass()

# R11_ss = [s/R11_Mr/1000 for s in R11_env.smolar_vap]
R11_ss = R11_env.smolar_vap
R11_ts = R11_env.T

plt.plot(R11_ss, R11_ts, label="Isentropic - R11")


# fluid = "n-Heptane"
# # rho0 = PropsSI("Dmolar", "T", Tref, "Q", 0, fluid)
# # cp.CoolProp.set_reference_state(fluid, Tref, rho0, 0, 0)
# cyclo = cp.AbstractState("?", fluid)
#
# cyclo.build_phase_envelope("TS")
# cyclo_env = cyclo.get_phase_envelope_data()
# cyclo_Mr = cyclo.molar_mass()
#
# # R11_ss = [s/R11_Mr/1000 for s in R11_env.smolar_vap]
# cyclo_ss = cyclo_env.smolar_vap
# cyclo_ts = cyclo_env.T
#
# plt.plot(cyclo_ss, cyclo_ts, label="Real Isentropic - Cyclopentane")


plt.xlabel("Entropy/\\unit{\\kilo\\joule\\per\\kg\\per\\K}")
plt.ylabel("Temperature/\\unit{\\K}")
plt.ylim(300, None)
plt.xlim(0, None)
plt.legend()

tikzplotlib.save("WorkingFluidTypes.tex")

plt.show()


