from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib


Tin_H = 273.15 + 180  # K

Tin_C = 298
Pin_C = 20e5

water = Fluid(["water", 1])
water = MaterialStream(water, m=1)

butane = Fluid(["butane", 1])
butane = MaterialStream(butane, m=1)
butane_out = butane.copy()

HX = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0)

fig, axs = plt.subplots(ncols=3)

# vapour quality = 0.00
as_Q = [0, 25.7166, 29.1978, 51.4331, 77.1497, 102.866, 128.583, 154.299, 180.016, 205.732, 231.449, 257.166, 261.346, 282.882, 308.599, 334.315, 360.032, 385.748, 411.465, 437.181, 462.898, 488.614, 514.331]
as_T_hot = [453.15, 447.297, 446.502, 441.414, 435.503, 429.567, 423.607, 417.624, 411.622, 405.6, 399.561, 393.506, 392.52, 387.437, 381.354, 375.26, 369.156, 363.042, 356.919, 350.789, 344.653, 338.511, 332.365]
as_T_cold = [397.521, 388.671, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 381.118, 373.081, 364.688, 355.981, 346.988, 337.725, 328.204, 318.432, 308.413, 298.15]
as_MassRatio = 1.02071221365665
as_T_hot_out = min(as_T_hot)

as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)
as_min_Q = as_Q[as_DT.index(as_min_DT)]

Qin_H = 0
water.update("TQ", Tin_H, Qin_H)

Tout_C = max(as_T_cold)
butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(MassRatio=-1, Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[0].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[0].plot([0,0], [297,297], "k", label="PowerCycle")
axs[0].plot([0,0], [297,297], label="Hot", color="red")
axs[0].plot([0,0], [297,297], label="Cold", color="blue")
axs[0].plot([0,0], [297,297], label="Pinch Point", color="green")

axs[0].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[0].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")

axs[0].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[0].plot(as_Q, as_T_cold, "--", color="#203864")

min_DT = HX.min_deltaT
DT = HX.T_profile[0] - HX.T_profile[1]
min_Q = np.flip(HX.Duty_profile[1])[np.where(DT==min_DT)[0][0]]

axs[0].plot([as_min_Q, as_min_Q], [min(as_T_cold), max(as_T_hot)], "--", color="green")
axs[0].plot([min_Q/1000, min_Q/1000], [min(as_T_cold), max(as_T_hot)], color="green")

axs[0].set_title("Vapour Quality=\\qty{0.00}{\\kg\\per\\kg}")
axs[0].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[0].set_ylabel("Temperature/\\unit{\\K}")
# axs[1].set_xlim((0, max(as_Q)))
axs[0].set_ylim((298, None))

print("Qin", Qin_H)
print("MassRatio: Aspen {} Power Cycle {} Diff {}".format(as_MassRatio, HX.MassRatio, 100*(as_MassRatio-HX.MassRatio)/as_MassRatio))
print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))

# vapour quality = 0.05
as_Q = [0, 35.2604, 40.0336, 70.5208, 105.781, 141.042, 176.302, 211.562, 246.823, 282.083, 317.344, 352.604, 358.336, 387.864, 423.125, 458.385, 493.645, 528.906, 564.166, 599.427, 634.687, 669.947, 705.208]
as_T_hot = [453.15, 453.15, 453.15, 453.15, 451.998, 443.956, 435.861, 427.718, 419.531, 411.304, 403.042, 394.748, 393.397, 386.427, 378.081, 369.715, 361.331, 352.931, 344.519, 336.097, 327.666, 319.23, 310.789]
as_T_cold = [397.521, 388.671, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 381.118, 373.081, 364.688, 355.981, 346.988, 337.725, 328.204, 318.432, 308.413, 298.15]
as_MassRatio = 1.39951545100481
as_T_hot_out = min(as_T_hot)

as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)
as_min_Q = as_Q[as_DT.index(as_min_DT)]

Qin_H = 0.05
water.update("TQ", Tin_H, Qin_H)

Tout_C = max(as_T_cold)
butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(MassRatio=-1, Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[1].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[1].plot([0,0], [297,297], "k", label="PowerCycle")
axs[1].plot([0,0], [297,297], label="Hot", color="red")
axs[1].plot([0,0], [297,297], label="Cold", color="blue")
axs[1].plot([0,0], [297,297], label="Pinch Point", color="green")

axs[1].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[1].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")

axs[1].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[1].plot(as_Q, as_T_cold, "--", color="#203864")

min_DT = HX.min_deltaT
DT = HX.T_profile[0] - HX.T_profile[1]
min_Q = np.flip(HX.Duty_profile[1])[np.where(DT==min_DT)[0][0]]

axs[1].plot([as_min_Q, as_min_Q], [min(as_T_cold), max(as_T_hot)], "--", color="green")
axs[1].plot([min_Q/1000, min_Q/1000], [min(as_T_cold), max(as_T_hot)], color="green")

axs[1].set_title("Vapour Quality=\\qty{0.05}{\\kg\\per\\kg}")
axs[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[1].set_ylabel("Temperature/\\unit{\\K}")
# axs[1].set_xlim((0, max(as_Q)))
axs[1].set_ylim((298, None))

print("Qin", Qin_H)
print("MassRatio: Aspen {} Power Cycle {} Diff {}".format(as_MassRatio, HX.MassRatio, 100*(as_MassRatio-HX.MassRatio)/as_MassRatio))
print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))


# vapour quality = 0.15
as_Q = [0, 46.9266, 53.2791, 93.8533, 140.78, 187.707, 234.633, 281.56, 328.487, 375.413, 422.34, 469.266, 476.896, 516.193, 563.12, 610.046, 656.973, 703.9, 750.826, 797.753, 844.68, 891.606, 938.533]
as_T_hot = [453.15, 453.15, 453.15, 453.15, 453.15, 453.15, 453.15, 453.15, 447.149, 436.392, 425.548, 414.629, 412.847, 403.644, 392.603, 381.515, 370.387, 359.227, 348.041, 336.835, 325.615, 314.384, 303.15]
as_T_cold = [397.521, 388.671, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 381.118, 373.081, 364.688, 355.981, 346.988, 337.725, 328.204, 318.432, 308.413, 298.15]
as_MassRatio = 1.86255919885638
as_T_hot_out = min(as_T_hot)

as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)
as_min_Q = as_Q[as_DT.index(as_min_DT)]

Qin_H = 0.15
water.update("TQ", Tin_H, Qin_H)

Tout_C = max(as_T_cold)
butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(MassRatio=-1, Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[2].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[2].plot([0,0], [297,297], "k", label="PowerCycle")
axs[2].plot([0,0], [297,297], label="Hot", color="red")
axs[2].plot([0,0], [297,297], label="Cold", color="blue")
axs[2].plot([0,0], [297,297], label="Pinch Point", color="green")

axs[2].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[2].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")

axs[2].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[2].plot(as_Q, as_T_cold, "--", color="#203864")

min_DT = HX.min_deltaT
DT = HX.T_profile[0] - HX.T_profile[1]
min_Q = np.flip(HX.Duty_profile[1])[np.where(DT==min_DT)[0][0]]

axs[2].plot([as_min_Q, as_min_Q], [min(as_T_cold), max(as_T_hot)], "--", color="green")
axs[2].plot([min_Q/1000, min_Q/1000], [min(as_T_cold), max(as_T_hot)], color="green")

axs[2].set_title("Vapour Quality=\\qty{0.15}{\\kg\\per\\kg}")
axs[2].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[2].set_ylabel("Temperature/\\unit{\\K}")
# axs[1].set_xlim((0, max(as_Q)))
axs[2].set_ylim((298, None))
axs[2].legend()

tikzplotlib.save("HXPerf_Pinch.tex")

print("Qin", Qin_H)
print("MassRatio: Aspen {} Power Cycle {} Diff {}".format(as_MassRatio, HX.MassRatio, 100*(as_MassRatio-HX.MassRatio)/as_MassRatio))
print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))

plt.show()