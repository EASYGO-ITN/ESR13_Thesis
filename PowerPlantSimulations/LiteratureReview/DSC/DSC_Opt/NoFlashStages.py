import matplotlib.pyplot as plt
import tikzplotlib

n_stages = [0, 1, 2, 3, 4, 6, 8, 10]
turb_power = [89.8001140083628, 103.462742653141, 109.431755736854, 110.500151644578, 110.863961589981, 111.157147855904, 111.283300629718, 111.353502452385]

fig, ax = plt.subplots()

ax.plot(n_stages, turb_power, "o-")
ax.set_xlabel("Number of flash stages")
ax.set_ylabel("Turbine Power/\\unit{\\kilo\\watt\\per\\kg\\s}")
ax.set_ylim([80, 120])
ax.set_xlim([0, 10])

ax_twin = ax.twinx()
ax_twin.set_ylabel("Turbine Power relative to no flash/\\unit{\\percent}")
ax_twin.set_ylim([100*80/min(turb_power), 100*120/min(turb_power)])
ax_twin.set_xlim([0, 10])

tikzplotlib.save("NoFlashStagesOptimisation.tex")

plt.show()
