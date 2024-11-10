import numpy as np
from typing import Optional, NoReturn, Union

from .PVT import AbstractState
from .factory import engine_creation_funcs
from .properties import Properties


class Fluid:
    """
    This class is a container for the fluid's compositional information

    Attributes
    ----------
    engine: str
        the name of the property engine
    name
    components: list[str]
        the names of all components
    composition: list[float]
        the mole fractions of all components
    mixture: bool
        flag to indicate whether the fluid is a mixture or pure
    state: AbstractState
        the property engine
    properties: Properties
        the properties of the fluid
    args: tuple[any]
        the additional arguments submitted at creation
    kwargs: dict[any,any]
        the additional keyword arguments submitted at creation

    Methods
    -------
    __init__()
        initiates the

    """

    def __init__(self,
                 comps: list[str | float],
                 *args: tuple[any],
                 engine: Optional[str] = "default",
                 **kwargs: Optional[Union[dict[any, any], any]]) -> NoReturn:
        """
        Instantiates a Fluid

        Parameters
        ----------
        comps: list[str|float]
            a list of component names and their mole fractions, like ["name1", frac1, "name2", frac2, ...]
        *args: tuple[any]
            any additional arguments required for creating the fluid
        engine: Optional[str]
            the name of engine to be used for this fluid. Default is "coolprop"
        **kwargs: dict[any, any]
            any additional key word arguments for creating the fluid

        Returns
        -------
        NoReturn

        Raises
        ValueError
            The specified engine does not exist
        """

        if engine in engine_creation_funcs:
            self.engine = engine  # the calculation engine to be used for this fluid
        else:
            msg = "\nThe specified PVT engine \"{}\" is not registered. The available engines are:\n".format(engine)

            for eng in engine_creation_funcs:
                msg += " - {}\n".format(eng)

            msg += "Please check spelling or add engine to \"engines.json\""
            raise ValueError(msg)

        self.name = ""
        self.components = []
        self.composition = []

        for i in range(0, len(comps) - 1, 2):
            self.name += comps[i] + "[" + str(comps[i+1]) + "]&"
            self.components.append(comps[i])
            self.composition.append(comps[i+1])
        self.name = self.name[:-1]

        sum_compo = sum(self.composition) + 1e-6
        self.composition = [compo / sum_compo for compo in self.composition]

        self.mixture = False
        if len(self.components) > 1:
            self.mixture = True

        self.state = AbstractState(engine, self.components, self.composition, *args, **kwargs)  # this will later on be used to perform property calculations
        self.properties = Properties({"P":0})

        self.args = args
        self.kwargs = kwargs

    def update(self, InputSpec: str, Input1: float, Input2: float, *args: tuple[any], PhaseProps=False, **kwargs: dict[any]) -> NoReturn:
        """
        Updates the properties of the fluid for some state specifications

        Parameters
        ----------
        InputSpec: str
            The state variables. This should be two letter, e.g. "PH" for a pressure enthalpy calculation
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

        kwargs["PhaseProps"] = PhaseProps

        self.properties = self.state.update(InputSpec, Input1, Input2, *args, **kwargs)

    def update_composition(self, Zs: list[float], InPlace: Optional[bool] = True) -> "Fluid":
        """
        Updates the composition of the fluid

        Parameters
        ----------
        Zs: list[float]
            The new composition
        InPlace: bool
            flag to decide, whether to create a new Fluid or to update the current Fluid

        Returns
        -------
        Fluid

        Raises
        ------
        ValueError
            the new and existing composition are not of the same length
        """

        if len(Zs) != len(self.composition):
            msg = "\nThe new composition has {} components but the existing composition has {}".format(len(Zs), len(self.composition))
            raise ValueError(msg)

        if InPlace:
            self.composition = Zs

            self.state.update_composition(Zs)

            return self
        else:
            comps = []
            for i, comp in enumerate(self.components):
                comps.append(comp)
                comps.append(Zs[i])

            temp_fluid = Fluid(comps, *self.args, engine=self.engine, **self.kwargs)

            return temp_fluid  # type: ignore

    def copy(self) -> "Fluid":
        """
        Creates a deepcopy of the current fluid

        Returns
        -------
        Fluid

        """

        comps = []
        for i, comp in enumerate(self.components):
            comps.append(comp)
            comps.append(self.composition[i])

        temp_props = self.properties.copy()

        temp_fluid = Fluid(comps, *self.args, engine=self.engine, **self.kwargs)
        temp_fluid.properties = temp_props

        return temp_fluid  # type: ignore

    def phase_to_fluid(self, phase: str) -> "Fluid":
        """
        Promote a phase to a fluid

        Parameters
        ----------
        phase: str
            The phase to be promoted. Either "liq" or "vap"

        Returns
        -------
        Fluid

        Raises
        ------
        ValueError
            the phase identifier is not recognised

        """

        if phase == "liq":
            comps = self.properties.LiqProps.components
            compo = self.properties.LiqProps.composition
            props = self.properties.LiqProps.as_dict()

        elif phase == "vap":
            comps = self.properties.VapProps.components
            compo = self.properties.VapProps.composition
            props = self.properties.VapProps.as_dict()
        else:
            msg = "Phase identifier \"{}\" not recognised".format(phase)
            raise ValueError(msg)

        components = []
        for i, comp in enumerate(comps):
            components.append(comp)
            components.append(compo[i])

        temp_fluid = Fluid(components, engine=self.engine)

        del props["components"]
        del props["composition"]
        del props["exists"]

        temp_fluid.properties = Properties(props)

        return temp_fluid  # type: ignore

