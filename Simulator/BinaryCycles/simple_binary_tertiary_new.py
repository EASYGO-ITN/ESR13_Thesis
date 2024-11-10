import time

from ..cycle import BinaryCycle
import Simulator
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar, minimize_scalar, minimize, Bounds
from FluidProperties import Tref
import math

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

        self.superheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap+0.1)

        self.evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.geo_condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)
        self.WF_evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.temp_HX = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.recuperator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap)
        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq)

        self.coolingpump = Simulator.pump(0.85)

        self.turbine = Simulator.turbine(0.85)

    def set_tertiaryfluid(self, stream):
        self.tfluid = stream

    def _calc_Tevap(self, P):
        temp_stream = self.wfluid.copy()
        temp_stream.update("PQ", P, 0)
        Tevap = temp_stream.properties.T

        if self.Tmax < Tevap + self.deltaT_superheat:
            msg = "The maximum temperature, {:.2f} K, is below the working fluid's mininimum superheated temperature, {:.2f} K".format(
                self.Tmax, Tevap + self.deltaT_superheat)
            raise ValueError(msg)

        return Tevap

    def __calc_Tmin(self, stream, Pmin):
        stream.update("PQ", Pmin, 0)
        T_cond = stream.properties.T

        return T_cond - self.deltaT_subcool

    def __calc_Pmin(self, stream, Tmin):
        Tcond = Tmin + self.deltaT_subcool
        stream.update("TQ", Tcond, 0)
        self.Pmin = stream.properties.P

    def __calc_feedpump(self, wfluid):
        # calculate Pmin from Tmin
        self.__calc_Pmin(wfluid, self.Tmin)

        WF_pump_in = self.wfluid.copy()
        WF_pump_in.update("PT", self.Pmin, self.Tmin)

        # calculate the feedpump -> returns the recuperator cold inlet stream
        self.feedpump.set_inputs(WF_pump_in, self.Pmax)
        WF_pump_out = self.feedpump.calc()

        return WF_pump_in, WF_pump_out

    def __calc_turbine(self,WF_turb_in):
        # calculate the turbine -> returns the recuperator hot inlet stream
        WF_turb_P_out = self.Pmin + self.condenser.deltaP_hot
        if self.recuperated:
            WF_turb_P_out += self.recuperator.deltaP_hot
        self.turbine.set_inputs(WF_turb_in, WF_turb_P_out)
        return self.turbine.calc()

    def __calc_PHE_streams(self):
        WF_Pevap_in = self.Pmax - self.preheater.deltaP_cold
        if self.recuperated:
            WF_Pevap_in -= self.recuperator.deltaP_cold
        WF_Tevap = self._calc_Tevap(WF_Pevap_in)
        WF_Tevap_in = WF_Tevap - self.deltaT_subcool

        WF_evap_in = self.wfluid.copy()
        WF_evap_in.update("PT", WF_Pevap_in, WF_Tevap - self.deltaT_subcool)

        WF_Psup_in = WF_Pevap_in - self.evaporator.deltaP_cold
        WF_Tsup_in = WF_Tevap + self.deltaT_superheat
        WF_sup_in = self.wfluid.copy()
        WF_sup_in.update("PT", WF_Psup_in, WF_Tsup_in)

        WF_Pturb_in = WF_Psup_in - self.superheater.deltaP_cold
        WF_Tturb_in = self.Tmax
        WF_turb_in = self.wfluid.copy()
        WF_turb_in.update("PT", WF_Pturb_in, WF_Tturb_in)

        return WF_evap_in, WF_sup_in, WF_turb_in

    def __calc_recuperator(self, WF_recu_hot_in, WF_recu_cold_in, WF_evap_in):

        if self.recuperated:
            self.recuperator.set_inputs(Inlet_hot=WF_recu_hot_in, Inlet_cold=WF_recu_cold_in)
            WF_cond_in, WF_preh_in = self.recuperator.calc()

            if WF_preh_in.properties.T > WF_evap_in.properties.T:  # this is only needed when the preheater is effectively not needed
                WF_preh_in = self.wfluid.copy()
                WF_Tpreh_in = WF_evap_in.properties.T - 1
                WF_preh_in.update("PT", self.Pmax - self.recuperator.deltaP_cold, WF_Tpreh_in)

                self.recuperator.set_inputs(Inlet_hot=WF_recu_hot_in, Inlet_cold=WF_recu_cold_in, Outlet_cold=WF_preh_in)
                WF_cond_in, WF_preh_in = self.recuperator.calc()
        else:
            WF_cond_in = WF_recu_hot_in
            WF_preh_in = WF_recu_cold_in

        return WF_cond_in, WF_preh_in

    def __calc_condenser(self, WF_cond_in, WF_pump_in):

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=WF_cond_in, Inlet_cold=self.coolant_in,
                                  Outlet_hot=WF_pump_in)
        WF_stream, self.coolant_out = self.condenser.calc()

    def __calc_PHE(self, WF_preh_in, WF_evap_in, WF_sup_in, WF_turb_in):

        def R_search(R):

            self.superheater.set_inputs(MassRatio=R, Inlet_hot=geofluid, Inlet_cold=WF_sup_in,
                                        Outlet_cold=WF_turb_in)
            GF_Evap_in, WF_stream = self.superheater.calc()

            TF_T_evap_in = GF_Evap_in.properties.T - self.geo_condenser.deltaT_pinch
            TF_evap_in = self.tfluid.copy()
            TF_evap_in.update("TQ", TF_T_evap_in, 0)

            def dT_search(dT):
                self.evaporator.deltaT_pinch = dT
                self.evaporator.set_inputs(MassRatio=-1, Inlet_hot=GF_Evap_in, Inlet_cold=WF_evap_in, Outlet_cold=WF_sup_in)
                tempGF_PreH_in, tempTF = self.evaporator.calc()

                diff = R - self.evaporator.MassRatio

                # self.WF_evaporator.set_inputs(MassRatio=-1, Inlet_hot=TF_evap_in, Inlet_cold=WF_evap_in, Outlet_cold=WF_sup_in)
                # TF_gcond_in, WF_stream = self.WF_evaporator.calc()
                #
                # TF_T_gcond_out = GF_Evap_in.properties.T - self.geo_condenser.deltaT_pinch
                # TF_P_gcond_out = TF_gcond_in.properties.P - self.geo_condenser.deltaP_cold
                # TF_gcond_out = self.tfluid.copy()
                # TF_gcond_out.update("PT", TF_P_gcond_out, TF_T_gcond_out)
                #
                # dT_out = tempGF_PreH_in.properties.T - TF_gcond_in.properties.T
                # if (dT_out - self.geo_condenser.deltaT_pinch)/ self.geo_condenser.deltaT_pinch < 0.01:
                #
                #     return (dT_out - self.geo_condenser.deltaT_pinch)/ self.geo_condenser.deltaT_pinch
                # else:
                #     Rgcond = R / self.WF_evaporator.MassRatio
                #     # self.geo_condenser.set_inputs(MassRatio=-1, Inlet_hot=GF_Evap_in, Inlet_cold=TF_gcond_in,
                #     #                               Outlet_hot=tempGF_PreH_in, Outlet_cold=TF_gcond_out)
                #     self.geo_condenser.set_inputs(MassRatio=Rgcond, Inlet_hot=GF_Evap_in, Inlet_cold=TF_gcond_in, Outlet_cold=TF_gcond_out)
                #     A, B = self.geo_condenser.calc()
                #
                #     return (self.geo_condenser.min_deltaT - self.geo_condenser.deltaT_pinch) / self.geo_condenser.deltaT_pinch

                return diff

            dTmin = self.geo_condenser.deltaT_pinch + self.WF_evaporator.deltaT_pinch
            dTmax = GF_Evap_in.properties.T - WF_sup_in.properties.T

            if dT_search(dTmin) > 0:
                res = root_scalar(dT_search, method="brentq", bracket=[dTmin, dTmax])
                dT_sol = res.root
            else:
                dT_sol = dTmax

            self.evaporator.deltaT_pinch = dT_sol
            self.evaporator.set_inputs(MassRatio=R, Inlet_hot=GF_Evap_in, Inlet_cold=WF_evap_in, Outlet_cold=WF_sup_in)
            GF_PreH_in, temp_WF = self.evaporator.calc()

            self.WF_evaporator.set_inputs(MassRatio=-1, Inlet_hot=TF_evap_in, Inlet_cold=WF_evap_in,
                                          Outlet_cold=WF_sup_in)
            TF_gcond_in, WF_stream = self.WF_evaporator.calc()

            TF_T_gcond_out = GF_Evap_in.properties.T - self.geo_condenser.deltaT_pinch
            TF_P_gcond_out = TF_gcond_in.properties.P - self.geo_condenser.deltaP_cold
            TF_gcond_out = self.tfluid.copy()
            TF_gcond_out.update("PT", TF_P_gcond_out, TF_T_gcond_out)

            self.preheater.set_inputs(MassRatio=R, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                      Outlet_cold=WF_evap_in)
            GF_out, WF_stream = self.preheater.calc()

            dT_sup = self.superheater.min_deltaT
            dT_evap = self.evaporator.min_deltaT
            dT_gcond = min(self.evaporator.T_profile[0] - self.WF_evaporator.T_profile[0])
            dT_WFevap = self.WF_evaporator.min_deltaT
            dT_preh = self.preheater.min_deltaT

            app_sup = (dT_sup - self.superheater.deltaT_pinch)/self.superheater.deltaT_pinch
            app_evap = (dT_evap - self.evaporator.deltaT_pinch)/self.evaporator.deltaT_pinch
            app_gcond = (dT_gcond - self.geo_condenser.deltaT_pinch)/self.geo_condenser.deltaT_pinch
            app_WF_evap = (dT_WFevap - self.WF_evaporator.deltaT_pinch)/self.WF_evaporator.deltaT_pinch
            app_preh = (dT_preh - self.preheater.deltaT_pinch)/self.preheater.deltaT_pinch

            obj = app_sup**2 + app_preh**2 + app_evap**2
            # obj = app_sup**2 + app_evap**2 + app_preh**2 + app_WF_evap**2 + app_gcond**2

            if app_sup < -0.01:
                obj += 1e6 * app_sup**2
            # if app_evap < -0.01 and app_WF_evap < -0.01 and app_gcond < -0.01:
            #     obj += 1e6 * app_evap**2
            if app_WF_evap < 0:
                obj += 1e6 * app_WF_evap**2
            # if app_gcond < 0:
            #     obj += 1e6 * app_gcond**2
            if app_preh < -0.01:
                obj += 1e6 * app_preh**2

            print("R:{:.2f} obj:{:.2f} sup:{:.2f} evap:{:.2f} preh:{:.2f} gcond:{:.2f} WFev:{:.2f} ".format(R, obj, dT_sup, dT_evap, dT_preh, dT_gcond, dT_WFevap))

            return obj

        def cons_sup(x):
            res = (self.superheater.min_deltaT - self.superheater.deltaT_pinch) / self.superheater.deltaT_pinch

            if res < - 0.01:
                return res
            else:
                return 0

        def cons_evap(x):
            res = (self.evaporator.min_deltaT - self.evaporator.deltaT_pinch)/ self.evaporator.deltaT_pinch

            res_evap = (self.evaporator.min_deltaT - self.evaporator.deltaT_pinch)/self.evaporator.deltaT_pinch
            res_WF_evap = (self.WF_evaporator.min_deltaT - self.WF_evaporator.deltaT_pinch)/self.WF_evaporator.deltaT_pinch
            res_gcond = (self.geo_condenser.min_deltaT - self.geo_condenser.deltaT_pinch)/self.geo_condenser.deltaT_pinch

            if res_evap < - 0.01 and res_WF_evap < -0.01:
                return res
            else:
                return 0

        def cons_WF_evap(x):

            res = (self.WF_evaporator.min_deltaT - self.WF_evaporator.deltaT_pinch) / self.WF_evaporator.deltaT_pinch

            if res < - 0.01:
                return res
            else:
                return 0

        def cons_gcond(x):
            res = (self.geo_condenser.min_deltaT - self.geo_condenser.deltaT_pinch)/ self.geo_condenser.deltaT_pinch

            if res < - 0.01:
                return res
            else:
                return 0

        def cons_preh(x):
            res = (self.preheater.min_deltaT - self.preheater.deltaT_pinch) / self.preheater.deltaT_pinch

            if res < - 0.01:
                return res
            else:
                return 0


        # switch the geofluid to the interpolation fluid
        geofluid = self.geofluid.copy()
        if self.interpolation:
            temp_geo = self.geofluid_table.copy()
            temp_geo.fluid.update_composition(geofluid.fluid.composition[-2:])
            temp_geo._update_quantity(geofluid.m)
            temp_geo.update("PH", geofluid.properties.P, geofluid.properties.H)

            geofluid = temp_geo

        dTs = [self.preheater.deltaT_pinch, self.evaporator.deltaT_pinch + self.geo_condenser.deltaT_pinch, self.superheater.deltaT_pinch]
        self.temp_HX.deltaP_cold = self.preheater.deltaP_cold + self.evaporator.deltaP_cold + self.superheater.deltaP_cold
        self.temp_HX.deltaP_hot = self.preheater.deltaP_hot + self.evaporator.deltaP_hot + self.superheater.deltaP_hot

        # calculate Rmax
        self.temp_HX.deltaT_pinch = min(dTs)
        self.temp_HX.set_inputs(MassRatio=-1, Inlet_hot=geofluid, Inlet_cold=WF_preh_in, Outlet_cold=WF_turb_in)
        temp_GF_out, temp_WF_out = self.temp_HX.calc()
        Rmax = self.temp_HX.MassRatio

        self.temp_HX.deltaT_pinch = max(dTs)
        self.temp_HX.set_inputs(MassRatio=-1, Inlet_hot=geofluid, Inlet_cold=WF_preh_in, Outlet_cold=WF_turb_in)
        temp_GF_out, temp_WF_out = self.temp_HX.calc()
        Rmin = self.temp_HX.MassRatio

        # error = 1
        # Rmax = 0.2
        # while error > 0:
        #     R_search(Rmax)
        #
        #     if cons_sup(0) < 0 or cons_evap(0) <0 or cons_preh(0) < 0:
        #     # if cons_sup(0) < 0 or cons_evap(0) <0 or cons_preh(0) < 0 or cons_WF_evap(0) < 0 or cons_gcond(0) < 0:
        #         error = -1
        #     else:
        #         Rmin = Rmax
        #         Rmax = Rmin + 0.2

        # result = minimize_scalar(R_search, method="bounded", bounds=[Rmin, Rmax], options={"xatol":1e-4})
        result = minimize_scalar(R_search, method="bounded", bounds=[Rmin, Rmax])

        GF_out = self.preheater.outlet[0].copy()

        if self.interpolation:
            self.geofluid_out = self.geofluid.copy()
            self.geofluid_out.update("PH", GF_out.properties.P, GF_out.properties.H)

        else:
            self.geofluid_out = GF_out.copy()

    def __calc_mass_rates(self):

        # updating the component mass rates
        self.wfluid._update_quantity(self.geofluid_out.m * self.preheater.MassRatio)
        self.tfluid._update_quantity(self.wfluid.m / self.WF_evaporator.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.feedpump.update_inlet_rate(self.wfluid.m)
        self.turbine.update_inlet_rate(self.wfluid.m)
        if self.recuperated:
            self.recuperator.update_inlet_rate(self.wfluid.m, self.wfluid.m)

        self.superheater.update_inlet_rate(self.geofluid.m, self.wfluid.m)
        self.evaporator.update_inlet_rate(self.geofluid.m, self.tfluid.m)
        # self.geo_condenser.update_inlet_rate(self.tfluid.m, self.wfluid.m)
        self.preheater.update_inlet_rate(self.geofluid.m, self.wfluid.m)

        self.condenser.update_inlet_rate(self.wfluid.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

    def __calc_performance(self):
        # calculate the net-power produced
        self.cycle_power = self.turbine.work + self.feedpump.work
        self.parasitic_power = self.coolingpump.work
        self.net_power = self.cycle_power + self.parasitic_power

        # calculate the heat flow into and out of the plant
        self.Q_in = self.geofluid.m*(self.geofluid_in.properties.H - self.geofluid_out.properties.H)
        self.Q_in_max = self.geofluid.m * self.geofluid_in.properties.H
        self.Q_out = self.coolant.m*(self.coolant_out.properties.H - self.coolant_in.properties.H)

        # calculate the exergy flow into and out of the plant
        self.Ein = self.geofluid.m * (self.geofluid_in.properties.H - Tref * self.geofluid_in.properties.S)
        self.Ein += self.coolant.m * (self.coolant_in.properties.H - Tref * self.coolant_in.properties.S)
        self.Eout = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        self.Eout += self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        # perform exergy balance on all components
        self.superheater.calc_exergy_balance()
        self.evaporator.calc_exergy_balance()
        self.preheater.calc_exergy_balance()
        self.condenser.calc_exergy_balance()
        self.feedpump.calc_exergy_balance()
        self.turbine.calc_exergy_balance()

        self.Eloss = self.superheater.Eloss + self.evaporator.Eloss + self.preheater.Eloss + self.condenser.Eloss + self.feedpump.Eloss + self.turbine.Eloss
        if self.recuperated:
            self.recuperator.calc_exergy_balance()
            self.Eloss += self.recuperator.Eloss

        # this is to QC the results
        self.energy_balance = self.Q_in-self.Q_out + self.cycle_power  # this should be zero
        self.exergy_balance = self.Ein - self.Eout - self.Eloss - abs(self.cycle_power)  # this should be zero

        self.eta_I_cycle = -self.net_power / self.Q_in
        self.eta_I_recov = self.Q_in / self.Q_in_max
        self.eta_I_plant = self.eta_I_cycle * self.eta_I_recov

        self.eta_II_BF = -self.net_power / self.Ein
        self.eta_II_FUNC = -self.net_power / (self.Ein - self.Eout)

    def calc(self, P_max, T_max, T_min):

        self.Pmax = P_max
        self.Tmax = T_max
        self.Tmin = T_min

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

        WF_pump_in, WF_recu_cold_in = self.__calc_feedpump(wfluid)

        WF_evap_in, WF_sup_in, WF_turb_in = self.__calc_PHE_streams()

        WF_recu_hot_in = self.__calc_turbine(WF_turb_in)

        WF_cond_in, WF_preh_in = self.__calc_recuperator(WF_recu_hot_in, WF_recu_cold_in, WF_evap_in)

        self.__calc_condenser(WF_cond_in, WF_pump_in)

        self.__calc_PHE(WF_preh_in, WF_evap_in, WF_sup_in, WF_turb_in)

        self.__calc_mass_rates()

        self.__calc_performance()

        return self.net_power * 1.0

    def plot_TQ(self):

        wf_style = {"color": "green", "label": "working fluid"}
        geo_style = {"color": "red", "label": "geofluid"}
        cool_style = {"color": "blue", "label": "coolant"}
        recu_style = {"linestyle": "--", "color": "black"}
        tert_style = {"color": "black", "label": "tert fluid"}

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

        duty = self.WF_evaporator.Duty_profile[1] * self.tfluid.m
        T_hot = self.WF_evaporator.T_profile[0]
        plt.plot(duty + offset, T_hot, **tert_style)


        duty = self.evaporator.Duty_profile[1] * self.geofluid_out.m
        T_hot = self.evaporator.T_profile[0]
        T_cold = self.evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style)

        offset += duty[-1]

        duty = self.superheater.Duty_profile[1] * self.geofluid_out.m
        T_hot = self.superheater.T_profile[0]
        T_cold = self.superheater.T_profile[1]

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

    def plot_Eloss(self):

        E_reinjected = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        E_rejected = self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        store = [{"equip":"Reinjected", "val": E_reinjected},
                 {"equip": "Rejected", "val": E_rejected},
                 {"equip": "Superheater", "val": self.superheater.Eloss},
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


