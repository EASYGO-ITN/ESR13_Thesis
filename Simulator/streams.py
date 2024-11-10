from typing import Optional, NoReturn


class MaterialStream:

    """
    The Material Stream contains information about its composition, mass rate and its properties

    Attributes
    ----------
    fluid: Fluid
        the fluid composition
    m: float
        the mass rate in kg/s
    quantity: float
        the quantity of the stream in kg/s
    properties: Properties
        the properties of the stream
    """

    def __init__(self, fluid: "Fluid", m: Optional[float]=0.0) -> NoReturn:
        """
        Instantiates a MaterialStream

        Parameters
        ----------
        fluid: Fluid
            the fluid composition
        m: float
            the mass rate in kg/s

        Returns
        -------
        NoReturn
        """

        self.fluid = fluid
        self.m = m
        self.quantity = m

        self.properties = fluid.properties

    def update(self, InputSpec: str, Input1: float, Input2: float, PhaseProps=False) -> NoReturn:
        """
        Updates the properties of the stream for some state specifications

        Parameters
        ----------
        InputSpec: str
            The state variables. This should be two letters, e.g. "PH" for a pressure enthalpy calculation
        Input1: float
            The value corresponding to state variable 1
        Input2: float
            The value corresponding to state variable 2
        *args: tuple[any]
            Any additional arguments needed by the calculation engine

        Returns
        -------
        NoReturn
        """

        self.fluid.update(InputSpec, Input1, Input2, PhaseProps=PhaseProps)

        self.properties = self.fluid.properties

    def copy(self) -> "MaterialStream":
        """
        Creates a deepcopy of the current stream

        Returns
        -------
        MaterialStream

        """

        temp_fluid = self.fluid.copy()
        temp_m = self.m * 1.0

        return MaterialStream(temp_fluid, m=temp_m)  # type: ignore

    def liquid_stream(self) -> "MaterialStream":
        """
        Returns the liquid phase to a Material Stream

        Returns
        -------
        MaterialStream
        """

        if self.fluid.properties.LiqProps.exists:

            Qliq_mass = (1 - self.properties.Q) * self.properties.LiqProps.Mr / self.properties.Mr
            temp_m = self.m * Qliq_mass

            temp_fluid = self.fluid.phase_to_fluid("liq")

            return MaterialStream(temp_fluid, m=temp_m)  # type: ignore

        else:
            temp_fluid = self.fluid.copy()

            return MaterialStream(temp_fluid, m=0.0)  # type: ignore

    def vapour_stream(self) -> "MaterialStream":
        """
        Returns the vapour phase to a Material Stream

        Returns
        -------
        MaterialStream
        """

        if self.fluid.properties.VapProps.exists:

            Qvap_mass = self.properties.Q * self.properties.VapProps.Mr / self.properties.Mr
            temp_m = self.m * Qvap_mass

            temp_fluid = self.fluid.phase_to_fluid("vap")

            return MaterialStream(temp_fluid, m=temp_m)  # type: ignore
        else:
            temp_fluid = self.fluid.copy()

            return MaterialStream(temp_fluid, m=0.0)  # type: ignore

    def _update_quantity(self, value: float) -> NoReturn:
        """
        Updates the stream's quantity and mass rate

        Parameters
        ----------
        value: float
            the new mass rate in kg/s

        Returns
        -------
        NoReturn

        """
        self.m = value
        self.quantity = value


class HeatStream:
    """
    The HeatStream contains information about the streams heat rate

    Attributes
    ----------
    W: float
        the heat rate in J/s
    quantity: float
        the quantity of the stream in J/s
    """

    def __init__(self, Q: float) -> NoReturn:
        """
        Instantiates a HeatStream

        Parameters
        ----------
        Q: float
            the heat rate in J/s

        Returns
        -------
        NoReturn
        """

        self.Q = Q
        self.quantity = Q

    def _update_quantity(self, value: float) -> NoReturn:
        """
        Updates the stream's quantity and heat rate

        Parameters
        ----------
        value: float
            the new heat rate in J/s

        Returns
        -------
        NoReturn

        """
        self.Q = value
        self.quantity = value


class WorkStream:

    """
    The WorkStream contains information about the streams work rate

    Attributes
    ----------
    W: float
        the work rate in J/s
    quantity: float
        the quantity of the stream in J/s
    """

    def __init__(self, W: float) -> NoReturn:
        """
        Instantiates a WorkStream

        Parameters
        ----------
        W: float
            the work rate in J/s

        Returns
        -------
        NoReturn
        """

        self.W = W
        self.quantity = W

    def _update_quantity(self, value: float) -> NoReturn:
        """
        Updates the stream's quantity and work rate

        Parameters
        ----------
        value: float
            the new work rate in J/s

        Returns
        -------
        NoReturn
        """

        self.W = value
        self.quantity = value

