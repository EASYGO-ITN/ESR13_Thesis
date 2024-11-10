from GeoProp.Model.Fluid import Fluid
from GeoProp.Model.Databases import Comp
from GeoProp.Model.PartitionModel import Partition
from GeoProp.Model.PropertyModel import PropertyModel

import numpy as np
import matplotlib.pyplot as plt


def to_tex2D(xs, ys):

    # xys = [ "("+str(round(xs[i], 3))+","+str(round(ys[i], 3))+")" for i in range(len(xs))]
    xys = ["({:.3e},{:.3e})".format(xs[i],ys[i]) for i in range(len(xs))]
    coords = " ".join(xys)

    return coords


# Analysis of Sample No.68
# initialising the calculation parameters
n = 13
ts = np.linspace(273.2, 333.15, n)
p = 101325

# initialising the fluid
liq_components = [Comp.WATER,
                  Comp.Ca,
                  Comp.K,
                  Comp.Mg,
                  Comp.Na,
                  Comp.S,
                  Comp.Se,
                  Comp.Si,
                  Comp.Cl,
                  Comp.SO4_minus2]
liq_composition = [1e6,
                   49.2,
                   10.2,
                   32.9,
                   396,
                   240,
                   2.4,
                   13.8,
                   152,
                   749]
liq_composition = [i * 1e-6 for i in liq_composition]

# creating the liquid fluid container
fluid = Fluid(components=liq_components, composition=liq_composition)
partition = Partition()
fluid = partition.calc(fluid, 101325, 273.15)
fluid.cullComponents()

# initialising the datastores
gp_density = np.zeros(n)
gp_enthalpy = np.zeros(n)

rho_ts = np.array([277.15, 283.15, 293.15, 303.15, 313.15, 323.15, 333.15])
No68_density = [1000.78, 1000.55, 999.01, 996.4, 992.92, 988.70, 983.69]

h_ts = np.array([273.2, 278.15, 283.15, 293.15, 303.15, 313.15, 323.15, 333.15])
No68_enthalpy = np.array([0.0, 21.251, 42.361, 84.257, 125.87, 167.4, 209.02, 250.91]) - (84.257+ 125.87)/2

# calculate the properties
property = PropertyModel()

for i, t in enumerate(ts):
    props = property.calc(fluid, p, t).total.props

    gp_density[i] = props.rho
    gp_enthalpy[i] = props.h

# processing results
# gp_enthalpy -= gp_enthalpy[0]

# report results
print("___No68___;")
print("Density")
print(to_tex2D(rho_ts, No68_density ))
print("Enthalpy")
print(to_tex2D(h_ts, No68_enthalpy))

print("___GEOPROP___;")
print("Density")
print(to_tex2D(ts, gp_density))
print("Enthalpy")
print(to_tex2D(ts, gp_enthalpy))


fig, axs = plt.subplots(1, 2)

ax1 = axs[0]
ax1.plot(rho_ts-273.15, No68_density, "bo", label="No68")
ax1.plot(ts-273.15, gp_density, "b-",label="GeoProp")
ax1.set_xlabel("Temperature, degC")
ax1.set_ylabel("Density, kg/m3")
ax1.legend()

ax1 = axs[1]
ax1.plot(h_ts-273.15, No68_enthalpy, "bo",label="No69")
ax1.plot(ts-273.15, gp_enthalpy, "b-",label="GeoProp")
ax1.set_xlabel("Temperature, degC")
ax1.set_ylabel("Enthalpy, kJ/kg")
ax1.legend()

plt.tight_layout()
plt.show()
