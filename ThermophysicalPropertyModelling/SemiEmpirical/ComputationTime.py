import matplotlib.pyplot as plt
import numpy as np
import scipy
from time import perf_counter

from CombinedModel import WaterCO2, Water, CO2
from CombinedModel import Model

N = 10000

pa = 5
pb = 7
ps = np.power(10, pa + (pb-pa)*np.random.rand(N))

ta = 298
tb = 573
ts = ta + (tb-ta)*np.random.rand(N)

za = -3.5
zb = 3.5
zs = za + (zb-za)*np.random.rand(N)
zs = scipy.stats.norm.cdf(zs, 0, 1)

mixture = WaterCO2()
model = Model()
wat = Water()
co2 = CO2()

MIXSTART = perf_counter()
mix_failed = 0
for i, z in enumerate(zs):
    try:
        mixture.calc(ps[i], ts[i], (1-z), z)
    except:
        mix_failed += 1
        pass
MIXEND = perf_counter()
print("HEOS Mixture:\nStart:{}\nEND:{}\nDuration:{}s\nFailed:{}\n".format(MIXSTART, MIXEND, MIXEND-MIXSTART, mix_failed))

MODSTART = perf_counter()
mod_failed = 0
for i, z in enumerate(zs):
    try:
        model.calc(ps[i], ts[i], (1-z), z)
    except:
        mod_failed += 1
        pass
MODEND = perf_counter()
print("Coupled Model:\nStart:{}\nEND:{}\nDuration:{}s\nFailed:{}\n".format(MODSTART, MODEND, MODEND-MODSTART, mod_failed))

WATSTART = perf_counter()
wat_failed = 0
for i, z in enumerate(zs):
    try:
        wat.calc(ps[i], ts[i])
    except:
        wat_failed += 1
        pass
WATEND = perf_counter()
print("HEOS Water:\nStart:{}\nEND:{}\nDuration:{}s\nFailed:{}\n".format(WATSTART, WATEND, WATEND-WATSTART, wat_failed))

CO2START = perf_counter()
co2_failed = 0
for i, z in enumerate(zs):
    try:
        co2.calc(ps[i], ts[i])
    except:
        co2_failed += 1
        pass
CO2END = perf_counter()
print("HEOS CO2:\nStart:{}\nEND:{}\nDuration:{}s\nFailed:{}\n".format(CO2START, CO2END, CO2END-CO2START, co2_failed))
