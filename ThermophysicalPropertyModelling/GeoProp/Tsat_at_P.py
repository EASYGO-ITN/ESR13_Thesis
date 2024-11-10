import reaktoro as rkt
import CoolProp as cp
import numpy as np
import matplotlib.pyplot as plt


def to_tex2D(xs, ys):

    # xys = [ "("+str(round(xs[i], 3))+","+str(round(ys[i], 3))+")" for i in range(len(xs))]
    xys = ["({:.3e},{:.3e})".format(xs[i],ys[i]) for i in range(len(xs))]
    coords = " ".join(xys)

    return coords


# specific volume of pure water as a function of temperature for different EOS and activity models
samples = 200
p = 10e5

water = cp.AbstractState("?", "water")
water.update(cp.PQ_INPUTS, p, 0)
tsat = water.T()
print("Tsat;"+str(tsat))
ts = np.linspace(445, 465, samples)

cp_state = cp.AbstractState("?", "water")
cp_svol = np.zeros(samples)

db = rkt.SupcrtDatabase('supcrtbl')
aqueous = rkt.AqueousPhase("H2O(aq)")

ideal_gaseous = rkt.GaseousPhase("H2O(g)")
ideal_system = rkt.ChemicalSystem(db, aqueous, ideal_gaseous)
ideal_state = rkt.ChemicalState(ideal_system)
ideal_state.set('H2O(aq)', 1, 'kg')
ideal_state.pressure(p, "Pa")
rkt_ideal_svol = np.zeros(samples)

SRK_gaseous = rkt.GaseousPhase("H2O(g)")
SRK_gaseous.set(rkt.ActivityModelSoaveRedlichKwong())
SRK_system = rkt.ChemicalSystem(db, aqueous, SRK_gaseous)
SRK_state = rkt.ChemicalState(SRK_system)
SRK_state.set('H2O(aq)', 1, 'kg')
SRK_state.pressure(p, "Pa")
rkt_SRK_svol = np.zeros(samples)

for i, t in enumerate(ts):

    def get_svolume(state, t):
        state.temperature(t, "K")

        res = rkt.equilibrate(state)
        props = rkt.ChemicalProps(state)
        phases = state.system().phases().size()
        masses = np.array([props.phaseProps(i).mass()[0] for i in range(phases)])
        volumes = np.array([props.phaseProps(i).volume()[0] for i in range(phases)])

        _total_mass = sum(masses)
        _total_volume = sum(volumes)

        return _total_volume/_total_mass

    rkt_ideal_svol[i] = get_svolume(ideal_state, t)
    rkt_SRK_svol[i] = get_svolume(SRK_state, t)

    cp_state.update(cp.PT_INPUTS, p, t)
    cp_svol[i] = 1/ cp_state.rhomass()

# p_str = "P0;"+ str(p) + ";"
# ts_str = "Ts;"
# cp_rho_str = "cp_svol;"
# rkt_ideal_rho_str = "rkt_ideal_svol;"
# rkt_SRK_rho_str = "rkt_SRK_svol;"
# for i in range(len(ts)):
#     ts_str += str(ts[i]) + ";"
#     cp_rho_str += str(cp_svol[i]) + ";"
#     rkt_ideal_rho_str += str(rkt_ideal_svol[i]) + ";"
#     rkt_SRK_rho_str += str(rkt_SRK_svol[i]) + ";"

# print(p_str)
# print(ts_str)
# print(cp_rho_str)
# print(rkt_ideal_rho_str)
# print(rkt_SRK_rho_str)
#
# plt.plot(ts, cp_svol, label="WagnerPruß")
# plt.plot(ts, rkt_ideal_svol, label="IdealGas")
# plt.plot(ts, rkt_SRK_svol, label="SRK")
# plt.xlabel("Temperature, K")
# plt.ylabel("Specific Volume, m3/kg")
#
# plt.legend()
# plt.show()

print("COOLPROP")
cp_liq_sV = [x if x < 0.002 else "nan" for x in cp_svol]
cp_vap_sV = [x if x > 0.002 else "nan" for x in cp_svol]

iT = cp_liq_sV.index("nan")
cp_liq_sV = cp_liq_sV[:iT]
cp_vap_sV = cp_vap_sV[iT:]

cp_Tsat = (ts[iT] + ts[iT+1])/2
cp_liq_T = ts[:iT]
cp_vap_T = ts[iT+1:]

cp_liq_coords = to_tex2D(cp_liq_T, cp_liq_sV)
cp_vap_coords = to_tex2D(cp_vap_T, cp_vap_sV)
print("Liquid Volume")
print(cp_liq_coords)
print("Vapour Volume")
print(cp_vap_coords)
print("Tsat")
print(cp_Tsat)

print("REAKTORO - IdealGas")
rkt_ideal_liq_sV = [x if x < 0.002 else "nan" for x in rkt_ideal_svol]
rkt_ideal_vap_sV = [x if x > 0.002 else "nan" for x in rkt_ideal_svol]

iT = rkt_ideal_liq_sV.index("nan")
rkt_ideal_liq_sV = rkt_ideal_liq_sV[:iT]
rkt_ideal_vap_sV = rkt_ideal_vap_sV[iT:]

rkt_ideal_Tsat = (ts[iT] + ts[iT+1])/2
rkt_ideal_liq_T = ts[:iT]
rkt_ideal_vap_T = ts[iT+1:]

rkt_ideal_liq_coords = to_tex2D(rkt_ideal_liq_T, rkt_ideal_liq_sV)
rkt_ideal_vap_coords = to_tex2D(rkt_ideal_vap_T, rkt_ideal_vap_sV)
print("Liquid Volume")
print(rkt_ideal_liq_coords)
print("Vapour Volume")
print(rkt_ideal_vap_coords)
print("Tsat")
print(rkt_ideal_Tsat)

print("REAKTORO - SRK")
rkt_SRK_liq_sV = [x if x < 0.002 else "nan" for x in rkt_SRK_svol]
rkt_SRK_vap_sV = [x if x > 0.002 else "nan" for x in rkt_SRK_svol]

iT = rkt_SRK_liq_sV.index("nan")
rkt_SRK_liq_sV = rkt_SRK_liq_sV[:iT]
rkt_SRK_vap_sV = rkt_SRK_vap_sV[iT:]

rkt_SRK_Tsat = (ts[iT] + ts[iT+1])/2
rkt_SRK_liq_T = ts[:iT]
rkt_SRK_vap_T = ts[iT+1:]

rkt_SRK_liq_coords = to_tex2D(rkt_SRK_liq_T, rkt_SRK_liq_sV)
rkt_SRK_vap_coords = to_tex2D(rkt_SRK_vap_T, rkt_SRK_vap_sV)
print("Liquid Volume")
print(rkt_SRK_liq_coords)
print("Vapour Volume")
print(rkt_SRK_vap_coords)
print("Tsat")
print(rkt_SRK_Tsat)








