import math
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib

HS_Cp = 4
HS_Hfg = 0

T_H = 450
T_C = 300

def calc_Qmax(Cp=None, Hfg=None):

    if Cp is None:
        Cp = HS_Cp
    if Hfg is None:
        Hfg = HS_Hfg

    return Cp*(T_H-T_C) + Hfg


def calc_Q(T, Cp=None, Hfg=None):

    if Cp is None:
        Cp = HS_Cp
    if Hfg is None:
        Hfg = HS_Hfg

    return Cp*(T_H-T) + Hfg


def calc_eta_cycle(T):
    return 1 - T_C/T

def calc_eta_Triangular(T):
    return (T-T_C)/(T+T_C)

def calc_eta_Lohrenz(T):

    if T == T_C:
        return 0
    else:
        T_LM = (T-T_C)/math.log(T/T_C)
        return 1 - T_C/T_LM

def calc_eta_recov(T, **kwargs):
    return calc_Q(T, **kwargs) / calc_Qmax(**kwargs)


def calc_eta_plant(T, **kwargs):

    return calc_eta_cycle(T)*calc_eta_recov(T, **kwargs)


def calc_Topt(Cp=None, Hfg=None):
    if Cp is None:
        Cp = HS_Cp
    if Hfg is None:
        Hfg = HS_Hfg

    if Hfg/Cp < T_H*(T_H/T_C-1):
        return math.sqrt(T_C*(T_H + Hfg/Cp))
    else:
        return T_H

if __name__ == "__main__":
    nT = 50
    ts = np.linspace(T_C, T_H, nT)
    eta_cycle = np.ones(nT)*np.NaN
    eta_recov = np.ones(nT)*np.NaN
    eta_plant = np.ones(nT)*np.NaN

    for i, t in enumerate(ts):
        eta_cycle[i] = calc_eta_cycle(t)*100
        eta_recov[i] = calc_eta_recov(t)*100
        eta_plant[i] = calc_eta_plant(t)*100

    BEP_t = calc_Topt()
    BEP_ts = [BEP_t, BEP_t, BEP_t]
    BEP_etas = [calc_eta_recov(BEP_t)*100, calc_eta_cycle(BEP_t)*100, calc_eta_plant(BEP_t)*100]
    BEP_etas.sort()

    fig, ax = plt.subplots()
    ax.plot(ts, eta_recov, label="Recovery")
    ax.plot(ts, eta_cycle, label="Cycle")
    ax.plot(ts, eta_plant, label="Plant")
    ax.plot(BEP_ts, BEP_etas, "ko:", label="BEP")

    ax.set_xlabel("Maximum Cycle Temperature/\\unit{\\K}")
    ax.set_ylabel("Efficiency/\\unit{\\percent}")


    ax.set_ylim(0, 100)
    ax.set_xlim(T_C, T_H+5)

    ax.legend()

    tikzplotlib.save("Recov_Cycle_Plant_eff.tex")

if __name__ == "__main__":

    fig, ax = plt.subplots()

    hfgs = [0, 250, 500, 1000, 2000, 4000]

    nT = 50
    ts = np.linspace(T_C, T_H, nT)

    BEP_ts = []
    BEP_etas = []

    for hfg in hfgs:
        eta_plant = np.ones(nT)*np.NaN

        for i, t in enumerate(ts):
            eta_plant[i] = calc_eta_plant(t, Hfg=hfg)*100

        BEP_t = calc_Topt(Hfg=hfg)
        BEP_ts.append(BEP_t)
        BEP_etas.append(calc_eta_plant(BEP_t, Hfg=hfg)*100)

        label = "\\(x\\Delta H_{fg}=\\)\\qty{"+"{}".format(hfg)+"}{\\kilo\\joule\\per\\kg}"
        ax.plot(ts, eta_plant, label=label)

    eta_carnot = [calc_eta_cycle(t)*100 for t in ts]
    label = "\\(x\\Delta H_{fg}=\\infty\\)\\unit{\\kilo\\joule\\per\\kg}"
    ax.plot(ts, eta_carnot, "k--", label=label)

    BEP_ts.append(T_H)
    BEP_etas.append(eta_carnot[-1])
    ax.plot(BEP_ts, BEP_etas, "ko:", label="BEP")

    ax.set_xlabel("Maximum Cycle Temperature/\\unit{\\K}")
    ax.set_ylabel("Efficiency/\\unit{\\percent}")

    ax.set_ylim(0, 40)
    ax.set_xlim(T_C, T_H+5)

    ax.legend()

    tikzplotlib.save("Plant_eff_vs_DH.tex")

if __name__ == "__main__":

    fig, ax = plt.subplots()

    hfgs = [0, 250, 500, 1000, 2000, 4000]

    nT = 50
    ts = np.linspace(T_C, T_H, nT)

    BEP_ts = []
    BEP_etas = []

    for hfg in hfgs:
        eta_plant = np.ones(nT)*np.NaN

        for i, t in enumerate(ts):
            eta_plant[i] = calc_eta_plant(t, Hfg=hfg)*100

        BEP_t = calc_Topt(Hfg=hfg)
        BEP_ts.append(BEP_t)
        BEP_etas.append(calc_eta_plant(BEP_t, Hfg=hfg)*100)

        label = "\\(x\\Delta H_{fg}=\\)\\qty{"+"{}".format(hfg)+"}{\\kilo\\joule\\per\\kg}"
        ax.plot(ts, eta_plant, label=label)

    eta_carnot = [calc_eta_cycle(t)*100 for t in ts]
    label = "\\(x\\Delta H_{fg}=\\infty\\)\\unit{\\kilo\\joule\\per\\kg}"
    ax.plot(ts, eta_carnot, "k--", label=label)

    # eta_triangular = [calc_eta_Triangular(t) * 100 for t in ts]
    # ax.plot(ts, eta_triangular, "r", label="Triangular Cycle")

    eta_lorenz = [calc_eta_Lohrenz(t) * 100 for t in ts]
    ax.plot(ts, eta_lorenz, "r", label="Triangular Cycle")

    BEP_ts.append(T_H)
    BEP_etas.append(eta_carnot[-1])
    ax.plot(BEP_ts, BEP_etas, "k:", label="BEP")

    ax.set_xlabel("Maximum Cycle Temperature/\\unit{\\K}")
    ax.set_ylabel("Efficiency/\\unit{\\percent}")

    ax.set_ylim(0, 40)
    ax.set_xlim(T_C, T_H+5)

    ax.legend()

    tikzplotlib.save("Plant_eff_vs_DH_and_Triangular.tex")

plt.show()