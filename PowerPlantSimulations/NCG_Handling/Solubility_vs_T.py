import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib
from scipy.optimize import root_scalar

from SP2009 import SpycherPruss2009 as SP

sp = SP()
fig, ax = plt.subplots()

nT = 20
zs = [0.125, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.4]
zs.reverse()

ts = np.linspace(298, 473, nT)
psat = [65 for t in ts]
ax.plot(ts, psat, "k--", label="\\(P_{sat}^{CO_2}\\)\\ at \\qty{298}{\\K}")

for j, z in enumerate(zs):
    target = z

    ps = np.ones(nT) * np.NaN

    for i, T in enumerate(ts):

        def Psearch(p):
            xCO2 = sp.calc_xCO2(p, T)

            return (target - xCO2) / target

        p0 = 1e5
        p1 = 500e5

        try:
            res = root_scalar(Psearch, method="brentq", bracket=[p0, p1])

            ps[i] = res.root
        except:
            continue


    label = "\\(z_{CO_2}=\\)\\qty{"+"{:.2f}".format(z)+"}{\\mol\\percent}"
    ax.plot(ts, ps*1e-5, label=label)

# ps_flash = [2850299.5400033947,
#             3014836.930355626,
#             4143382.4690827,
#             4054945.510707532,
#             6686015.417102253,
#             6664995.52381017,
#             6100592.361339722,
#             6058857.713905563,
#             5960877.566928461,
#             5999659.538425079
#             ]
# ps_flash_bar = [p*1e-5 for p in ps_flash]
# ts_flash = [414.2698508196169,
#             399.47181272996346,
#             409.794392697642,
#             407.1038243078245,
#             415.8132768873969,
#             413.4352587388571,
#             419.2127896916713,
#             421.5307797199874,
#             420.36645180586453,
#             420.6100497795135]
# ax.plot(ts_flash, ps_flash_bar, "o--", label="DSC")

ax.set_xlabel("Absorption Temperature/\\unit{\\K}")
ax.set_ylabel("Pressure/\\unit{\\bar}")
ax.set_yscale("log")
ax.legend()

tikzplotlib.save("Plots/Solubility_P_vs_t.tex")

plt.show()
