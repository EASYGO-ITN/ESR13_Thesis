import matplotlib.pyplot as plt
import tikzplotlib

ts=[100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200]
Flash=[35.2567433,38.2818443,41.3004323,44.3117238,47.3148713,50.3089601,53.3340685,56.4482273,59.626363,62.8741286,66.1929052,69.5629039,73.0278918,76.5381404,80.102991,83.7524883,87.4502268,91.2069006,95.0211773,98.892433,102.819033]
ORC=[16.8292014,19.13499754,21.80709184,24.73610752,27.66006249,30.59799153,33.54160133,36.90585492,41.02826437,45.53822915,50.53598622,56.63516703,65.81557373,75.19588111,84.57618849,97.12765292,101.90288357,106.14390762,124.96199506,130.83175868,136.7015223]
Isobutane=[16.81617538,19.05751841,21.47542806,24.16540297,27.03802771,30.20499215,33.19663929,36.90585492,41.02826437,45.53822915,50.53598622,56.63516703,65.81557373,75.19588111,84.57618849,97.12765292,101.90288357,106.14390762,109.81742035,111.77087391,114.37518581]
nButane=[16.8292014,19.13499754,21.57513281,24.18017411,26.93225864,29.89666033,33.22485914,36.39397393,39.95785152,43.64281233,48.05258889,52.43564947,57.74866508,63.33219831,69.38585437,76.75831134,86.54745138,95.88322838,124.96199506,130.83175868,136.7015223]
Isopentane=[15.962330818,18.88305143,21.80709184,24.73610752,27.66006249,30.59799153,33.54160133,36.4927679,39.8805452,43.2683225,46.90076797,51.06383234,55.35175701,59.88245942,64.67161774,69.74350827,75.12461463,80.84996528,87.05322895,93.71435417,101.0889739]
nPentane=[12.181814031,15.674996195,19.168178359,22.6577126,26.15435538,29.66857772,33.18644436,36.71857279,40.25595982,43.79334685,47.34352201,50.98726603,54.95416534,59.36924121,64.05907519,68.95824173,74.14377322,79.61504083,85.41044739,91.56633738,98.13321794]
Cyclopentane=[15.33078002,18.09750337,20.86422672,23.63095007,26.39767342,29.16439677,31.83450878,34.99649668,38.319305605,41.64211453,45.13984965,48.7568396,52.58167674,56.5874609,60.74854179,65.06128243,69.62452441,74.32135168,79.23943479,84.501764495,89.7640942]

fig, ax = plt.subplots()

ax.plot(ts, Flash, label="DSC")
ax.plot(ts, Isobutane, label="iso-Butane")
ax.plot(ts, nButane, label="n-Butane")
ax.plot(ts, Isopentane, label="iso-Pentane")
ax.plot(ts, nPentane, label="n-Pentane")
ax.plot(ts, Cyclopentane, label="cyclo-Pentane")
# ax.plot(ts, ORC, label="Best WF", color="k")

ax.set_xlabel("Temperature/\\unit{\\degreeCelsius}")
ax.set_ylabel("Specific net power/\\unit{\\kilo\\watt\\s\\per\\kg}")
ax.legend()

tikzplotlib.save("PureWater_TSLice.tex")

plt.show()