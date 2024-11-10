import matplotlib.pyplot as plt
from math import pow, log10, log, exp

import numpy as np
import tikzplotlib


def NETL(A):
    # Spiral
    cost = 468 * A + 8190

    return cost


def Peters(A):
    # Spiral
    cost = 11700 * pow(A, 0.44)

    return cost


def Peters_gask(A):
    # gasket
    cost = 29 * A + 1560

    return cost


def Peters_weld(A):
    # welded
    cost = 69 * A + 4670

    return cost


As = np.logspace(1, 4)

cost_NETL = [NETL(a) for a in As]
spec_cost_NETL = [NETL(a)/a for a in As]

cost_Peters = [Peters(a) for a in As]
spec_cost_Peters = [Peters(a)/a for a in As]

cost_Peters_gask = [Peters_gask(a) for a in As]
spec_cost_Peters_gask = [Peters_gask(a)/a for a in As]

cost_Peters_weld = [Peters_weld(a) for a in As]
spec_cost_Peters_weld = [Peters_weld(a)/a for a in As]


figa, axa = plt.subplots()
axa.plot(As, cost_NETL, label="\\citeauthor{Loh2002}\\textsuperscript{a, b}")  # spiral
axa.plot(As, cost_Peters, label="\\citeauthor{Peters2003}\\textsuperscript{a, b}")  # spiral
axa.plot(As, cost_Peters_gask, label="\\citeauthor{Peters2003}\\textsuperscript{a, c}")  # gaskets
axa.plot(As, cost_Peters_weld, label="\\citeauthor{Peters2003}\\textsuperscript{a, d}")  # welded

axa.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axa.set_ylabel("Cost/\\unit{\\USD}200X")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()


figb, axb = plt.subplots()
axb.plot(As, spec_cost_NETL, label="\\citeauthor{Loh2002}\\textsuperscript{a, b}")  # spiral
axb.plot(As, spec_cost_Peters, label="\\citeauthor{Peters2003}\\textsuperscript{a, b}")  # spiral
axb.plot(As, spec_cost_Peters_gask, label="\\citeauthor{Peters2003}\\textsuperscript{a, c}")  # gaskets
axb.plot(As, spec_cost_Peters_weld, label="\\citeauthor{Peters2003}\\textsuperscript{a, d}")  # welded

axb.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\square\\m}")
axb.set_xscale("log")
axb.legend()

tikzplotlib.save("PlateCost.tex", figure=figa)
tikzplotlib.save("PlateSpecCost.tex", figure=figb)

plt.show()