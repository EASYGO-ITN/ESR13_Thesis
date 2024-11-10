import CoolProp as cp
import numpy as np
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
import tikzplotlib

wfs = ["n-Propane", "CycloPropane", "IsoButane", "n-Butane", "Isopentane", "Isohexane", "Cyclopentane", "n-Heptane"]

if __name__ == "__main_":

    ps = []
    ts = []

    fig, ax1 = plt.subplots()
    ax2 = ax1.twiny()

    for wf in wfs:
        state = cp.AbstractState("?", wf)

        # ps.append(state.p_critical()*1e-5)
        # ts.append(state.T_critical())

        pcrit = state.p_critical()*1e-5
        tcrit = state.T_critical()

        ax1.plot([tcrit], [pcrit], "o", label=wf)



    ax1.set_xlabel("Crtical Temperature/\\unit{\\K}")
    ax1.set_ylabel("Critical Pressure/\\unit{\\bar}")
    ax1.legend()

    lims = ax1.get_xlim()
    lims = [l - 273.15 for l in lims]
    ax2.set_xlim(lims)
    ax2.set_xlabel("Crtical Temperature/\\unit{\\degreeCelsius}")

    tikzplotlib.save("WorkingFLuids.tex")

if __name__ == "__main__":

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    for i, wf in enumerate(wfs):

        print(cp.CoolProp.get_aliases(wf))

        # rho_ref = PropsSI("Dmolar", "P", 101325, "T", 298, wf)
        rho_ref = PropsSI("Dmolar", "Q", 0, "T", 298, wf)
        cp.CoolProp.set_reference_state(wf, 298, rho_ref, 0, 0)

        state = cp.AbstractState("?", wf)
        state.build_phase_envelope("TS")

        state.update(cp.PT_INPUTS, 101325, 298)
        print(state.smolar())

        env = state.get_phase_envelope_data()

        ss = [s/1000 for s in env.smolar_vap]
        ts = [t for t in env.T]

        ax1.plot(ss, ts, label=wf)

    ax1.legend()
    ax1.set_xlabel("Entropy/\\unit{\\kilo\\joule\\per\\mol\\per\\K}")
    ax1.set_ylabel("Temperature/\\unit{\\K}")
    ax1.set_ylim(300, None)
    ax1.set_xlim(0, None)


    ax2.set_ylim([l - 273.15 for l in ax1.get_ylim()])
    ax2.set_ylabel("Temperature/\\unit{\\degreeCelsius}")

    tikzplotlib.save("WorkingFluids_TS_envelopes.tex")

# if __name__ == "__main":
#
#     fig, ax1 = plt.subplots()
#     ax2 = ax1.twinx()
#
#     for i, wf in enumerate(wfs):
#
#         rho_ref = PropsSI("Dmolar", "Q", 0, "T", 298, wf)
#         cp.CoolProp.set_reference_state(wf, 298, rho_ref, 0, 0)
#
#         state = cp.AbstractState("?", wf)
#         state.build_phase_envelope("TS")
#
#         ts = np.linspace(298, state.T_critical() - 0.1)
#         sliq = []
#         svap = []
#         for t in ts:
#             state.update(cp.QT_INPUTS, 0, t)
#             sliq.append(state.smolar()/1000)
#
#             state.update(cp.QT_INPUTS, 1, t)
#             svap.append(state.smolar()/1000)
#
#         state.update(cp.DmolarT_INPUTS, state.rhomolar_critical(), state.T_critical())
#         scrit = state.smolar() / 1000
#
#         ts_env = [t for i, t in enumerate(ts)] + [state.T_critical()] + [ts[-i-1] for i, t in enumerate(ts)]
#         ss = sliq + [scrit] + [svap[-i-1] for i, t in enumerate(svap)]
#
#         ax1.plot(ss, ts_env, label=wf)
#
#     ax1.legend()
#     ax1.set_xlabel("Entropy/\\unit{\\kilo\\joule\\per\\mol\\per\\K}")
#     ax1.set_ylabel("Temperature/\\unit{\\K}")
#
#     ax2.set_ylim([l - 273.15 for l in ax1.get_ylim()])
#     ax2.set_ylabel("Temperature/\\unit{\\degreeCelsius}")


plt.show()