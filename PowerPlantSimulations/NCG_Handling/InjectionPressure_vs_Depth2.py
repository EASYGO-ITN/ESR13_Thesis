import math

import CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt

g = 9.81
rho_brine = 1000

TCO2 = 298
CO2 = cp.AbstractState("?", "CO2")

def P_brine(z, p0=101325):
    return rho_brine * g * z + p0


# approximating the static pressure gradients
if __name__ == "__main__":
    Nz = 50
    zs = np.linspace(0, 4000, Nz)
    pbrines = np.array([P_brine(z) for z in zs])

    fig, ax = plt.subplots()
    ax.plot(pbrines*1e-5, zs, label="Brine")
    zs_mix_gradient = [100, 200, 500, 1000, 2000, 4000]

    for z_mix in zs_mix_gradient:

        P_at_depth = P_brine(z_mix)

        zs_CO2 = np.linspace(z_mix, 0, Nz)
        ps_CO2 = np.empty(Nz)

        PCO2 = P_at_depth
        for i, z in enumerate(zs_CO2):
            dZ = zs_CO2[i - 1] - z
            if i != 0:
                rho_CO2_in = rho_CO2_out

                P_test = PCO2 - rho_CO2_in * g * dZ

                for j in range(5):
                    CO2.update(cp.PT_INPUTS, P_test, TCO2)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 - (rho_CO2_in +rho_CO2_out)/2* g * dZ

                CO2.update(cp.PT_INPUTS, P_test, TCO2)
                rho_CO2_out = CO2.rhomass()

                PCO2 -= (rho_CO2_in +rho_CO2_out)/2* g * dZ
                ps_CO2[i] = PCO2 * 1.0
            else:
                ps_CO2[i] = PCO2 * 1.0

                CO2.update(cp.PT_INPUTS, PCO2, TCO2)
                rho_CO2_out = CO2.rhomass()

        ax.plot(ps_CO2 * 1e-5, zs_CO2, label="z={}".format(z_mix))

    ax.set_xlabel("Pressure/bar")
    ax.set_ylabel("Depth/m")
    ax.invert_yaxis()
    ax.legend()


# approximating the required injection welhead pressure
if __name__ == "__main__":
    CO2.update(cp.QT_INPUTS, 0, TCO2)
    Psat_CO2 = CO2.p()


    zs_mix = list(np.linspace(100,4000))
    ps_inj = []

    for z_mix in zs_mix:

        P_at_depth = P_brine(z_mix)

        Nz = max(50, math.ceil((z_mix - 0)/2.5))

        zs_CO2 = np.linspace(z_mix, 0, Nz)
        ps_CO2 = np.empty(Nz)

        PCO2 = P_at_depth

        for i, z in enumerate(zs_CO2):
            dZ = zs_CO2[i - 1] - z
            if i != 0:
                rho_CO2_in = rho_CO2_out

                P_test = PCO2 - rho_CO2_in * g * dZ

                for j in range(5):
                    CO2.update(cp.PT_INPUTS, P_test, TCO2)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 - (rho_CO2_in +rho_CO2_out)/2* g * dZ

                CO2.update(cp.PT_INPUTS, P_test, TCO2)
                rho_CO2_out = CO2.rhomass()

                PCO2 -= (rho_CO2_in +rho_CO2_out)/2* g * dZ
                ps_CO2[i] = PCO2 * 1.0
            else:
                ps_CO2[i] = PCO2 * 1.0

                CO2.update(cp.PT_INPUTS, PCO2, TCO2)
                rho_CO2_out = CO2.rhomass()

        ps_inj.append(PCO2)

    ps_inj = np.array(ps_inj)*1e-5

    fig2, ax2 = plt.subplots()
    ax2.plot(zs_mix, ps_inj)

    ax2.set_xlabel("Reservoir Depth/m")
    ax2.set_ylabel("Minimum Wellhead Pressure/bar")


plt.show()


