from ..cycle import BinaryCycle
import Simulator
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar
from FluidProperties import Tref

"""

      *--------------> Turb ----*
      |                         |
      |             *---------- Recup <---- Pump <----*
      |             |               |                 |
----> Evap ----> PreH ---->         *----> Cond ------*
         |       |
         *-------*

"""


class ORC(BinaryCycle):

    def __init__(self, recu=True):

        super().__init__()

        self.recuperated = recu

        self.feedpump = Simulator.pump(0.85)

        self.evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.recuperator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.coolingpump = Simulator.pump(0.85)

        self.turbine = Simulator.turbine(0.85)

    def _calc_Tevap(self, stream, P, Tmax):
        temp_stream = stream.copy()
        temp_stream.update("PQ", P, 0)
        Tevap = temp_stream.properties.T

        if Tmax < Tevap + self.deltaT_superheat:
            msg = "The maximum temperature, {:.2f} K, is below the working fluid's mininimum superheated temperature, {:.2f} K".format(
                Tmax, Tevap + self.deltaT_superheat)
            raise ValueError(msg)

        return Tevap

    def __calc_Tmin(self, stream, Pmin):
        stream.update("PQ", Pmin, 0)
        T_cond = stream.properties.T

        return T_cond - self.deltaT_subcool

    def __calc_Pmin(self, stream, Tmin):
        Tcond = Tmin + self.deltaT_subcool
        stream.update("TQ", Tcond, 0)
        Pmin = stream.properties.P

        return Pmin

    def calc(self, P_max, T_max, T_min, P_min=None):

        self.geofluid_in = self.geofluid.copy()
        self.coolant_in = self.coolant.copy()

        # (re)initialise the stream mass rates
        wfluid = self.wfluid.copy()
        wfluid._update_quantity(1.0)
        gfluid = self.geofluid.copy()
        gfluid._update_quantity(1.0)
        if self.interpolation:
            gfluid_table = self.geofluid_table.copy()
            gfluid_table._update_quantity(1.0)
        cfluid = self.coolant.copy()
        cfluid._update_quantity(1.0)

        # calculate the HP evaporation temperature
        WF_Tevap = self._calc_Tevap(self.wfluid, P_max, T_max)

        if P_min is not None:
            # calculate the condensation temperature
            WF_Tmin = self.__calc_Tmin(wfluid, P_min)
        else:
            P_min = self.__calc_Pmin(wfluid, T_min)
            WF_Tmin = T_min

        # calculate the working fluid at the feedpump inlet
        WF_pump_in = self.wfluid.copy()
        WF_pump_in.update("PT", P_min, WF_Tmin)

        # calculate the feedpump -> returns the recuperator cold inlet stream
        self.feedpump.set_inputs(WF_pump_in, P_max)
        WF_recu_cold_in = self.feedpump.calc()

        # calculate the working fluid at the evaporator inlet
        WF_evap_P_in = P_max - self.recuperator.deltaP_cold - self.preheater.deltaP_cold
        WF_evap_in = self.wfluid.copy()
        WF_evap_in.update("PT", WF_evap_P_in, WF_Tevap - self.deltaT_subcool)

        # calculate the working fluid at the turbine inlet
        WF_turb_P_in = WF_evap_P_in - self.evaporator.deltaP_cold
        WF_turbine_in = self.wfluid.copy()
        WF_turbine_in.update("PT", WF_turb_P_in, T_max)

        # calculate the turbine -> returns the recuperator hot inlet stream
        WF_turb_P_out = P_min + self.recuperator.deltaP_hot + self.condenser.deltaP_hot
        self.turbine.set_inputs(WF_turbine_in, WF_turb_P_out)
        WF_recu_hot_in = self.turbine.calc()

        if self.recuperated:
            self.recuperator.set_inputs(Inlet_hot=WF_recu_hot_in, Inlet_cold=WF_recu_cold_in)
            WF_cond_in, WF_preh_in = self.recuperator.calc()

            if WF_preh_in.properties.T > WF_evap_in.properties.T:  # this is only needed when the preheater is effectively not needed
                WF_preh_in = self.wfluid.copy()
                WF_preh_in.update("PT", P_max - self.recuperator.deltaP_cold, WF_Tevap - self.deltaT_subcool - 1)

                self.recuperator.set_inputs(Inlet_hot=WF_recu_hot_in, Inlet_cold=WF_recu_cold_in, Outlet_cold=WF_preh_in)
                WF_cond_in, WF_preh_in = self.recuperator.calc()

        else:
            WF_cond_in = WF_recu_hot_in
            WF_preh_in = WF_recu_cold_in

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=WF_cond_in, Inlet_cold=self.coolant_in,
                                  Outlet_hot=WF_pump_in)
        WF_stream, self.coolant_out = self.condenser.calc()

        # switch the geofluid to the interpolation fluid
        geofluid = self.geofluid.copy()
        if self.interpolation:
            temp_geo = self.geofluid_table.copy()
            temp_geo.fluid.update_composition(geofluid.fluid.composition[-2:])
            temp_geo._update_quantity(geofluid.m)
            temp_geo.update("PH", geofluid.properties.P, geofluid.properties.H)

            geofluid = temp_geo

        # calculate the brine evaporator
        self.evaporator.set_inputs(MassRatio=-1, Inlet_hot=geofluid, Inlet_cold=WF_evap_in,
                                   Outlet_cold=WF_turbine_in)
        GF_PreH_in, WF_stream = self.evaporator.calc()

        # calculate the pre-heater
        self.preheater.set_inputs(MassRatio=-1, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                  Outlet_cold=WF_evap_in)
        BF_out, WF_stream = self.preheater.calc()

        WF_PreH = geofluid.m * self.preheater.MassRatio
        WF_Evap = geofluid.m * self.evaporator.MassRatio

        R_0 = self.evaporator.MassRatio
        R_1 = self.preheater.MassRatio

        if WF_PreH > WF_Evap:
            MassRatio = self.evaporator.MassRatio
            self.preheater.set_inputs(MassRatio=MassRatio, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                      Outlet_cold=WF_evap_in)
            GF_out, temp_evap_in = self.preheater.calc()

        else:

            def R_search(R):
                self.evaporator.set_inputs(MassRatio=R, Inlet_hot=geofluid, Inlet_cold=WF_evap_in,
                                           Outlet_cold=WF_turbine_in)
                GF_PreH_in, temp_turb_in = self.evaporator.calc()

                self.preheater.set_inputs(MassRatio=-1, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                          Outlet_cold=WF_evap_in)
                GF_out, temp_evap_in = self.preheater.calc()

                WF_PreH = geofluid.m * self.preheater.MassRatio
                WF_Evap = geofluid.m * self.evaporator.MassRatio

                error = (WF_PreH - WF_Evap) / (WF_PreH + 1e-6)

                return error

            result = root_scalar(R_search, method="brentq", bracket=[R_0, R_1])
            R = result.root

            self.evaporator.set_inputs(MassRatio=R, Inlet_hot=geofluid, Inlet_cold=WF_evap_in,
                                       Outlet_cold=WF_turbine_in)
            GF_PreH_in, temp_turb_in = self.evaporator.calc()

            self.preheater.set_inputs(MassRatio=-1, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                      Outlet_cold=WF_evap_in)
            GF_out, temp_evap_in = self.preheater.calc()

        WF_PreH = geofluid.m * self.preheater.MassRatio
        WF_Evap = geofluid.m * self.evaporator.MassRatio

        if self.interpolation:
            self.geofluid_out = self.geofluid.copy()
            self.geofluid_out.update("PH", GF_out.properties.P, GF_out.properties.H)

        else:
            self.geofluid_out = GF_out.copy()

        # updating the component mass rates
        self.wfluid._update_quantity(self.geofluid_out.m * self.preheater.MassRatio)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.feedpump.update_inlet_rate(self.wfluid.m)
        self.turbine.update_inlet_rate(self.wfluid.m)
        if self.recuperated:
            self.recuperator.update_inlet_rate(self.wfluid.m, self.wfluid.m)

        self.evaporator.update_inlet_rate(self.geofluid.m, self.wfluid.m)
        self.preheater.update_inlet_rate(self.geofluid.m, self.wfluid.m)

        self.condenser.update_inlet_rate(self.wfluid.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

        self.cycle_power = (self.turbine.work + self.feedpump.work)
        self.parasitic_power = self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power
        # self.net_power = self.cycle_power

        self.calc_energy_balance()

        return self.net_power * 1.0

    def plot_TQ(self):

        wf_style = {"color": "green", "label": "working fluid"}
        geo_style = {"color": "red", "label": "geofluid"}
        cool_style = {"color": "blue", "label": "coolant"}
        recu_style = {"linestyle": "--", "color": "black"}

        offset = 0.0

        duty = self.condenser.Duty_profile[1] * self.wfluid.m
        T_hot = self.condenser.T_profile[0]
        T_cold = self.condenser.T_profile[1]

        plt.plot(duty, T_hot, **wf_style)
        plt.plot(duty, T_cold, **cool_style)

        offset += duty[-1]

        if self.recuperated:
            duty = self.recuperator.Duty_profile[1] * self.wfluid.m
            T_hot = self.recuperator.T_profile[0]
            T_cold = self.recuperator.T_profile[1]
            recu_offset = duty[-1]

            plt.plot(duty, T_cold, **wf_style)
            plt.plot(duty + offset, T_hot, **wf_style)

            duty_cold = [self.recuperator.Duty_profile[1][0], offset]
            T_cold = [self.recuperator.T_profile[1][0], self.recuperator.T_profile[0][0]]
            plt.plot(duty_cold, T_cold, **recu_style)

            duty_hot = [recu_offset, recu_offset + offset]
            T_hot = [self.recuperator.T_profile[1][-1], self.recuperator.T_profile[0][-1]]
            plt.plot(duty_hot, T_hot, **recu_style)

        offset = 0.0
        if self.recuperated:
            offset += duty[-1]

        duty = self.preheater.Duty_profile[1] * self.geofluid_out.m
        T_hot = self.preheater.T_profile[0]
        T_cold = self.preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)

        offset += duty[-1]

        duty = self.evaporator.Duty_profile[1] * self.geofluid_out.m
        T_hot = self.evaporator.T_profile[0]
        T_cold = self.evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Heat Transferred, J/(kg/s)")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power/1000))

        plt.show()

    def plot_TS(self):

        wf_style = {"color": "green", "label": "working fluid"}
        env_style = {"color": "black", "linewidth": 0.5}

        s = [self.feedpump.inlet.properties.S, self.feedpump.outlet.properties.S]
        T = [self.feedpump.inlet.properties.T, self.feedpump.outlet.properties.T]
        plt.plot(s, T, **wf_style)

        if self.recuperated:
            s = self.recuperator.S_profile[1]
            T = self.recuperator.T_profile[1]
            plt.plot(s, T, **wf_style)

        s = self.preheater.S_profile[1]
        T = self.preheater.T_profile[1]
        plt.plot(s, T, **wf_style)

        s = self.evaporator.S_profile[1]
        T = self.evaporator.T_profile[1]
        plt.plot(s, T, **wf_style)

        s = [self.turbine.inlet.properties.S, self.turbine.outlet.properties.S]
        T = [self.turbine.inlet.properties.T, self.turbine.outlet.properties.T]
        plt.plot(s, T, **wf_style)

        if self.recuperated:
            s = self.recuperator.S_profile[0]
            T = self.recuperator.T_profile[0]
            plt.plot(s, T, **wf_style)

        s = self.condenser.S_profile[0]
        T = self.condenser.T_profile[0]
        plt.plot(s, T, **wf_style)

        ss, ts = self._calc_TS_envelope()

        plt.plot(ss, ts, **env_style)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Specific Entropy, J/kg/K")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power/1000))

        plt.show()

    def exergy_loss(self):

        store = [{"equip":"Reinjected", "val": self.Eout},
                 {"equip": "Evaporator", "val": self.evaporator.Eloss},
                 {"equip": "PreHeater", "val": self.preheater.Eloss},
                 {"equip": "Condenser", "val": self.condenser.Eloss},
                 {"equip": "Turbine", "val": self.turbine.Eloss},
                 {"equip": "Pump", "val": self.feedpump.Eloss}
                 ]
        if self.recuperated:
            store.append({"equip": "Recuperator", "val": self.recuperator.Eloss})

        def sortFunc(e):
            return e["val"]

        store.sort(key=sortFunc, reverse=True)

        labels = [x["equip"] for x in store]
        values = [x["val"] for x in store]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct='%1.1f%%')
        plt.show()

    def calc_exergy_balance(self):
        self.evaporator.calc_exergy_balance()
        self.preheater.calc_exergy_balance()
        if self.recuperated:
            self.recuperator.calc_exergy_balance()
        self.condenser.calc_exergy_balance()

        self.feedpump.calc_exergy_balance()
        self.turbine.calc_exergy_balance()

        self.Ein = self.geofluid.m * (self.geofluid_in.properties.H - Tref * self.geofluid_in.properties.S)
        self.Ein += self.coolant.m * (self.coolant_in.properties.H - Tref * self.coolant_in.properties.S)

        self.Eout = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        self.Eout += self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        self.Eloss = self.evaporator.Eloss + self.preheater.Eloss + self.condenser.Eloss + self.recuperator.Eloss + self.feedpump.Eloss + self.turbine.Eloss

        print((self.Ein - self.Eout) - self.Eloss, abs(self.cycle_power))
