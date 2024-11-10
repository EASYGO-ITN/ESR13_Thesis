from typing import NoReturn

from .base_engine import Engine

from FluidProperties.properties import Properties
from FluidProperties import factory, Tref, Pref

import CoolProp as cp


class CoolPropEngine(Engine):
    """
    The GeoProp Calculation Engine

    Attributes
    ----------
    properties: list[str]
        the properties this calculation engine can calculate
    calc_input_pairs: list[str]
        the supported state calculation input pairs
    components: list[str]
        the component names
    composition: list[float]
        the component mole fractions
    comps: str
        composition in the CoolProp format
    state: cp.AbstractState
        the CoolProp State to be used to evaluate the fluid properties
    mixtureFlag: bool
        flag to indicate whether the fluid is a mixture or pure
    properties_initialised: bool
        flag to indicate whether the properties have been initialised
    state_properties: Properties
        the state properties
    """

    # TODO implement something to revert to a pure fluid if other components are negligible

    properties = ["H", "S", "P", "T", "D", "V", "Q", "MU", "Mr", "LiqProps", "VapProps"]  # list of all supported properties

    calc_input_pairs = ["PT", "TP", "PH", "HP", "PS", "SP", "PQ", "QP", "TQ", "QT"]

    def __init__(self, components: list[str], composition: list[float]) -> NoReturn:

        """
        This function should create the equivalent of CoolProp's Abstract State

        Parameters
        ----------
        components: list[str]
            list of component names
        composition: list[float]
            list of component mole fractions

        Returns
        -------
        NoReturn
        """

        super().__init__(components, composition)

        comps = ""
        for comp in components:
            comps += comp + "&"
        comps = comps[:-1]

        self.components = components
        self.composition = composition
        self.comps = comps

        self.state = cp.AbstractState("?", comps)

        self.mixtureFlag = (len(components) > 1)

        if self.mixtureFlag:
            self.state.set_mole_fractions(composition)

        self.properties_initialised = False
        self.state_properties = Properties({"P": 0.0})

    def __init_props(self) -> NoReturn:
        """
        Initialises the properties at the reference conditions

        Returns
        -------
        NoReturn
        """
        self.state.update(cp.PT_INPUTS, Pref, Tref)
        self.h0 = self.state.hmass()
        self.s0 = self.state.smass()

        self.properties_initialised = True

    def calc(self, InputSpec: str, Input1: float, Input2: float, *args: tuple[any], **kwargs:dict[any]) -> NoReturn:
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

        Raises
        ------
        ValueError
            The combination of state variables is not supported
        """

        if not self.properties_initialised:
            self.__init_props()

        if InputSpec not in self.calc_input_pairs:
            msg = "\nThe input specification \"{}\" is not supported".format(InputSpec)
            raise ValueError(msg)

        match InputSpec:

            case "PT":
                self.__calc_PT(Input1, Input2)

            case "TP":
                self.__calc_PT(Input2, Input1)

            case "PH":
                self.__calc_PH(Input1, Input2)

            case "HP":
                self.__calc_PH(Input2, Input1)

            case "PS":
                self.__calc_PS(Input1, Input2)

            case "SP":
                self.__calc_PS(Input2, Input1)

            case "PQ":
                self.__calc_PQ(Input1, Input2)

            case "QP":
                self.__calc_PQ(Input2, Input1)

            case "TQ":
                self.__calc_TQ(Input1, Input2)

            case "QT":
                self.__calc_TQ(Input2, Input1)

        self.state_properties = self.__get_properties(kwargs["PhaseProps"])

    def __calc_PT(self, p: float, T: float) -> NoReturn:
        """
        Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        p: float
            Pressure in Pa
        T: float
            Temperature in K

        Returns
        -------
        NoReturn
        """

        self.state.update(cp.PT_INPUTS, p, T)

    def __calc_PH(self, p: float, H: float) -> NoReturn:
        """
        Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        p: float
            Pressure in Pa
        H: float
            Specific enthalpy in J/kg relative to the reference temperature, Tref, and pressure, Pref

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            PH calculations are not yet supported for mixtures
        """

        if self.mixtureFlag:
            msg = "\nThe PH or HP calculation mode has not yet been implemtented for mixtures"
            raise ValueError(msg)

        self.state.update(cp.HmassP_INPUTS, H + self.h0, p)

    def __calc_PS(self, p: float, S: float) -> NoReturn:
        """
        Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        p: float
            Pressure in Pa
        S: float
            Specific Entropy in J/kg/K relative to the reference temperature, Tref, and pressure, Pref

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            PS calculations are not yet supported for mixtures
        """

        if self.mixtureFlag:
            msg = "\nThe PS or SP calculation mode has not yet been implemtented for mixtures"
            raise ValueError(msg)

        self.state.update(cp.PSmass_INPUTS, p, S + self.s0)

    def __calc_PQ(self, p: float, Q: float) -> NoReturn:
        """
        Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        p: float
            Pressure in Pa
        Q: float
            Vapour Quality

        Returns
        -------
        NoReturn
        """

        if self.mixtureFlag:
            self.state.update(cp.PQ_INPUTS, p, Q)
        else:
            p_crit = self.state.p_critical()
            T_crit = self.state.T_critical()
            if p > p_crit:
                self.state.update(cp.PT_INPUTS, p, T_crit)
            else:
                self.state.update(cp.PQ_INPUTS, p, Q)

    def __calc_TQ(self, T: float, Q: float) -> NoReturn:
        """
                Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        T: float
            Temperature in K
        Q: float
            Vapour Quality

        Returns
        -------
        NoReturn
        """

        if self.mixtureFlag:
            self.state.update(cp.QT_INPUTS, Q, T)
        else:
            p_crit = self.state.p_critical()
            T_crit = self.state.T_critical()
            if T > T_crit:
                self.state.update(cp.PT_INPUTS, T, p_crit)
            else:
                self.state.update(cp.QT_INPUTS, Q, T)

    def __get_LiqProps(self):

        try:
            liquid = cp.AbstractState("?", self.comps)

            liquid.set_mole_fractions(self.state.mole_fractions_liquid())

            liquid.update(cp.PT_INPUTS, Pref, Tref)
        except:

            components = self.components
            composition = self.state.mole_fractions_liquid()
            comps = ""
            compo = []

            for i, comp in enumerate(components):
                if composition[i] > 1e-3:
                    comps += comp + "&"
                    compo.append(composition[i])
            comps = comps[:-1]
            corr = 1 / sum(compo)
            compo = [x * corr for x in compo]

            liquid = cp.AbstractState("?", comps)

            if len(compo) > 1:
                liquid.set_mole_fractions(compo)

            liquid.update(cp.PT_INPUTS, Pref, Tref)

        h0 = liquid.hmass()
        s0 = liquid.smass()

        p = self.state.p() * 1.0
        T = self.state.T() * 1.0
        try:
            liquid.update(cp.QT_INPUTS, 0.0, T)
            # liquid.update(cp.PQ_INPUTS, p, 0.0)  # I changed it to TQ because it was too sensitive for PQ
        except:
            liquid.update(cp.PT_INPUTS, p, T)

        if abs(T - liquid.T()) / T > 0.01:
            liquid.update(cp.PT_INPUTS, p, T)

        components = [comp for comp in self.components]

        liq_props = {"composition": self.state.mole_fractions_liquid(),
                     "components": components,
                     "T": liquid.T(),
                     "P": liquid.p(),
                     "H": liquid.hmass() - h0,
                     "S": liquid.smass() - s0,
                     "D": liquid.rhomass(),
                     "V": 1 / liquid.rhomass(),
                     "Mr": liquid.molar_mass(),
                     "Q": 0.0,
                     "exists": True}

        return Properties(liq_props)

    def __get_VapProps(self):

        try:
            vapour = cp.AbstractState("?", self.comps)
            vapour.set_mole_fractions(self.state.mole_fractions_vapor())

            vapour.update(cp.PT_INPUTS, Pref, Tref)

        except:
            components = self.components
            composition = self.state.mole_fractions_vapor()
            comps = ""
            compo = []

            for i, comp in enumerate(components):
                if composition[i] > 1e-4:
                    comps += comp + "&"
                    compo.append(composition[i])
            comps = comps[:-1]
            corr = 1 / sum(compo)
            compo = [x * corr for x in compo]

            vapour = cp.AbstractState("?", comps)

            if len(compo) > 1:
                vapour.set_mole_fractions(compo)

            vapour.update(cp.PT_INPUTS, Pref, Tref)

        h0 = vapour.hmass()
        s0 = vapour.smass()

        p = self.state.p() * 1.0
        T = self.state.T() * 1.0
        try:
            vapour.update(cp.PQ_INPUTS, p, 1.0)
        except:
            vapour.update(cp.PT_INPUTS, p, T)

        if abs(T - vapour.T()) / T > 0.01:
            vapour.update(cp.PT_INPUTS, p, T)

        components = [comp for comp in self.components]

        vap_props = {"composition": self.state.mole_fractions_vapor(),
                     "components": components,
                     "T": vapour.T(),
                     "P": vapour.p(),
                     "H": vapour.hmass() - h0,
                     "S": vapour.smass() - s0,
                     "D": vapour.rhomass(),
                     "V": 1 / vapour.rhomass(),
                     "Mr": vapour.molar_mass(),
                     "Q": 1.0,
                     "exists": True}

        return Properties(vap_props)

    def __get_properties(self, PhaseProps) -> Properties:
        """
        Helper function to retrieve the fluid properties

        Returns
        -------
        Properties

        Raises
        ValueError
            calculated phase is not recognised
        """

        props = {}
        for prop in self.properties:

            match prop:
                case "P":
                    props["P"] = self.state.p()

                case "T":
                    props["T"] = self.state.T()

                case "H":
                    props["H"] = self.state.hmass() - self.h0

                case "S":
                    props["S"] = self.state.smass() - self.s0

                case "D":
                    props["D"] = self.state.rhomass()

                case "V":
                    props["V"] = 1 / self.state.rhomass()

                case "Q":
                    phase = self.state.phase()

                    def check_Q(Q_tar):

                        if self.mixtureFlag:
                            z = self.state.get_mole_fractions()
                            x = self.state.mole_fractions_liquid()
                            y = self.state.mole_fractions_vapor()

                            Q = (z[0] - x[0]) / (y[0] - x[0])

                            rho = self.state.rhomass()
                            if rho < 100:
                               Q = 1.0
                            elif rho > 500:
                                Q = 0.0

                            if abs(Q - Q_tar) > 0.01:
                                props["Q"] = Q
                        else:
                            pass

                    if phase in [cp.iphase_twophase]:
                        props["Q"] = self.state.Q()

                    elif phase in [cp.iphase_supercritical_liquid, cp.iphase_liquid]:
                        props["Q"] = 0.0

                        check_Q(0.0)

                    elif phase in [cp.iphase_supercritical, cp.iphase_critical_point, cp.iphase_supercritical_gas, cp.iphase_gas]:
                        props["Q"] = 1.0

                        check_Q(1.0)

                    else:
                        msg = "\nCalculated phase type not recognised"
                        raise ValueError(msg)

                case "MU":
                    try:
                        props["MU"] = self.state.viscosity()
                    except:
                        props["MU"] = None

                case "Mr":
                    props["Mr"] = self.state.molar_mass()

                case "LiqProps":

                    if PhaseProps and "LiqProps" not in props:
                        props["LiqProps"] = self.__get_LiqProps()
                    else:
                        props["LiqProps"] = Properties({"exists": False})

                case "VapProps":

                    if PhaseProps and "VapProps" not in props:
                        props["VapProps"] = self.__get_VapProps()
                    else:
                        props["VapProps"] = Properties({"exists": False})

        return Properties(props)  # type: ignore


def register() -> NoReturn:
    """
    Registers the CoolProp property calculation engine

    Returns
    -------
    NoReturn
    """
    factory.register("coolprop", CoolPropEngine)