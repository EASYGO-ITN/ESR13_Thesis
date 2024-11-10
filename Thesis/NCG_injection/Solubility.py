from FluidProperties.fluid import Fluid

geofluid = Fluid(["water", 0.98, "carbondioxide", 0.02])
geofluid.update("TQ", 200+273, 0.001, PhaseProps=True)

geofluid = Fluid(["water", 0.98, "carbondioxide", 0.02])
geofluid.update("PT", 20e5, 200+273, PhaseProps=True)

print()
