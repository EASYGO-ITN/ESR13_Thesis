import CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

g = 9.81
rho_brine = 1000

fig, ax = plt.subplots()

def P_brine(z, p0=101325):
    return rho_brine * g * z + p0

Nz = 50
zs = np.linspace(0, 4000, Nz)
pbrines = np.array([P_brine(z) for z in zs])

ax.plot(pbrines*1e-5, zs, label="Brine")

TCO2 = 298
CO2 = cp.AbstractState("?", "CO2")
zs_mix = list(np.linspace(100,4000))
zs_mix_gradient = [100.0, 200, 500, 1000, 2000, 3000]

zs_mix += zs_mix_gradient
zs_mix.sort()

P_inj = []
for z_mix in zs_mix:

    P_at_depth = P_brine(z_mix)

    zs_CO2 = np.linspace(z_mix, 0, Nz)
    ps_CO2 = np.empty(Nz)

    PCO2 = P_at_depth
    for i, z in enumerate(zs_CO2):

        if i != 0:
            CO2.update(cp.PT_INPUTS, PCO2, TCO2)
            rho_CO2 = CO2.rhomass()
            dZ = zs_CO2[i-1] - z
            dP = rho_CO2 * g * dZ

            PCO2 -= dP

            ps_CO2[i] = PCO2 * 1.0
        else:
            ps_CO2[i] = PCO2 * 1.0

    P_inj.append(ps_CO2[-1])

    if z_mix in zs_mix_gradient:
        ax.plot(ps_CO2 * 1e-5, zs_CO2, label="z={}".format(z_mix))

P_inj = np.array(P_inj)

ax.set_xlabel("Pressure/bar")
ax.set_ylabel("Depth/m")
ax.invert_yaxis()
ax.legend()

fig2, ax2 = plt.subplots()
ax2.plot(zs_mix, P_inj*1e-5)


plt.show()


