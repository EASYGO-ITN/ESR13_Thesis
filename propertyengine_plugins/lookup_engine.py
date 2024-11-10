from typing import NoReturn, Optional, Union
import math
import pickle
import matplotlib.pyplot as plt
import scipy
from scipy.optimize import root_scalar
import numpy as np

from .base_engine import Engine
from .coolprop_engine import CoolPropEngine

from FluidProperties import factory
from FluidProperties.properties import Properties


class LookUpTable(Engine):

    """
    The LookUpTable Engine

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
    InputSpec: str
        the state variables for which the LookUpTable is generated. E.g. "PT" for pressure and temperature
    filename: str
        the filepath and name of the LookUpTable
    loaded: bool
        flag indicating that the table has been loaded
    mixtureFlag: bool
        flag indicating that the fluid is a mixture
    cp_state_pure: CoolPropEngine
        the calculation state for a pure fluid

    Composition
    minZ
    maxZ
    Inputs1
    min1
    max1
    mode1
    Inputs2
    min2
    max2
    mode2
    Points
    ValuesT
    ValuesP
    ValuesH
    ValuesS
    ValuesQ
    ValuesD
    ValuesV

    """

    properties = ["H", "S", "P", "T", "D", "V", "Q"]  # list of all supported properties

    calc_input_pairs = ["PT", "TP", "PH", "HP", "PS", "SP", "PQ", "QP", "TQ", "QT"]

    def __init__(self,
                 components: list[str],
                 composition: list[float],
                 *args: tuple[any],
                 InputSpec: Optional[str]="PT",
                 filename: Optional[str | None]=None) -> NoReturn:
        """
        instantiates the LookUPTable engine

        Parameters
        ----------
        components: list[str]
            the component names
        composition: list[float]
            the component mole fractions
        *args: tuple[any]
            any additional arguments
        InputSpec: str
            the state variables for which the LookUpTable is generated. E.g. "PT" for pressure and temperature
        filename: str
            the filepath and name of the LookUpTable

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            only water-carbon dioxide binary fluids are permitted
        """

        self.components = components
        self.composition = composition

        super().__init__(components, composition)

        self.InputSpec = InputSpec

        if filename is not None:
            self.load(filename)
        else:
            self.filename = None
            self.loaded = False

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

    def set_table(self, filename: str) -> NoReturn:
        """
        set the LookUpTable from a file

        Parameters
        ----------
        filename: str
            the filepath and name of the look up table file

        Returns
        -------
        NoReturns

        """
        self.load(filename)

    def set_composition(self,
                        z: Optional[Union[list[float], np.array, None]]=None,
                        min: Optional[float| None]=None,
                        max: Optional[float| None]=None,
                        nz: Optional[int]=10) -> NoReturn:
        """
        set the composition range for the table

        Parameters
        ----------
        z: Optional[list[float] | np.array | None]
            the mole fractions
        min: Optional[float| None]
            the minimum mole fraction
        max: Optional[float| None]
            the maximum mole fraction
        nz: int
            the numer of mole fraction

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            insufficient inputs

        """

        if z is not None:
            self.Composition = z

            self.minZ = np.min(z)
            self.maxZ = np.max(z)

        elif min is not None and max is not None:
            self.Composition = np.linspace[min, max, nz]
            self.minZ = min
            self.maxZ = max

        else:
            msg = "Insufficient Inputs have been provided"
            raise ValueError(msg)

    def set_Input1(self,
                   inputs: Optional[Union[list[float], np.array, None]]=None,
                   min: Optional[float | None]=None,
                   max: Optional[float | None]=None,
                   N: Optional[int]=20,
                   log: Optional[bool]=False):
        """
        set the inputs for state variable 1

        Parameters
        ----------
        inputs: Optional[list[float] | np.array | None]
            the values for state variable 1
        min: Optional[float | None]
            the minimum value for state variable 1
        max: Optional[float | None]
            the maximum value for state variable 1
        N: int
            the number of values for state variable 1
        log: bool
            flag indicating whether log scale should be used

        Returns
        -------
        NoReturn

        """

        if inputs is not None:
            self.Inputs1 = inputs

            self.min1 = np.min(inputs)
            self.max1 = np.max(inputs)

        elif min is not None and max is not None:

            if log:
                self.Inputs1 = np.logspace(math.log10(min), math.log10(max), N)
                self.mode1 = "log"
            else:
                self.Inputs1 = np.linspace(min, max, N)
                self.mode1 = "linear"

            self.min1 = min
            self.max1 = max

    def set_Input2(self,
                   inputs: Optional[Union[list[float], np.array, None]] = None,
                   min: Optional[float | None] = None,
                   max: Optional[float | None] = None,
                   N: Optional[int] = 20,
                   log: Optional[bool] = False):
        """
        set the inputs for state variable 1

        Parameters
        ----------
        inputs: Optional[list[float] | np.array | None]
            the values for state variable 1
        min: Optional[float | None]
            the minimum value for state variable 1
        max: Optional[float | None]
            the maximum value for state variable 1
        N: int
            the number of values for state variable 1
        log: bool
            flag indicating whether log scale should be used

        Returns
        -------
        NoReturn

        """

        if inputs is not None:
            self.Inputs2 = inputs

            self.min2 = np.min(inputs)
            self.max2 = np.max(inputs)

        elif min is not None and max is not None:

            if log:
                self.Inputs2 = np.logspace(math.log10(min), math.log10(max), N)
                self.mode2 = "log"
            else:
                self.Inputs2 = np.linspace(min, max, N)
                self.mode2 = "linear"

            self.min2 = min
            self.max2 = max

    def generateTable(self, fluid: "Fluid") -> NoReturn:
        """
        generate the LookUpTable

        Parameters
        ----------
        fluid: Fluid

        Returns
        -------
        NoReturn

        Raises
        ValueError
            no values can be calculated for a given pressure
        """

        nzH = self.Composition.size
        n1 = self.Inputs1.size
        n2 = self.Inputs2.size

        # Results
        self.ValuesT = np.empty((nzH, n1, n2))
        self.ValuesP = np.empty((nzH, n1, n2))
        self.ValuesH = np.empty((nzH, n1, n2))
        self.ValuesS = np.empty((nzH, n1, n2))
        self.ValuesQ = np.empty((nzH, n1, n2))
        self.ValuesD = np.empty((nzH, n1, n2))
        self.ValuesV = np.empty((nzH, n1, n2))

        for i, z in enumerate(self.Composition):

            composition = [z, 1 - np.sum(z)]

            print("generating table for {}".format(composition))

            base_fluid = fluid.update_composition(composition, InPlace=False)


            for j, Input1 in enumerate(self.Inputs1):
                for k, Input2 in enumerate(self.Inputs2):

                    try:
                        temp_fluid = base_fluid.copy()
                        temp_fluid.update(self.InputSpec, Input1, Input2)

                        # TODO there is an issue in GeoProp whereby the composition changes during the calculation...
                        # print(sum(temp_fluid.state.state.fluid.total.molefrac[-4:-3]))

                        self.ValuesT[i, j, k] = temp_fluid.properties.T
                        self.ValuesP[i, j, k] = temp_fluid.properties.P
                        self.ValuesH[i, j, k] = temp_fluid.properties.H
                        self.ValuesS[i, j, k] = temp_fluid.properties.S
                        self.ValuesQ[i, j, k] = temp_fluid.properties.Q
                        self.ValuesD[i, j, k] = temp_fluid.properties.D
                        self.ValuesV[i, j, k] = 1 / temp_fluid.properties.D

                    except:
                        self.ValuesT[i, j, k] = np.NaN
                        self.ValuesP[i, j, k] = np.NaN
                        self.ValuesH[i, j, k] = np.NaN
                        self.ValuesS[i, j, k] = np.NaN
                        self.ValuesQ[i, j, k] = np.NaN
                        self.ValuesD[i, j, k] = np.NaN
                        self.ValuesV[i, j, k] = np.NaN

                isNaN = np.isnan(self.ValuesT[i, j, :])
                if sum(isNaN) > 0:
                    if sum(isNaN) >= n2 - 1:
                        raise ValueError("uh uh cannot calculate any values for this pressure :(")

                    bad_indeces = isNaN
                    good_indeces = np.logical_not(isNaN)

                    good_x = self.Inputs2[good_indeces]
                    bad_x = self.Inputs2[bad_indeces]

                    good_T = self.ValuesT[i, j, good_indeces]
                    interpolated_T = np.interp(bad_x, good_x, good_T)
                    self.ValuesT[i, j, bad_indeces] = interpolated_T

                    good_P = self.ValuesP[i, j, good_indeces]
                    interpolated_P = np.interp(bad_x, good_x, good_P)
                    self.ValuesP[i, j, bad_indeces] = interpolated_P

                    good_H = self.ValuesH[i, j, good_indeces]
                    interpolated_H = np.interp(bad_x, good_x, good_H)
                    self.ValuesH[i, j, bad_indeces] = interpolated_H

                    good_S = self.ValuesS[i, j, good_indeces]
                    interpolated_S = np.interp(bad_x, good_x, good_S)
                    self.ValuesS[i, j, bad_indeces] = interpolated_S

                    good_Q = self.ValuesQ[i, j, good_indeces]
                    interpolated_Q = np.interp(bad_x, good_x, good_Q)
                    self.ValuesQ[i, j, bad_indeces] = interpolated_Q

                    good_D = self.ValuesD[i, j, good_indeces]
                    interpolated_D = np.interp(bad_x, good_x, good_D)
                    self.ValuesD[i, j, bad_indeces] = interpolated_D
                    self.ValuesV[i, j, bad_indeces] = 1 / interpolated_D


        if self.mode1 == "log":
            inputs1 = np.log10(self.Inputs1)
        else:
            inputs1 = self.Inputs1

        if self.mode2 == "log":
            inputs2 = np.log10(self.Inputs2)
        else:
            inputs2 = self.Inputs2

        self.Points = [self.Composition, inputs1, inputs2]

    def plot(self,
             filename: Optional[str]="",
             show: Optional[bool]=True,
             legend: Optional[bool]=False) -> NoReturn:
        """
        plots the look up table

        Parameters
        ----------
        filename: Optional[str]
            filename to save the plot as an image
        show: Optional[bool]
            flag indicating whether to show the plot
        legend: Optional[bool]
            flag indicating whether to show the legend

        Returns
        -------
        NoReturn

        """

        nZ = self.Composition.size
        Props = ["H", "S", "Q", "D"]
        nProps = len(Props)

        Values = {"H, J/kg": self.ValuesH, "S, J/kg/K": self.ValuesS, "Q, -": self.ValuesQ, "D, kg/m3": self.ValuesD}

        fig, axes = plt.subplots(nrows=nProps, ncols=nZ)

        x = self.Points[2]

        for i, z in enumerate(self.Composition):

            axes[0][i].set_title("Z={:.3f}".format(z))

            for j, prop in enumerate(Values):

                axes[j][i].set_ylabel(prop)
                axes[j][i].set_xlabel("Temperature, K")

                for k, P in enumerate(self.Points[1]):

                    y = Values[prop][i, k, :]
                    axes[j][i].plot(x, y, label="P={:.2e}".format(P), linewidth=0.5)

        if show:
            if legend:
                plt.legend()
            plt.show()

        if filename:
            fig.savefig(filename)

    def save(self, filename:str) -> NoReturn:
        """
        save the LookUpTable to File

        Parameters
        ----------
        filename: str
            the filepath and name

        Returns
        -------
        NoReturn

        """

        container = {"InputSpec": self.InputSpec,
                     "Composition": self.Composition,
                     "minZ": self.minZ,
                     "maxZ": self.maxZ,
                     "Inputs1": self.Inputs1,
                     "min1": self.min1,
                     "max1": self.max1,
                     "mode1": self.mode1,
                     "Inputs2": self.Inputs2,
                     "min2": self.min2,
                     "max2": self.max2,
                     "mode2": self.mode2,
                     "Points": self.Points,
                     "ValuesT": self.ValuesT,
                     "ValuesP": self.ValuesP,
                     "ValuesH": self.ValuesH,
                     "ValuesS": self.ValuesS,
                     "ValuesQ": self.ValuesQ,
                     "ValuesD": self.ValuesD}

        with open(filename, "wb") as file:
            pickle.dump(container, file)

    def load(self, filename: str) -> NoReturn:
        """
        loads the Look Up Table from a file

        Parameters
        ----------
        filename:
            filepath and name of the file

        Returns
        -------
        NoReturn
        """

        with open(filename, "rb") as file:
            container = pickle.load(file)

        self.InputSpec = container["InputSpec"]

        self.Composition = container["Composition"]
        self.minZ = container["minZ"]
        self.maxZ = container["maxZ"]

        self.Inputs1 = container["Inputs1"]
        self.min1 = container["min1"]
        self.max1 = container["max1"]
        self.mode1 = container["mode1"]

        self.Inputs2 = container["Inputs2"]
        self.min2 = container["min2"]
        self.max2 = container["max2"]
        self.mode2 = container["mode2"]

        self.Points = container["Points"]

        self.ValuesT = container["ValuesT"]
        self.ValuesP = container["ValuesP"]
        self.ValuesH = container["ValuesH"]
        self.ValuesS = container["ValuesS"]
        self.ValuesQ = container["ValuesQ"]
        self.ValuesD = container["ValuesD"]

        self.loaded = True
        self.filename = filename

    def update_composition(self, Zs: Union[list[float], np.array]) -> NoReturn:
        """
        updates the fluid composition

        Parameters
        ----------
        Zs: list[float] | np.array
            the new component mole fractions

        Returns
        -------
        NoReturn

        """
        self.composition = Zs

        self.mixtureFlag = (len(Zs) > 1)
        corr = sum(Zs)
        Zs[0] /= corr
        Zs[1] /= corr

        # check if the fluid is close to being pure
        if Zs[0] > 0.999:
            self.cp_state_pure = CoolPropEngine([self.components[0]], [Zs[0]])
            self.mixtureFlag = False
        elif Zs[1] > 0.999:
            self.cp_state_pure = CoolPropEngine([self.components[1]], [Zs[1]])
            self.mixtureFlag = False

    def calc(self, InputSpec: str, Input1: float, Input2: float, *args: tuple[any], **kwargs: dict[any]) -> NoReturn | None:
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
        NoReturn | None

        Raises
        ------
        ValueError
            the combination of state variables is not supported
        ValueError
            the combination of state variables has not yet been implemented

        """

        if not self.loaded:
            self.load(self.filename)

        if not self.mixtureFlag:
            self.cp_state_pure.calc(InputSpec, Input1, Input2)
            self.state_properties = self.cp_state_pure.state_properties

            return

        if InputSpec not in self.calc_input_pairs:
            msg = "\nThe input specification \"{}\" is not supported".format(InputSpec)
            raise ValueError(msg)

        z = self.composition[0]

        match InputSpec:

            case "PT":
                self.state_properties = self.__calc_PT(z, Input1, Input2)
                return

            case "TP":
                self.state_properties = self.__calc_PT(z, Input2, Input1)
                return

            case "PH":
                self.state_properties = self.__calc_PH(z, Input1, Input2)
                return

            case "HP":
                self.state_properties = self.__calc_PH(z, Input2, Input1)
                return

            case "PS":
                self.state_properties = self.__calc_PS(z, Input1, Input2)
                return

            case "SP":
                self.state_properties = self.__calc_PS(z, Input2, Input1)
                return

            case "PQ":
                self.state_properties = self.__calc_PQ(z, Input1, Input2)
                return

            case "QP":
                self.state_properties = self.__calc_PQ(z, Input2, Input1)
                return

            case "TQ":
                self.state_properties = self.__calc_TQ(z, Input1, Input2)
                return

            case "QT":
                self.state_properties = self.__calc_TQ(z, Input2, Input1)
                return

            case _:
                msg = "\nThe input specification {} has not yet been implemented".format(InputSpec)
                raise ValueError(msg)

    def __calc_PT(self, z: float, Input1: float, Input2: float) -> Properties:
        """
        Helper function for performing a state calculation using pressure and temperature

        Parameters
        ----------
        Input1: float
            Pressure in Pa
        Input2: float
            Temperature in K

        Returns
        -------
        Properties
        """

        if self.InputSpec in ["PT", "TP"]:

            if self.InputSpec == "TP":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        else:

            if self.mode1 == "log":
                min1 = math.log10(self.min1)
                max1 = math.log10(self.max1)
            else:
                min1 = self.min1
                max1 = self.max1

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, self.min1, self.min2]

            def P_search(y):

                def T_search(x):
                    point[2] = x

                    T = scipy.interpolate.interpn(self.Points, self.ValuesT, point)[0]

                    return T - Input2

                point[1] = y

                solution_T = root_scalar(T_search, method="brentq", bracket=[min2, max2], rtol=0.001)
                point[2] = solution_T.root

                P = scipy.interpolate.interpn(self.Points, self.ValuesP, point)[0]

                return P - Input1

            solution_P = root_scalar(P_search, method="brentq", bracket=[min1, max1], rtol=0.001)

            point[1] = solution_P.root

        return self.__get_properties(point)

    def __calc_PH_old(self, z, Input1, Input2):

        if self.InputSpec in ["PH", "HP"]:

            if self.InputSpec == "HP":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        else:

            if self.mode1 == "log":
                min1 = math.log10(self.min1)
                max1 = math.log10(self.max1)
            else:
                min1 = self.min1
                max1 = self.max1

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, max1, min2]

            def P_search(y):

                def H_search(x):
                    point[2] = x

                    H = scipy.interpolate.interpn(self.Points, self.ValuesH, point)[0]

                    return H - Input2

                point[1] = y

                if self.mode2 == "log":
                    min2 = math.log10(self.min2)
                    max2 = math.log10(self.max2)
                else:
                    min2 = self.min2
                    max2 = self.max2

                solution_H = root_scalar(H_search, method="brentq", bracket=[min2, max2], rtol=0.001)
                point[2] = solution_H.root

                P = scipy.interpolate.interpn(self.Points, self.ValuesP, point)[0]

                return P - Input1

            solution_P = root_scalar(P_search, method="brentq", bracket=[min1, max1], rtol=0.001)

            point[1] = solution_P.root

        return self.__get_properties(point)

    def __calc_PH(self, z: float, Input1: float, Input2: float) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific enthalpy

        Parameters
        ----------
        Input1: float
            Pressure in Pa
        Input2: float
            Specific enthalpy in J/kg

        Returns
        -------
        Properties
        """

        if self.InputSpec in ["PH", "HP"]:

            if self.InputSpec == "HP":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        elif "P" in self.InputSpec:

            if self.InputSpec[1] == "P":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, Input1, min2]

            def H_search(x):
                point[2] = x

                H = scipy.interpolate.interpn(self.Points, self.ValuesH, point)[0]

                return H - Input2

            solution_H = root_scalar(H_search, method="brentq", bracket=[min2, max2], rtol=0.001)
            point[2] = solution_H.root

        else:
            raise NotImplementedError

        return self.__get_properties(point)

    def __calc_PS(self, z: float, Input1: float, Input2: float) -> Properties:
        """
        Helper function for performing a state calculation using pressure and specific entropy

        Parameters
        ----------
        Input1: float
            Pressure in Pa
        Input2: float
            Specific entropy in j/kg/K

        Returns
        -------
        Properties
        """

        if self.InputSpec in ["PS", "SP"]:

            if self.InputSpec == "SP":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        else:

            if self.mode1 == "log":
                min1 = math.log10(self.min1)
                max1 = math.log10(self.max1)
            else:
                min1 = self.min1
                max1 = self.max1

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, self.min1, self.min2]

            def P_search(y):

                def S_search(x):
                    point[2] = x

                    S = scipy.interpolate.interpn(self.Points, self.ValuesS, point)[0]

                    return S - Input2

                point[1] = y

                solution_S = root_scalar(S_search, method="brentq", bracket=[min2, max2], rtol=0.001)
                point[2] = solution_S.root

                P = scipy.interpolate.interpn(self.Points, self.ValuesP, point)[0]

                return P - Input1

            solution_P = root_scalar(P_search, method="brentq", bracket=[min1, max1], rtol=0.001)

            point[1] = solution_P.root

        return self.__get_properties(point)

    def __calc_PQ(self, z: float, Input1: float, Input2: float) -> Properties:
        """
        Helper function for performing a state calculation using pressure and vapour quality

        Parameters
        ----------
        Input1: float
            Pressure in Pa
        Input2: float
            Vapour Quality

        Returns
        -------
        Properties
        """

        if self.InputSpec in ["PQ", "QP"]:

            if self.InputSpec == "QP":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        else:

            if self.mode1 == "log":
                min1 = math.log10(self.min1)
                max1 = math.log10(self.max1)
            else:
                min1 = self.min1
                max1 = self.max1

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, self.min1, self.min2]

            def P_search(y):

                def Q_search(x):
                    point[2] = x

                    Q = scipy.interpolate.interpn(self.Points, self.ValuesQ, point)[0]

                    return Q - Input2

                point[1] = y

                solution_Q = root_scalar(Q_search, method="brentq", bracket=[min2, max2], rtol=0.001)
                point[2] = solution_Q.root

                P = scipy.interpolate.interpn(self.Points, self.ValuesP, point)[0]

                return P - Input1

            solution_P = root_scalar(P_search, method="brentq", bracket=[min1, max1], rtol=0.001)

            point[1] = solution_P.root

        return self.__get_properties(point)

    def __calc_TQ(self, z: float, Input1: float, Input2: float) -> Properties:
        """
        Helper function for performing a state calculation using temperature and vapour quality

        Parameters
        ----------
        Input1: float
            Temperature in K
        Input2: float
            Vapour Quality

        Returns
        -------
        Properties
        """

        if self.InputSpec in ["TQ", "QT"]:

            if self.InputSpec == "QT":
                Input1, Input2 = Input2, Input1

            if self.mode1 == "log":
                Input1 = math.log10(Input1)

            if self.mode2 == "log":
                Input2 = math.log10(Input2)

            point = [z, Input1, Input2]

        else:

            if self.mode1 == "log":
                min1 = math.log10(self.min1)
                max1 = math.log10(self.max1)
            else:
                min1 = self.min1
                max1 = self.max1

            if self.mode2 == "log":
                min2 = math.log10(self.min2)
                max2 = math.log10(self.max2)
            else:
                min2 = self.min2
                max2 = self.max2

            point = [z, self.min1, self.min2]

            def T_search(y):

                def Q_search(x):
                    point[2] = x

                    Q = scipy.interpolate.interpn(self.Points, self.ValuesQ, point)[0]

                    return Q - Input2

                point[1] = y

                solution_Q = root_scalar(Q_search, method="brentq", bracket=[min2, max2], rtol=0.001)
                point[2] = solution_Q.root

                T = scipy.interpolate.interpn(self.Points, self.ValuesT, point)[0]

                return T - Input1

            solution_T = root_scalar(T_search, method="brentq", bracket=[min1, max1], rtol=0.001)

            point[1] = solution_T.root

        return self.__get_properties(point)

    def __get_properties(self, point: list[float, float, float]) -> Properties:
        """
        Helper function to retrieve the properties for a given point

        Parameters
        ----------
        point: list[float, float, float]
            the point to be evaluated

        Returns
        -------
        Properties
        """

        P = scipy.interpolate.interpn(self.Points, self.ValuesP, point)[0]
        T = scipy.interpolate.interpn(self.Points, self.ValuesT, point)[0]
        H = scipy.interpolate.interpn(self.Points, self.ValuesH, point)[0]
        S = scipy.interpolate.interpn(self.Points, self.ValuesS, point)[0]
        Q = scipy.interpolate.interpn(self.Points, self.ValuesQ, point)[0]
        D = scipy.interpolate.interpn(self.Points, self.ValuesD, point)[0]
        V = 1 / D

        return Properties({"P": P, "T": T, "H": H, "S": S, "Q": Q, "D": D, "V": V})


def register() -> NoReturn:
    """
    Registers the LookUpTable property calculation engine

    Returns
    -------
    NoReturn
    """

    factory.register("tables", LookUpTable)