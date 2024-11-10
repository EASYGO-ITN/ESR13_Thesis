import CoolProp as cp
import matplotlib.pyplot as plt
import tikzplotlib

# fluids = ["1-Butene",
#           "Acetone",
#           "Air",
#           "Ammonia",
#           "Argon",
#           "Benzene",
#           "CarbonDioxide",
#           "CarbonMonoxide",
#           "CarbonylSulfide",
#           "CycloHexane",
#           "CycloPropane",
#           "Cyclopentane",
#           "D4",
#           "D5",
#           "D6",
#           "Deuterium",
#           "Dichloroethane",
#           "DiethylEther",
#           "DimethylCarbonate",
#           "DimethylEther",
#           "Ethane",
#           "Ethanol",
#           "EthylBenzene",
#           "Ethylene",
#           "EthyleneOxide",
#           "Fluorine",
#           "HFE143m",
#           "HeavyWater",
#           "Helium",
#           "Hydrogen",
#           "HydrogenChloride",
#           "HydrogenSulfide",
#           "IsoButane",
#           "IsoButene",
#           "Isohexane",
#           "Isopentane",
#           "Krypton",
#           "MD2M",
#           "MD3M",
#           "MD4M",
#           "MDM",
#           "MM",
#           "Methane",
#           "Methanol",
#           "MethylLinoleate",
#           "MethylLinolenate",
#           "MethylOleate",
#           "MethylPalmitate",
#           "MethylStearate",
#           "Neon",
#           "Neopentane",
#           "Nitrogen",
#           "NitrousOxide",
#           "Novec649",
#           "OrthoDeuterium",
#           "OrthoHydrogen",
#           "Oxygen",
#           "ParaDeuterium",
#           "ParaHydrogen",
#           "Propylene",
#           "Propyne",
#           "R11",
#           "R113",
#           "R114",
#           "R115",
#           "R116",
#           "R12",
#           "R123",
#           "R1233zd(E)",
#           "R1234yf",
#           "R1234ze(E)",
#           "R1234ze(Z)",
#           "R124",
#           "R1243zf",
#           "R125",
#           "R13",
#           "R134a",
#           "R13I1",
#           "R14",
#           "R141b",
#           "R142b",
#           "R143a",
#           "R152A",
#           "R161",
#           "R21",
#           "R218",
#           "R22",
#           "R227EA",
#           "R23",
#           "R236EA",
#           "R236FA",
#           "R245ca",
#           "R245fa",
#           "R32",
#           "R365MFC",
#           "R40",
#           "R404A",
#           "R407C",
#           "R41",
#           "R410A",
#           "R507A",
#           "RC318",
#           "SES36",
#           "SulfurDioxide",
#           "SulfurHexafluoride",
#           "Toluene",
#           "Water",
#           "Xenon",
#           "cis-2-Butene",
#           "m-Xylene",
#           "n-Butane",
#           "n-Decane",
#           "n-Dodecane",
#           "n-Heptane",
#           "n-Hexane",
#           "n-Nonane",
#           "n-Octane",
#           "n-Pentane",
#           "n-Propane",
#           "n-Undecane",
#           "o-Xylene",
#           "p-Xylene",
#           "trans-2-Butene"]
#
# p_crits = []
# t_crits = []
#
# for fluid in fluids:
#     AS = cp.AbstractState("?", fluid)
#     p_crits.append(AS.p_critical() * 1e-5)
#     t_crits.append(AS.T_critical())

hydrocarbons = ["1-Butene",
                "Benzene",
                "CycloHexane",
                "CycloPropane",
                "Cyclopentane",
                "Ethane",
                "EthylBenzene",
                "Ethylene",
                "EthyleneOxide",
                "IsoButane",
                "IsoButene",
                "Isohexane",
                "Isopentane",
                "Methane",
                "Neopentane",
                "Propylene",
                "Propyne",
                "Toluene",
                "cis-2-Butene",
                "m-Xylene",
                "n-Butane",
                "n-Decane",
                "n-Dodecane",
                "n-Heptane",
                "n-Hexane",
                "n-Nonane",
                "n-Octane",
                "n-Pentane",
                "n-Propane",
                "n-Undecane",
                "o-Xylene",
                "p-Xylene",
                "trans-2-Butene"]
h_p_crits = []
h_t_crits = []
for hydrocarbon in hydrocarbons:
    AS = cp.AbstractState("?", hydrocarbon)
    h_p_crits.append(AS.p_critical() * 1e-5)
    h_t_crits.append(AS.T_critical())

refrigerants = ["R11",
                "R113",
                "R114",
                "R115",
                "R116",
                "R12",
                "R123",
                "R1233zd(E)",
                "R1234yf",
                "R1234ze(E)",
                "R1234ze(Z)",
                "R124",
                "R1243zf",
                "R125",
                "R13",
                "R134a",
                "R13I1",
                "R14",
                "R141b",
                "R142b",
                "R143a",
                "R152A",
                "R161",
                "R21",
                "R218",
                "R22",
                "R227EA",
                "R23",
                "R236EA",
                "R236FA",
                "R245ca",
                "R245fa",
                "R32",
                "R365MFC",
                "R40",
                "R404A",
                "R407C",
                "R41",
                "R410A",
                "R507A",
                "RC318",
                "SES36"]
r_p_crits = []
r_t_crits = []
for refrigerant in refrigerants:
    AS = cp.AbstractState("?", refrigerant)
    r_p_crits.append(AS.p_critical() * 1e-5)
    r_t_crits.append(AS.T_critical())

silicones = ["D4",
             "D5",
             "D6",
             "MD2M",
             "MD3M",
             "MD4M",
             "MDM",
             "MM"]
s_p_crits = []
s_t_crits = []
for silicone in silicones:
    AS = cp.AbstractState("?", silicone)
    s_p_crits.append(AS.p_critical() * 1e-5)
    s_t_crits.append(AS.T_critical())

organics = ["Acetone",
            "Dichloroethane",
            "DiethylEther",
            "DimethylCarbonate",
            "DimethylEther",
            "Ethanol",
            "EthyleneOxide",
            "Methanol",
            "MethylLinoleate",
            "MethylLinolenate",
            "MethylOleate",
            "MethylPalmitate",
            "MethylStearate"]
o_p_crits = []
o_t_crits = []
for organic in organics:
    AS = cp.AbstractState("?", organic)
    o_p_crits.append(AS.p_critical() * 1e-5)
    o_t_crits.append(AS.T_critical())

inorganics = ["Ammonia",
              "CarbonDioxide",
              "CarbonMonoxide",
              "SulfurDioxide",
              "SulfurHexafluoride",
              "Water"]
i_p_crits = []
i_t_crits = []
for inorganic in inorganics:
    AS = cp.AbstractState("?", inorganic)
    i_p_crits.append(AS.p_critical() * 1e-5)
    i_t_crits.append(AS.T_critical())

plt.plot(h_t_crits, h_p_crits, "o", label="Hydrocarbons")
plt.plot(r_t_crits, r_p_crits, "o", label="Refrigerants")
plt.plot(s_t_crits, s_p_crits, "o", label="Silicones")
plt.plot(o_t_crits, o_p_crits, "o", label="Organics")
plt.plot(i_t_crits, i_p_crits, "o", label="Inorganics")

notables = ["CarbonDioxide",
            "n-Propane",
            "Isobutane",
            "n-Butane",
            "Isopentane",
            "n-Pentane",
            "Ammonia",
           # "CycloHexane",
           # "CycloPropane",
           # "Cyclopentane",
           # "Water",
           # "n-Butane",
           # "n-Pentane",
           # "n-Propane",
            "R32", "R134a", "R245fa"]
n_p_crits = []
n_t_crits = []
for notable in notables:
    AS = cp.AbstractState("?", notable)
    n_p_crits.append(AS.p_critical() * 1e-5)
    n_t_crits.append(AS.T_critical())
plt.plot(n_t_crits, n_p_crits, "k*", label="Notables", markersize="10")

for notable in notables:
    if notable not in ["n-Propane", "R227ea"]:
        AS = cp.AbstractState("?", notable)
        plt.annotate(notable, xy=(AS.T_critical(), AS.p_critical()*1e-5), xytext=(AS.T_critical()+5, AS.p_critical()*1e-5*1.1), arrowprops=dict(arrowstyle="->", color="0.5",
                                    shrinkA=5, shrinkB=5,
                                    patchA=None, patchB=None,
                                    connectionstyle="arc,angleA=-90,angleB=0,armA=0,armB=40,rad=0",
                                    ), bbox = dict(boxstyle="round", fc="0.8"))
    else:
        AS = cp.AbstractState("?", notable)
        plt.annotate(notable, xy=(AS.T_critical(), AS.p_critical() * 1e-5),
                     xytext=(AS.T_critical() - 5, AS.p_critical() * 1e-5 * 1.1),
                     arrowprops=dict(arrowstyle="->", color="0.5",
                                     shrinkA=5, shrinkB=5,
                                     patchA=None, patchB=None,
                                     connectionstyle="arc,angleA=-90,angleB=180,armA=0,armB=40,rad=0",
                                     ), ha="right", bbox = dict(boxstyle="round", fc="0.8"))
 # bbox = dict(boxstyle="round", fc="0.8")

geo_ts = [100 + 273.15, 300 + 273.15]
geo_pmins = [1, 1]
geo_pmaxs = [1000, 1000]



plt.fill_between(geo_ts, geo_pmins, geo_pmaxs, color="red", alpha=0.3)

plt.yscale("log")
plt.ylim([10, 100])
plt.legend()

tikzplotlib.save("CriticalProperties.tex")

plt.show()


