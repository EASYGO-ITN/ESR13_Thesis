import matplotlib.pyplot as plt
import tikzplotlib


NCG=[0,0.003,0.006,0.009,0.012,0.015,0.018,0.021,0.024,0.027,0.03]
Flash=[132.711179,128.465446,124.193662,119.90836,115.609411,111.185462,106.859127,102.518494,98.167011,93.8024848,89.4235443]
ORC=[112.510505,112.930169,113.355197,113.780212,114.205472,114.631033,115.056365,115.483483,115.91014,116.33709,116.764336]

fig, ax = plt.subplots()

ax.plot(NCG, Flash, label="DSC")
ax.plot(NCG, ORC, label="ORC")
# ax.plot(qs, ORC, label="Best WF", color="k")

ax.set_xlabel("NCG content/\\unit{\\kg\\per\\kg}")
ax.set_ylabel("Specific net power/\\unit{\\kilo\\watt\\s\\per\\kg}")
ax.legend()

tikzplotlib.save("PureWater_SalLice.tex")

plt.show()