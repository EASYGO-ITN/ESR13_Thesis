from typing import NoReturn, Optional
from .base_component import Component
from Simulator import factory
from FluidProperties import Tref


class separator(Component):

    """
    the separator component

    Attributes
    ----------
    inlet: MaterialStream
        the inlet stream
    outlet: MaterialStream
        the outlet stream
    input_spec: str
        the state variables for the separation
    input_1: float
        the value of state variable 1
    input_2: float
        the value of state variable 2
    """


    def __init__(self) -> NoReturn:
        """
        instantiates the separator component
        """
        super().__init__()

    def set_inputs(self,
                   inlet_stream: "MaterialStream",
                   InputSpec: Optional[str | None] =None,
                   Input1: Optional[float | None]=None,
                   Input2: Optional[float | None]=None) -> NoReturn:
        """
        set the inputs for the separator calculation

        Parameters
        ----------
        inlet_stream: MaterialStream
            the inlet stream
        InputSpec: str
            The state variables. This should be two letters, e.g. "PH" for a pressure enthalpy calculation
        Input1: float
            The value corresponding to state variable 1
        Input2: float
            The value corresponding to state variable 2

        Returns
        -------

        """

        self.inlet = inlet_stream.copy()

        if InputSpec is None or Input1 is None or Input2 is None:
                InputSpec = None

        self.input_spec = InputSpec
        self.input_1 = Input1
        self.input_2 = Input2

    def calc(self) -> tuple["MaterialStream", "MaterialStream"]:
        """
        calculate the separator performance

        Returns
        -------
        tuple["MaterialStream", "MaterialStream"]

        """

        temp_stream = self.inlet.copy()

        # re-equilibrate the fluid if calculation specs have been defined
        if self.input_spec is not None:
            temp_stream.update(self.input_spec, self.input_1, self.input_2, PhaseProps=True)
        else:
            temp_stream.update("PH", self.inlet.properties.P, self.inlet.properties.H, PhaseProps=True)

        liquid_stream = temp_stream.liquid_stream()
        vapour_stream = temp_stream.vapour_stream()

        self.outlet = [liquid_stream, vapour_stream]

        return liquid_stream.copy(), vapour_stream.copy()

    def calc_exergy_balance(self):

        self.Ein = self.inlet.m * (self.inlet.properties.H - Tref * self.inlet.properties.S)

        self.Eout = 0
        for i, stream in enumerate(self.outlet):
            self.Eout += stream.m * (stream.properties.H - Tref * stream.properties.S)

        self.Eloss = self.Ein - self.Eout

        if abs(self.Eloss) < 1e-4:
            self.Eloss = 0

        # print(self.Ein, self.Eout, self.Eloss)

    def update_inlet_rate(self, m):

        alpha = self.outlet[0].m / self.inlet.m

        self.inlet._update_quantity(m)

        self.outlet[0]._update_quantity(m*alpha)
        self.outlet[1]._update_quantity(m*(1-alpha))

    def calc_cost(self):

        cost = 0
        self.cost = cost

        return cost


def register() -> NoReturn:
    """
    Registers the separator component

    Returns
    -------
    NoReturn
    """
    factory.register("separator", separator)