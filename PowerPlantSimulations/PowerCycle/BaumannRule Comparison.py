import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib

MrCO2 = 0.044
MrH2O = 0.018

alpha = 0.1
# As = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
As = list((np.linspace(0, 1, 51) + 1e-6)/(1+1e-6))
zHs = [1, 0.98, 0.95, 0.91, 0.86, 0.8, 0.7, 0.5, 0.02]

fig, axs = plt.subplots(ncols=2)

for zH in zHs:
    zC = 1-zH

    xHs = [1 for a in As]

    yCs = [zC/a if zC/a<=1 else 1 for a in As]
    yHs = [1- yC for yC in yCs]

    mvap = [As[i]*(MrCO2*yCs[i] + MrH2O*yHs[i]) for i in range(len(As))]
    mliq = [(1-As[i])*MrH2O*xHs[i] for i in range(len(As))]

    Amass = [mvap[i]/(mvap[i]+mliq[i]) for i in range(len(As))]

    Adiff = [100*(Amass[i]-As[i]+1e-6)/(Amass[i]+1e-6) for i in range(len(As))]

    Eff = [85*(Amass[i]+1)/2 for i in range(len(As))]
    Eff0 = [85*(As[i]+1)/2 for i in range(len(As))]
    EffDiff = [(Eff[i]/Eff0[i]-1)*100 for i in range(len(As))]


    label="\\qty{"+str(int(zC*100))+"}{\\percent}"
    axs[0].plot(As, Eff, label=label)
    axs[1].plot(As, EffDiff, label=label)

axs[0].set_xlabel("Mole-based Vapour Quality/\\unit{\\mole\\per\\mole}")
axs[0].set_ylabel("Mass-based Isentropic Efficiency/\\unit{\\percent}")
axs[0].legend()

axs[1].set_xlabel("Mole-based Vapour Quality/\\unit{\\mole\\per\\mole}")
axs[1].set_ylabel("Difference in Isentropic Efficiency/\\unit{\\percent}")
axs[1].legend()

plt.tight_layout()
plt.legend()
# plt.show()

tikzplotlib.save("BaumannRuleComparison.tex")

