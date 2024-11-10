import math

import CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

g = 9.81
rho_brine = 1000

TCO2 = 298 + 10
CO2 = cp.AbstractState("?", "CO2")

def P_brine(z, p0=101325):
    return rho_brine * g * z + p0

## Top to bottom
# approximating the static pressure gradients
if __name__ == "__main_":
    Pwh_brine = 10e5

    Nz = 50
    zs = np.arange(0, 4000, 5)
    pbrines = np.array([P_brine(z, p0=Pwh_brine) for z in zs])

    fig3, ax3 = plt.subplots()
    ax3.plot(pbrines*1e-5, zs, label="Brine")

    ps_wh = np.arange(10, 150, 20)* 1e5
    for p_wh in ps_wh:
        # ps_CO2 = np.empty(Nz)

        PCO2 = p_wh * 1.0
        z_actual = []
        p_actual = []
        for i, z in enumerate(zs):
            dZ = z - zs[i - 1]
            if i != 0:
                rho_CO2_in = rho_CO2_out

                P_test = PCO2 + rho_CO2_in * g * dZ

                for j in range(5):
                    CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 + (rho_CO2_in +rho_CO2_out)/2* g * dZ

                CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                rho_CO2_out = CO2.rhomass()

                PCO2 += (rho_CO2_in +rho_CO2_out)/2* g * dZ
                # ps_CO2[i] = PCO2 * 1.0

                z_actual.append(z)
                p_actual.append(PCO2*1)

                if PCO2 < P_brine(z, p0=Pwh_brine):
                    # print(CO2.phase(), cp.iphase_supercritical_gas, cp.iphase_gas, cp.iphase_supercritical)
                    break

            else:
                # ps_CO2[i] = PCO2 * 1.0
                z_actual.append(z)
                p_actual.append(PCO2*1)

                CO2.update(cp.PT_INPUTS, PCO2, TCO2)
                rho_CO2_out = CO2.rhomass()
                h_CO2 = CO2.hmass()

        # print(CO2.phase(), CO2.T())

        if len(z_actual) > 2:

            ax3.plot(np.array(p_actual) * 1e-5, z_actual, label="Pinj={:.0f}".format(p_wh*1e-5))
        # ax3.plot(ps_CO2 * 1e-5, zs, label="Pinj={:.0f}".format(p_wh*1e-5))

        ax3.set_xlabel("Pressure/\\unit{\\bar}")
        ax3.set_ylabel("Depth/\\unit{\\m}")
        ax3.set_ylim(0, 4000)
        ax3.invert_yaxis()
        ax3.legend()

        tikzplotlib.save("Plots/Pvd_for_Pinj.tex")

# approximating the required injection welhead pressure
if __name__ == "__main_":


    CO2.update(cp.QT_INPUTS, 0, TCO2)
    Psat_CO2 = CO2.p()

    ps_wh_vap = np.linspace(5, Psat_CO2*1e-5-0.1, 20)*1e5
    ps_wh_liq = np.linspace(Psat_CO2*1e-5 + 0.1,  Psat_CO2*1e-5 + 20, 20)*1e5

    zs_max = []
    dZ = 10

    for p_wh in ps_wh_vap:

        z = 0
        PCO2 = p_wh * 1.0

        CO2.update(cp.PT_INPUTS, PCO2, TCO2)
        rho_CO2_out = CO2.rhomass()
        h_CO2 = CO2.hmass()

        while PCO2 > P_brine(z, p0=Pwh_brine):

            rho_CO2_in = rho_CO2_out

            P_test = PCO2 + rho_CO2_in * g * dZ
            for j in range(4):
                CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                rho_CO2_out = CO2.rhomass()

                P_test = PCO2 + (rho_CO2_in + rho_CO2_out) / 2 * g * dZ

            PCO2 = P_test *1.0
            CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
            rho_CO2_out = CO2.rhomass()

            z += dZ

            # print(z, P_brine(z), PCO2)

        zs_max.append(z)

    ps_wh = list(ps_wh_vap*1e-5) + [np.NaN]
    zs_max.append(np.NaN)

    for p_wh in ps_wh_liq:

        z = 0
        PCO2 = p_wh * 1.0

        CO2.update(cp.PT_INPUTS, PCO2, TCO2)
        rho_CO2_out = CO2.rhomass()
        h_CO2 = CO2.hmass()

        try:

            while PCO2 > P_brine(z, p0=Pwh_brine) and z <= 4000:

                rho_CO2_in = rho_CO2_out

                P_test = PCO2 + rho_CO2_in * g * dZ
                for j in range(4):
                    CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 + (rho_CO2_in + rho_CO2_out) / 2 * g * dZ

                PCO2 = P_test *1.0
                CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                rho_CO2_out = CO2.rhomass()

                z += dZ

                # print(z, P_brine(z), PCO2)
            if z > 4000:
                zs_max.append(np.NaN)
            else:
                zs_max.append(z)
        except:
            zs_max.append(np.NAN)

    ps_wh += list(ps_wh_liq*1e-5)

    fig3, ax3 = plt.subplots()
    ax3.plot(zs_max, ps_wh)

    ax3.set_xlabel("Reservoir Depth/\\unit{\\m}")
    ax3.set_ylabel("Minimum Wellhead Pressure/\\unit{\\bar}")
    ax3.set_ylim(10, 70)
    # ax3[1].legend()

    tikzplotlib.save("Plots/Pinj_vs_d.tex")

if __name__ == "__main_":

    Pwh_brine = 15e5
    ps_wh = np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120])*1e5
    ts_wh = np.array([15, 20, 25, 30, 40, 50, 60]) + 273.15

    dZ = 10
    zmax = 7000

    fig3, ax3 = plt.subplots()
    ax3.set_xlabel("Reservoir Depth/\\unit{\\m}")
    ax3.set_ylabel("Minimum Wellhead Pressure/\\unit{\\bar}")
    ax3.set_xlim(0, 7000)


    for TCO2 in ts_wh:
        zs_max = []

        for p_wh in ps_wh:

            z = 0
            PCO2 = p_wh * 1.0

            CO2.update(cp.PT_INPUTS, PCO2, TCO2)
            rho_CO2_out = CO2.rhomass()
            h_CO2 = CO2.hmass()

            while PCO2 > P_brine(z, p0=Pwh_brine) and z<zmax:

                rho_CO2_in = rho_CO2_out

                P_test = PCO2 + rho_CO2_in * g * dZ
                for j in range(4):
                    CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 + (rho_CO2_in + rho_CO2_out) / 2 * g * dZ

                PCO2 = P_test * 1.0
                CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                rho_CO2_out = CO2.rhomass()

                z += dZ

                # print(z, P_brine(z), PCO2)

            zs_max.append(z)

        # ps_wh = list(ps_wh_vap * 1e-5) + [np.NaN]
        # zs_max.append(np.NaN)

        ax3.plot(zs_max, ps_wh*1e-5, label=TCO2)

    ax3.legend()

    tikzplotlib.save("Plots/Pinj_vs_d.tex")

if __name__ == "__main__":

    Pwh_brine = 15e5
    ts_wh = np.array([25, 30, 40, 60, 90, 130]) + 273.15

    dZ = 10
    zmax = 4010

    fig3, ax3 = plt.subplots()
    ax3.set_xlabel("Reservoir Depth/\\unit{\\m}")
    ax3.set_ylabel("Minimum Wellhead Pressure/\\unit{\\bar}")
    ax3.set_xlim(0, 4000)


    for TCO2 in ts_wh:

        if TCO2 < CO2.T_critical():
            CO2.update(cp.QT_INPUTS, 0, TCO2)
            psat = CO2.p()*1e-5
            ps_wh_liq = list(np.linspace(Pwh_brine*1e-5, psat - 0.1, 10))
            ps_wh_vap = list(np.linspace(psat + 0.1, 120, 10))
            ps_wh = np.array(ps_wh_liq + ps_wh_vap)*1e5

        else:
            ps_wh = np.linspace(Pwh_brine*1e-5, 120, 20)*1e5
            # ps_wh = np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120]) * 1e5

        zs_max = []

        for p_wh in ps_wh:

            z = 0
            PCO2 = p_wh * 1.0

            CO2.update(cp.PT_INPUTS, PCO2, TCO2)
            rho_CO2_out = CO2.rhomass()
            h_CO2 = CO2.hmass()

            while PCO2 > P_brine(z, p0=Pwh_brine) and z<zmax:

                rho_CO2_in = rho_CO2_out

                P_test = PCO2 + rho_CO2_in * g * dZ
                for j in range(4):
                    CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                    rho_CO2_out = CO2.rhomass()

                    P_test = PCO2 + (rho_CO2_in + rho_CO2_out) / 2 * g * dZ

                PCO2 = P_test * 1.0
                CO2.update(cp.HmassP_INPUTS, h_CO2, P_test)
                rho_CO2_out = CO2.rhomass()

                z += dZ

                # print(z, P_brine(z), PCO2)

            zs_max.append(z)

        # ps_wh = list(ps_wh_vap * 1e-5) + [np.NaN]
        # zs_max.append(np.NaN)

        ax3.plot(zs_max, ps_wh*1e-5, "-o", label=TCO2)

    ax3.legend()

    tikzplotlib.save("Plots/Pinj_vs_d.tex")

plt.show()


