from typing import NoReturn, Optional

from .base_component import Component
from Simulator import factory


class splitter(Component):

    """
    the splitter component

    Attributes
    ----------
    inlet: MaterialStream
        the inlet stream
    outlet: tuple[MaterialStream]
        the outlet streams
    n: int
        the number of outlet streams
    frac: list[float]
        the fractions of n - 1 outlet streams
    amount: list[float]
        the amounts of n -1 outlet streams
    stream_type = MaterialStream | HeatStream | WorkStream

    """

    def __init__(self) -> NoReturn:
        """
        instantiates the splitter component
        """

        super().__init__()

    def set_inputs(self,
                   inlet: "MaterialStream",
                   n: Optional[int | None]=None,
                   frac: Optional[list[float] | None]=None,
                   amount: Optional[list[float] | None]=None) -> NoReturn:
        """
        set the inputs for the splitter component

        Parameters
        ----------
        inlet: MaterialStream | HeatStream | WorkStream
            the inlet stream
        n: Optional[int | None]
            the number of outlet streams
        frac: Optional[list[float] | None]
            the fractions of n - 1 streams
        amount: Optional[list[float] | None]
            the amounts of n - 1 streams

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            no splitting method has been defined
        """

        self.inlet = inlet.copy()

        if n is None and frac is None and amount is None:
            msg = "No splitting method has been defined"
            raise ValueError(msg)

        self.n = n  # splitt into n even streams
        self.frac = frac  # specify the fraction of n - 1 outlet streams
        self.amount = amount  # specifiy the amount of n - 1 outlet streams

        self.stream_type = type(inlet)

    def calc(self) -> list["MaterialStream"] | list["HeatStream"] | list["WorkStream"]:
        """
        calcualte the splitter performance

        Returns
        -------
        list["MaterialStream"] | list["HeatStream"] | list["WorkStream"]

        Raises
        ------
        ValueError
            split fractions are greater than 1.0
        ValueError
            amounts are greater than parent stream amount
        """

        if self.n is not None:
            n = self.n
            ms = [self.inlet.quantity / n for i in range(n)]

        elif self.frac is not None:
            n = len(self.frac) + 1
            if sum(self.frac) > 1.0:
                msg = "\nThe split fractions specified are greater than 1.0."
                raise ValueError(msg)
            else:
                self.frac.append(1.0 - sum(self.frac))
                ms = [self.inlet.quantity * frac for frac in self.frac]

        else:
            n = len(self.amount) + 1

            if abs(self.inlet.quantity) - abs(sum(self.amount)) < 0.0:
                msg = "\nThe split amounts specified do not match the parent stream amount"
                raise ValueError(msg)
            else:
                self.amount.append(self.inlet.quantity - sum(self.amount))
                ms = [amount for amount in self.amount]

        self.outlet = [self.inlet.copy() for i in range(n)]

        for i, stream in enumerate(self.outlet):
            stream._update_quantity(ms[i])

        return self.outlet


def register() -> NoReturn:
    """
    Registers the splitter component

    Returns
    -------
    NoReturn
    """

    factory.register("splitter", splitter)