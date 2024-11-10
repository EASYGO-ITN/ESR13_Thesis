from typing import NoReturn
import math

from .base_component import Component
from Simulator import factory
import Simulator
from FluidProperties import Tref


class pump(Component):

    """
    the pump component

    Attributes
    ----------
    eta_isentropic: float
        the isentropic efficiency
    delta_h: float
        the specific enthalpy difference
    delta_s: float
        the specific entropy difference
    eork: float
        the work done
    inlet: MaterialStream
        the inlet stream
    outlet: MaterialStream
        the outlet stream
    Pout: float
        the outlet pressure
    """

    def __init__(self, isen_eff: float, mech_eff=1, cost_model=None) -> NoReturn:
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

        self.delta_h = 0.0
        self.delta_s = 0.0

        self.work = 0.0

        if cost_model is None:
            self.cost_model = "default"
        else:
            self.cost_model = cost_model

    def set_inputs(self, inlet_stream: "MaterialStream", Pout: float) -> NoReturn:
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

        if self.Pout < self.inlet.properties.P:
            msg = "\nThe specified outlet pressure ({:.2e} Pa) is less than the inlet pressure ({:.2e} Pa)".\
                format(self.Pout, self.inlet.properties.P)
            raise ValueError(msg)

        temp_outlet = self.inlet.copy()

        temp_outlet.update("PS", self.Pout, self.inlet.properties.S)

        delta_h_isentropic = temp_outlet.properties.H - self.inlet.properties.H

        if delta_h_isentropic < 0:
            msg = "Pump error: Wrong sign in enthalpy computation"
            raise ValueError(msg)

        h_out = self.inlet.properties.H + delta_h_isentropic / self.eta_isentropic

        temp_outlet.update("PH", self.Pout, h_out)

        self.delta_s = temp_outlet.properties.S - self.inlet.properties.S
        if self.delta_s < 0:
            msg = "Pump error: Wrong sign in entropy computation"
            raise ValueError(msg)

        self.delta_h = temp_outlet.properties.H - self.inlet.properties.H

        self.work = self.delta_h * self.inlet.m

        self.power_elec = self.work / self.eta_mechanical

        self.outlet = temp_outlet.copy()

        return temp_outlet

    def calc_exergy_balance(self):

        self.Ein = self.inlet.m * (self.inlet.properties.H - Tref * self.inlet.properties.S) + abs(self.work)

        self.Eout = self.outlet.m * (self.outlet.properties.H - Tref * self.outlet.properties.S)

        self.Eloss = self.Ein - self.Eout

        # print(self.Ein, self.Eout, self.Eloss)

    def update_inlet_rate(self, m):

        self.inlet._update_quantity(m)
        self.outlet._update_quantity(m)

        self.work = self.delta_h * m
        self.power_elec = self.work / self.eta_mechanical

    def calc_cost(self):

        match self.cost_model:

            case "default":
                # using the correlation for cost from GETEM - circulation pump
                # via genGeo paper

                cost = 1185 * math.pow(1.34 * abs(self.work)/1000, 0.767)  # cost in $2002

                exchange_rate = 1
                corr_PPI = Simulator.calc_PPI("pump", Simulator.Yref) / Simulator.calc_PPI("pump",
                                                                                                     2002)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case "astolfi":
                # using the correlation for cost from Astolfi et al. 2014
                # DOI: http://dx.doi.org/10.1016/j.energy.2013.11.057

                cost = 14000 * math.pow(abs(self.work)/200000, 0.67)

                exchange_rate = Simulator.convert_EUR_to_USD(1, 2013)
                corr_PPI = Simulator.calc_PPI("pump", Simulator.Yref) / Simulator.calc_PPI("pump", 2013)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case "fan":
                # using the correlation from Smith 2005 "Chemical process design and integration"
                # via Walraven's thesis

                work = abs(self.work)

                if work < 20000:
                    specific_cost = 1.31e4 * math.pow(20000/50000, 0.76) / 20000
                    cost = specific_cost * work
                elif work > 200000:
                    specific_cost = 1.31e4 * math.pow(200000/50000, 0.76) / 200000
                    cost = specific_cost * work
                else:
                    cost = 1.31e4 * math.pow(work / 50000, 0.76)

                exchange_rate = Simulator.convert_EUR_to_USD(1, 2005)
                corr_PPI = Simulator.calc_PPI("pump", Simulator.Yref) / Simulator.calc_PPI("pump", 2005)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case _:
                cost = 0

        self.cost = cost * 1.0
        return cost


def register() -> NoReturn:
    """
    Registers the pump component

    Returns
    -------
    NoReturn
    """

    factory.register("pump", pump)
