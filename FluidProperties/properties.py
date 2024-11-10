from typing import NoReturn


class Properties:
    """
    This class contains the properties of a given fluid and its sub-phases (i.e. liquid, vapour, solid)
    """

    def __init__(self, props_dict: dict[str, float]) -> NoReturn:
        """
        initiates the Properties from a dictionary

        Parameters
        ----------
        props_dict: dict[str, float]
            dictionary of properties

        Returns
        -------
        NoReturn
        """

        # creates a variable for each of the items in props
        vars = set(props_dict)

        # assigns the value to each property
        for var in vars:
            setattr(self, var, props_dict[var])

    def __getitem__(self, item: str) -> float:
        """
        Allows the property to be retrieved by either "Properties.xzy" or "Properties["xyz"]

        Parameters
        ----------
        item: str
            name of item to be retrieved

        Returns
        -------
        float
        """

        item = "" + item
        return getattr(self, item)

    def copy(self) -> "Properties":
        """
        copies the Properties object

        Returns
        -------
        "Properties"
        """

        return Properties(self.__dict__)  # type: ignore

    def as_dict(self) -> dict[str, float]:
        """
        converts the Properties object to a dictionary

        Returns
        -------
        dict[str, float]

        """

        return {item: self.__dict__[item] for item in self.__dict__}
