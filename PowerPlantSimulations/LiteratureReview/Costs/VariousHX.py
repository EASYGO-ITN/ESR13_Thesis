import matplotlib.pyplot as plt
from math import pow, log10, log, exp

import numpy as np
import tikzplotlib


def Astolfi_PHE(A):
    cost = 1500 * pow(1000*A/4000, 0.9)

    return cost


def Astolfi_REC(A):
    cost = 260 * pow(1000*A/650, 0.9)

    return cost


def Turton_HX(A):
    if 10 <= A <= 1000:
        logA = log10(A)
        logC = 4. - 0.2503*logA + 0.1974*logA*logA

        cost = pow(10, logC)
    else:
        cost = np.NAN

    return cost


def Turton_Evap(A):

    if 10 <= A <= 100:
        logA = log10(A)
        logC = 4.4646 - 0.5277 * logA + 0.3955 * logA * logA

        cost = pow(10, logC)
    else:
        cost = np.NAN

    return cost


As = np.linspace(10, 4000)

cost_Astolfi_PHE = [Astolfi_PHE(a) for a in As]
spec_cost_Astolfi_PHE = [Astolfi_PHE(a)/a for a in As]

cost_Astolfi_REC = [Astolfi_REC(a) for a in As]
spec_cost_Astolfi_REC = [Astolfi_REC(a)/a for a in As]

cost_Turton_hx = [Turton_HX(a) for a in As]
spec_cost_Turton_hx = [Turton_HX(a)/a for a in As]

cost_Turton_evap = [Turton_Evap(a) for a in As]
spec_cost_Turton_evap = [Turton_Evap(a)/a for a in As]


figa, axa = plt.subplots()
axa.plot(As, cost_Astolfi_PHE, label="Astolfi - PHE")
axa.plot(As, cost_Astolfi_REC, label="Astolfi - REC")
axa.plot(As, cost_Turton_hx, label="Turton - HX")
axa.plot(As, cost_Turton_evap, label="Turton - Evap.")

axa.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axa.set_ylabel("Cost/\\unit{\\USD}200X")

axa.set_xscale("log")
# axa.set_yscale("log")
axa.legend()


figb, axb = plt.subplots()
axb.plot(As, spec_cost_Astolfi_PHE, label="Astolfi - PHE")
axb.plot(As, spec_cost_Astolfi_REC, label="Astolfi - REC")
axb.plot(As, spec_cost_Turton_hx, label="Turton - HX")
axb.plot(As, spec_cost_Turton_evap, label="Turton - Evap.")

axb.set_xlabel("Heat Transfer Area/\\unit{\\square\\m}")
axb.set_ylabel("Specific Cost/\\unit{\\USD\\per\\square\\m}")
axb.set_xscale("log")
axb.legend()

# tikzplotlib.save("VariousHXCost.tex", figure=figa)
# tikzplotlib.save("VariousHXSpecCost.tex", figure=figb)

plt.show()