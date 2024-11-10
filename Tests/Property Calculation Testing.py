import math
import numpy as np
import matplotlib.pyplot as plt

from FluidProperties.fluid import Fluid
from Simulator.streams import MaterialStream
import Simulator

zH2O = 0.95
brine = Fluid(["water", zH2O, "carbondioxide", 1 - zH2O], engine="geoprop")
brine.update("PT", 1013250, 430)

brine_stream = MaterialStream(brine, 1.0)

separator = Simulator.separator()
separator.set_inputs(brine_stream)
brine_liq, brine_vap = separator.calc()

s = brine_vap.properties.S * 1.0
print(s)


# ps = np.logspace(math.log10(1e4), math.log10(1e6), 21)
# for p in ps:
#     brine_vap.update("PS", p, s)
#     print(p, brine_vap.properties.S, brine_vap.properties.T)



# zH2O = 0.99
# brine = Fluid(["water", zH2O, "carbondioxide", 1 - zH2O], engine="geoprop")
#
# brine.update("PT", 2.6e5, 401)
# print(brine.properties.S)
# print(brine.composition)
#
# brine.update("PT", 2.6e5, 402)
# print(brine.properties.S)
# print(brine.composition)

p = 6.5e4
n_t = 100
ts = np.linspace(300, 400, n_t)
# n_t = 2
# ts = np.linspace(343.15, 343.2, n_t)
h = []

# for t in ts:
#     brine_vap.update("PT", p, t)
#     h.append(brine_vap.properties.S)
#     print(t, brine_vap.properties.S, brine_vap.properties.VapProps.composition)
#
# plt.plot(ts, h, "o")
# plt.xlabel("Temperature, K")
# plt.ylabel("Entropy, J/kg/K")
# plt.show()

brine_vap.update("PS", p, s)
h = brine_vap.properties.H
print(h)

brine_vap.update("PH", p, h)
print(brine_vap.properties.S)


print(brine_vap.properties.T)