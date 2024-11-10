import numpy as np
from FluidProperties import Tref

from scipy.optimize import root_scalar
import matplotlib.pyplot as plt


class Cycle:

    def __init__(self):

        self.net_power = 0.0
        self.eff_1st_law = None
        self.eff_2nd_law = None

        self.P_ambient = 101325
        self.T_ambient = 298

        self.deltaT_pinch_liq = 5
        self.deltaT_pinch_vap = 10

        self.deltaT_subcool = 3
        self.deltaT_superheat = 5

        self.geofluid = None
        self.geofluid_in = None
        self.geofluid_out = None

        self.coolant = None
        self.coolant_in = None
        self.coolant_out = None

    def set_ambient_conditions(self, P=None, T=None):

        if P is not None:
            self.P_ambient = P

        if T is not None:
            self.T_ambient = T

        if self.coolant is not None:
            self.coolant.update("PT", self.P_ambient, self.T_ambient)

    def set_geofluid(self, stream, interpolation=None, InputSpec=None, Input1=None, Input2=None):

        self.geofluid = stream

        if InputSpec is not None and Input1 is not None and Input2 is not None:
            self.geofluid.update(InputSpec, Input1, Input2)

        if interpolation is not None:
            self.geofluid_table = interpolation
            self.interpolation = True
        else:
            self.geofluid_table = stream
            self.interpolation = False

    def set_coolant(self, stream):

        self.coolant = stream.copy()
        self.coolant.update("PT", self.P_ambient, self.T_ambient)

    def calc(self, *args, **kwargs):
        pass

    def second_law_efficiency(self):
        if self.geofluid_in is None or self.geofluid_out is None or self.net_power == 0.0:
            msg = "Cannot calculate the second law efficiency as the system has not yet been calculated"
            raise ValueError(msg)

        h_in = self.geofluid_in.properties.H
        s_in = self.geofluid_in.properties.S
        e_in = h_in - s_in * Tref
        E_in = self.geofluid.m * e_in

        self.eff_2nd_law = -self.net_power / E_in

        return self.eff_2nd_law

    def plot(self):
        pass

    def calc_NPV(self, price, discount_rate=0.1, duration=20, tax=0.0, operating=0.05, inflation=0.03, capacity=1):
        NPV = [x for x in range(duration + 1)]
        NPV[0] = -self.cost

        operating_costs_0 = operating * self.cost

        inv_discount = 1/(1+discount_rate)
        value_of_money = 1
        cum_inflation = 1

        for i, temp in enumerate(NPV[1:]):
            value_of_money *= inv_discount
            cum_inflation *= 1 + inflation

            income = abs(self.net_power*365*24/1000) * price * 1e-6
            operating_costs = operating_costs_0 * cum_inflation

            profit = income - operating_costs
            profit_after_tax = (1 - tax) * profit

            NPV[i+1] = NPV[i] + profit_after_tax * value_of_money

        return NPV

    def calc_economics(self, discount_rate=0.1, price=0.4, duration=20, tax=0.2, operating=0.05):

        def price_search(price):

            NPV = self.calc_NPV(price, discount_rate=discount_rate, duration=duration, tax=tax, operating=operating)

            finalNPV = NPV[-1]
            return finalNPV

        res = root_scalar(price_search, method="secant", x0=price, x1=price*2)
        self.LCOE = res.root*1e3  # €$/MWh

        def discount_search(discount):
            NPV = self.calc_NPV(price, discount_rate=discount, duration=duration, tax=tax, operating=operating)

            final_NPV = NPV[-1]
            return final_NPV

        # res = root_scalar(discount_search, method="brentq", bracket=[0, 10])
        res = root_scalar(discount_search, method="secant", x0=discount_rate, x1=discount_rate*2)
        self.IRR = res.root  # %

        self.NPV_profile = self.calc_NPV(price, discount_rate=discount_rate, duration=duration, tax=tax, operating=operating)
        self.NPV = self.NPV_profile[-1]

        self.ROI = (self.NPV - self.cost) / self.cost

    def plot_Eloss(self):

        def sortFunc(e):
            return e["val"]

        self.exergy_losses.sort(key=sortFunc, reverse=True)

        labels = [x["equip"] for x in self.exergy_losses]
        values = [x["val"] for x in self.exergy_losses]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()

    def plot_costs(self):

        def sortFunc(e):
            return e["val"]

        self.costs.sort(key=sortFunc, reverse=True)

        labels = [x["equip"] for x in self.costs]
        values = [x["val"] for x in self.costs]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()


class BinaryCycle(Cycle):

    def __init__(self):

        super().__init__()

        self.wfluid = None

    def set_workingfluid(self, stream):
        self.wfluid = stream

    def first_law_efficiency(self):
        if self.geofluid_in is None or self.geofluid_out is None or self.net_power == 0.0:
            msg = "Cannot calculate the first law efficiency as the system has not yet been calculated"
            raise ValueError(msg)

        h_in = self.geofluid_in.properties.H
        h_out = self.geofluid_out.properties.H
        delta_H = h_in - h_out

        Q_in = self.geofluid.m * delta_H

        self.eff_1st_law = - self.net_power/Q_in

        return self.eff_1st_law * 1.0

    def calc_energy_balance(self):
        self.Q_in = self.geofluid.m*(self.geofluid_in.properties.H - self.geofluid_out.properties.H)
        self.Q_out = self.coolant.m*(self.coolant_out.properties.H - self.coolant_in.properties.H)
        Q_net = self.Q_in-self.Q_out

        self.energy_balance = Q_net + self.cycle_power

    def _calc_TS_envelope(self, fluid=None):

        if fluid is None:
            fluid = self.wfluid

        N = 25
        wfluid = fluid.copy()
        Tcrit = wfluid.fluid.state.state.state.T_critical()
        ts1 = np.linspace(self.T_ambient, Tcrit-0.1, N)

        ts = np.zeros(N*2)
        ss = np.zeros(N*2)

        for i, t in enumerate(ts1):
            wfluid.update("TQ", t, 0)
            ss[i] = wfluid.properties.S
            ts[i] = t

            wfluid.update("TQ", t, 1)
            ss[-i-1] = wfluid.properties.S
            ts[-i-1] = t

        return ss, ts


