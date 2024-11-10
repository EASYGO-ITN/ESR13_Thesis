import math
from typing import NoReturn, Optional
import numpy as np
import scipy

from .base_component import Component
from Simulator import factory, convert_EUR_to_USD, calc_PPI, Yref
from FluidProperties import Tref
from FluidProperties.fluid import Fluid


class turbine(Component):

    """
    the turbine component

    Attributes
    ----------
    inlet: MaterialStream
        the inlet stream
    outlet: tuple[MaterialStream]
        the outlet streams
    eta_isentropic: float
        the dry isentropic efficiency
    BaumannCorrection: bool
        flag to indicate whether the Baumann Rule for wet expansion should be applied
    delta_h_isentropic: float
        the specific enthalpy difference following an isentropic expansion
    delta_h_polytropic: float
        the specific enthalpy difference following a real expansion
    delta_h_BaumannCorr: float
        the specific enthalpy difference following a real wet expansion
    delta_h: float
        the specific enthalpy difference
    delta_s: float
        the specific entropy difference
    work: float
        the work done
    Pout: float
        the outlet pressure
    eta_isentropic_app: float
        the apparent isentropic efficiency of a wet expansion
    """

    def __init__(self,
                 isen_eff: float,
                 mech_eff = 0.95,
                 BaumannCorrection: Optional[bool]=False,
                 cost_model=None) -> NoReturn:
        """
        instantiates the turbine component

        Parameters
        ----------
        isen_eff: float
            the dry isentropic efficiency
        BaumannCorrection: bool
            flag to indicate whether the Baumann RUle for wet expansion should be used
        """

        super().__init__()

        self.eta_isentropic = isen_eff
        self.eta_mechanical = mech_eff
        self.BaumannCorrection = BaumannCorrection

        self.delta_h_isentropic = 0.0
        self.delta_h_polytropic = 0.0
        self.delta_h_BaumannCorr = 0.0
        self.delta_h = 0.0

        self.delta_s = 0.0

        self.work = 0.0

        if cost_model is None:
            self.cost_model = "default"
        else:
            self.cost_model = cost_model

    def set_inputs(self,
                   inlet_stream: "MaterialStream",
                   Pout: float) -> NoReturn:
        """
        set the inputs for the turbine performance calculation

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
        calculate the performance of the turbine

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            outlet pressure is larger than inlet pressure
        """

        if self.Pout > self.inlet.properties.P:
            msg = "\nThe specified outlet pressure ({:.2e} Pa) is greater than the inlet pressure ({:.2e} Pa)".\
                format(self.Pout, self.inlet.properties.P)
            raise ValueError(msg)

        if not self.BaumannCorrection:
            temp_outlet = self.__polytropic_expansion()
        else:
            temp_outlet = self.__BaumannRule_expansion()

        self.work = self.delta_h * self.inlet.m
        self.power_elec = self.work * self.eta_mechanical

        self.outlet = temp_outlet.copy()

        return temp_outlet

    def __isentropic_expansion(self, Pout: Optional[float | None]=None) -> "MaterialStream":
        """
        Helper function to calculate an isentropic expansion

        Parameters
        ----------
        Pout: Optional[float | None]
            the outlet pressure in Pa

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            specific enthalpy difference is positive

        """
        if Pout is None:
            Pout = self.Pout

        temp_outlet = self.inlet.copy()

        temp_outlet.update("PS", Pout, self.inlet.properties.S)

        self.outlet_isentropic = temp_outlet.copy()

        self.delta_h_isentropic = temp_outlet.properties.H - self.inlet.properties.H

        self.delta_h = temp_outlet.properties.H - self.inlet.properties.H

        dh_rel = abs(self.delta_h / self.inlet.properties.H)
        if self.delta_h_isentropic > 0 and dh_rel > 0.01:
            msg = "Turbine error: Wrong sign in enthalpy computation"
            raise ValueError(msg)

        return temp_outlet

    def __polytropic_expansion(self,
                               Pout: Optional[float | None] = None,
                               eta_isen: Optional[float | None] = None) -> "MaterialStream":
        """
        Helper function to calculate a dry real expansion

        Parameters
        ----------
        Pout: Optional[float | None]
            the outlet pressure in Pa
        eta_isen: Optional[float | None]
            the isentropic efficiency

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            the specific entropy difference is negative

        """

        if Pout is None:
            Pout = self.Pout

        if eta_isen is None:
            eta_isen = self.eta_isentropic

        temp_outlet = self.__isentropic_expansion(Pout=Pout)

        h_out = self.inlet.properties.H + self.delta_h_isentropic * eta_isen

        temp_outlet.update("PH", Pout, h_out)

        self.delta_h_polytropic = temp_outlet.properties.H - self.inlet.properties.H
        self.delta_h = self.delta_h_polytropic * 1.0

        self.delta_s = temp_outlet.properties.S - self.inlet.properties.S
        if self.delta_s < 0:
            msg = "Turbine error: Wrong sign in entropy computation"
            raise ValueError(msg)

        return temp_outlet

    def __BaumannRule_expansion_old(self):

        # the fluid is vapour at the inlet

        # this also calculates the isentropic and polytropic enthalpy changes
        temp_outlet = self.__polytropic_expansion()

        if self.inlet.properties.Q > 1 - 1e-5:
            # the fluid is vapour at the inlet

            if temp_outlet.properties.Q > 1 - 1e-5:
                # the fluid is also dry at the outlet - single phase expansion
                # TODO maybe do a line search to check for crosses of the vapour dome...

                # there is no wet correction so Baumann delta h is just the polytropic delta h
                self.delta_h_BaumannCorr = self.delta_h_polytropic * 1.0
                self.delta_h = self.delta_h_polytropic * 1.0

                return temp_outlet

            # the fluid at the outlet is two-phase
            dry_turbine = turbine(self.eta_isentropic)

            # search for the intermediate pressure for which the expnsion ceases to be dry
            ps = np.linspace(self.Pout, self.inlet.properties.P * 0.999, 10)
            _p = self.Pout * 1.0
            _q = temp_outlet.properties.Q * 1.0
            for p in ps:
                dry_turbine.set_inputs(self.inlet, p)

                try:
                    out_stream = dry_turbine.calc()

                    if out_stream.properties.Q > 0.999:
                        break
                    else:
                        _p = p
                        _q = out_stream.properties.Q * 1.0
                except:
                    pass

            P_intermediate = (_p + p) / 2

            dry_turbine.set_inputs(self.inlet, P_intermediate)
            intermediate = dry_turbine.calc()

            intermediate.properties.Q = 0.99

            # TODO hmm this does not quite work because the above migth well find a condition where Q is still 1.0 and
            #  then it goes into an infinite loop with the Baumann Rule...
            wet_turbine = turbine(self.eta_isentropic, BaumannCorrection=True)
            wet_turbine.set_inputs(intermediate, self.Pout)
            temp_outlet = wet_turbine.calc()

            self.delta_h_BaumannCorr = dry_turbine.delta_h + wet_turbine.delta_h_BaumannCorr
            self.delta_h = dry_turbine.delta_h + wet_turbine.delta_h

        else:
            # the fluid is two-phase at the inlet
            temp_outlet = self.__polytropic_expansion()

            delta_dh = abs((
                                       self.delta_h_isentropic - self.delta_h) / self.delta_h_isentropic)  # this is just to get a starting point for the iterations
            dh_prev = self.delta_h * 1.0
            count = 0

            while delta_dh > 1e-3 and count < 10:
                eta_corr = (self.inlet.properties.Q + temp_outlet.properties.Q) / 2
                eta_s = eta_corr * self.eta_isentropic
                temp_outlet = self.__polytropic_expansion(eta_isen=eta_s)

                delta_dh = abs((dh_prev - self.delta_h) / dh_prev)
                dh_prev = self.delta_h * 1.0

                count += 1

            if delta_dh > 1e-3:
                msg = "The Baumann Rule iterations have not converged on a solution the maximum number of iterations."
                raise ValueError(msg)

            self.delta_h_BaumannCorr = temp_outlet.properties.H - self.inlet.properties.H
            self.delta_h = self.delta_h_BaumannCorr * 1.0

            self.eta_isentropic_app = self.delta_h / self.delta_h_isentropic

        return temp_outlet

    def __BaumannRule_expansion(self) -> "MaterialStream":
        """
        Helper function to calculate a real wet expansion using the Baumann Rule

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            iterations have not converged

        """

        # the fluid is vapour at the inlet

        # this also calculates the isentropic and polytropic enthalpy changes
        temp_outlet = self.__polytropic_expansion()
        dh_polytropic = self.delta_h_polytropic*1.0

        if temp_outlet.properties.Q > 1 - 1e-5:
            # the fluid is also dry at the outlet - single phase expansion
            # TODO maybe do a line search to check for crosses of the vapour dome...

            # there is no wet correction so Baumann delta h is just the polytropic delta h
            self.delta_h_BaumannCorr = self.delta_h_polytropic * 1.0
            self.delta_h = self.delta_h_polytropic * 1.0

            return temp_outlet

        delta_dh = abs((self.delta_h_isentropic - self.delta_h) / self.delta_h_isentropic)  # this is just to get a starting point for the iterations
        dh_prev = self.delta_h * 1.0
        count = 0

        while delta_dh > 1e-3 and count < 10:
            eta_corr = (self.inlet.properties.Q + temp_outlet.properties.Q) / 2
            eta_s = eta_corr * self.eta_isentropic
            temp_outlet = self.__polytropic_expansion(eta_isen=eta_s)

            delta_dh = abs((dh_prev - self.delta_h) / dh_prev)
            dh_prev = self.delta_h * 1.0

            count += 1

        if delta_dh > 1e-3:
            msg = "The Baumann Rule iterations have not converged on a solution the maximum number of iterations."
            raise ValueError(msg)

        self.delta_h_polytropic = dh_polytropic
        self.delta_h_BaumannCorr = temp_outlet.properties.H - self.inlet.properties.H
        self.delta_h = self.delta_h_BaumannCorr * 1.0

        self.eta_isentropic_app = self.delta_h / self.delta_h_isentropic

        return temp_outlet

    def calc_exergy_balance(self):

        self.Ein = self.inlet.m * (self.inlet.properties.H - Tref * self.inlet.properties.S)

        self.Eout = self.outlet.m * (self.outlet.properties.H - Tref * self.outlet.properties.S) + abs(self.work)

        self.Eloss = self.Ein - self.Eout

        # print(self.Ein, self.Eout, self.Eloss)

    def update_inlet_rate(self, m):

        self.inlet._update_quantity(m)
        self.outlet._update_quantity(m)
        self.outlet_isentropic._update_quantity(m)

        self.work = self.delta_h * m
        self.power_elec = self.work * self.eta_mechanical

    def calc_cost(self):

        match self.cost_model:

            case "default" | "similitude":

                dH_stage_max = -65000  # J/kg
                Vr_stage_max = 4  # m3/m3

                n_dH = self.delta_h_isentropic / dH_stage_max
                Vr = self.inlet.properties.D / self.outlet_isentropic.properties.D
                n_Vr = math.log(Vr, Vr_stage_max)

                n = math.ceil(max(n_dH, n_Vr))
                self.n_stages = n*1
                self.H_stages = n_dH*1
                self.V_stages = n_Vr*1

                dH_isentropic_stage = abs(self.delta_h_isentropic / n)
                V_rate = self.outlet_isentropic.m / self.outlet_isentropic.properties.D

                C0 = 1230000
                n0 = 2
                a = 0.5
                SP0 = 0.18
                b = 1.1

                SP = math.sqrt(V_rate) / (math.sqrt(math.sqrt(abs(dH_isentropic_stage))))
                cost_turbine = C0 * math.pow(n/n0, a) * math.pow(SP/SP0, b)

                self.SP = SP*1.0

                D0 = 200000
                W0 = 5e6
                c = 0.67
                cost_generator = D0 * math.pow(abs(self.power_elec) / W0, c)

                cost = cost_turbine + cost_generator

                exchange_rate = convert_EUR_to_USD(1, 2013)
                corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", 2013)
                corr = exchange_rate * corr_PPI

                cost *= corr

            case "thermoflex":

                a1 = -0.0408229
                a2 = 1.303859
                a3 = -0.158304

                x = math.log(abs(self.power_elec)/1000)
                lny = a1*x*x + a2*x + a3
                cost = math.exp(lny) * 1e3

                # water = Fluid(["water", 1])
                # water.update("PH", self.inlet.properties.P, self.inlet.properties.H)
                # water.update("PS", self.outlet.properties, water.properties.S)

                if "steam" in self.outlet_isentropic.fluid.components:
                    i_H2O = self.outlet_isentropic.fluid.components.index("steam")
                elif "water" in self.outlet_isentropic.fluid.components:
                    i_H2O = self.outlet_isentropic.fluid.components.index("water")
                else:
                    raise ValueError("fluid does not contain water")

                # i_H2O = self.outlet_isentropic.fluid.components.index("steam")
                y_H2O = self.outlet_isentropic.fluid.composition[i_H2O] * 1.0  # assuming ideal gas
                corr = math.pow(1/y_H2O, 0.55)

                cost *= corr

                exchange_rate = convert_EUR_to_USD(1, 2021)
                corr_PPI = calc_PPI("turbine", Yref) / calc_PPI("turbine", 2019)
                corr = exchange_rate * corr_PPI

                cost *= corr

        self.cost = cost * 1.0

        return cost


def register() -> NoReturn:
    """
    Registers the turbine component

    Returns
    -------
    NoReturn
    """
    factory.register("turbine", turbine)
