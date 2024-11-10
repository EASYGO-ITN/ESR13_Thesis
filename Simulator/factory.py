from typing import Callable

component_creation_funcs = {}  # [str: Engine]


def register(engine_name: str, creation_func: Callable[..., "Component"]) -> None:  # type: ignore
    """
    Register a new calculation engine

    Parameters
    ----------
    engine_name: str
        name of the engine to be registered
    creation_func: Callable[..., Engine]
        function that instantiates the engine
    Returns
    -------
    None
    """

    component_creation_funcs[engine_name] = creation_func


def unregister(engine_name: str) -> None:
    """
    Unregister a calculation engine.

    Parameters
    ----------
    engine_name: str
        name of the engine to be unregistered
    Returns
    -------
    None
    """

    component_creation_funcs.pop(engine_name, None)


def create(arguments: dict[str, any]) -> Callable[..., "Component"]:  # type: ignore
    """
    Create a calculation engine given JSON data.

    Parameters
    ----------
    arguments: dict
        the arguments required for creating an engine

    Returns
    -------
    Callable
        the function for instantiating an engine

    Raises
    ------
    ValueError
        if engine type is not a registered engine

    """
    args_copy = arguments.copy()
    component_type = args_copy.pop("type")
    try:
        creator_func = component_creation_funcs[component_type]
    except KeyError:
        raise ValueError(f"unknown engine type {component_type!r}") from None
    return creator_func