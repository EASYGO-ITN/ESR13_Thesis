from FluidProperties.fluid import Fluid

fluid = Fluid(["water", 1])
fluid.update("PT", P, T)

props = fluid.properties
H, S, D = props.H, props.S, props.D