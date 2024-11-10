import numpy as np
from typing import Optional, Union, NoReturn

from . import engines
from .properties import Properties


class AbstractState:
    """
    This class is for calculating the state of a fluid

    Attributes
    ----------
    state: Engine
        the fluid state
    """

    def __init__(self,
                 engine: str,
                 components: list[str],
                 composition: list[float],
                 *args:tuple[any],
                 **kwargs:dict[any, any]) -> NoReturn:

        """
        instantiates the Abstract state

        Parameters
        ----------
        engine: str
            name of the calculation engine
        components: list[str]
            list of the component names
        composition: list[float]
            list of the component mole fractions
        *args: tuple[any]
            any additional arguments
        **kwargs: dict[any, any]
            any additional keyword arguments

        Returns
        -------
        NoReturn
        """

        self.state = engines[engine](components, composition, *args, **kwargs)

    def update(self, InputSpec: str, Input1: float, Input2: float, *args: tuple[any], **kwargs: dict[any]) -> Properties:
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
        Properties
        """

        self.state.calc(InputSpec, Input1, Input2, *args, **kwargs)

        return self.state.state_properties

    def update_composition(self, composition: list[float]) -> NoReturn:
        """
        Updates the component mole fractions in the underlying state

        Parameters
        ----------
        composition: list[float]
            the new mole fractions of all components

        Returns
        -------
        NoReturn

        """
        self.state.update_composition(composition)


def PropSI(prop: str,
           x_str: str,
           x: Union[float, list[float], np.float64, np.array],
           y_str: str,
           y: Union[float, list[float], np.float64, np.array],
           fluid: "Fluid",
           profile: Optional[bool]=False) -> Union[float, list[float], np.float64, np.array]:

    """
    This is a wrapper around the Abstract state to calculate specific properties

    Parameters
    ----------
    prop: str
        the property to be evaluated, e.g. "D" for density
    x_str: str
        the state variable 1. This should be one letter, e.g. "P" for pressure
    x: Union[float, list[float], np.float64, np.array]
        the value(s) of state variable 1
    y_str: str
        the state variable 1. This should be one letter, e.g. "H" for specific enthalpy
    y: Union[float, list[float], np.float64, np.array]
        the value(s) of state variable 2
    fluid: Fluid
        the fluid to be evaluated
    profile: Optional[bool]
        whether the properties should be evaluated as a profile or as combinations

    Returns
    -------
    Union[float, list[float], np.float64, np.array]

    Raises
    ------
    ValueError
        state variable inputs are of unrecognised type
    """

    temp_fluid = fluid.copy()

    xy_str = x_str + y_str

    # convert a scalar input to a list
    if type(x) in [float, int, np.float64]:
        x_ = np.array([x])
    elif type(x) in [np.array]:
        x_ = x
    elif type(x) in [list]:
        x_ = np.array(x)
    else:
        raise ValueError("unrecognised type")

    if type(y) in [float, int, np.float64]:
        y_ = np.array([y])
    elif type(y) in [np.array]:
        y_ = y
    elif type(y) in [list]:
        y_ = np.array(y)
    else:
        raise ValueError("unrecognised type")

    if x_.size == y_.size and profile is True:

        z = np.zeros(x_.size)
        for i, x in enumerate(x_):
            temp_fluid.update(xy_str, x, y_[i])
            z[i] = temp_fluid.properties[prop]

    elif x_.size == 1 and y_.size == 1:

        temp_fluid.update(xy_str, x, y)
        z = temp_fluid.properties[prop]

    else:
        z = np.zeros((x_.size, y_.size))
        for i, x in enumerate(x_):
            for j, y in enumerate(y_):
                temp_fluid.update(xy_str, x, y)
                z[i, j] = temp_fluid.properties[prop]

    return z

