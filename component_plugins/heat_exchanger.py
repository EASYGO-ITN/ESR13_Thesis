import math

import numpy as np
import scipy
from scipy.optimize import root_scalar
import matplotlib.pyplot as plt
from typing import NoReturn, Optional

import Simulator
from .base_component import Component
from Simulator import factory
from FluidProperties import Tref


class heat_exchanger(Component):

    Uvalues = {
        # "Brine_organic_liquid_liquid":592.223415738037,
        "water_organic_liquid_liquid": 1038.39920261662,
        "water_organic_condensing_liquid": 1192.60627398921,
        "water_organic_vapour_liquid": 935.910748994861,
        "Brine_organic_liquid_boiling": 592.223415738037,
        "water_organic_liquid_boiling": 1038.39920261662,
        "water_organic_condensing_boiling": 1192.60627398921,
        "water_organic_vapour_boiling": 935.910748994861,
        # "Brine_organic_liquid_vapour": 675.066631587376,
        "water_organic_liquid_vapour": 1323.09420726695,
        "water_organic_condensing_vapour": 1584.07558683136,
        "water_organic_vapour_vapour": 1161.08786610879,
        "water_air_liquid_vapour": 1354.66291,
        "water_air_condensing_vapour": 1372.47168854583,
        "water_air_vapour_vapour": 333.474790893784,
        "organic_air_liquid_vapour": 1047.597276,
        "organic_air_condensing_vapour": 1089.00710805132,
        "organic_air_vapour_vapour": 322.35440458389,
        "water_water_vapour_liquid": 101.706803834463,
        "water_water_condensing_liquid": 1330.2752293578,
        "water_water_liquid_liquid": 1265.76139670223,
        "organic_organic_vapour_liquid": 98.92552398
    }

    """
    the heat exchanger component

    Attributes
    ----------
    inlet: list[MaterialStream, MaterialStream]
        the hot and cold input streams
    outlet: list[MaterialStream, MaterialStream]
        the hot and cold outlet streams
    tablemode: str
        the mode in which the interpolation tables are generated. Default: "PH"
    deltaT_pinch: float
        the pinch temperature difference
    deltaP_hot: float
        the pressure drop on the hot side
    deltaP_cold: float
        the pressure drop on the cold side
    N: int
        the length of the interpolation table
    _T_PHtable_H: np.array
        the interpolation table for the hot side
    _T_PHtable_C: np.array
        the interpolation table for the cold side
    T_profile: list[np.array, np.array]
        the temperature profile
    H_profile: list[np.array, np.array]
        the enthalpy profile
    P_profile: list[np.array, np.array]
        the pressure profile
    Duty_profile: list[np.array, np.array]
        the duty profile
    Tambient: float
        the ambient temperature - this serves as a minimum temperature
    Tmaximum: float
        the maximum temperature. Default - 573 K (300 degC)

    MassRatio: float
        the mass rate ratio of hot and cold streams. i.e. mass rate of cold stream divided by mass rate of hot stream
    stream_in_H: MaterialStream
        the hot inlet stream
    stream_out_H: MaterialStream
        the hot outlet stream
    stream_in_C: MaterialStream
        the cold inlet stream
    stream_out_C: MaterialStream
        the cold outlet stream
    calculation_mode: list[int, int, int, int, int]
        the calculation mode
    min_deltaT: float
        the minimum temperature aproach in K
    deltaQ: float
        the heat exchanger duty in J/s

    """

    # TODO the Duty profiled for the hot streams should be reversed? For now it is convenient to check that everything is working

    def __init__(self,
                 deltaT_pinch: Optional[float]=5.0,
                 deltaP_hot: Optional[float]=1e4,
                 deltaP_cold: Optional[float]=1e4,
                 N_discretisation: Optional[int]=20,
                 Tambient: Optional[float]=298,
                 Tmaximum: Optional[float]=273 + 300,
                 tablemode: Optional[str]="PH",
                 cost_model = None) -> NoReturn:

        """
        instantiates the heat exchanger

        Parameters
        ----------
        deltaT_pinch: float
            the pinch temperature difference. Default: 5.0 K
        deltaP_hot: float
            the pressure drop on the hot side. Default: 1e4 Pa
        deltaP_cold: float
            the pressure drop on the cold side. Default: 1e4 Pa
        N_discretisation: int
            the number of discretisations. Default: 20
        Tambient: float
            the ambient temperature - this serves as a minimum temperature. Default: 298 K
        Tmaximum: float
            the maximum temperature. Default: 573K
        tablemode: str
            the mode for generating the interpolation tables. Default: "PH", i.e. pressure-enthalpy

        Returns
        -------
        NoReturn
        """

        super().__init__()

        self.inlet = ["", ""]
        self.outlet = ["", ]

        self.tablemode = tablemode

        self.deltaT_pinch = deltaT_pinch

        self.deltaP_hot = deltaP_hot
        self.deltaP_cold = deltaP_cold

        self.N = N_discretisation

        self._T_PHtable_H = None
        self._T_PHtable_C = None

        self.T_profile = [np.empty(1), np.empty(1)]
        self.H_profile = [np.empty(1), np.empty(1)]
        self.P_profile = [np.empty(1), np.empty(1)]
        self.Duty_profile = [np.empty(1), np.empty(1)]

        self.min_deltaT = -1

        self.Tambient = Tambient
        self.Tmaximum = Tmaximum

        if cost_model is None:
            self.cost_model = "default"
        else:
            self.cost_model = cost_model

        self.U = None

    def set_inputs(self,
                   MassRatio: Optional[float | None]=None,
                   Inlet_hot: Optional[float | None]=None,
                   Outlet_hot: Optional[float | None]=None,
                   Inlet_cold: Optional[float | None]=None,
                   Outlet_cold: Optional[float | None]=None) -> NoReturn:
        """
        set the inputs for the heat exchanger calculations

        Parameters
        ----------
        MassRatio: Optional[float | None]
            the mass ratio of the cold to the hot stream
        Inlet_hot: Optional[float | None]
            the hot inlet stream
        Outlet_hot: Optional[float | None]
            the hot outlet stream
        Inlet_cold: Optional[float | None]
            the cold inlet stream
        Outlet_cold: Optional[float | None]
            the cold outlet stream

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            hot inlet and outlet streams are not defined
        ValueError
            cold inlet and outlet streams are not defined
        ValueError
            mass rates of both hot and cold streams is zero
        ValueError
            insufficient boundary conditions have been defined
        ValueError
            too many boundary conditions have been defined
        """

        # check if sufficient inputs have been provided
        if Inlet_hot is None and Outlet_hot is None:
            msg = "\nCalculation cannot be completed - either the inlet or outlet hot streams must be defined"
            raise ValueError(msg)

        if Inlet_cold is None and Outlet_cold is None:
            msg = "\nCalculation cannot be completed - either the inlet or outlet cold streams must be defined"
            raise ValueError(msg)

        inputs = [Inlet_hot, Outlet_hot, Inlet_cold, Outlet_cold]
        inputs_mask = [1 if i is not None else 0 for i in inputs]

        self.stream_in_H = Inlet_hot.copy() if Inlet_hot is not None else Outlet_hot.copy()
        self.stream_out_H = Outlet_hot.copy() if Outlet_hot is not None else Inlet_hot.copy()

        self.stream_in_C = Inlet_cold.copy() if Inlet_cold is not None else Outlet_cold.copy()
        self.stream_out_C = Outlet_cold.copy() if Outlet_cold is not None else Inlet_cold.copy()

        if MassRatio is None:
            if self.stream_in_H.m > 0 and self.stream_in_C.m > 0:
                self.MassRatio = self.stream_in_C.m / self.stream_in_H.m
                inputs_mask.insert(0, 1)
            else:
                msg = "\nThe mass rate of one or both streams has been defined as zero. Please specify a valid mass rate"
                raise ValueError(msg)
        elif MassRatio < 0:
            self.MassRatio = MassRatio
            inputs_mask.insert(0, 0)
        else:
            self.MassRatio = MassRatio
            inputs_mask.insert(0, 1)

        input_counter = sum(inputs_mask)

        if 4 < input_counter < 2:

            if input_counter < 2:
                msg = "Insufficient boundary conditions have been defined. Received {} but at least 2 were expected.".format(input_counter)
                raise ValueError(msg)
            else:
                msg = "Too many boundary conditions have been defined. Received {} but at most 4 were expected".format(input_counter)
                raise ValueError(msg)

        self.calculation_mode = inputs_mask

    def plot(self) -> NoReturn:
        """
        plots the heat exchanger duty profile

        Returns
        -------
        NoReturn

        """

        plt.plot(self.Duty_profile[1], self.T_profile[0], "r", label="Hot")
        plt.plot(self.Duty_profile[1], self.T_profile[1], "b", label="Cold")
        plt.xlabel("Duty, J")
        plt.ylabel("Temperature, K")
        plt.legend()

        plt.show()

    def calc(self) -> tuple["MaterialStream", "MaterialStream"]:
        """
        calculates the heat exchanger performance

        Returns
        -------
        tuple["MaterialStream", "MaterialStream"]

        Raises
        ------
        ValueError
            the calculation mode is not recognised

        """

        match self.calculation_mode:

            case [0, 1, 1, 1, 1]:
                # Inlet Hot, Outlet Hot, Inlet Cold and Outlet Cold are defined
                # Searching for:
                #  - MassRatio

                streams = self.__calc_R()

            case [1, 0, 1, 1, 1]:
                # MassRatio, Outlet Hot, Inlet Cold and Outlet Cold are defined
                # Searching for:
                #  - Inlet Hot

                streams =  self.__calc_Tih()

            case [1, 1, 0, 1, 1]:
                # MassRatio, Inlet Hot, Inlet Cold and Outlet Cold are defined
                # Searching for:
                #  - Outlet Hot

                streams =  self.__calc_Toh()

            case [1, 1, 1, 0, 1]:
                # MassRatio, Inlet Hot, Outlet Hot and Outlet Cold are defined
                # Searching for:
                #  - Inlet Cold

                streams =  self.__calc_Tic()

            case [1, 1, 1, 1, 0]:
                # MassRatio, Inlet Hot, Outlet Hot and Inlet Cold are defined
                # Searching for:
                #  - Outlet Cold

                streams =  self.__calc_Toc()

            case [1, 1, 0, 1, 0]:
                # MassRatio, Inlet Hot Stream and Outlet Cold Stream are defined
                # Searching for:
                #  - Outlet Hot Stream
                #  - Outlet Cold Stream

                # Equivalent to wopycle "heat exchanger" component

                streams =  self.__calc_Toh_Toc()

            case [1, 1, 0, 0, 1]:
                # MassRatio, Inlet Hot Stream and Outlet Cold Streams are defined
                # Searching for:
                #  - Outlet Hot Stream
                #  - Inlet Cold Stream

                streams =  self.__calc_Toh_Tic()

            case [1, 0, 1, 1, 0]:
                # MassRatio, Outlet Hot Stream and Inlet Cold Stream are defined
                # Searching for:
                #  - Inlet Hot Stream
                #  - Outlet Cold Stream

                streams =  self.__calc_Tih_Toc()

            case [1, 0, 1, 0, 1]:
                # MassRatio, Outlet Hot Stream and Outlet Cold Stream are defined
                # Searching for:
                #  - Inlet Hot Stream
                #  - Inlet Cold Stream

                streams =  self.__calc_Tih_Tic()

            case [0, 1, 1, 1, 0]:
                # Inlet Hot Stream, Outlet Hot Stream and Outlet Cold Streams are defined
                # Searching for:
                #  - MassRatio
                #  - Outlet Cold Stream

                streams =  self.__calc_R_Toc()

            case [0, 1, 1, 0, 1]:
                # Inlet Hot Stream, Outlet Hot Stream and Outlet Cold Stream are defined
                # Searching for:
                #  - MassRatio
                #  - Inlet Cold Stream

                # Equivalent to wopycle's "HRSG_highP" component

                streams =  self.__calc_R_Tic()

            case[0, 1, 0, 1, 1]:
                # Inlet Hot Stream, Inlet Cold Stream and Outlet Cold Streams are defined
                # Searching for:
                #  - MassRatio
                #  - Outlet Hot Stream

                # Equivalent to wopycle's "HRSG" or "HRSG_preheater" components

                streams =  self.__calc_R_Toh()

            case [0, 0, 1, 1, 1]:
                # Outlet Hot Stream, Inlet Cold Stream and Outlet Cold Stream are defined
                # Searching for:
                #  - MassRatio
                #  - Inlet Hot Stream

                # Equivalent to wopycle's "Condenser" component

                streams =  self.__calc_R_Tih()

            case _:
                msg = "the calculation mode has not been recognised"
                raise ValueError(msg)

        self.__validate_PP()

        self.__get_results()

        return self.stream_out_H.copy(), self.stream_out_C.copy()

    def __validate_cold_side(self):
        T_in_C = self.stream_in_C.properties.T
        T_out_H = self.stream_out_H.properties.T

        if T_out_H - T_in_C < 0.999*self.deltaT_pinch:
            msg = "The temperature approach at the cold side is below the pinch temperature difference"
            raise ValueError(msg)

    def __validate_hot_side(self):
        T_out_C = self.stream_out_C.properties.T
        T_in_H = self.stream_in_H.properties.T

        if (T_in_H - T_out_C - self.deltaT_pinch) / self.deltaT_pinch < -0.005:
            msg = "The temperature approach at the hot side is below the pinch temperature difference"
            raise ValueError(msg)

    def __validate_inlet(self):
        T_in_C = self.stream_in_C.properties.T
        T_in_H = self.stream_in_H.properties.T

        if (T_in_H - T_in_C - self.deltaT_pinch) / self.deltaT_pinch < -0.005:
            msg = "The temperature approach between the hot and cold inlet streams is below the pinch temperature difference"
            raise ValueError(msg)

    def __validate_PP(self):

        if (self.min_deltaT - self.deltaT_pinch) / (self.deltaT_pinch + 1e-6) < -1e4:
            msg = "The calculated minimum temperature difference, {:.2e},  is below the specified target, {:.2e}".format(self.min_deltaT, self.deltaT_pinch)
            raise ValueError(msg)

    def __get_stream_props(self, stream):
        return stream.properties.H, stream.properties.T, stream.properties.P, stream.properties.Q, stream.properties.S

    def __get_results(self):
        h_in_C, T_in_C, P_in_C, Q_in_C, S_in_C = self.__get_stream_props(self.stream_in_C)
        h_out_C, T_out_C, P_out_C, Q_out_C, S_out_C = self.__get_stream_props(self.stream_out_C)

        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(self.stream_in_H)
        h_out_H, T_out_H, P_out_H, Q_out_H, S_out_H = self.__get_stream_props(self.stream_out_H)

        self.inlet = [self.stream_in_H, self.stream_in_C]
        self.inlet_P = [P_in_H, P_in_C]
        self.inlet_H = [h_in_H, h_in_C]
        self.inlet_T = [T_in_H, T_in_C]
        self.inlet_Q = [Q_in_H, Q_in_C]
        self.inlet_S = [S_in_H, S_in_C]

        self.outlet = [self.stream_out_H, self.stream_out_C]
        self.outlet_P = [P_out_H, P_out_C]
        self.outlet_H = [h_out_H, h_out_C]
        self.outlet_T = [T_out_H, T_out_C]
        self.outlet_Q = [Q_out_H, Q_out_C]
        self.outlet_S = [S_out_H, S_out_C]

        self.hot_side = [self.stream_in_H, self.stream_out_C]
        self.hot_side_P = [P_in_H, P_out_C]
        self.hot_side_H = [h_in_H, h_out_C]
        self.hot_side_T = [T_in_H, T_out_C]
        self.hot_side_Q = [Q_in_H, Q_out_C]
        self.hot_side_S = [S_in_H, S_out_C]

        self.cold_side = [self.stream_out_H, self.stream_in_C]
        self.cold_side_P = [P_out_H, P_in_C]
        self.cold_side_H = [h_out_H, h_in_C]
        self.cold_side_T = [T_out_H, T_in_C]
        self.cold_side_Q = [Q_out_H, Q_in_C]
        self.cold_side_S = [S_out_H, S_in_C]

        H_H = self.H_profile[0]
        H_C = self.H_profile[1]

        self.Duty_profile = [-(H_H - H_H[0]), (H_C - H_C[0]) * self.MassRatio]

        cold = self.stream_in_C.copy()
        hot = self.stream_in_H.copy()

        self.S_profile = [np.zeros(self.N), np.zeros(self.N)]
        self.Q_profile = [np.zeros(self.N), np.zeros(self.N)]
        for i, p in enumerate(self.P_profile[0]):
            hot.update("PH", self.P_profile[0][i], self.H_profile[0][i])
            cold.update("PH", self.P_profile[1][i], self.H_profile[1][i])

            self.S_profile[0][i] = hot.properties.S
            self.S_profile[1][i] = cold.properties.S

            self.Q_profile[0][i] = hot.properties.Q
            self.Q_profile[1][i] = cold.properties.Q

    def __calc_R(self) -> NoReturn:
        """
        helper function to calculate the mass ratio

        Returns
        -------
        NoReturn

        """

        self.__validate_cold_side()
        self.__validate_hot_side()

        h_in_H = self.stream_in_H.properties.H
        h_out_H = self.stream_out_H.properties.H
        deltaH_H = h_in_H - h_out_H

        h_in_C = self.stream_in_C.properties.H
        h_out_C = self.stream_out_C.properties.H
        deltaH_C = h_out_C - h_in_C

        self.MassRatio = deltaH_H / deltaH_C

        self.__calc_PP1()

    def __calc_Tih(self) -> NoReturn:
        """
        Helper function to calculate the hot inlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_cold_side()

        h_in_C = self.stream_in_C.properties.H
        h_out_C = self.stream_out_C.properties.H
        deltaH_C = h_out_C - h_in_C

        delta_H_H = self.MassRatio * deltaH_C
        h_out_H = self.stream_out_H.properties.H
        P_out_H = self.stream_out_H.properties.P

        h_in_H = h_out_H + delta_H_H
        P_in_H = P_out_H + self.deltaP_hot

        temp_hot = self.stream_out_H.copy()
        temp_hot.update("PH", P_in_H, h_in_H)
        self.stream_in_H = temp_hot

        self.__calc_PP1()

    def __calc_Toh(self) -> NoReturn:
        """
        Helper function to calculate the hot outlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_hot_side()

        h_in_C = self.stream_in_C.properties.H
        h_out_C = self.stream_out_C.properties.H
        deltaH_C = h_out_C - h_in_C

        delta_H_H = self.MassRatio * deltaH_C
        h_in_H = self.stream_in_H.properties.H
        P_in_H = self.stream_in_H.properties.P

        h_out_H = h_in_H - delta_H_H
        P_out_H = P_in_H - self.deltaP_hot

        temp_hot = self.stream_in_H.copy()
        temp_hot.update("PH", P_out_H, h_out_H)
        self.stream_out_H = temp_hot

        self.__calc_PP1()

    def __calc_Tic(self) -> NoReturn:
        """
        Helper function to calculate the cold inlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_hot_side()

        h_in_H = self.stream_in_H.properties.H
        h_out_H = self.stream_out_H.properties.H
        deltaH_H = h_in_H - h_out_H

        delta_H_C = deltaH_H / self.MassRatio
        h_out_C = self.stream_out_C.properties.H
        P_out_C = self.stream_out_C.properties.P

        h_in_C = h_out_C - delta_H_C
        P_in_C = P_out_C + self.deltaP_cold

        temp_cold = self.stream_out_C.copy()
        temp_cold.update("PH", P_in_C, h_in_C)
        self.stream_in_C = temp_cold

        self.__calc_PP1()

    def __calc_Toc(self) -> NoReturn:
        """
        Helper function to calculate the cold outlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_cold_side()

        h_in_H = self.stream_in_H.properties.H
        h_out_H = self.stream_out_H.properties.H
        deltaH_H = h_in_H - h_out_H

        delta_H_C = deltaH_H / self.MassRatio
        h_in_C = self.stream_in_C.properties.H
        P_in_C = self.stream_in_C.properties.P

        h_out_C = h_in_C + delta_H_C
        P_out_C = P_in_C - self.deltaP_cold

        temp_cold = self.stream_in_C.copy()
        temp_cold.update("PH", P_out_C, h_out_C)
        self.stream_out_C = temp_cold

        self.__calc_PP1()

    def __calc_PP1(self) -> NoReturn:
        """
        Helper function to calculate the pinch point temperature approach

        Returns
        -------
        NoReturn

        """

        # calculate the profiles
        P_H = np.linspace(self.stream_out_H.properties.P, self.stream_in_H.properties.P, self.N)
        H_H = np.linspace(self.stream_out_H.properties.H, self.stream_in_H.properties.H, self.N)
        T_H = np.zeros(self.N)

        temp_hot = self.stream_out_H.copy()
        for i, p in enumerate(P_H):
            temp_hot.update("PH", p, H_H[i])
            T_H[i] = temp_hot.properties.T

        P_C = np.linspace(self.stream_in_C.properties.P, self.stream_out_C.properties.P, self.N)
        H_C = np.linspace(self.stream_in_C.properties.H, self.stream_out_C.properties.H, self.N)
        T_C = np.zeros(self.N)

        temp_cold = self.stream_out_C.copy()
        for i, p in enumerate(P_C):
            temp_cold.update("PH", p, H_C[i])
            T_C[i] = temp_cold.properties.T

        self.P_profile = [P_H, P_C]
        self.H_profile = [H_H, H_C]
        self.T_profile = [T_H, T_C]

        DT = T_H - T_C

        self.min_deltaT = min(DT)

    def __calc_Toh_Tic(self) -> NoReturn:
        """
        Helper function to calculate the hot outlet temperature and cold inlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_hot_side()

        # get calculation inputs
        temp_hot = self.stream_in_H.copy()
        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(temp_hot)
        P_out_H = P_in_H - self.deltaP_hot

        temp_cold = self.stream_out_C.copy()
        h_out_C, T_out_C, P_out_C, Q_out_C, S_out_C = self.__get_stream_props(temp_cold)
        P_in_C = P_out_C + self.deltaP_cold

        # calculate the minimum enthalpy of the hot stream (i.e. T_out_H = T_in_C)
        temp_hot.update("PT", P_out_H, self.Tambient)
        h_out_H_min = temp_hot.properties.H
        Q_out_H_min = temp_hot.properties.Q

        # calculate the maximum enthalpy of the cold stream (i.e. T_out_C = T_in_H)
        temp_cold.update("PT", P_in_C, self.Tambient)
        h_in_C_min = temp_cold.properties.H
        Q_in_C_min = temp_cold.properties.Q

        # generating the temperature tables
        self._T_PHtable_H = self.__generate_splines(P_out_H, P_in_H, h_out_H_min, h_in_H, Q_in_H, Q_out_H_min, temp_hot)
        self._T_PHtable_C = self.__generate_splines(P_out_C, P_in_C, h_in_C_min, h_out_C, Q_out_C, Q_in_C_min, temp_cold)

        deltaH_H_max = h_in_H - h_out_H_min
        deltaH_C_max = h_out_C - h_in_C_min
        deltaQ_C_max = deltaH_C_max * self.MassRatio

        if deltaH_H_max > deltaQ_C_max:
            deltaH_H_max = deltaQ_C_max

        DQ_line = np.linspace(deltaH_H_max, 0, 10)

        def ___calc_PP(deltaQ) -> float:
            deltaH_H = deltaQ * 1.0
            deltaH_C = deltaQ / self.MassRatio

            self.stream_out_H.update("PH", P_out_H, h_in_H - deltaH_H)
            self.stream_in_C.update("PH", P_in_C, h_out_C - deltaH_C)

            return self.__calc_PP2()

        for i, DQ in enumerate(DQ_line):
            deltaT_pinch_error = ___calc_PP(DQ)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DQ_line[i - 1], DQ_line[i]])
                DQ_pinch = solution.root

                break

    def __calc_Toh_Toc(self) -> NoReturn:
        """
        Helper function to calculate the hot outlet temperature and cold outlet temperature

        Returns
        -------
        NoReturn

        """

        # MassRatio, Inlet Hot Stream and Outlet Cold Stream are defined
        # Searching for:
        #  - Outlet Hot Stream
        #  - Outlet Cold Stream

        self.__validate_inlet()

        temp_hot = self.stream_in_H.copy()
        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(temp_hot)
        P_out_H = P_in_H - self.deltaP_hot

        temp_cold = self.stream_in_C.copy()
        h_in_C, T_in_C, P_in_C, Q_in_C, S_in_C = self.__get_stream_props(temp_cold)
        P_out_C = P_in_C - self.deltaP_cold

        # calculate the minimum enthalpy of the hot stream (i.e. T_out_H = T_in_C)
        temp_hot.update("PT", P_out_H, T_in_C)
        h_out_H_min = temp_hot.properties.H
        Q_out_H_min = temp_hot.properties.Q

        # calculate the maximum enthalpy of the cold stream (i.e. T_out_C = T_in_H)
        temp_cold.update("PT", P_out_C, T_in_H)
        h_out_C_max = temp_cold.properties.H
        Q_out_C_max = temp_cold.properties.Q

        # generating the temperature tables
        self._T_PHtable_H = self.__generate_splines(P_out_H, P_in_H, h_out_H_min, h_in_H, Q_in_H, Q_out_H_min, temp_hot)
        self._T_PHtable_C = self.__generate_splines(P_out_C, P_in_C, h_in_C, h_out_C_max, Q_in_C, Q_out_C_max, temp_cold)

        DQ_line = np.linspace(0, h_in_H - h_out_H_min, 10)

        def ___calc_PP(deltaQ) -> float:
            deltaH_H = deltaQ * 1.0
            deltaH_C = deltaQ / self.MassRatio

            self.stream_out_H.update("PH", P_out_H, h_in_H - deltaH_H)
            self.stream_out_C.update("PH", P_out_C, h_in_C + deltaH_C)

            return self.__calc_PP2()

        for i, DQ in enumerate(DQ_line):
            deltaT_pinch_error = ___calc_PP(DQ)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DQ_line[i - 1], DQ_line[i]])
                DQ_pinch = solution.root

                break

    def __calc_R_Toc(self) -> NoReturn:
        """
        Helper function to calculate the mass ratio and cold outlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_cold_side()

        temp_hot_in = self.stream_in_H.copy()
        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(temp_hot_in)

        temp_hot_out = self.stream_out_H.copy()
        h_out_H, T_out_H, P_out_H, Q_out_H, S_out_H = self.__get_stream_props(temp_hot_out)
        self.deltaP_hot = P_in_H - P_out_H

        temp_cold = self.stream_in_C.copy()
        h_in_C, T_in_C, P_in_C, Q_in_C, S_inC = self.__get_stream_props(temp_cold)
        P_out_C = P_in_C - self.deltaP_cold

        # the profile is already defined for the hot stream
        self.P_profile[0] = np.linspace(P_out_H, P_in_H, self.N)
        self.H_profile[0] = np.linspace(h_out_H, h_in_H, self.N)
        self.T_profile[0] = np.zeros(self.N)
        for i, p in enumerate(self.P_profile[0]):
            temp_hot_out.update("PH", p, self.H_profile[0][i])
            self.T_profile[0][i] = temp_hot_out.properties.T

        # calculate the maximum enthalpy of the cold stream (i.e. T_out_C = T_in_H)
        temp_cold.update("PT", P_out_C, T_in_H)
        h_out_C_max = temp_cold.properties.H
        Q_out_C_max = temp_cold.properties.Q

        # generating the temperature tables
        self._T_PHtable_C = self.__generate_splines(P_out_C, P_in_C, h_in_C, h_out_C_max, Q_in_C, Q_out_C_max, temp_cold)

        deltaH_H = h_in_H - h_out_H
        deltaH_C_max = h_out_C_max - h_in_C
        self.MassRatio = deltaH_H / deltaH_C_max
        self.deltaQ = deltaH_H

        DH_line = np.linspace(deltaH_C_max, 0, 10)

        def ___calc_PP(deltaH_C) -> float:

            deltaH_H = h_in_H - h_out_H

            self.MassRatio = deltaH_H / (deltaH_C + 1e-6)

            self.stream_out_C.update("PH", P_out_C, h_in_C + deltaH_C)

            return self.__calc_PP2()

        for i, DH in enumerate(DH_line):
            deltaT_pinch_error = ___calc_PP(DH)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DH_line[i - 1], DH_line[i]])
                DH = solution.root

                break

        if DH == 0.0:
            raise ValueError("Heat Exchanger has zero duty")

    def __calc_R_Toh(self) -> NoReturn:

        """
        Helper function to calculate the mass ratio and hot outlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_hot_side()

        temp_cold_in = self.stream_in_C.copy()
        h_in_C, T_in_C, P_in_C, Q_in_C, S_in_C = self.__get_stream_props(temp_cold_in)

        temp_cold_out = self.stream_out_C.copy()
        h_out_C, T_out_C, P_out_C, Q_out_C, S_out_C = self.__get_stream_props(temp_cold_out)
        self.deltaP_cold = P_in_C - P_out_C

        temp_hot = self.stream_in_H.copy()
        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(temp_hot)
        P_out_H = P_in_H - self.deltaP_hot

        # the profile is already defined for the cold stream
        self.P_profile[1] = np.linspace(P_in_C, P_out_C, self.N)
        self.H_profile[1] = np.linspace(h_in_C, h_out_C, self.N)
        self.T_profile[1] = np.zeros(self.N)
        for i, p in enumerate(self.P_profile[1]):
            temp_cold_out.update("PH", p, self.H_profile[1][i])
            self.T_profile[1][i] = temp_cold_out.properties.T

        # calculate the maximum enthalpy of the cold stream (i.e. T_out_C = T_in_H)
        temp_hot.update("PT", P_out_H, T_in_C)
        h_out_H_min = temp_hot.properties.H
        Q_out_H_min = temp_hot.properties.Q

        # generating the temperature tables
        self._T_PHtable_H = self.__generate_splines(P_out_H, P_in_H, h_out_H_min, h_in_H, Q_in_H, Q_in_H, temp_hot)

        deltaH_C = h_out_C - h_in_C
        deltaH_H_max = h_in_H - h_out_H_min
        self.MassRatio = deltaH_H_max / deltaH_C
        self.deltaQ = deltaH_C

        DH_line = np.linspace(0, deltaH_H_max, 10)

        def ___calc_PP(deltaH) -> float:

            self.MassRatio = deltaH / (deltaH_C + 1e-6)

            self.stream_out_H.update("PH", P_out_H, h_in_H - deltaH)

            error = self.__calc_PP2()

            return error

        for i, DH in enumerate(DH_line):
            deltaT_pinch_error = ___calc_PP(DH)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DH_line[i - 1], DH_line[i]])
                DH_pinch = solution.root

                break

    def __calc_R_Tic(self) -> NoReturn:

        """
        Helper function to calculate the mass ratio and cold inlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_hot_side()

        temp_hot_in = self.stream_in_H.copy()
        h_in_H, T_in_H, P_in_H, Q_in_H, S_in_H = self.__get_stream_props(temp_hot_in)

        temp_hot_out = self.stream_out_H.copy()
        h_out_H, T_out_H, P_out_H, Q_out_H, S_out_H = self.__get_stream_props(temp_hot_out)
        self.deltaP_hot = P_in_H - P_out_H

        temp_cold = self.stream_out_C.copy()
        h_out_C, T_out_C, P_out_C, Q_out_C, S_out_C = self.__get_stream_props(temp_cold)
        P_in_C = P_out_C + self.deltaP_cold

        # the profile is already defined for the hot stream
        temp_hot = self.stream_in_H.copy()
        self.P_profile[0] = np.linspace(P_out_H, P_in_H, self.N)
        self.H_profile[0] = np.linspace(h_out_H, h_in_H, self.N)
        self.T_profile[0] = np.zeros(self.N)
        for i, p in enumerate(self.P_profile[0]):
            temp_hot.update("PH", p, self.H_profile[0][i])
            self.T_profile[0][i] = temp_hot.properties.T

        # self.Duty_profile = [H_H[0] - H_H, 0]

        # calculate the minimum enthalpy of the cold stream (i.e. T_in_C = T_ambient)
        temp_cold.update("PT", P_in_H, self.Tambient)
        h_in_C_min = temp_cold.properties.H
        Q_in_C_min = temp_cold.properties.Q

        # generating the temperature tables
        self._T_PHtable_C = self.__generate_splines(P_out_C, P_in_C, h_in_C_min, h_out_C, Q_out_C, Q_in_C_min, temp_cold)

        deltaH_H = h_in_H - h_out_H
        deltaH_C_max = h_out_C - h_in_C_min
        self.MassRatio = deltaH_C_max / deltaH_H
        self.deltaQ = deltaH_H

        DH_line = np.linspace(0, deltaH_C_max,  10)

        def ___calc_PP(deltaH_C) -> float:

            self.MassRatio = deltaH_H / (deltaH_C + 1e-6)

            self.stream_in_C.update("PH", P_in_C, h_out_C - deltaH_C)

            return self.__calc_PP2()

        for i, DH in enumerate(DH_line):
            deltaT_pinch_error = ___calc_PP(DH)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DH_line[i - 1], DH_line[i]])
                DH_pinch = solution.root

                break

    def __calc_R_Tih(self) -> NoReturn:

        """
        Helper function to calculate the mass ratio and hot inlet temperature

        Returns
        -------
        NoReturn

        """

        self.__validate_cold_side()

        temp_cold_in = self.stream_in_C.copy()
        h_in_C, T_in_C, P_in_C, Q_in_C, S_in_C = self.__get_stream_props(temp_cold_in)

        temp_cold_out = self.stream_out_C.copy()
        h_out_C, T_out_C, P_out_C, Q_out_C, S_out_C = self.__get_stream_props(temp_cold_out)
        self.deltaP_cold = P_in_C - P_out_C

        temp_hot = self.stream_out_H.copy()
        h_out_H, T_out_H, P_out_H, Q_out_H, S_out_H = self.__get_stream_props(temp_hot)
        P_in_H = P_out_H + self.deltaP_hot

        # the profile is already defined for the cold stream
        self.P_profile[1] = np.linspace(P_in_C, P_out_C, self.N)
        self.H_profile[1] = np.linspace(h_in_C, h_out_C, self.N)
        self.T_profile[1] = np.zeros(self.N)
        for i, p in enumerate(self.P_profile[1]):
            temp_cold_out.update("PH", p, self.H_profile[1][i])
            self.T_profile[1][i] = temp_cold_out.properties.T

        # calculate the maximum enthalpy of the cold stream (i.e. T_out_C = T_in_H)
        temp_hot.update("PT", P_in_C, self.Tmaximum)
        h_in_H_max = temp_hot.properties.H
        Q_in_H_max = temp_hot.properties.Q

        # generating the temperature tables
        self._T_PHtable_H = self.__generate_splines(P_out_H, P_in_H, h_out_H, h_in_H_max, Q_in_H_max, Q_out_H, temp_hot)

        deltaH_C = h_out_C - h_in_C
        deltaH_H_max = h_in_H_max - h_out_H
        self.MassRatio = deltaH_H_max / deltaH_C
        self.deltaQ = deltaH_C

        DH_line = np.linspace(0, deltaH_H_max, 10)

        def ___calc_PP(deltaH_H) -> float:

            self.MassRatio = deltaH_H / deltaH_C

            self.stream_in_H.update("PH", P_in_H, h_out_H + deltaH_H)

            return self.__calc_PP2()

        for i, DH in enumerate(DH_line):
            deltaT_pinch_error = ___calc_PP(DH)
            if deltaT_pinch_error > 0:  # The error starts with negative sign and as soon as it switches to positive the calculated temperature distribution provides a DTpp which is close (actually already smaller) to the desired value of DTpp.

                solution = root_scalar(___calc_PP, method="brentq", bracket=[DH_line[i - 1], DH_line[i]])
                DH_pinch = solution.root

                break

    def __calc_Tih_Toc(self):

        raise NotImplementedError

        pass

    def __calc_Tih_Tic(self):

        raise NotImplementedError

        pass

    def __calc_PP2(self) -> float:
        """
        Helper function to calculate the pinch point temperature approach

        Returns
        -------
        NoReturn

        """

        if self._T_PHtable_H is None:
            # calculate the profiles
            P_H = self.P_profile[0]
            H_H = self.H_profile[0]
            T_H = self.T_profile[0]
        else:
            T_H, P_H, H_H = self.__interp_PH_line(self.stream_out_H.properties.P, self.stream_in_H.properties.P,
                                                  self.stream_out_H.properties.H, self.stream_in_H.properties.H,
                                                  self._T_PHtable_H)

        if self._T_PHtable_C is None:
            # calculate the profiles
            P_C = self.P_profile[1]
            H_C = self.H_profile[1]
            T_C = self.T_profile[1]

        else:
            T_C, P_C, H_C, = self.__interp_PH_line(self.stream_out_C.properties.P, self.stream_in_C.properties.P,
                                                   self.stream_in_C.properties.H, self.stream_out_C.properties.H,
                                                   self._T_PHtable_C)

        self.P_profile = [P_H, P_C]
        self.H_profile = [H_H, H_C]
        self.T_profile = [T_H, T_C]

        DT = T_H - T_C

        self.min_deltaT = min(DT)

        result = (min(DT) - 0.995*self.deltaT_pinch) / (0.995*self.deltaT_pinch)

        return result

    def __generate_splines(self,
                          Pmin: float,
                          Pmax: float,
                          hmin: float,
                          hmax: float,
                          Q1: float,
                          Q2: float,
                          stream: "MaterialStream") -> scipy.interpolate.RectBivariateSpline:

        """
        Helper function to generate the interpolation tables

        Parameters
        ----------
        Pmin: float
            the minimum pressure
        Pmax: float
            the maximum pressure
        hmin: float
            the minimum specific enthalpy
        hmax: float
            the maximum specific enthalpy
        stream: MaterialStream
            the hot or cold stream

        Returns
        -------
        tuple[np.array, np.array, np.array]

        Raises
        ------
        NotImplemented
            tablemode is not recognised

        """

        hs = np.linspace(hmin, hmax, self.N, endpoint=True)
        Ps = np.linspace(Pmin, Pmax+1e-4, 2, endpoint=True)

        Ts = np.zeros((len(Ps), len(hs)))

        delta_h = abs(hmax - hmin)
        delta_p = abs(Pmax - Pmin)

        corr_h = 1/(hmax - hmin) if delta_h > 0 else 1e-4
        corr_p = 1/(Pmax - Pmin) if delta_p > 0 else 1e-4
        corr_i = 1/self.N

        # calculating the temperature for each point in the enthalpy-pressure table
        if self.tablemode == "PH":
            for i, p in enumerate(Ps):
                for j, h in enumerate(hs):
                    stream.update("PH", p, h)

                    corr = 1e-4 * (h * corr_h + p * corr_p)

                    Ts[i, j] = stream.properties.T + corr  # just adding a little bit of gradient
        elif self.tablemode == "PT":
            stream.update("PH", Pmin, hmin)
            Tmin = stream.properties.T
            stream.update("PH", Pmax, hmax)
            Tmax = stream.properties.T

            temp_ts = np.linspace(Tmin, Tmax, self.N)
            temp_hs = np.zeros(self.N)
            for i, p in enumerate(Ps):
                for j, t in enumerate(temp_ts):
                    stream.update("PT", p, t)
                    temp_hs[j] = stream.properties.H

                interp = scipy.interpolate.interp1d(temp_hs, temp_ts, fill_value="extrapolate")

                corr = 1e-4 * (hs * corr_h + p * corr_p + i * corr_i)

                Ts[i] = interp(hs)
                Ts[i] += corr

                # fig, ax = plt.subplots()
                # ax.plot(temp_ts, temp_hs, "bo")
                # ax.plot(Ts[i], hs,"ro")
                # plt.show()
        else:
            raise NotImplementedError

        k_y = 1 if Q1 == Q2 else 3

        spline = scipy.interpolate.RectBivariateSpline(Ps, hs, Ts, kx=1, ky=k_y)

        return spline

    def __interp_PH_line(self,
                         P1: float,
                         P2: float,
                         h1: float,
                         h2: float,
                         table: np.array) -> tuple[np.array, np.array, np.array]:
        """
        Helper function to interpolate the tables along a profile along the fluid's path through the heat exchanger

        Parameters
        ----------
        P1: float
            pressure at point 1, in Pa
        P2: float
            pressure at point 2, in Pa
        h1: float
            specific enthalpy at point 1, in J/kg
        h2: float
            specific enthalpy at point 2, in J/kg
        table: np.array
            the interpolation table

        Returns
        -------
        tuple[np.array, np.array, np.array]

        """

        P = np.linspace(P1, P2, self.N, endpoint=True)
        h = np.linspace(h1, h2, self.N, endpoint=True)

        # this performs the interpolation for each P and h point
        T = [table(p, h[i])[0][0] for i, p in enumerate(P)]
        T = np.array(T)

        return T, P, h

    def __interp_PH_point(self, P: float, h: float, table: np.array) -> tuple[float, float, float]:
        """
        Helper function to interpolate the tables for a point in the heat exchanger

        Parameters
        ----------
        P: float
            the pressure
        h: float
            the specific enthalpy
        table: np.array
            the interpolation table

        Returns
        -------
        tuple[float, float, float]
        """

        # this performs the interpolation for each P and h point
        T = table(P, h)[0][0]

        return T, P, h

    def calc_exergy_balance(self):

        self.Ein_hot = self.inlet[0].m * (self.inlet[0].properties.H - Tref * self.inlet[0].properties.S)
        self.Ein_cold = self.inlet[1].m * (self.inlet[1].properties.H - Tref * self.inlet[1].properties.S)

        self.Eout_hot = self.outlet[0].m * (self.outlet[0].properties.H - Tref * self.outlet[0].properties.S)
        self.Eout_cold = self.outlet[1].m * (self.outlet[1].properties.H - Tref * self.outlet[1].properties.S)

        self.Ein = self.Ein_hot + self.Ein_cold
        self.Eout = self.Eout_hot + self.Eout_cold

        self.Eloss = self.Ein - self.Eout

        # print("in: {} out: {} loss:{}".format(self.Ein, self.Eout, self.Eloss))
        # print("hot: {} {} cold: {} {}".format(self.Ein_hot, self.Eout_hot, self.Ein_cold, self.Eout_cold))

    def update_inlet_rate(self, m_hot, m_cold):

        self.inlet[0]._update_quantity(m_hot)
        self.outlet[0]._update_quantity(m_hot)

        self.inlet[1]._update_quantity(m_cold)
        self.outlet[1]._update_quantity(m_cold)

    def calc_cost(self):

        deltaTs = self.T_profile[0] - self.T_profile[1]
        lmtds = deltaTs[:-1] * 1
        for i, lmtd in enumerate(lmtds):
            if deltaTs[i+1] != deltaTs[i] and deltaTs[i+1] != 0:
                lmtds[i] = (deltaTs[i] - deltaTs[i+1]) / math.log(deltaTs[i] / deltaTs[i+1])
            elif deltaTs[i+1] != 0:
                lmtds[i] = deltaTs[i+1]
            else:
                raise ValueError

        duty = self.Duty_profile[1] * self.inlet[0].m
        deltaDuty = duty[1:] - duty[:-1]

        self.UA_profile = deltaDuty / lmtds
        self.UA = np.sum(self.UA_profile)

        if self.U is None and self.cost_model not in ["recuperator"]:
            self.U = self.__calc_U()
        else:
            self.U = 1000

        self.A = self.UA / self.U

        match self.cost_model:

            case "default":
                cost = 1

                pass

            case "condenser-astolfi":
                # using the correlations for U and cost from Astolfi et al. 2014
                # DOI: http://dx.doi.org/10.1016/j.energy.2013.11.057

                dT_ap_cond = self.T_profile[0][0] - self.T_profile[1][0]
                dT_pp_cond_star = self.T_profile[0][np.where(deltaTs == self.min_deltaT)] - self.T_profile[1][-1]
                delta = dT_pp_cond_star / dT_ap_cond

                # I am capping the value here because the original correlation was only designed for values of delta up to 0.12...
                # if delta is much higher, given the 2nd order polynomical, U begins to decrease...
                if delta > 0.12:
                    delta = 0.12

                self.U = -9.84e3 * delta * delta + 3.61e3*delta + 9.72e2

                self.A = self.UA / self.U

                cost = 530e3 * math.pow(self.A / 3563, 0.9)  # cost presumably in €2013

                exchange_rate = Simulator.convert_EUR_to_USD(1, 2013)
                corr_PPI = Simulator.calc_PPI("heat_exchanger", Simulator.Yref) / Simulator.calc_PPI("heat_exchanger", 2013)
                corr = exchange_rate * corr_PPI

                cost *= corr


            case "condenser-smith":

                # using the correlation from Smith 2005 "Chemical process design and integration"
                # via Walraven's thesis

                A = self.A * 1.0
                n = 1

                if A < 200:
                    specific_cost = 1.67e5 * math.pow(200/200, 0.89) / 200  # cost in €2013
                    cost = self.A * specific_cost
                elif A > 2000:
                    specific_cost = 1.67e5 * math.pow(2000/200, 0.89) / 2000  # cost in €2013
                    cost = self.A * specific_cost
                else:
                    cost = 1.67e5 * math.pow(A / 200, 0.89)  # cost in €2013

                exchange_rate = Simulator.convert_EUR_to_USD(1, 2013)
                corr_PPI = Simulator.calc_PPI("heat_exchanger", Simulator.Yref) / Simulator.calc_PPI("heat_exchanger", 2013)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case "condenser-GETEM":

                # using the correlation from GETEM

                A = self.A * 1.0
                n = 1

                cost = 768 * math.pow(A, 0.85)

                # exchange_rate = Simulator.convert_EUR_to_USD(1, 2013)
                exchange_rate = 1
                corr_PPI = Simulator.calc_PPI("heat_exchanger", Simulator.Yref) / Simulator.calc_PPI("heat_exchanger", 2002)
                corr = exchange_rate * corr_PPI

                cost *= corr


            case "recuperator":
                # using the correlation for cost from Astolfi et al. 2014
                # DOI: http://dx.doi.org/10.1016/j.energy.2013.11.057

                # pressure correction
                a1 = -0.00164
                a2 = -0.00627
                a3 = 0.0123

                P = max(self.P_profile[0].max(), self.P_profile[1].max())
                logP = math.log10(P/1e5)
                corr = a1 + a2*logP + a3*logP*logP

                cost = 260e3 * math.pow(self.UA / 650e3, 0.9)*math.pow(10, corr)

                exchange_rate = Simulator.convert_EUR_to_USD(1, 2013)
                corr_PPI = Simulator.calc_PPI("heat_exchanger", Simulator.Yref) / Simulator.calc_PPI("heat_exchanger",
                                                                                                     2013)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case "peters-floating":
                # using the correlation for cost from Peters, M. et al. (2003). Heat-Transfer Equipment—Design and Costs.
                # Plant Design and Economics for Chemical Engineers, 5.
                # via genGeo paper

                cost = 239 * self.A + 13400  # cost in $2002

                exchange_rate = 1
                corr_PPI = Simulator.calc_PPI("heat_exchanger", Simulator.Yref) / Simulator.calc_PPI("heat_exchanger",
                                                                                                     2002)
                corr = exchange_rate * corr_PPI

                cost *= corr

        self.cost = cost * 1.0
        return cost

    def __calc_U_old(self):

        resistances = {"water_liquid": 0.000223333333333333,
                       "water_boiling": 0.000232857142857143,
                       "water_vapour": 0.000362162162162162,
                       "water_condensing": 0.000132183908045977,
                       # "water_LP_vapour": 0.00240229885057471,
                       "ORC_liquid": 0.000706315789473684,
                       "ORC_boiling": 0.000706315789473684,
                       "ORC_vapour": 0.000499099099099099,
                       "ORC_condensing": 0.00032183908045977,
                       # "ORC_LP_vapour": 0.00250574712643678,
                       }

        resistance = []

        for i, stream in enumerate(self.inlet):
            x_in = self.inlet[i].properties.Q
            x_out = self.outlet[i].properties.Q
            delta_x = x_out - x_in

            if "water" in stream.fluid.components or "steam" in stream.fluid.components:
                fluid = "water"
            else:
                fluid = "ORC"

            if delta_x < -0.05:
                process = "condensing"
            elif delta_x > 0.05:
                process = "boiling"
            else:
                if x_in > 0.9:
                    process = "vapour"
                else:
                    process = "liquid"

            resistance.append(resistances[fluid+"_"+process])

        overall_resistance = sum(resistance)
        U = 1/overall_resistance

        return U

    def __calc_U(self):

        fluids = []
        for i, stream in enumerate(self.inlet):
            if "water" in stream.fluid.components or "steam" in stream.fluid.components:
                fluids.append("water")
            elif "air" in stream.fluid.components:
                fluids.append("air")
            else:
                fluids.append("organic")

        U = self.UA_profile * 1
        for i in range(self.N - 1):
            # deltaX_hot = (self.Q_profile[0][i] - self.Q_profile[0][i+1])/(self.Q_profile[0][i] + 1e-6)
            # deltaX_cold = (self.Q_profile[1][-1 - i] - self.Q_profile[1][-2 - i])/(self.Q_profile[1][-1 - i] + 1e-6)

            deltaX_hot = (self.Q_profile[0][i] - self.Q_profile[0][i+1])/(self.Q_profile[0][i] + 1e-6)
            deltaX_cold = (self.Q_profile[1][i+1] - self.Q_profile[1][i])/(self.Q_profile[1][i] + 1e-6)


            if deltaX_hot < -0.001:
                process_hot = "condensing"
            elif (self.Q_profile[0][i]+self.Q_profile[0][i+1])/2 < 0.05:
                process_hot = "liquid"
            else:
                process_hot = "vapour"

            if deltaX_cold > 0.001:
                process_cold = "boiling"
            elif (self.Q_profile[1][i]+self.Q_profile[1][i])/2 < 0.05:
                process_cold = "liquid"
            else:
                process_cold = "vapour"

            U[i] = self.Uvalues[fluids[0] + "_" + fluids[1] + "_" + process_hot + "_" + process_cold]

        self.A = sum(self.UA_profile / U)
        self.U_profile = U * 1

        self.U = self.UA / self.A

        return self.U * 1


def register() -> NoReturn:
    """
    Registers the heat exchanger component

    Returns
    -------
    NoReturn
    """

    factory.register("heat_exchanger", heat_exchanger)