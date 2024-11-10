from typing import NoReturn


class Engine:
    """
    this class is the blueprint for all calculation engines

    Attributes
    ----------
    properties: list[str]
        the properties this calculation engine can calculate
    calc_input_pairs: list[str]
        the supported state calculation input pairs
    """

    properties = ["H", "S", "P", "T", "D", "V", "Q", "MU"]  # list of all supported properties

    calc_inputs = ["P", "T", "H", "S", "Q", "D"]

    def __init__(self, components: list[str], composition: list[float]) -> NoReturn:
        """
        This function should create the equivalent of CoolProp's Abstract State

        Parameters
        ----------
        components: list[str]
            list of component names
        composition: list[str]
            list of component mole fractions

        Returns
        -------
        NoReturn
        """
        pass

    def calc(self, InputSpec: str, Input1: float, Input2: float, *args: tuple[any], **kwargs: dict[any]) -> NoReturn:
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

        Returns
        -------
        NoReturn
        """
        print("calculating something")

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
        pass
