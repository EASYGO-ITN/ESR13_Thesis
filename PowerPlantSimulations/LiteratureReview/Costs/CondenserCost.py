import matplotlib.pyplot as plt
from math import pow, log10, log, exp

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

def Smith(A):

    yref = 2000

    if 200 <= A <= 2000:
        cost = 1.56e5 * pow(A/200, 0.89)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def Turton(A):

    yref = 2001

    if 10 <= A <= 10000:
        logA = log10(A)
        logC = 4.0336 + 0.2341*logA + 0.0497*logA*logA

        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def GETEM(A):

    yref = 2002

    cost = 768 * pow(A, 0.85)

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def GETEM_ncg(A):

    yref = 2002

    cost = 1780 * pow(A, 0.72)

    corr_currency = 1
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


def Astolfi(A):

    yref = 2014

    cost = 5.3e5 * pow(A/3563, 0.9)

    corr_currency = convert_EUR_to_USD(1, year=yref)
    corr_PPI = calc_PPI("heat_exchanger", Yref) / calc_PPI("heat_exchanger", yref)

    cost *= corr_currency*corr_PPI

    return cost


As = np.logspace(1, 4)

cost_Smith = [Smith(a) for a in As]
spec_cost_Smith = [Smith(a)/a for a in As]

cost_Turton = [Turton(a) for a in As]
spec_cost_Turton = [Turton(a)/a for a in As]

cost_GETEM = [GETEM(a) for a in As]
spec_cost_GETEM = [GETEM(a)/a for a in As]

cost_GETEM_ncg = [GETEM_ncg(a) for a in As]
spec_cost_GETEM_ncg = [GETEM_ncg(a)/a for a in As]

cost_Astolfi = [Astolfi(a) for a in As]
spec_cost_Astolfi = [Astolfi(a)/a for a in As]


figa, axa = plt.subplots()
axa.plot(As, cost_Smith, label="Smith \\cite{Smith2005}")
axa.plot(As, cost_Turton, label="Turton \\cite{Turton2012}")
axa.plot(As, cost_GETEM, label="GETEM \\cite{GETEM2016, Addams2021}")
axa.plot(As, cost_GETEM_ncg, label="GETEM\\cite{GETEM2016, Addams2021}\\textsuperscript{a}")
axa.plot(As, cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}")

axa.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axa.set_ylabel("Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()


figb, axb = plt.subplots()
axb.plot(As, spec_cost_Smith, label="Smith \\cite{Smith2005}")
axb.plot(As, spec_cost_Turton, label="Turton \\cite{Turton2012}")
axb.plot(As, spec_cost_GETEM, label="GETEM \\cite{GETEM2016}")
axb.plot(As, spec_cost_GETEM_ncg, label="GETEM \\cite{GETEM2016}\\textsuperscript{a}")
axb.plot(As, spec_cost_Astolfi, label="Astolfi \\cite{Astolfi2014B}")

axb.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\square\\m}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("CondenserCost.tex", figure=figa)
tikzplotlib.save("CondenserSpecCost.tex", figure=figb)

plt.show()