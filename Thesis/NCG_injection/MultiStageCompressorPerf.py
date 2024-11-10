import matplotlib.pyplot as plt
import numpy as np
import math

from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream

Pin = 0.1e5  # Pa
Tin = 293  # K

ps_in = [0.1e5, 1e5, 10e5]

fig, ax = plt.subplots()

for j, Pin in enumerate(ps_in):

    N = 100
    ps_wh = np.logspace(math.log10(Pin*1.1e-5), math.log10(150), N)*1e5
    ws_comp = np.empty(N)
    ns_stage = np.empty(N)

    for i, Pout in enumerate(ps_wh):

        inlet = Fluid(["carbondioxide", 1])
        inlet = MaterialStream(inlet, m=1)

        # find Psat
        inlet.update("TQ", Tin, 1)
        Psat = inlet.properties.P

        # initialise the inlet stream
        inlet.update("PT", Pin, Tin)


        compressor = Simulator.multistage_compression(0.75, 1, mech_eff=0.95)


        if Pout < Psat:
            compressor.set_inputs(inlet, Pout, findN=True)
            outlet = compressor.calc()

            work = compressor.work

        else:
            compressor.set_inputs(inlet, Psat, findN=True)
            temp_outlet = compressor.calc()

            temp_outlet.update("PQ", Psat, 0)

            pump = Simulator.pump(0.85, mech_eff=0.95)

            work = compressor.work + pump.work

        ws_comp[i] = work
        ns_stage[i] = compressor.N

    ax.plot(ps_wh*1e-5, ws_comp*1e-3, label="Pin={}bar".format(Pin*1e-5))

plt.axvline(x = Psat*1e-5, linestyle="--", color = 'k', label = 'Psat @ 20degC')
ax.set_xlabel("Injection Pressure/bar")
ax.set_ylabel("Specific Compression Work/kW s kg-1")

ax.set_xscale("log")
ax.legend()

plt.show()




