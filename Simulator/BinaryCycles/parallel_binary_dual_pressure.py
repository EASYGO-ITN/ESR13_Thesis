from ..cycle import BinaryCycle
import Simulator
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

"""

                *-------*
                |       |
      *----> Evap ----> PreH ---->
      |      |             |
      |      |             *---- HPump <----*
      |      |                              |
      |      *----> HTurb ----> Mixer ------+--> LTurb ----* 
----> Sep                       |           |              |
      |      *------------------*           |              |
      |      |                              |              |
      |      |          *-------------- Splitter --------- Recu <---- Pump <----*
      |      |          |                                     |                 |
      *----> Evap ----> PreH ---->                            *----> Cond ------*
                |       |
                *-------*

"""


class ORC(BinaryCycle):

    def __init__(self, recu=True):

        super().__init__()

        self.recuperated = recu

        self.separator = Simulator.separator()

        self.feedpump_lp = Simulator.pump(0.85)
        self.feedpump_hp = Simulator.pump(0.85)

        self.brine_evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)
        self.brine_preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.vapour_evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.vapour_preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.recuperator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.coolingpump = Simulator.pump(0.85)

        self.turbine_hp = Simulator.turbine(0.85)
        self.turbine_lp = Simulator.turbine(0.85)

        self.mixer = Simulator.mixer()
        self.geo_mixer = Simulator.mixer()
        self.splitter = Simulator.splitter()

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

    def _calc_BrineBranch(self, brine, WF_LP_preh_in, WF_LP_evap_in, WF_LP_evap_out):

        # reset the stream mass rates
        WF_LP_preh_in._update_quantity(1.0)
        WF_LP_evap_in._update_quantity(1.0)
        WF_LP_evap_out._update_quantity(1.0)

        if self.interpolation:
            temp_brine = self.geofluid_table.copy()
            temp_brine.fluid.update_composition(brine.fluid.composition[-2:])
            temp_brine._update_quantity(brine.m)
            temp_brine.update("PH", brine.properties.P, brine.properties.H)

            brine = temp_brine

        # calculate the brine evaporator
        self.brine_evaporator.set_inputs(MassRatio=-1, Inlet_hot=brine, Inlet_cold=WF_LP_evap_in,
                                  Outlet_cold=WF_LP_evap_out)
        BF_PreH_in, WF_stream = self.brine_evaporator.calc()

        # calculate the pre-heater
        self.brine_preheater.set_inputs(MassRatio=-1, Inlet_hot=BF_PreH_in, Inlet_cold=WF_LP_preh_in,
                                  Outlet_cold=WF_LP_evap_in)
        BF_out, WF_stream = self.brine_preheater.calc()

        WF_BPreH = brine.m * self.brine_preheater.MassRatio
        WF_BEvap = brine.m * self.brine_evaporator.MassRatio

        R_0 = self.brine_evaporator.MassRatio
        R_1 = self.brine_preheater.MassRatio

        if WF_BPreH > WF_BEvap:
            BrineMassRatio = self.brine_evaporator.MassRatio
            self.brine_preheater.set_inputs(MassRatio=BrineMassRatio, Inlet_hot=BF_PreH_in, Inlet_cold=WF_LP_preh_in,
                                            Outlet_cold=WF_LP_evap_in)
            BF_out, WF_stream = self.brine_preheater.calc()
        else:

            def R_search(R):
                self.brine_evaporator.set_inputs(MassRatio=R, Inlet_hot=brine, Inlet_cold=WF_LP_evap_in,
                                                 Outlet_cold=WF_LP_evap_out)
                BF_PreH_in, WF_stream = self.brine_evaporator.calc()

                self.brine_preheater.set_inputs(MassRatio=-1, Inlet_hot=BF_PreH_in, Inlet_cold=WF_LP_preh_in,
                                                Outlet_cold=WF_LP_evap_in)
                BF_out, WF_stream = self.brine_preheater.calc()

                WF_BPreH = brine.m * self.brine_preheater.MassRatio
                WF_BEvap = brine.m * self.brine_evaporator.MassRatio

                error = (WF_BPreH - WF_BEvap) / (WF_BPreH + 1e-6)

                return error

            result = root_scalar(R_search, method="brentq", bracket=[R_1, R_0])

            R = result.root

            self.brine_evaporator.set_inputs(MassRatio=R, Inlet_hot=brine, Inlet_cold=WF_LP_evap_in,
                                             Outlet_cold=WF_LP_evap_out)
            BF_PreH_in, WF_stream = self.brine_evaporator.calc()

            self.brine_preheater.set_inputs(MassRatio=-1, Inlet_hot=BF_PreH_in, Inlet_cold=WF_LP_preh_in,
                                            Outlet_cold=WF_LP_evap_in)
            BF_out, WF_stream = self.brine_preheater.calc()

        WF_BPreH = brine.m * self.brine_preheater.MassRatio
        WF_BEvap = brine.m * self.brine_evaporator.MassRatio

        if self.interpolation:
            temp_brine_out = brine.copy()
            temp_brine_out.update("PH", BF_out.properties.P, BF_out.properties.H)
        else:
            temp_brine_out = BF_out.copy()

        return temp_brine_out, WF_BPreH

    def _calc_VapourBranch(self, vapour, WF_HP_feedpump_in, WF_HP_evap_in, WF_HPturbine_in, HPmax):

        # reset the stream mass rates
        WF_HP_feedpump_in._update_quantity(1.0)
        WF_HP_evap_in._update_quantity(1.0)
        WF_HPturbine_in._update_quantity(1.0)

        self.feedpump_hp.set_inputs(WF_HP_feedpump_in, HPmax)
        WF_HP_preh_in = self.feedpump_hp.calc()

        # switch the geofluid to the interpolation fluid
        if self.interpolation:
            temp_vapour = self.geofluid_table.copy()
            temp_vapour.fluid.update_composition(vapour.fluid.composition)
            temp_vapour._update_quantity(vapour.m)
            temp_vapour.update("PH", vapour.properties.P, vapour.properties.H)

            vapour = temp_vapour

        temp_vapour = vapour.copy()
        _P = vapour.properties.P - self.vapour_evaporator.deltaP_hot
        _T = WF_HP_evap_in.properties.T + self.vapour_evaporator.deltaT_pinch
        temp_vapour.update("PT", _P, _T)

        # calculate the brine evaporator
        self.vapour_evaporator.set_inputs(MassRatio=-1, Inlet_hot=vapour, Inlet_cold=WF_HP_evap_in,
                                Outlet_cold=WF_HPturbine_in, Outlet_hot=temp_vapour)
        VF_PreH_in, WF_stream = self.vapour_evaporator.calc()

        # calculate the pre-heater
        self.vapour_preheater.set_inputs(MassRatio=-1, Inlet_hot=VF_PreH_in, Inlet_cold=WF_HP_preh_in,
                                Outlet_cold=WF_HP_evap_in)
        VF_out, WF_stream = self.vapour_preheater.calc()

        WF_VPreH = vapour.m * self.vapour_preheater.MassRatio
        WF_VEvap = vapour.m * self.vapour_evaporator.MassRatio

        R_0 = self.vapour_evaporator.MassRatio
        R_1 = self.vapour_preheater.MassRatio

        if WF_VPreH > WF_VEvap:
            VapourMassRatio = self.vapour_evaporator.MassRatio
            self.vapour_preheater.set_inputs(MassRatio=VapourMassRatio, Inlet_hot=VF_PreH_in, Inlet_cold=WF_HP_preh_in,
                                             Outlet_cold=WF_HP_evap_in)
            VF_out, WF_stream = self.vapour_preheater.calc()
        else:

            def R_search(R):
                self.vapour_evaporator.set_inputs(MassRatio=R, Inlet_hot=vapour, Inlet_cold=WF_HP_evap_in,
                                        Outlet_cold=WF_HPturbine_in)
                VF_PreH_in, WF_stream = self.vapour_evaporator.calc()

                self.vapour_preheater.set_inputs(MassRatio=-1, Inlet_hot=VF_PreH_in, Inlet_cold=WF_HP_preh_in,
                                        Outlet_cold=WF_HP_evap_in)
                VF_out, WF_stream = self.vapour_preheater.calc()

                WF_VPreH = vapour.m * self.vapour_preheater.MassRatio
                WF_VEvap = vapour.m * self.vapour_evaporator.MassRatio

                error = (WF_VPreH - WF_VEvap) / (WF_VPreH + 1e-6)

                return error

            result = root_scalar(R_search, method="brentq", bracket=[R_0, R_1])
            R = result.root

            self.vapour_evaporator.set_inputs(MassRatio=R, Inlet_hot=vapour, Inlet_cold=WF_HP_evap_in,
                                              Outlet_cold=WF_HPturbine_in)
            VF_PreH_in, WF_stream = self.vapour_evaporator.calc()

            self.vapour_preheater.set_inputs(MassRatio=-1, Inlet_hot=VF_PreH_in, Inlet_cold=WF_HP_preh_in,
                                             Outlet_cold=WF_HP_evap_in)
            VF_out, WF_stream = self.vapour_preheater.calc()

        WF_VPreH = vapour.m * self.vapour_preheater.MassRatio
        WF_VEvap = vapour.m * self.vapour_evaporator.MassRatio

        if self.interpolation:
            temp_vapour_out = vapour.copy()
            temp_vapour_out.update("PH", VF_out.properties.P, VF_out.properties.H)
        else:
            temp_vapour_out = VF_out.copy()
        return temp_vapour_out, WF_VPreH

    def calc(self, HP_max, HT_max, LP_max, LT_max, T_min, P_min=None):

        # print(HT_max, LT_max)

        self.geofluid_in = self.geofluid.copy()
        self.coolant_in = self.coolant.copy()

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
        WF_T_evap_HP = self._calc_Tevap(self.wfluid, HP_max, HT_max)

        # calculate the LP evaporation temperature
        WF_T_evap_LP = self._calc_Tevap(self.wfluid, LP_max, LT_max)

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
        self.feedpump_lp.set_inputs(WF_pump_in, LP_max)
        WF_recup_in_cold = self.feedpump_lp.calc()

        # calculate the working fluid at the LP evaporator inlet
        WF_evap_lp_Pin = LP_max - self.recuperator.deltaP_cold - self.brine_preheater.deltaP_cold
        WF_evap_lp_in = self.wfluid.copy()
        WF_evap_lp_in.update("PT", WF_evap_lp_Pin, WF_T_evap_LP - self.deltaT_subcool)

        # calculate the working fluid at the LP evaporator outlet
        WF_evap_lp_Pout = WF_evap_lp_Pin - self.brine_evaporator.deltaP_cold
        WF_evap_lp_out = self.wfluid.copy()
        WF_evap_lp_out.update("PT", WF_evap_lp_Pout, LT_max)

        # calculate the working fluid at the HP evaporator inlet
        WF_evap_hp_Pin = HP_max - self.recuperator.deltaP_cold - self.vapour_preheater.deltaP_cold
        WF_evap_hp_in = self.wfluid.copy()
        WF_evap_hp_in.update("PT", WF_evap_hp_Pin, WF_T_evap_HP - self.deltaT_subcool)

        # calculate the working fluid at the HP turbine inlet
        WF_turb_hp_Pin = WF_evap_hp_Pin - self.vapour_evaporator.deltaP_cold
        WF_turbine_hp_in = self.wfluid.copy()
        WF_turbine_hp_in.update("PT", WF_turb_hp_Pin, HT_max)

        # calculate the HP turbine -> returns the HP turbine outlet
        self.turbine_hp.set_inputs(WF_turbine_hp_in, WF_evap_lp_Pout)
        WF_turbine_hp_out = self.turbine_hp.calc()

        self.mixer.set_inputs(WF_evap_lp_out, WF_turbine_hp_out)
        WF_turbine_lp_in = self.mixer.calc()
        WF_turbine_lp_in._update_quantity(1.0)

        # calculate the LP turbine
        WF_turb_lp_Pout = P_min + self.recuperator.deltaP_hot + self.condenser.deltaP_hot
        self.turbine_lp.set_inputs(WF_turbine_lp_in, WF_turb_lp_Pout)
        WF_recup_in_hot = self.turbine_lp.calc()

        WF_BrineBranch = 1
        WF_VapourBranch = 1
        T_LP_turbine_out = WF_recup_in_hot.properties.T
        error = 1
        iter = 0

        while error > 1e-4 and iter < 10:
            if self.recuperated:
                self.recuperator.set_inputs(Inlet_hot=WF_recup_in_hot, Inlet_cold=WF_recup_in_cold)
                WF_cond_in, WF_recup_out_cold = self.recuperator.calc()

                if WF_recup_out_cold.properties.T > WF_evap_lp_in.properties.T:  # this is only needed when the preheater is effectively not needed
                    WF_recup_out_cold = self.wfluid.copy()
                    WF_recup_out_cold.update("PT", LP_max - self.recuperator.deltaP_cold, WF_T_evap_LP - self.deltaT_subcool - 1)

                    self.recuperator.set_inputs(Inlet_hot=WF_recup_in_hot, Inlet_cold=WF_recup_in_cold,
                                                Outlet_cold=WF_recup_out_cold)
                    WF_cond_in, WF_preh_in = self.recuperator.calc()

            else:
                WF_cond_in = WF_recup_in_hot
                WF_recup_out_cold = WF_recup_in_cold

            WF_recup_out_cold._update_quantity(1.0)
            WF_preh_lp_in = WF_recup_out_cold.copy()
            WF_feedpump_hp_in = WF_recup_out_cold.copy()

            BF_out, WF_BrineBranch = self._calc_BrineBranch(brine, WF_preh_lp_in, WF_evap_lp_in, WF_evap_lp_out)
            VF_out, WF_VapourBranch = self._calc_VapourBranch(vapour, WF_feedpump_hp_in, WF_evap_hp_in, WF_turbine_hp_in, HP_max)

            # calc mixer
            WF_evap_lp_out._update_quantity(WF_BrineBranch)
            WF_turbine_hp_out._update_quantity(WF_VapourBranch)

            self.mixer.set_inputs(WF_evap_lp_out, WF_turbine_hp_out)
            WF_turbine_lp_in = self.mixer.calc()
            WF_turbine_lp_in._update_quantity(1.0)

            # calculate the LP turbine
            self.turbine_lp.set_inputs(WF_turbine_lp_in, WF_turb_lp_Pout)
            WF_recup_in_hot = self.turbine_lp.calc()

            error = abs(T_LP_turbine_out - WF_recup_in_hot.properties.T)/T_LP_turbine_out
            T_LP_turbine_out = WF_recup_in_hot.properties.T

            iter += 1

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        # calculate the condenser
        WF_cond_in._update_quantity(1.0)
        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=WF_cond_in, Inlet_cold=self.coolant,
                             Outlet_hot=WF_pump_in)
        WF_stream, self.coolant_out = self.condenser.calc()

        self.geo_mixer.set_inputs(BF_out, VF_out)
        self.geofluid_out = self.geo_mixer.calc()

        # calculate the stream mass rates
        self.brine = brine
        self.vapour = vapour

        WF_brine_branch = brine.m * self.brine_preheater.MassRatio
        WF_vapour_branch = vapour.m * self.vapour_preheater.MassRatio
        self.wfluid._update_quantity(WF_brine_branch + WF_vapour_branch)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.cycle_power = WF_vapour_branch * (self.turbine_hp.work + self.feedpump_hp.work)
        self.cycle_power += self.wfluid.m * (self.turbine_lp.work + self.feedpump_lp.work)
        self.parasitic_power = self.coolant.m * self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power

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

        duty = self.brine_preheater.Duty_profile[1] * self.brine.m
        T_hot = self.brine_preheater.T_profile[0]
        T_cold = self.brine_preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)
        offset += duty[-1]

        duty = self.brine_evaporator.Duty_profile[1] * self.brine.m
        T_hot = self.brine_evaporator.T_profile[0]
        T_cold = self.brine_evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)
        offset += duty[-1]

        duty = self.vapour_preheater.Duty_profile[1] * self.vapour.m
        T_hot = self.vapour_preheater.T_profile[0]
        T_cold = self.vapour_preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)
        offset += duty[-1]

        duty = self.vapour_evaporator.Duty_profile[1] * self.vapour.m
        T_hot = self.vapour_evaporator.T_profile[0]
        T_cold = self.vapour_evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)
        offset += duty[-1]

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Heat Transferred, J/(kg/s)")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power/1000))

        plt.show()

    def plot_TS(self):

        wf_style = {"color": "green", "label": "working fluid"}
        wf_lp_style = {"color": "red", "label": "LP cycle"}
        wf_hp_style = {"color": "orange", "label": "HP cycle"}
        mix_style = {"color": "black", "linestyle": "--"}
        env_style = {"color": "black", "linewidth": 0.5}

        s = [self.feedpump_lp.inlet.properties.S, self.feedpump_lp.outlet.properties.S]
        T = [self.feedpump_lp.inlet.properties.T, self.feedpump_lp.outlet.properties.T]
        plt.plot(s, T, **wf_style)

        if self.recuperated:
            s = self.recuperator.S_profile[1]
            T = self.recuperator.T_profile[1]
            plt.plot(s, T, **wf_style)

        s = [self.feedpump_hp.inlet.properties.S, self.feedpump_hp.outlet.properties.S]
        T = [self.feedpump_hp.inlet.properties.T, self.feedpump_hp.outlet.properties.T]
        plt.plot(s, T, **wf_hp_style)

        s = self.brine_preheater.S_profile[1]
        T = self.brine_preheater.T_profile[1]
        plt.plot(s, T, **wf_lp_style)

        s = self.brine_evaporator.S_profile[1]
        T = self.brine_evaporator.T_profile[1]
        plt.plot(s, T, **wf_lp_style)

        s = self.vapour_preheater.S_profile[1]
        T = self.vapour_preheater.T_profile[1]
        plt.plot(s, T, **wf_hp_style)

        s = self.vapour_evaporator.S_profile[1]
        T = self.vapour_evaporator.T_profile[1]
        plt.plot(s, T, **wf_hp_style)

        s = [self.turbine_hp.inlet.properties.S, self.turbine_hp.outlet.properties.S]
        T = [self.turbine_hp.inlet.properties.T, self.turbine_hp.outlet.properties.T]
        plt.plot(s, T, **wf_hp_style)

        s = [self.turbine_hp.outlet.properties.S, self.turbine_lp.inlet.properties.S]
        T = [self.turbine_hp.outlet.properties.T, self.turbine_lp.inlet.properties.T]
        plt.plot(s, T, **mix_style)

        s = [self.brine_evaporator.outlet[1].properties.S, self.turbine_lp.inlet.properties.S]
        T = [self.brine_evaporator.outlet[1].properties.T, self.turbine_lp.inlet.properties.T]
        plt.plot(s, T, **mix_style)

        s = [self.turbine_lp.inlet.properties.S, self.turbine_lp.outlet.properties.S]
        T = [self.turbine_lp.inlet.properties.T, self.turbine_lp.outlet.properties.T]
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
