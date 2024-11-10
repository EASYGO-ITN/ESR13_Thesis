from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream
import matplotlib.pyplot as plt
import numpy as np
import tikzplotlib


Tin_H = 273.15 + 180  # K
Qin_H = 0.05

Tin_C = 298


water = Fluid(["water", 1])
water = MaterialStream(water, m=1)
water.update("TQ", Tin_H, Qin_H)

butane = Fluid(["butane", 1])
butane = MaterialStream(butane, m=1)
butane_out = butane.copy()

HX = Simulator.heat_exchanger(deltaP_hot=0, deltaP_cold=0)

fig, axs = plt.subplots(ncols=3)

# 20 bar
as_Q = [0, 25.1947, 28.6053, 50.3894, 75.5841, 100.779, 125.974, 151.168, 176.363, 201.558, 226.752, 251.947, 256.043, 277.142, 302.337, 327.531, 352.726, 377.921, 403.115, 428.31, 453.505, 478.7, 503.894]
as_T_hot = [453.15, 453.15, 453.15, 453.15, 453.15, 453.134, 447.399, 441.637, 435.847, 430.033, 424.196, 418.337, 417.383, 412.459, 406.562, 400.649, 394.719, 388.776, 382.82, 376.852, 370.874, 364.887, 358.891]
as_T_cold = [397.521, 388.671, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 387.521, 381.118, 373.081, 364.688, 355.981, 346.988, 337.725, 328.204, 318.432, 308.413, 298.15]

as_T_hot_out = min(as_T_hot)
as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)

Pin_C = 20e5
Tout_C = max(as_T_cold)

butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[0].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[0].plot([0,0], [297,297], "k", label="PowerCycle")
axs[0].plot([0,0], [297,297], label="Hot", color="red")
axs[0].plot([0,0], [297,297], label="Cold", color="blue")

axs[0].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[0].plot(as_Q, as_T_cold, "--", color="#203864")

axs[0].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[0].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")

axs[0].set_title("Pressure=\\qty{20}{\\bar}")
axs[0].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[0].set_ylabel("Temperature/\\unit{\\K}")
axs[0].set_xlim((0, max(as_Q)))
axs[0].set_ylim((298, None))
# axs[0].legend()

print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))
print("Pinch: Aspen {} Power Cycle {} Diff {}".format(as_min_DT, HX.min_deltaT, 100*(as_min_DT-HX.min_deltaT)/as_min_DT))

# 32 bar
as_Q = [0, 26.4636, 44.3597, 52.9271, 79.3907, 105.854, 132.318, 158.781, 181.715, 185.245, 211.709, 238.172, 264.636, 291.099, 317.563, 344.026, 370.49, 396.954, 423.417, 449.881, 476.344, 502.808, 529.271]
as_T_hot = [453.15, 453.15, 453.15, 453.15, 453.15, 451.981, 445.951, 439.89, 434.614, 433.8, 427.684, 421.543, 415.379, 409.194, 402.99, 396.768, 390.53, 384.278, 378.012, 371.735, 365.447, 359.15, 352.844]
as_T_cold = [425.125, 425.125, 414.733, 425.125, 425.125, 425.05, 423.406, 419.433, 414.733, 414.086, 408.272, 401.35, 393.738, 385.625, 377.107, 368.241, 359.061, 349.588, 339.836, 329.812, 319.521, 308.967, 298.15]

as_T_hot_out = min(as_T_hot)
as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)

Pin_C = 32e5
Tout_C = max(as_T_cold)

butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[1].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[1].plot([0,0], [297,297], "k", label="PowerCycle")
axs[1].plot([0,0], [297,297], label="Hot", color="red")
axs[1].plot([0,0], [297,297], label="Cold", color="blue")

axs[1].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[1].plot(as_Q, as_T_cold, "--", color="#203864")

axs[1].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[1].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")
# ax.plot([0, max(as_Q)], [424.733065, 424.733065], "k--")

axs[1].set_title("Pressure=\\qty{32}{\\bar}")
axs[1].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[1].set_ylabel("Temperature/\\unit{\\K}")
axs[1].set_xlim((0, max(as_Q)))
axs[1].set_ylim((298, None))
# axs[1].legend()

print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))
print("Pinch: Aspen {} Power Cycle {} Diff {}".format(as_min_DT, HX.min_deltaT, 100*(as_min_DT-HX.min_deltaT)/as_min_DT))

# 45 bar
as_Q = [0, 26.1513, 52.3026, 78.4539, 104.605, 130.756, 156.908, 183.059, 209.21, 235.362, 261.513, 287.664, 313.816, 339.967, 366.118, 392.269, 418.421, 444.572, 470.723, 496.875, 523.026]
as_T_hot = [453.15, 453.15, 453.15, 453.15, 452.265, 446.308, 440.32, 434.304, 428.263, 422.196, 416.108, 409.998, 403.87, 397.724, 391.562, 385.386, 379.196, 372.995, 366.783, 360.562, 354.333]
as_T_cold = [443.15, 439.454, 436.87, 434.712, 432.095, 428.178, 422.87, 416.541, 409.501, 401.935, 393.949, 385.608, 376.954, 368.011, 358.795, 349.318, 339.586, 329.602, 319.367, 308.883, 298.15]

as_T_hot_out = min(as_T_hot)
as_DT = [as_T_hot[i] - as_T_cold[i] for i in range(len(as_T_hot))]
as_min_DT = min(as_DT)

Pin_C = 45e5
Tout_C = 170 + 273.15

butane.update("PT", Pin_C, Tin_C)
butane_out.update("PT", Pin_C, Tout_C)

HX.set_inputs(Inlet_hot=water, Inlet_cold=butane, Outlet_cold=butane_out)
water_out, butane_out = HX.calc()

axs[2].plot([0,0], [297,297], "k--", label="Aspen Plus")
axs[2].plot([0,0], [297,297], "k", label="PowerCycle")
axs[2].plot([0,0], [297,297], label="Hot", color="red")
axs[2].plot([0,0], [297,297], label="Cold", color="blue")

axs[2].plot(as_Q, as_T_hot, "--", color="#C00000")
axs[2].plot(as_Q, as_T_cold, "--", color="#203864")

axs[2].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[0], color="red")
axs[2].plot(np.flip(HX.Duty_profile[1]*1e-3), HX.T_profile[1], color="blue")
# ax.plot([0, max(as_Q)], [424.733065, 424.733065], "k--")

axs[2].set_title("Pressure=\\qty{32}{\\bar}")
axs[2].set_xlabel("Heat Transferred/\\unit{\\kilo\\watt}")
axs[2].set_ylabel("Temperature/\\unit{\\K}")
axs[2].set_xlim((0, max(as_Q)))
axs[2].set_ylim((298, None))
axs[2].legend()

print("Temperature: Aspen {} Power Cycle {} Diff {}".format(as_T_hot_out, water_out.properties.T, 100*(as_T_hot_out-water_out.properties.T)/as_T_hot_out))
print("Pinch: Aspen {} Power Cycle {} Diff {}".format(as_min_DT, HX.min_deltaT, 100*(as_min_DT-HX.min_deltaT)/as_min_DT))

tikzplotlib.save("HXPerf.tex")

# plt.show()
