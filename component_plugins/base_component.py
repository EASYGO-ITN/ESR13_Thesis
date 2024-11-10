from typing import NoReturn


class Component:
    """
    The base component class

    Attributes
    ----------
    inlet: list[any]
    outlet: list[any]
    """

    def __init__(self) -> NoReturn:
        """
        initiates the base component

        Returns
        -------
        NoReturn
        """

        self.inlet = []
        self.outlet = []

    def calc(self) -> list[any]:
        """
        calculates a component

        Returns
        -------
        list[any]

        """

        self.outlet = self.inlet.copy()

        return self.inlet.copy()

    def update_inlet_rate(self, m):

        pass

    def calc_cost(self):

        return 0