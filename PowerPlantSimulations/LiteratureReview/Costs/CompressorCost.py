import matplotlib.pyplot as plt
from math import pow, log10, log, exp
from CoolProp.CoolProp import PropsSI

import numpy as np
import tikzplotlib

from CostConversion import Yref, convert_EUR_to_USD, calc_PPI

def Turton(W):

    yref = 2001

    if 450 <= W <= 3000:
        logW = log10(W)

        logC = 2.2897 + 1.3604*logW - 0.1027*logW*logW

        cost = pow(10, logC)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency*corr_PPI

    return cost

def Smith(W):

    yref = 2000

    if 4 <=W <= 700:
        cost = 9.84e4 * pow(W/250, 0.46)
    else:
        cost = np.NAN

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency * corr_PPI

    return cost

def Duc(W):

    yref = 2005

    cost = 7248 * pow(1.34*W, 0.82)

    corr_currency = 1
    corr_PPI = calc_PPI("pump", Yref) / calc_PPI("pump", yref)

    cost *= corr_currency * corr_PPI

    return cost

Ws = np.logspace(0, 3)

cost_Turton = [Turton(w) for w in Ws]
spec_cost_Turton = [Turton(w)/w for w in Ws]

cost_Smith = [Smith(w) for w in Ws]
spec_cost_Smith = [Smith(w)/w for w in Ws]

cost_Duc = [Duc(w) for w in Ws]
spec_cost_Duc = [Duc(w)/w for w in Ws]

figa, axa = plt.subplots()
axa.plot(Ws, cost_Turton, label="Turton \\cite{Turton2012}")
# axa.plot(Ws, cost_Astolfi, label="\\citeauthor{Astolfi2014B}")
axa.plot(Ws, cost_Smith, label="Smith \\cite{Smith2005}")
axa.plot(Ws, cost_Duc, label="Duc \\cite{Duc2007}")

axa.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axa.set_ylabel("Turbine Cost/\\unit{\\USD}2023")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()

figb, axb = plt.subplots()
axb.plot(Ws, spec_cost_Turton, label="TUrton \\cite{Turton2012}")
# axb.plot(Ws, spec_cost_Astolfi, label="\\citeauthor{Astolfi2014B}")
axb.plot(Ws, spec_cost_Smith, label="Smith \\cite{Smith2005}")
axb.plot(Ws, spec_cost_Duc, label="Duc \\cite{Duc2007}")

axb.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\kilo\\watt}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("CompressorCost.tex", figure=figa)
tikzplotlib.save("CompressorSpecCost.tex", figure=figb)

plt.show()
