import matplotlib.pyplot as plt
from math import pow, log10, log, exp

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

def Smith(A):

    yref = 2000

    if 80 <= A <= 4000:
        cost = 3.28e4 * pow(A/80, 0.68)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def NETL(A):

    yref = 2002

    cost = 235 * A + 17900

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI


    return cost


def Peters_fixed(A):

    yref = 2002

    cost = 181 * A + 3320

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI


    return cost


def Peters_floating(A):

    yref = 2002

    cost = 239 * A + 13400

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI


    return cost


def Turton_fixed(A):

    yref = 2001

    if 10 <= A <= 1000:
        logA = log10(A)
        logC = 4.3247 - 0.3030*logA + 0.1634*logA*logA
        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI


    return cost

def Turton_floating(A):

    yref = 2001

    if 10 <= A <= 1000:
        logA = log10(A)
        logC = 4.8306 - 0.8509*logA + 0.3187*logA*logA
        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def Turton_kettle(A):

    yref = 2001

    if 10 <= A <= 100:
        logA = log10(A)
        logC = 4.4646 - 0.5277*logA + 0.3955*logA*logA
        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency * corr_PPI

    return cost


def Astolfi_PHE(A):

    yref = 2014

    cost = 1500 * pow(1000*A/4000, 0.9)

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def Astolfi_REC(A):

    yref = 2014

    cost = 260 * pow(1000*A/650, 0.9)

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


As = np.logspace(1, 4)

cost_Smith = [Smith(a) for a in As]
spec_cost_Smith = [Smith(a)/a for a in As]

cost_NETL = [NETL(a) for a in As]
spec_cost_NETL = [NETL(a)/a for a in As]

cost_Peters_fix = [Peters_fixed(a) for a in As]
spec_cost_Peters_fix = [Peters_fixed(a)/a for a in As]

cost_Peters_flo = [Peters_floating(a) for a in As]
spec_cost_Peters_flo = [Peters_floating(a)/a for a in As]

cost_Turton_fixed = [Turton_fixed(a) for a in As]
spec_cost_Turton_fixed = [Turton_fixed(a)/a for a in As]

cost_Turton_floating = [Turton_floating(a) for a in As]
spec_cost_Turton_floating = [Turton_floating(a)/a for a in As]

cost_Turton_kettle = [Turton_kettle(a) for a in As]
spec_cost_Turton_kettle = [Turton_kettle(a)/a for a in As]

cost_Astolfi_PHE = [Astolfi_PHE(a) for a in As]
spec_cost_Astolfi_PHE = [Astolfi_PHE(a)/a for a in As]

cost_Astolfi_REC = [Astolfi_REC(a) for a in As]
spec_cost_Astolfi_REC = [Astolfi_REC(a)/a for a in As]

figa, axa = plt.subplots()
axa.plot(As, cost_Smith, label="Smith \\cite{Smith2005}")
axa.plot(As, cost_NETL, label="NETL \\cite{Loh2002, Adams2021}\\textsuperscript{a}")
axa.plot(As, cost_Peters_flo, label="Peters \\cite{Peters2003, Adams2021}\\textsuperscript{b}")
axa.plot(As, cost_Peters_fix, label="Peters \\cite{Peters2003, Adams2021}\\textsuperscript{c}")
axa.plot(As, cost_Turton_fixed, label="Turton \\cite{Turton2012}\\textsuperscript{a}")
axa.plot(As, cost_Turton_floating, label="Turton \\cite{Turton2012}\\textsuperscript{b}")
axa.plot(As, cost_Turton_kettle, label="Turton \\cite{Turton2012}\\textsuperscript{d}")
axa.plot(As, cost_Astolfi_PHE, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{e}")
axa.plot(As, cost_Astolfi_REC, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{f, g}")

axa.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axa.set_ylabel("Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()


figb, axb = plt.subplots()
axb.plot(As, spec_cost_Smith, label="Smith \\cite{Smith2005}")
axb.plot(As, spec_cost_NETL, label="NETL \\cite{Loh2002, Adams2021}\\textsuperscript{a}")
axb.plot(As, spec_cost_Peters_flo, label="Peters \\cite{Peters2003, Adams2021}\\textsuperscript{b}")
axb.plot(As, spec_cost_Peters_fix, label="Peters \\cite{Peters2003, Adams2021}\\textsuperscript{c}")
axb.plot(As, spec_cost_Turton_fixed, label="Turton \\cite{Turton2012}\\textsuperscript{a}")
axb.plot(As, spec_cost_Turton_floating, label="Turton \\cite{Turton2012}\\textsuperscript{b}")
axb.plot(As, spec_cost_Turton_kettle, label="Turton \\cite{Turton2012}\\textsuperscript{d}")
axb.plot(As, spec_cost_Astolfi_PHE, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{e}")
axb.plot(As, spec_cost_Astolfi_REC, label="Astolfi \\cite{Astolfi2014B}\\textsuperscript{f, g}")
axb.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\square\\m}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("ShellAndTubeHXCost.tex", figure=figa)
tikzplotlib.save("ShellAndTubeHXSpecCost.tex", figure=figb)

plt.show()