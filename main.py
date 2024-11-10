import numpy as np
import CoolProp as cp
from CoolProp.CoolProp import PropsSI
import math
import matplotlib.pyplot as plt


def to_tex2D(xs, ys):

    xys = [ "("+str(round(xs[i], 3))+","+str(round(ys[i], 3))+")" for i in range(len(xs))]
    coords = " ".join(xys)

    return coords


Pref = 101325
Tref = 298

wat_rho_ref = PropsSI("Dmolar", "P", Pref, "Q", 0, "Water")
wat_T_ref = PropsSI("T", "P", Pref, "Q", 0, "Water")
co2_rho_ref = PropsSI("Dmolar", "T", Tref, "Q", 0, "CO2")
co2_P_ref = PropsSI("P", "T", Tref, "Q", 0, "CO2")

cp.CoolProp.set_reference_state('Water', wat_T_ref, wat_rho_ref, 0, 0)
cp.CoolProp.set_reference_state('CO2', Tref, co2_rho_ref, 0, 0)

water = cp.AbstractState("HEOS", "water")
water.build_phase_envelope("PH")
tab_water = water.get_phase_envelope_data()

co2 = cp.AbstractState("HEOS", "CO2")
co2.build_phase_envelope("PH")
tab_co2 = co2.get_phase_envelope_data()

print("Water")
print("PT SaturationCurve")
print(to_tex2D(tab_water.T, np.array(tab_water.p)/1e5))

print("PH SaturationCurve")
print(to_tex2D(tab_water.hmolar_liq, np.array(tab_water.p)/1e5))

print("CO2")
print("PT SaturationCurve")
print(to_tex2D(tab_co2.T, np.array(tab_co2.p)/1e5))

print("PH SaturationCurve")
print(to_tex2D(tab_co2.hmolar_liq, np.array(tab_co2.p)/1e5))

# plt.rcParams.update({
#     "text.usetex": True,
#     # "font.family": "Helvetica"
# })

plt.plot(tab_water.T, tab_water.p)
# plt.savefig('figure.pdf')
# plt.show()

