import matplotlib.pyplot as plt
from math import pow, log10, log, exp
from CoolProp.CoolProp import PropsSI

import numpy as np
import tikzplotlib

dP = 120  # Pa
S_air_in = PropsSI("S", "P", 101325, "T", 298, "air")
H_air_in = PropsSI("H", "P", 101325, "T", 298, "air")
D_air_in = PropsSI("D", "P", 101325, "T", 298, "air")
H_air_out = PropsSI("H", "P", 101325 + dP, "S", S_air_in, "air")

dH = (H_air_out - H_air_in) / 0.6 *1e-3

def Turton(W):
    V = W / dH / D_air_in

    if 1 <= V <= 100:
        logV = log10(V)

        logC = 3.5391 - 0.3533*logV + 0.4477*logV*logV

        cost = pow(10, logC)
    else:
        cost = np.NAN

    return cost


# def Astolfi(W):
#
#     cost = 1.4e4 * pow(W/200, 0.67)
#
#     return cost


def Smith(W):

    if 50 <=W <= 200:
        cost = 1.23e4 * pow(W/50, 0.76)
    else:
        cost = np.NAN

    return cost

Ws = np.logspace(0, 3)

cost_Turton = [Turton(w) for w in Ws]
spec_cost_Turton = [Turton(w)/w for w in Ws]

# cost_Astolfi = [Astolfi(w) for w in Ws]
# spec_cost_Astolfi = [Astolfi(w)/w for w in Ws]

cost_Smith = [Smith(w) for w in Ws]
spec_cost_Smith = [Smith(w)/w for w in Ws]


figa, axa = plt.subplots()
axa.plot(Ws, cost_Turton, label="\\citeauthor{Turton2012}\\textsuperscript{a}")
# axa.plot(Ws, cost_Astolfi, label="\\citeauthor{Astolfi2014}")
axa.plot(Ws, cost_Smith, label="\\citeauthor{Smith2005}")

axa.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axa.set_ylabel("Turbine Cost/\\unit{\\EUR}200X")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()

figb, axb = plt.subplots()
axb.plot(Ws, spec_cost_Turton, label="\\citeauthor{Turton2012}\\textsuperscript{a}")
# axa.plot(Ws, spec_cost_Astolfi, label="\\citeauthor{Astolfi2014}")
axb.plot(Ws, spec_cost_Smith, label="\\citeauthor{Smith2005}")

axb.set_xlabel("Fluid Power/\\unit{\\kilo\\watt}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\kilo\\watt}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("FanCost.tex", figure=figa)
tikzplotlib.save("FanSpecCost.tex", figure=figb)

plt.show()
