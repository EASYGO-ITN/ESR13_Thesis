from scipy.optimize import root_scalar
import numpy as np
from typing import Optional, Union, NoReturn

from .base_engine import Engine
from .coolprop_engine import CoolPropEngine

from FluidProperties.properties import Properties
from FluidProperties import factory, Tref, Pref

from GeoProp.Model.Databases import Comp as GeoComp
from GeoProp.Model.Fluid import Fluid as GeoFluid
from GeoProp.Model.PartitionModel import PartitionModelOptions  #, Partition
from GeoProp.Model.PropertyModel import PropertyModelOptions  #, PropertyModel
from GeoProp.Model.State import State


class GeoPropEngine(Engine):

    """
    The GeoProp Calculation Engine

    Attributes
    ----------
    properties: list[str]
        the properties this calculation engine can calculate
    calc_input_pairs: list[str]
        the supported state calculation input pairs
    NameToComp: dict[str, GeoComp]
        map to translate from component name to GeoProp component
    CompToName: dict[GeoComp, str]
        map to translate from GeoProp component to component name
    Tmin: float
        the minimum supported temperature in K
    Tmax: float
        the maximum supported temperature in K
    Pminmin: float
        the mimumum supported pressure in Pa
    Pmin: float
        the minimum pressure supported by GeoProp in Pa
    Pmax: float
        the maximum supported pressure in Pa
    fluid: GeoFLuid
        the GeoProp Fluid
    components: list [str]
        the component names
    GeoProp_components: list[GeoComp]
        the GeoProp components
    composition: list[float]
        the component mole fractions
    part_opts: PartitionModelOptions
        the partition model options to be used
    prop_opts: PropertyModelOptions
        the property model options to be used
    state: State
        the GeoProp State to be used to evaluate the fluid properties
    mixtureFlag: bool
        flag indicating whether the fluid is a mixture or pure
    cp_state_pure: CoolPropEngine
        the CoolProp engine to be used to evaluate pure fluids
    cp_state_mixture:
        the CoolProp engine to be used to evaluate mixture fluids, e.g. at low pressures
    properties_initialised: bool
        flag to indicate whether the properties have been initialised
    state_properties: Properties
        the state properties
    """

    properties = ["H", "S", "P", "T", "D", "V", "Q", "Mr", "LiqProps", "VapProps"]  # list of all supported properties

    calc_input_pairs = ["PT", "TP", "PH", "HP", "PS", "SP", "PQ", "QP", "TQ", "QT"]

    NameToComp = {"water": GeoComp.WATER,
                  "WATER": GeoComp.WATER,
                  "steam": GeoComp.STEAM,
                  "STEAM": GeoComp.STEAM,
                  "CO2": GeoComp.CARBONDIOXIDE,
                  "carbondioxide": GeoComp.CARBONDIOXIDE,
                  "CarbonDioxide": GeoComp.CARBONDIOXIDE,
                  "CARBONDIOXIDE": GeoComp.CARBONDIOXIDE,
                  "CO2(aq)": GeoComp.CO2_aq,
                  "CO2(a)": GeoComp.CO2_aq,
                  "NaCl": GeoComp.Halite,
                  "Na+": GeoComp.Na_plus,
                  "Cl-": GeoComp.Cl_minus,
                  "K+": GeoComp.K_plus,
                  "Mg+2": GeoComp.Mg_plus2,
                  "Ca+2": GeoComp.Ca_plus2,
                  "SO4-2": GeoComp.SO4_minus2
                  }

    CompToName = {GeoComp.WATER: "water",
                  GeoComp.STEAM: "steam",
                  GeoComp.CARBONDIOXIDE: "carbondioxide",
                  GeoComp.CO2_aq: "CO2(aq)",
                  GeoComp.Na_plus: "Na+",
                  GeoComp.Cl_minus: "Cl-",
                  GeoComp.K_plus: "K+",
                  GeoComp.Mg_plus2: "Mg+2",
                  GeoComp.Ca_plus2: "Ca+2",
                  GeoComp.SO4_minus2: "SO4-2"}

    Tmin = 12 + 273.15
    Tmax = 300 + 273.15

    Pminmin = 5e3
    Pmin = 1e5
    Pmax = 200e5

    def __init__(self,
                 components: list[str],
                 composition: list[float],
                 *args: tuple[any],
                 **kwargs: dict[any, any]) -> NoReturn:
        """
        This function should create the equivalent of CoolProp's Abstract State

        Parameters
        ----------
        components: list[str]
            list of component names
        composition: list[flaot]
            list of component mole fractions
        *args: list[any]
            any additional arguments
        **kwargs: dict[any]
            any additional keyword arguments

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            a component is not recognised
        ValueError
            the fluid is pure, but not either water or carbon dioxide
        """

        super().__init__(components, composition)

        comps = [i for i in components]
        for i, comp in enumerate(components):
            if comp in self.NameToComp:
                comps[i] = self.NameToComp[comp]
            else:
                msg = "The component {} is not recognised".format(comp)
                raise ValueError(msg)

        self.fluid = GeoFluid(components=comps, composition=composition, CompInMole=True)
        self.components = components
        self.GeoProp_components = comps
        self.composition = composition

        self.part_opts = None
        self.prop_opts = None

        self.state = State()
        self.set_calc_options(part_opts="default", prop_opts="default")

        self.mixtureFlag = (len(composition) > 1)
        if not self.mixtureFlag:
            if components[0] in ["water", "carbondioxide"]:
                self.cp_state_pure = CoolPropEngine(components, composition)
            else:
                msg = "\nThe GeoProp engine only permits pure fluids of either \"water\" or \"carbondioxide\". " \
                      "Specified component is {}.".format(components[0])
                raise ValueError(msg)
        else:
            temp_components = ["water", "carbondioxide"]
            temp_composition = [0.0, 0.0]
            if "water" in components:
                temp_composition[0] += composition[components.index("water")]

            if "steam" in components:
                temp_composition[0] += composition[components.index("steam")]

            if "carbondioxide" in components:
                temp_composition[1] += composition[components.index("carbondioxide")]

            if "CO2(aq)" in components:
                temp_composition[1] += composition[components.index("CO2(aq)")]

            corr = sum(temp_composition)
            temp_composition[0] /= corr
            temp_composition[1] /= corr

            # check if the fluid is close to being pure
            if temp_composition[0] > 0.999:
                self.cp_state_pure = CoolPropEngine([temp_components[0]], [temp_composition[0]])
                self.mixtureFlag = False
            elif temp_composition[1] > 0.999:
                self.cp_state_pure = CoolPropEngine([temp_components[1]], [temp_composition[1]])
                self.mixtureFlag = False
            else:
                self.cp_state_mixture = CoolPropEngine(temp_components, temp_composition)

        self.properties_initialised = False
        self.state_properties = Properties({"P": 0.0})

    def set_calc_options(self,
                         part_opts: Optional[Union[str, None]]=None,
                         prop_opts: Optional[Union[str, None]]=None) -> NoReturn:
        """
        set the specific calculation options

        Parameters
        ----------
        part_opts: str, None
            the PartitionModelOptions to be used, either "default", "spycher", "reaktoro"
        prop_opts: str, None
            the PartitionModelOptions to be used, either "default", "preload"

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            partition model configuration not recognised
        ValueError
            property model configuration not recognised
        """

        opts = PartitionModelOptions()
        if part_opts is not None:
            match part_opts:

                case "default":
                    opts.model = PartitionModelOptions.PartitionModels.SPYCHERPRUSS

                case "spycher":
                    opts.model = PartitionModelOptions.PartitionModels.SPYCHERPRUSS

                case "reaktoro":
                    opts.model = PartitionModelOptions.PartitionModels.REAKTORO

                case _:
                    msg = "\nThe specified partition model configuration, {}, is not recognised. Please check spelling".format(part_opts)
                    raise ValueError(msg)
            self.part_opts = opts

        if prop_opts is not None:
            opts = PropertyModelOptions()
            match prop_opts:
                case "default":
                    opts.ThermoFun.init_engine()

                case "preload":
                    opts.ThermoFun.init_engine()

                case _:
                    msg = "\nThe specified property model configuration, {}, is not recognised. Please check spelling".format(part_opts)
                    raise ValueError(msg)
            self.prop_opts = opts

        self.state = State(part_options=self.part_opts, prop_options=self.prop_opts)

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

        components_geoprop = self.GeoProp_components

        self.fluid = GeoFluid(components=components_geoprop, composition=composition, CompInMole=True)
        self.properties_initialised = False

        components = self.components
        self.mixtureFlag = (len(composition) > 1)
        temp_components = ["water", "carbondioxide"]
        temp_composition = [0.0, 0.0]
        if "water" in components:
            temp_composition[0] += composition[components.index("water")]

        if "steam" in components:
            temp_composition[0] += composition[components.index("steam")]

        if "carbondioxide" in components:
            temp_composition[1] += composition[components.index("carbondioxide")]

        if "CO2(aq)" in components:
            temp_composition[1] += composition[components.index("CO2(aq)")]

        corr = sum(temp_composition)
        temp_composition[0] /= corr
        temp_composition[1] /= corr

        # check if the fluid is close to being pure
        if temp_composition[0] > 0.999:
            self.cp_state_pure = CoolPropEngine([temp_components[0]], [temp_composition[0]])
            self.mixtureFlag = False
        elif temp_composition[1] > 0.999:
            self.cp_state_pure = CoolPropEngine([temp_components[1]], [temp_composition[1]])
            self.mixtureFlag = False
        else:
            self.cp_state_mixture = CoolPropEngine(temp_components, temp_composition)

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
        Properties

        Raises
        ------
        ValueError
            The combination of state variables is not supported
        """

        if not self.properties_initialised:
            self.__init_props(**kwargs)

        if not self.mixtureFlag:
            self.cp_state_pure.calc(InputSpec, Input1, Input2, **kwargs)
            self.state_properties = self.cp_state_pure.state_properties

            return

        if InputSpec not in self.calc_input_pairs:
            msg = "\nThe input specification \"{}\" is not supported".format(InputSpec)
            raise ValueError(msg)

        match InputSpec:

            case "PT":
                self.state_properties = self.__calc_PT(Input1, Input2, **kwargs)
                return

            case "TP":
                self.state_properties = self.__calc_PT(Input2, Input1, **kwargs)
                return

            case "PH":
                self.state_properties = self.__calc_PH(Input1, Input2, **kwargs)
                return

            case "HP":
                self.state_properties = self.__calc_PH(Input2, Input1, **kwargs)
                return

            case "PS":
                self.state_properties = self.__calc_PS(Input1, Input2, **kwargs)
                return

            case "SP":
                self.state_properties = self.__calc_PS(Input2, Input1, **kwargs)
                return

            case "PQ":
                self.state_properties = self.__calc_PQ(Input1, Input2, **kwargs)
                return

            case "QP":
                self.state_properties = self.__calc_PQ(Input2, Input1, **kwargs)
                return

            case "TQ":
                self.state_properties = self.__calc_TQ(Input1, Input2, **kwargs)
                return

            case "QT":
                self.state_properties = self.__calc_TQ(Input2, Input1, **kwargs)
                return

            case _:
                msg = "\nThe input specification {} has not yet been implemented".format(InputSpec)
                raise ValueError(msg)


    def __init_props(self, **kwargs) -> NoReturn:
        """
        Initialises the properties at the reference conditions

        Returns
        -------
        NoReturn
        """

        if self.mixtureFlag:
            props = self.__calc_PT(Pref, Tref)
            self.h0 = props.H
            self.s0 = props.S
        else:
            self.cp_state_pure.calc("PT", Pref, Tref, **kwargs)
            props = self.cp_state_pure.state_properties
            self.h0 = props.H + self.cp_state_pure.h0
            self.s0 = props.S + self.cp_state_pure.s0

        self.properties_initialised = True

    def __region(self, p: float, T: float) -> tuple[int, int]:
        """
        Helper function to determine what region the calculation falls under - this is used to decide whether GeoProp
        or CoolProp should be used

        Parameters
        ----------
        p: float
            Pressure in Pa
        T: float
            Temperature in K

        Returns
        -------
        tuple[int, int]
        """

        if p < self.Pminmin:
            i_P = -1
        elif self.Pminmin <= p < self.Pmin:
            i_P = 0
        elif self.Pmin <= p <= self.Pmax:
            i_P = 1
        else:
            i_P = 2

        if T < self.Tmin:
            i_T = 0
        elif self.Tmin <= T <= self.Tmax:
            i_T = 1
        else:
            i_T = 2

        return (i_T, i_P)

    def __calc_PT(self, p: float, T: float, **kwargs) -> Properties:
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
        Properties

        Raises
        ------
        ValueError
            temperature and pressure are outside the validation region
        """

        region = self.__region(p, T)

        match region:
            case (1, 1):
                self.fluid = self.state.calc_PT(self.fluid, p, T)

                return self.__get_properties_from_GeoProp()

            case (1, 0) | (2, 0) | (2, 1):
                # this is to use CoolProp for more regions outside of validation zone of SpycherPruess

                self.cp_state_mixture.calc("PT", p, T, **kwargs)
                return Properties(self.cp_state_mixture.state_properties.as_dict())

            case _:
                msg = "\nThe temperature, {:.2f} K, and pressure, {:.2e} Pa, are outside the validation range:\n" \
                      " - Temperature: {:.2f} to {:.2f} K\n" \
                      " - Pressure: {:.2e} to {:.2e} Pa".format(T, p, self.Tmin, self.Tmax, self.Pminmin, self.Pmax)
                raise ValueError(msg)

    def __calc_PH(self, p: float, H: float, **kwargs) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific enthalpy

        Parameters
        ----------
        p: float
            Pressure in Pa
        H: float
            Specific Enthalpy in J/kg relative to the reference temperature, Tref, and pressure, Pref

        Returns
        -------
        Properties
        """

        hist_T = []
        hist_H = []
        hist_S = []
        hist_Q = []

        def h(t):
            temp_props = self.__calc_PT(p, t, **kwargs)

            hist_T.append(t)
            hist_H.append(temp_props.H)
            hist_S.append(temp_props.S)
            hist_Q.append(temp_props.Q)

            return temp_props.H - H

        try:
            solution = root_scalar(h, method="secant", x0=350, rtol=0.001)

            if solution.converged:
                T = solution.root
            else:
                raise ValueError

        except:
            solution = root_scalar(h, method="brentq", bracket=[self.Tmin + 1, self.Tmax - 1], rtol=0.001)

            T = solution.root

        fin_props = self.__calc_PT(p, T, **kwargs)

        if abs(fin_props.H - H)/max([abs(fin_props.H), abs(H), 1e-5]) > 0.001:

            hist = np.column_stack((hist_H, hist_S, hist_Q, hist_T))
            hist = hist[hist[:, 0].argsort()]

            fin_props.H = H
            fin_props.S = np.interp(H, hist[:, 0], hist[:, 1])
            fin_props.Q = np.interp(H, hist[:, 0], hist[:, 2])
            fin_props.T = np.interp(H, hist[:, 0], hist[:, 3])

        return fin_props

    def __calc_PS(self, p: float, S: float, **kwargs) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific enthalpy

        Parameters
        ----------
        p: float
            Pressure in Pa
        S: float
            Specific Entropy in J/kg/K relative to the reference temperature, Tref, and pressure, Pref

        Returns
        -------
        Properties
        """

        hist_T = []
        hist_H = []
        hist_S = []
        hist_Q = []

        def s(t):

            temp_props = self.__calc_PT(p, t, **kwargs)

            hist_T.append(t)
            hist_H.append(temp_props.H)
            hist_S.append(temp_props.S)
            hist_Q.append(temp_props.Q)

            return temp_props.S - S

        try:
            solution = root_scalar(s, method="secant", x0=350, rtol=0.0001)

            if solution.converged:
                T = solution.root
            else:
                raise ValueError
        except:
            solution = root_scalar(s, method="brentq", bracket=[self.Tmin + 1, self.Tmax - 1], rtol=0.0001)
            T = solution.root

        fin_props = self.__calc_PT(p, T, **kwargs)

        if abs(fin_props.S - S) / max([abs(fin_props.S), abs(S), 1e-5]) > 0.001:

            hist = np.column_stack((hist_S, hist_H, hist_Q, hist_T))
            hist = hist[hist[:, 0].argsort()]

            fin_props.S = S
            fin_props.H = np.interp(S, hist[:, 0], hist[:, 1])
            fin_props.Q = np.interp(S, hist[:, 0], hist[:, 2])
            fin_props.T = np.interp(S, hist[:, 0], hist[:, 3])

        return fin_props

    def __calc_PQ(self, p: float, Q:float, **kwargs) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific enthalpy

        Parameters
        ----------
        p: float
            Pressure in Pa
        Q: float
            Vapour Quality

        Returns
        -------
        Properties
        """

        hist_T = []
        hist_H = []
        hist_S = []
        hist_Q = []

        def q(t):

            temp_props = self.__calc_PT(p, t, **kwargs)

            hist_T.append(t)
            hist_H.append(temp_props.H)
            hist_S.append(temp_props.S)
            hist_Q.append(temp_props.Q)

            return temp_props.Q - Q

        try:
            solution = root_scalar(q, method="secant", x0=350)

            if solution.converged:
                T = solution.root
            else:
                raise ValueError

        except:
            solution = root_scalar(q, method="brentq", bracket=[self.Tmin + 1, self.Tmax - 1])
            T = solution.root

        fin_props = self.__calc_PT(p, T)

        if abs(fin_props.Q - Q) / max([abs(fin_props.Q), abs(Q), 1e-5]) > 0.001:

            hist = np.column_stack((hist_Q, hist_H, hist_S, hist_T))
            hist = hist[hist[:, 0].argsort()]

            fin_props.Q = Q
            fin_props.H = np.interp(Q, hist[:, 0], hist[:, 1])
            fin_props.S = np.interp(Q, hist[:, 0], hist[:, 2])
            fin_props.T = np.interp(Q, hist[:, 0], hist[:, 3])

        return fin_props

    def __calc_TQ(self, T: float, Q: float, **kwargs) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific enthalpy

        Parameters
        ----------
        T: float
            Temperature in K
        Q: float
            Vapour Quality

        Returns
        -------
        Properties
        """

        hist_P = []
        hist_H = []
        hist_S = []
        hist_Q = []

        def q(p):

            temp_props = self.__calc_PT(p, T, **kwargs)

            hist_P.append(p)
            hist_H.append(temp_props.H)
            hist_S.append(temp_props.S)
            hist_Q.append(temp_props.Q)

            return temp_props.Q - Q

        try:
            solution = root_scalar(q, method="secant", x0=2e5, rtol=0.001)

            if solution.converged:
                p = solution.root
            else:
                raise ValueError

        except:
            solution = root_scalar(q, method="brentq", bracket=[self.Pminmin + 1, self.Pmax - 1], rtol=0.001)
            p = solution.root

        fin_props = self.__calc_PT(p, T, **kwargs)

        if abs(fin_props.Q - Q) / max([abs(fin_props.Q), abs(Q), 1e-5]) > 0.001:

            hist = np.column_stack((hist_Q, hist_H, hist_S, hist_P))
            hist = hist[hist[:, 0].argsort()]

            fin_props.Q = Q
            fin_props.H = np.interp(Q, hist[:, 0], hist[:, 1])
            fin_props.Q = np.interp(Q, hist[:, 0], hist[:, 2])
            fin_props.P = np.interp(Q, hist[:, 0], hist[:, 3])

        return fin_props

    def __get_properties_from_GeoProp(self) -> Properties:
        """
        Helper function to retrieve the properties from GeoProp

        Returns
        -------
        Properties
        """

        props = {}
        for prop in self.properties:

            match prop:
                case "P":
                    props["P"] = self.fluid.total.props.P

                case "T":
                    props["T"] = self.fluid.total.props.T

                case "H":
                    props["H"] = self.fluid.total.props.h * 1000

                case "S":
                    props["S"] = self.fluid.total.props.s * 1000

                case "D":
                    props["D"] = self.fluid.total.props.rho

                case "V":
                    props["V"] = self.fluid.total.props.v

                case "Q":

                    moles_g = sum([self.fluid.gaseous.moles[i] for i in self.fluid.gaseous.components])
                    moles_l = sum([self.fluid.aqueous.moles[i] for i in self.fluid.aqueous.components])

                    props["Q"] = moles_g / (moles_l + moles_g)

                case "Mr":

                    moles = sum([self.fluid.total.moles[i] for i in self.fluid.total.components])
                    mass = sum([self.fluid.total.mass[i] for i in self.fluid.total.components])

                    props["Mr"] = mass / moles

                case "LiqProps":

                    if self.fluid.aqueous.components:

                        composition = [compo for compo in self.fluid.aqueous.molefrac]
                        components = [self.CompToName[comp] for comp in self.fluid.aqueous.components]

                        moles = sum([self.fluid.aqueous.moles[i] for i in self.fluid.aqueous.components])
                        mass = sum([self.fluid.aqueous.mass[i] for i in self.fluid.aqueous.components])
                        Mr = mass / (moles + 1e-15)

                        liq_props = {"composition": composition,
                                     "components": components,
                                     "T": self.fluid.total.props.T,
                                     "P": self.fluid.total.props.P,
                                     "H": self.fluid.aqueous.props.h * 1000,
                                     "S": self.fluid.aqueous.props.s * 1000,
                                     "D": self.fluid.aqueous.props.rho,
                                     "V": self.fluid.aqueous.props.v,
                                     "Mr": Mr,
                                     "Q": 0.0,
                                     "exists": True}

                        props["LiqProps"] = Properties(liq_props)

                    else:

                        props["LiqProps"] = Properties({"exists": False})

                case "VapProps":

                    if self.fluid.gaseous.components:

                        composition = [compo for compo in self.fluid.gaseous.molefrac]
                        components = [self.CompToName[comp] for comp in self.fluid.gaseous.components]

                        moles = sum([self.fluid.gaseous.moles[i] for i in self.fluid.gaseous.components])
                        mass = sum([self.fluid.gaseous.mass[i] for i in self.fluid.gaseous.components])
                        Mr = mass / (moles + 1e-15)

                        vap_props = {"composition": composition,
                                     "components": components,
                                     "T": self.fluid.total.props.T,
                                     "P": self.fluid.total.props.P,
                                     "H": self.fluid.gaseous.props.h * 1000,
                                     "S": self.fluid.gaseous.props.s * 1000,
                                     "D": self.fluid.gaseous.props.rho,
                                     "V": self.fluid.gaseous.props.v,
                                     "Mr": Mr,
                                     "Q": 1.0,
                                     "exists": True}

                        props["VapProps"] = Properties(vap_props)

                    else:

                        props["VapProps"] = Properties({"exists": False})

        return Properties(props)


def register() -> NoReturn:
    """
    Registers the CoolProp property calculation engine

    Returns
    -------
    NoReturn
    """

    factory.register("geoprop", GeoPropEngine)
