from typing import NoReturn
from .base_component import Component
from Simulator import factory, Tref

import Simulator

import math
import numpy as np


class multistage_compression(Component):

    def __init__(self, isen_eff: float, N: int, cost_model=None, mech_eff=0.95) -> NoReturn:
        """
        instantiates the pump component

        Parameters
        ----------
        isen_eff: float
            the isentropic efficiency

        Returns
        -------
        None
        """

        super().__init__()

        self.eta_isentropic = isen_eff
        self.eta_mechanical = mech_eff
        self.N = N

        self.pump = Simulator.pump(self.eta_isentropic, mech_eff=mech_eff)

        self.Tmax = 273.15 + 200  # the maximum outlet temperature
        self.T_intercool = 273.15 + 25

        self.delta_h = 0.0
        self.delta_s = 0.0

        self.work = 0.0

        if cost_model is None:
            self.cost_model = "default"
        else:
            self.cost_model = cost_model

    def set_inputs(self, inlet_stream: "MaterialStream", Pout: float, findN=False) -> NoReturn:
        """
        sets the inputs for the pump calculation

        Parameters
        ----------
        inlet_stream: MaterialStream
            the inlet stream
        Pout: float
            the outlet pressure

        Returns
        -------
        NoReturn

        """
        self.inlet = inlet_stream.copy()
        self.Pout = Pout

        self.findN = findN

    def calc(self) -> "MaterialStream":
        """
        calculates the pump performance

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            outlet pressure is less than inlet pressure
        ValueError
            the enthalpy change is negative
        ValueError
            the entropy change is negative

        """
        Tout = 1000

        if self.findN:
            n = 0
        else:
            n = self.N-1

        P_in = self.inlet.properties.P
        P_out = self.Pout

        while Tout > self.Tmax and n<10:
            n += 1
            Ps = np.logspace(math.log10(P_in), math.log10(P_out), n + 1)
            temp_stream = self.inlet.copy()
            Q = 0
            W = 0
            pwr = 0
            for i in range(n):
                self.pump.set_inputs(temp_stream, Ps[i + 1])
                try:
                    temp_stream = self.pump.calc()
                except:
                    if self.findN:
                        Tout = self.Tmax + 1
                        break
                    else:
                        msg = "The multistage compression failed to calculate - this is likely because the outlet temperature is too high. Consider additional stages or cooling"
                        raise ValueError(msg)
                Tout = temp_stream.properties.T
                W += self.pump.work
                pwr += self.pump.power_elec

                if i + 1 != n:
                    h1 = temp_stream.properties.H
                    temp_stream.update("PT", temp_stream.properties.P, self.T_intercool)
                    h2 = temp_stream.properties.H
                    Q += h1 - h2

            # Tout = temp_stream.properties.T

            if self.findN is False:
                break

        if Tout > self.Tmax:
            msg = "The multistage_compression could not find a solution with less than 10 stages"
            raise ValueError(msg)

        self.N = n
        self.work = W
        self.power_elec = pwr

        self.cooling = Q

        self.delta_h = temp_stream.properties.H - self.inlet.properties.H
        self.delta_s = temp_stream.properties.S - self.inlet.properties.S

        self.outlet = temp_stream.copy()

        return temp_stream

    def calc_exergy_balance(self):

        # TODO pls fix

        self.Ein = self.inlet.m * (self.inlet.properties.H - Tref * self.inlet.properties.S) + abs(self.work)

        self.Eout = self.outlet.m * (self.outlet.properties.H - Tref * self.outlet.properties.S)

        self.Eloss = self.Ein - self.Eout

        # print(self.Ein, self.Eout, self.Eloss)

    def calc_cost(self):
        match self.cost_model:

            case "default":
                # using the correlations for U and cost from Duc et al. 2007
                # DOI: https://doi.org/10.1016/j.enconman.2006.09.024
                # via genGeo

                cost = 6950 * math.pow(1.34 * abs(self.work)/1000, 0.82)  # cost in $2002

                exchange_rate = 1
                corr_PPI = Simulator.calc_PPI("pump", Simulator.Yref) / Simulator.calc_PPI("pump", 2002)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case _:
                cost = 1

        self.cost = cost * 1.0
        return cost

    def update_inlet_rate(self, m):

        ratio = m / (self.inlet.m + 1e-6)

        self.inlet._update_quantity(m)
        self.outlet._update_quantity(m)

        self.work *= ratio
        self.cooling *= ratio
        self.power_elec *= ratio



def register():
    factory.register("multistage_compression", multistage_compression)