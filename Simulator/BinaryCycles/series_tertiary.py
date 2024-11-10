from ..cycle import BinaryCycle
import Simulator
import matplotlib.pyplot as plt

"""


                *----> Evap -------> Turb
                |      |  ^             |
                |      |  |             |
      *---------+----> Gcon ---->       |
      |         |                       |
----> Sep       |                       |
      |         |                       |
      *--------> PreH ---->             |
                    |                   |
                    *----------------- Recu <---- Pump <----*
                                        |                 |
                                        *----> Cond ------*      
"""


class ORC(BinaryCycle):
    # in this configuration a tertiary fluid is used to condense the geosteam, before evaporating the working fluid

    def __init__(self, recu=True):

        super().__init__()

        self.recuperated = recu

        self.separator = Simulator.separator()

        self.feedpump = Simulator.pump(0.85)

        self.geo_condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)
        self.evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)
        self.preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)
        self.recuperator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.turbine = Simulator.turbine(0.85)

        self.mixer = Simulator.mixer()

        self.tfluid = None

    def set_tertiaryfluid(self, stream):
        self.tfluid = stream

    def __calc_Tevap(self, stream, P, Tmax):
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

    def __calc_heat_introduction(self, brine, vapour, WF_preh_in, WF_evap_in, WF_turbine_in, TF_evap_in):

        # switch the geofluid to the interpolation fluid
        if self.interpolation:
            temp_brine = self.geofluid_table.copy()
            temp_brine.fluid.update_composition(brine.fluid.composition[-2:])
            temp_brine._update_quantity(brine.m)
            temp_brine.update("PH", brine.properties.P, brine.properties.H)

            temp_vapour = self.geofluid_table.copy()
            temp_vapour.fluid.update_composition(vapour.fluid.composition)
            temp_vapour._update_quantity(vapour.m)
            temp_vapour.update("PH", vapour.properties.P, vapour.properties.H)
        else:
            temp_brine = brine.copy()
            temp_vapour = vapour.copy()

        # calculate the pre-heater
        self.preheater.set_inputs(MassRatio=-1, Inlet_hot=temp_brine, Inlet_cold=WF_preh_in,
                                  Outlet_cold=WF_evap_in)
        brine_out, temp_WF_evap_in = self.preheater.calc()

        # calculate the WF evaporator and geosteam condenser and
        self.evaporator.set_inputs(MassRatio=-1, Inlet_hot=TF_evap_in, Inlet_cold=WF_evap_in, Outlet_cold=WF_turbine_in)
        TF_cond_in, temp_WF_turbine_in = self.evaporator.calc()

        self.geo_condenser.set_inputs(MassRatio=-1, Inlet_hot=temp_vapour, Inlet_cold=TF_cond_in,
                                      Outlet_cold=TF_evap_in)
        vapour_out, TF_gcond_out = self.geo_condenser.calc()

        WF_Mrate_PreH = temp_brine.m * self.preheater.MassRatio
        WF_Mrate_Evap = temp_vapour.m * self.evaporator.MassRatio * self.geo_condenser.MassRatio

        # check which (pre-heater or evaporator) is bottle necking the heat introduction
        if WF_Mrate_PreH > WF_Mrate_Evap:
            BrineMassRatio = WF_Mrate_Evap / temp_brine.m

            self.preheater.set_inputs(MassRatio=BrineMassRatio, Inlet_hot=temp_brine, Inlet_cold=WF_preh_in,
                                      Outlet_cold=WF_evap_in)
            brine_out, temp_WF_evap_in = self.preheater.calc()

        elif WF_Mrate_Evap > WF_Mrate_PreH:
            VapourMassRatio = WF_Mrate_PreH / (self.geo_condenser.MassRatio * temp_vapour.m)

            # calculate the WF evaporator
            self.evaporator.set_inputs(MassRatio=VapourMassRatio, Inlet_hot=TF_evap_in, Inlet_cold=WF_evap_in,
                                       Outlet_cold=WF_turbine_in)
            TF_cond_in, temp_WF_turbine_in = self.evaporator.calc()

            # calculate the geosteam condenser
            GMassRatio = WF_Mrate_PreH / self.evaporator.MassRatio / temp_vapour.m
            self.geo_condenser.set_inputs(MassRatio=GMassRatio, Inlet_hot=temp_vapour, Inlet_cold=TF_cond_in,
                                          Outlet_cold=TF_evap_in)
            vapour_out, TF_gcond_out = self.geo_condenser.calc()

        if self.interpolation:
            temp_brine_out = brine.copy()
            temp_brine_out.update("PH", brine_out.properties.P, brine_out.properties.H)

            temp_vapour_out = vapour.copy()
            temp_vapour_out.update("PH", vapour_out.properties.P, vapour_out.properties.H)
        else:
            temp_brine_out = brine_out.copy()
            temp_vapour_out = vapour_out.copy()

        self.mixer.set_inputs(temp_brine_out, temp_vapour_out)
        gfluid_out = self.mixer.calc()

        return gfluid_out, temp_WF_turbine_in

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

        # calculate the evaporation temperature
        WF_Tevap = self.__calc_Tevap(wfluid, P_max, T_max)

        if P_min is not None:
            # calculate the condensation temperature
            WF_Tmin = self.__calc_Tmin(wfluid, P_min)
        else:
            P_min = self.__calc_Pmin(wfluid, T_min)
            WF_Tmin = T_min

        # separate the geofluid liquid and vapour phases
        self.separator.set_inputs(self.geofluid_in)
        brine, vapour = self.separator.calc()

        # calculate the working fluid at the feedpump inlet
        WF_pump_in = wfluid.copy()
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
        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=WF_cond_in, Inlet_cold=self.coolant_in,
                                  Outlet_hot=WF_pump_in)
        WF_stream, self.coolant_out = self.condenser.calc()

        TF_evap_in = self.tfluid.copy()
        TF_evap_in.update("TQ", T_max + self.deltaT_pinch_liq, 0)

        self.geofluid_out, temp_WF = self.__calc_heat_introduction(brine, vapour, WF_preh_in, WF_evap_in, WF_turbine_in,
                                                                   TF_evap_in)

        # calculate the stream mass rates
        self.brine = brine
        self.vapour = vapour
        self.wfluid._update_quantity(brine.m * self.preheater.MassRatio)
        self.tfluid._update_quantity(vapour.m * self.geo_condenser.MassRatio)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.cycle_power = self.wfluid.m * (self.turbine.work + self.feedpump.work)
        self.parasitic_power = 0
        self.net_power = self.cycle_power

        self.calc_energy_balance()

        return self.net_power * 1.0

    def plot_TQ(self):

        wf_style = {"color": "green", "label": "working fluid"}
        geo_style = {"color": "red", "label": "geofluid"}
        cool_style = {"color": "blue", "label": "coolant"}
        tertiary_style = {"color": "black", "label": "tertiary"}
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

        duty = self.preheater.Duty_profile[1] * self.brine.m
        T_hot = self.preheater.T_profile[0]
        T_cold = self.preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)

        offset += duty[-1]

        duty = self.evaporator.Duty_profile[1] * self.vapour.m * self.geo_condenser.MassRatio
        T_hot = self.evaporator.T_profile[0]
        T_cold = self.evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **tertiary_style)
        plt.plot(duty + offset, T_cold, **wf_style)

        duty = self.geo_condenser.Duty_profile[1] * self.vapour.m
        T_hot = self.geo_condenser.T_profile[0]
        T_cold = self.geo_condenser.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **tertiary_style)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Heat Transferred, J/(kg/s)")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power / 1000))

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

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power / 1000))

        plt.show()
