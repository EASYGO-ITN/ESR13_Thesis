from GeoProp import Comp, Fluid, Partition, PropertyModel

components = [Comp.WATER, Comp.NaCl_aq, Comp.CARBONDIOXIDE]
composition = [1, 0.1, 0.02]

brine = Fluid(components=components, composition=composition)

P = 101325  # in Pa
T = 350  # in K

brine = Partition().calc(brine, P, T)
brine = PropertyModel().calc(brine, P, T)

print(brine)
