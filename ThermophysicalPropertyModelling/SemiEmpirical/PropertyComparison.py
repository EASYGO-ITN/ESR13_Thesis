import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

from CombinedModel import WaterCO2, Water, CO2
from CombinedModel import Model


def calc_plots(zCs, file_extension):
    nZ = len(zCs)
    nT = 5
    nP = 20

    ts = np.linspace(298, 250+273.15, nT)
    # ps = np.logspace(5, 7, nP)
    ps = np.linspace(1e5, 1e7, nP)
    ps_bar = ps*1e-5

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]
    nColors = len(colors)

    figD, axsD = plt.subplots(ncols=nZ)
    figV, axsV = plt.subplots(ncols=nZ)
    figH, axsH = plt.subplots(ncols=nZ)
    figS, axsS = plt.subplots(ncols=nZ)
    figa, axsa = plt.subplots(ncols=nZ)

    figDb, axsDb = plt.subplots(ncols=nZ)
    figVb, axsVb = plt.subplots(ncols=nZ)
    figHb, axsHb = plt.subplots(ncols=nZ)
    figSb, axsSb = plt.subplots(ncols=nZ)
    figab, axsab = plt.subplots(ncols=nZ)

    axsD[-1].plot([-1, -1], [10, 10], "k", label="Coupled Model")
    axsD[-1].plot([-1, -1], [10, 10], "kx", label="HEOS mixture")
    axsD[-1].plot([-1, -1], [10, 10], "ko", label="HEOS pure")
    axsV[-1].plot([-1, -1], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsV[-1].plot([-1, -1], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsV[-1].plot([-1, -1], [np.NAN, np.NAN], "ko", label="HEOS pure")
    axsH[-1].plot([-1, -1], [-10000, -10000], "k", label="Coupled Model")
    axsH[-1].plot([-1, -1], [-10000, -10000], "kx", label="HEOS mixture")
    axsH[-1].plot([-1, -1], [-10000, -10000], "ko", label="HEOS pure")
    axsS[-1].plot([-1, -1], [-10, -10], "k", label="Coupled Model")
    axsS[-1].plot([-1, -1], [-10, -10], "kx", label="HEOS mixture")
    axsS[-1].plot([-1, -1], [-10, -10], "ko", label="HEOS pure")
    axsa[-1].plot([-1, -1], [0, 0], "k", label="Coupled Model")
    axsa[-1].plot([-1, -1], [0, 0], "kx", label="HEOS mixture")
    axsa[-1].plot([-1, -1], [0, 0], "ko", label="HEOS pure")

    axsDb[-1].plot([0, 0], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsDb[-1].plot([0, 0], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsDb[-1].plot([0, 0], [np.NAN, np.NAN], "ko", label="HEOS pure")
    axsVb[-1].plot([0, 0], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsVb[-1].plot([0, 0], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsVb[-1].plot([0, 0], [np.NAN, np.NAN], "ko", label="HEOS pure")
    axsHb[-1].plot([0, 0], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsHb[-1].plot([0, 0], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsHb[-1].plot([0, 0], [np.NAN, np.NAN], "ko", label="HEOS pure")
    axsSb[-1].plot([0, 0], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsSb[-1].plot([0, 0], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsSb[-1].plot([0, 0], [np.NAN, np.NAN], "ko", label="HEOS pure")
    axsab[-1].plot([0, 0], [np.NAN, np.NAN], "k", label="Coupled Model")
    axsab[-1].plot([0, 0], [np.NAN, np.NAN], "kx", label="HEOS mixture")
    axsab[-1].plot([0, 0], [np.NAN, np.NAN], "ko", label="HEOS pure")


    # initialise the fluid states
    model = Model()
    water = Water()
    co2 = CO2()
    mixture = WaterCO2()
    for i, zC in enumerate(zCs):

        axsD[i].set_title("zC={:.2f}".format(zC))
        axsV[i].set_title("zC={:.2f}".format(zC))
        axsH[i].set_title("zC={:.2f}".format(zC))
        axsS[i].set_title("zC={:.2f}".format(zC))
        axsa[i].set_title("zC={:.2f}".format(zC))

        axsDb[i].set_title("zC={:.2f}".format(zC))
        axsVb[i].set_title("zC={:.2f}".format(zC))
        axsHb[i].set_title("zC={:.2f}".format(zC))
        axsSb[i].set_title("zC={:.2f}".format(zC))
        axsab[i].set_title("zC={:.2f}".format(zC))

        axsD[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsV[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsH[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsS[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsa[i].set_xlabel("Pressure/\\unit{\\bar}")

        axsDb[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsVb[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsHb[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsSb[i].set_xlabel("Pressure/\\unit{\\bar}")
        axsab[i].set_xlabel("Pressure/\\unit{\\bar}")

        axsD[i].set_ylabel("Density/\\unit{\\mole\\per\\cubic\\m}")
        axsV[i].set_ylabel("Volume/\\unit{\\cubic\\m\\per\\mole}")
        axsH[i].set_ylabel("Enthalpy/\\unit{\\joule\\per\\mole}")
        axsS[i].set_ylabel("Entropy/\\unit{\\joule\\per\\mole\\K}")
        axsa[i].set_ylabel("Quality/\\unit{\\mole\\per\\mole}")

        axsDb[i].set_ylabel("\\(\\frac{\\rho^{HEOS Mix}}{\\rho^{Couples}}\\)")
        axsVb[i].set_ylabel("\\(\\frac{\\v^{HEOS Mix}}{\\v^{Coupled}}\\)")
        axsHb[i].set_ylabel("\\(\\frac{\\h^{HEOS Mix}}{\\h^{Coupled}}\\)")
        axsSb[i].set_ylabel("\\(\\frac{\\s^{HEOS Mix}}{\\s^{Coupled}}\\)")
        axsab[i].set_ylabel("\\(\\frac{\\q^{HEOS Mix}}{\\q^{Coupled}}\\)")

        axsDb[i].set_ylim([0.75, 1.25])
        axsVb[i].set_ylim([0.75, 1.25])
        axsHb[i].set_ylim([0.75, 1.25])
        axsSb[i].set_ylim([0.75, 1.25])
        axsab[i].set_ylim([0.75, 1.25])

        axsD[i].set_xlim([0, 100])
        axsV[i].set_xlim([0, 100])
        axsH[i].set_xlim([0, 100])
        axsS[i].set_xlim([0, 100])
        axsa[i].set_xlim([0, 100])

        axsDb[i].set_xlim([0, 100])
        axsVb[i].set_xlim([0, 100])
        axsHb[i].set_xlim([0, 100])
        axsSb[i].set_xlim([0, 100])
        axsab[i].set_xlim([0, 100])

        axsD[i].set_yscale("log")
        axsV[i].set_yscale("log")

        # calculate the new model
        for j, t in enumerate(ts):

            label = "\\qty{" + str(int(t)) + "}{" + "\\K}"

            color = colors[j % nColors]

            D = np.empty(nP)
            V = np.empty(nP)
            H = np.empty(nP)
            S = np.empty(nP)
            A = np.empty(nP)

            Dcp = np.empty(nP)
            Vcp = np.empty(nP)
            Hcp = np.empty(nP)
            Scp = np.empty(nP)
            Acp = np.empty(nP)

            for k, p in enumerate(ps):
                D[k], V[k], H[k], S[k], g, vap, liq, A[k] = model.calc(p, t, (1-zC), zC)

                try:
                    Dcp[k], Vcp[k], Hcp[k], Scp[k], g, vap, liq, Acp[k] = mixture.calc(p, t, (1-zC), zC)
                except:
                    Dcp[k], Vcp[k], Hcp[k], Scp[k], g, vap, liq, Acp[k] = np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN, np.NAN

            A[A > 1] = np.NAN
            A[A < 0] = np.NAN
            axsD[i].plot(ps_bar, D, label=label, color=color)
            axsV[i].plot(ps_bar, V, label=label, color=color)
            axsH[i].plot(ps_bar, H, label=label, color=color)
            axsS[i].plot(ps_bar, S, label=label, color=color)
            axsa[i].plot(ps_bar, A, label=label, color=color)

            axsD[i].plot(ps_bar, Dcp, "x", color=color)
            axsV[i].plot(ps_bar, Vcp, "x", color=color)
            axsH[i].plot(ps_bar, Hcp, "x", color=color)
            axsS[i].plot(ps_bar, Scp, "x", color=color)
            axsa[i].plot(ps_bar, Acp, "x", color=color)

            Aratio = (A + 1e-6) / (Acp + 1e-6)
            Aratio[Aratio > 10] = np.NAN
            axsDb[i].plot(ps_bar, D/Dcp, label=label, color=color)
            axsVb[i].plot(ps_bar, V/Vcp, label=label, color=color)
            axsHb[i].plot(ps_bar, H/Hcp, label=label, color=color)
            axsSb[i].plot(ps_bar, S/Scp, label=label, color=color)
            axsab[i].plot(ps_bar, Aratio, label=label, color=color)

        # calculate the water HEOS
        if zC == 0:

            axsD[i].set_title("Pure Water")
            axsV[i].set_title("Pure Water")
            axsH[i].set_title("Pure Water")
            axsS[i].set_title("Pure Water")
            axsa[i].set_title("Pure Water")

            axsDb[i].set_title("Pure Water")
            axsVb[i].set_title("Pure Water")
            axsHb[i].set_title("Pure Water")
            axsSb[i].set_title("Pure Water")
            axsab[i].set_title("Pure Water")

            for j, t in enumerate(ts):

                label = "\\qty{" + str(int(t)) + "}{" + "\\K}"
                color = colors[j % nColors]

                Dw = np.empty(nP)
                Vw = np.empty(nP)
                Hw = np.empty(nP)
                Sw = np.empty(nP)
                Aw = np.empty(nP)

                D = np.empty(nP)
                V = np.empty(nP)
                H = np.empty(nP)
                S = np.empty(nP)
                A = np.empty(nP)

                for k, p in enumerate(ps):
                    Dw[k], Vw[k], Hw[k], Sw[k], g, vap, liq, Aw[k] = water.calc(p, t)
                    D[k], V[k], H[k], S[k], g, vap, liq, A[k] = model.calc(p, t, (1 - zC), zC)

                axsD[i].plot(ps_bar, Dw, "o", color=color)
                axsV[i].plot(ps_bar, Vw, "o",  color=color)
                axsH[i].plot(ps_bar, Hw, "o", color=color)
                axsS[i].plot(ps_bar, Sw, "o", color=color)
                axsa[i].plot(ps_bar, Aw, "o", color=color)

                Aratio = (A + 1e-6) / (Aw + 1e-6)
                Aratio[Aratio > 10] = np.NAN
                axsDb[i].plot(ps_bar, D / Dw, "o", color=color)
                axsVb[i].plot(ps_bar, V / Vw, "o", color=color)
                axsHb[i].plot(ps_bar, H / Hw, "o", color=color)
                axsSb[i].plot(ps_bar, S / Sw, "o", color=color)
                axsab[i].plot(ps_bar, Aratio, "o", color=color)

        # calculate the CO2 HEOS
        if zC == 1:

            axsD[i].set_title("Pure Carbon Dioxide")
            axsV[i].set_title("Pure Carbon Dioxide")
            axsH[i].set_title("Pure Carbon Dioxide")
            axsS[i].set_title("Pure Carbon Dioxide")
            axsa[i].set_title("Pure Carbon Dioxide")

            axsDb[i].set_title("Pure Carbon Dioxide")
            axsVb[i].set_title("Pure Carbon Dioxide")
            axsHb[i].set_title("Pure Carbon Dioxide")
            axsSb[i].set_title("Pure Carbon Dioxide")
            axsab[i].set_title("Pure Carbon Dioxide")

            for j, t in enumerate(ts):
                label = "\\qty{" + str(int(t)) + "}{" + "\\K}"
                color = colors[j % nColors]

                Dc = np.empty(nP)
                Vc = np.empty(nP)
                Hc = np.empty(nP)
                Sc = np.empty(nP)
                Ac = np.empty(nP)

                D = np.empty(nP)
                V = np.empty(nP)
                H = np.empty(nP)
                S = np.empty(nP)
                A = np.empty(nP)

                for k, p in enumerate(ps):
                    Dc[k], Vc[k], Hc[k], Sc[k], g, vap, liq, Ac[k] = co2.calc(p, t)
                    D[k], V[k], H[k], S[k], g, vap, liq, A[k] = model.calc(p, t, (1 - zC), zC)

                axsD[i].plot(ps_bar, Dc, "o", color=color)
                axsV[i].plot(ps_bar, Vc, "o", color=color)
                axsH[i].plot(ps_bar, Hc, "o", color=color)
                axsS[i].plot(ps_bar, Sc, "o", color=color)
                axsa[i].plot(ps_bar, Ac, "o", color=color)

                Aratio = (A + 1e-6) / (Ac + 1e-6)
                Aratio[Aratio > 10] = np.NAN
                axsDb[i].plot(ps_bar, D / Dc, "o", color=color)
                axsVb[i].plot(ps_bar, V / Vc, "o", color=color)
                axsHb[i].plot(ps_bar, H / Hc, "o", color=color)
                axsSb[i].plot(ps_bar, S / Sc, "o", color=color)
                axsab[i].plot(ps_bar, Aratio, "o", color=color)

    axsD[-1].legend()
    axsV[-1].legend()
    axsH[-1].legend()
    axsS[-1].legend()
    axsa[-1].legend()

    axsDb[-1].legend()
    axsVb[-1].legend()
    axsHb[-1].legend()
    axsSb[-1].legend()
    axsab[-1].legend()

    plt.tight_layout()
    # plt.get_current_fig_manager().window.showMaximized()
    # plt.show()

    tikzplotlib.save("LatexFiles/Properties_Dappendix_"+file_extension+".tex", figure=figD)
    tikzplotlib.save("LatexFiles/Properties_Vappendix_"+file_extension+".tex", figure=figV)
    tikzplotlib.save("LatexFiles/Properties_Happendix_"+file_extension+".tex", figure=figH)
    tikzplotlib.save("LatexFiles/Properties_Sappendix_"+file_extension+".tex", figure=figS)
    tikzplotlib.save("LatexFiles/Properties_Aappendix_"+file_extension+".tex", figure=figa)

    tikzplotlib.save("LatexFiles/Ratios_Dappendix_"+file_extension+".tex", figure=figDb)
    tikzplotlib.save("LatexFiles/Ratios_Vappendix_"+file_extension+".tex", figure=figVb)
    tikzplotlib.save("LatexFiles/Ratios_Happendix_"+file_extension+".tex", figure=figHb)
    tikzplotlib.save("LatexFiles/Ratios_Sappendix_"+file_extension+".tex", figure=figSb)
    tikzplotlib.save("LatexFiles/Ratios_Aappendix_"+file_extension+".tex", figure=figab)


zCs = [0, 0.00964186994535833, 0.0255880595216386, 0.059379940594793, 0.121000484421018]  # part 1
calc_plots(zCs, "part1")

zCs = [0.217695437585733, 0.348268273464018, 0.5, 0.651731726535982, 0.782304562414267]  # part 2
calc_plots(zCs, "part2")

zCs = [0.878999515578982, 0.940620059405207, 0.974411940478361, 0.990358130054642, 1]  # part 3
calc_plots(zCs, "part3")