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



# for the binary ORC
if __name__ == "__main__":
    water = cp.AbstractState("?", "water")
    water.update(cp.QT_INPUTS, 0, 473.15)

    Pwh_brine = water.p()
    # ts_wh = np.array([25, 30, 40, 55, 75, 100, 130]) + 273.15
    # ts_wh = np.array([25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]) + 273.15
    ts_wh = np.array([25, 30, 35, 40, 45, 50, 60, 80, 110, 150]) + 273.15
    ts_wh = np.flip(ts_wh)

    dZ = 10
    zmax = 5010

    fig3, ax3 = plt.subplots()
    ax3.set_xlabel("Reservoir Depth/\\unit{\\m}")
    ax3.set_ylabel("Minimum Wellhead Pressure/\\unit{\\bar}")
    ax3.set_xlim(0, 4000)

    for TCO2 in ts_wh:

        if TCO2 < CO2.T_critical():
            CO2.update(cp.QT_INPUTS, 0, TCO2)
            psat = CO2.p()*1e-5
        else:
            psat = CO2.p_critical()*1e-5
            # ps_wh = np.linspace(Pwh_brine*1e-5, 120, 20)*1e5
            # ps_wh = np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120]) * 1e5

        ps_wh_liq = list(np.linspace(Pwh_brine * 1e-5, psat - 0.1, 10))
        ps_wh_vap = list(np.linspace(psat + 0.1, 250, 20))
        ps_wh = np.array(ps_wh_liq + ps_wh_vap)

        zs_max = np.array([np.NaN for z in ps_wh])

        for i, p_wh in enumerate(ps_wh):

            if p_wh == -1:
                ps_wh[i] = np.NAN
                continue

            p_wh *= 1e5

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

            zs_max[i] = z
            if z >= zmax:
                break

        label = "\\(T_{NCG}^{inj}=\\) \\qty{"+"{:.0f}".format(TCO2)+"}{\\K}"
        ax3.plot(zs_max, ps_wh, label=label)

    ax3.legend()

    tikzplotlib.save("Plots/Pinj_vs_d_ORC.tex")

# for the single flash DSC
# no longer used as the brine pressure does not make a huge difference
if __name__ == "__main_":

    Pwh_brine = 0.1e5
    # ts_wh = np.array([25, 30, 40, 55, 75, 100, 130]) + 273.15
    # ts_wh = np.array([25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100]) + 273.15
    ts_wh = np.array([25, 30, 35, 40, 45, 50, 60, 80, 110, 150]) + 273.15
    ts_wh = np.flip(ts_wh)

    dZ = 10
    zmax = 5010

    fig3, ax3 = plt.subplots()
    ax3.set_xlabel("Reservoir Depth/\\unit{\\m}")
    ax3.set_ylabel("Minimum Wellhead Pressure/\\unit{\\bar}")
    ax3.set_xlim(0, 4000)

    for TCO2 in ts_wh:

        if TCO2 < CO2.T_critical():
            CO2.update(cp.QT_INPUTS, 0, TCO2)
            psat = CO2.p()*1e-5
        else:
            psat = CO2.p_critical()*1e-5
            # ps_wh = np.linspace(Pwh_brine*1e-5, 120, 20)*1e5
            # ps_wh = np.array([30, 40, 50, 60, 70, 80, 90, 100, 110, 120]) * 1e5

        ps_wh_liq = list(np.linspace(Pwh_brine * 1e-5, psat - 0.1, 10))
        ps_wh_vap = list(np.linspace(psat + 0.1, 250, 20))
        ps_wh = np.array(ps_wh_liq + [-1] + ps_wh_vap)

        zs_max = np.array([np.NaN for z in ps_wh])

        for i, p_wh in enumerate(ps_wh):

            if p_wh == -1:
                ps_wh[i] = np.NAN
                continue

            p_wh *= 1e5

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

            zs_max[i] = z
            if z >= zmax:
                break

        label = "\\(T_{NCG}^{inj}=\\) \\qty{"+"{:.0f}".format(TCO2)+"}{\\K}"
        ax3.plot(zs_max, ps_wh, label=label)

    ax3.legend()

    tikzplotlib.save("Plots/Pinj_vs_d_DSC.tex")


plt.show()


