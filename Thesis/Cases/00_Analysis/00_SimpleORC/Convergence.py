import json
import numpy as np
import matplotlib.pyplot as plt
import tikzplotlib
from CoolProp.CoolProp import PropsSI

with open("../../00_SimpleORC_ConvergencePlot/sensitivity_results.json", "r") as file:
    results = json.load(file)

fmin = np.array(results[0]["fmin"])
fmax = np.array(results[0]["fmax"])
favg = np.array(results[0]["favg"])
gens = [i for i, f in enumerate(fmin)]
fbest = min(fmin)


fig, axs = plt.subplots()

axs.plot(gens, fmax/fbest, label="Worst species")
axs.plot(gens, favg/fbest, label="Average species")
axs.plot(gens, fmin/fbest, label="Best species")

axs.set_xlabel("Number of generations")
axs.set_ylabel("Normalised Objective Function")

axs.legend()

tikzplotlib.save("Plots/IsoPentane_Convergence.tex", figure=fig)

plt.show()
