import Simulator
from Simulator.cycle import BinaryCycle
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar, minimize_scalar, minimize, Bounds
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

    def __init__(self, recu=True, NCG=True):

        super().__init__()

        self.recuperated = recu
        self.NCG_handled = NCG

        self.feedpump = Simulator.pump(0.75, cost_model="astolfi", mech_eff=0.95)

        self.superheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap + 0.1, deltaP_hot=0, deltaP_cold=0,
                                                    cost_model="peters-floating")
        self.evaporator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap, deltaP_hot=0, deltaP_cold=0,cost_model="peters-floating")
        self.preheater = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, deltaP_hot=0, deltaP_cold=0,cost_model="peters-floating")

        self.temp_HX = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, deltaP_hot=0, deltaP_cold=0,)

        self.recuperator = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_vap, deltaP_hot=0, deltaP_cold=0, cost_model="peters-floating")
        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, deltaP_hot=0, deltaP_cold=0, cost_model="condenser-GETEM")

        self.coolingpump = Simulator.pump(0.6, cost_model="none", mech_eff=0.95)

        self.turbine = Simulator.turbine(0.85, cost_model="similitude", mech_eff=0.95)

        self.ncg_sep = Simulator.separator()
        self.brine_pump = Simulator.pump(0.75, cost_model="astolfi")

        self.ncg_comp = Simulator.multistage_compression(0.7, 1, cost_model="default")
        self.ncg_pump = Simulator.pump(0.75, cost_model="astolfi")
        self.co2_liquefier = Simulator.heat_exchanger(deltaT_pinch=0.5, deltaP_hot=0, deltaP_cold=0, cost_model="condenser-GETEM")

        self.mixer = Simulator.mixer()

        self.geofluid_P_out = 75e5

        self.drilling_costs = 0

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

    def __calc_turbine(self, WF_turb_in):
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
        WF_evap_in.update("PT", WF_Pevap_in, WF_Tevap_in)

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

                self.recuperator.set_inputs(Inlet_hot=WF_recu_hot_in, Inlet_cold=WF_recu_cold_in,
                                            Outlet_cold=WF_preh_in)
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

            self.evaporator.set_inputs(MassRatio=R, Inlet_hot=GF_Evap_in, Inlet_cold=WF_evap_in,
                                       Outlet_cold=WF_sup_in)
            GF_PreH_in, WF_stream = self.evaporator.calc()

            self.preheater.set_inputs(MassRatio=R, Inlet_hot=GF_PreH_in, Inlet_cold=WF_preh_in,
                                      Outlet_cold=WF_evap_in)
            BF_out, WF_stream = self.preheater.calc()

            dT_sup = self.superheater.min_deltaT
            dT_evap = self.evaporator.min_deltaT
            dT_preh = self.preheater.min_deltaT

            app_sup = (dT_sup - self.superheater.deltaT_pinch) / self.superheater.deltaT_pinch
            app_evap = (dT_evap - self.evaporator.deltaT_pinch) / self.evaporator.deltaT_pinch
            app_preh = (dT_preh - self.preheater.deltaT_pinch) / self.preheater.deltaT_pinch

            obj = app_sup ** 2 + app_evap ** 2 + app_preh ** 2
            if app_sup < 0:
                obj += 1e6 * app_sup ** 2
            if app_evap < 0:
                obj += 1e6 * app_evap ** 2
            if app_preh < 0:
                obj += 1e6 * app_preh ** 2

            # print(R, obj, dT_sup, dT_evap, dT_preh)

            return obj

        def cons_sup(x):
            return self.superheater.min_deltaT - self.superheater.deltaT_pinch

        def cons_evap(x):
            return self.evaporator.min_deltaT - self.evaporator.deltaT_pinch

        def cons_preh(x):
            return self.preheater.min_deltaT - self.preheater.deltaT_pinch

        # switch the geofluid to the interpolation fluid
        geofluid = self.geofluid.copy()
        if self.interpolation:
            temp_geo = self.geofluid_table.copy()
            temp_geo.fluid.update_composition(geofluid.fluid.composition[-2:])
            temp_geo._update_quantity(geofluid.m)
            temp_geo.update("PH", geofluid.properties.P, geofluid.properties.H)

            geofluid = temp_geo

        dTs = [self.preheater.deltaT_pinch, self.evaporator.deltaT_pinch, self.superheater.deltaT_pinch]
        max_dT = max(dTs)
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

        error = 1
        iter = 0
        while error > 0 and iter < 25:
            R_search(Rmin)

            if cons_sup(0) > 0 and cons_evap(0) > 0 and cons_preh(0) > 0:
                error = -1
            else:
                Rmax = Rmin
                Rmin *= 0.99

            iter += 1

        result = minimize_scalar(R_search, method="bounded", bounds=[Rmin, Rmax], options={"xatol": 1e-4, "maxiter": 25})

        temp_GF_out = self.preheater.outlet[0].copy()

        if self.interpolation:
            geofluid_out = self.geofluid.copy()
            geofluid_out.update("PH", temp_GF_out.properties.P, temp_GF_out.properties.H)

        else:
            geofluid_out = temp_GF_out.copy()

        return geofluid_out

    def __calc_NCG_handling(self, gf_out):

        self.ncg_sep.set_inputs(gf_out)
        brine_out, ncg_out = self.ncg_sep.calc()

        self.NCG_handling = False
        if gf_out.properties.P < self.geofluid_P_out:

            self.NCG_handling = True

            self.brine_pump.set_inputs(brine_out, self.geofluid_P_out)
            brine_hp = self.brine_pump.calc()

            ncg_out.fluid.update_composition([0, 1])
            temp_co2 = ncg_out.copy()
            temp_co2.update("TQ", 300, 1)
            Psat = temp_co2.properties.P

            self.liquefaction = False
            if self.geofluid_P_out < Psat:
                self.ncg_comp.set_inputs(ncg_out, self.geofluid_P_out, findN=True)
                co2_hp = self.ncg_comp.calc()
            else:
                self.liquefaction = True

                self.ncg_comp.set_inputs(ncg_out, Psat, findN=True)
                co2_vap = self.ncg_comp.calc()

                temp_co2.update("TQ", 300, 0)
                co2_liq = temp_co2.copy()

                self.ncg_coolant_in = self.coolant_in.copy()
                self.co2_liquefier.set_inputs(MassRatio=-1, Inlet_hot=co2_vap, Inlet_cold=self.ncg_coolant_in,
                                              Outlet_hot=co2_liq)
                co2_liq, self.ncg_coolant_out = self.co2_liquefier.calc()

                self.ncg_pump.set_inputs(co2_liq, self.geofluid_P_out)
                co2_hp = self.ncg_pump.calc()

            self.mixer.set_inputs(brine_hp, co2_hp)
            self.geofluid_out = self.mixer.calc()

        else:
            self.geofluid_out = gf_out.copy()

    def update_mass_rate(self, m):

        self.geofluid._update_quantity(m)
        self.geofluid_in._update_quantity(m)
        self.geofluid_out._update_quantity(m)

        self.wfluid._update_quantity(m * self.preheater.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.feedpump.update_inlet_rate(self.wfluid.m)
        self.turbine.update_inlet_rate(self.wfluid.m)
        if self.recuperated:
            self.recuperator.update_inlet_rate(self.wfluid.m, self.wfluid.m)

        self.superheater.update_inlet_rate(m, self.wfluid.m)
        self.evaporator.update_inlet_rate(m, self.wfluid.m)
        self.preheater.update_inlet_rate(m, self.wfluid.m)

        self.condenser.update_inlet_rate(self.wfluid.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

        # NCG handling
        self.ncg_sep.update_inlet_rate(self.geofluid.m)
        lp_brine_m = self.ncg_sep.outlet[0].m
        lp_ncg_m = self.ncg_sep.outlet[1].m

        if self.NCG_handling:
            self.brine_pump.update_inlet_rate(lp_brine_m)
            self.ncg_comp.update_inlet_rate(lp_ncg_m)

            if self.liquefaction:
                ncg_coolant_m = lp_ncg_m * self.co2_liquefier.MassRatio
                self.co2_liquefier.update_inlet_rate(lp_ncg_m, ncg_coolant_m)
                self.ncg_pump.update_inlet_rate(lp_ncg_m)

        self.__calc_performance()
        self.__calc_cost()

        self.calc_economics()

    def __calc_mass_rates(self):

        # updating the component mass rates
        self.wfluid._update_quantity(self.geofluid_out.m * self.preheater.MassRatio)
        self.coolant_in._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant._update_quantity(self.wfluid.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(self.wfluid.m * self.condenser.MassRatio)

        self.feedpump.update_inlet_rate(self.wfluid.m)
        self.turbine.update_inlet_rate(self.wfluid.m)
        if self.recuperated:
            self.recuperator.update_inlet_rate(self.wfluid.m, self.wfluid.m)

        self.superheater.update_inlet_rate(self.geofluid.m, self.wfluid.m)
        self.evaporator.update_inlet_rate(self.geofluid.m, self.wfluid.m)
        self.preheater.update_inlet_rate(self.geofluid.m, self.wfluid.m)

        self.condenser.update_inlet_rate(self.wfluid.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

        # NCG handling
        self.ncg_sep.update_inlet_rate(self.geofluid.m)
        lp_brine_m = self.ncg_sep.outlet[0].m
        lp_ncg_m = self.ncg_sep.outlet[1].m

        if self.NCG_handling:
            self.brine_pump.update_inlet_rate(lp_brine_m)
            self.ncg_comp.update_inlet_rate(lp_ncg_m)

            if self.liquefaction:
                ncg_coolant_m = lp_ncg_m * self.co2_liquefier.MassRatio
                self.co2_liquefier.update_inlet_rate(lp_ncg_m, ncg_coolant_m)
                self.ncg_pump.update_inlet_rate(lp_ncg_m)

    def __calc_performance(self):
        # calculate the net-power produced
        self.cycle_power = self.turbine.work + self.feedpump.work

        self.ncg_handling_power = 0
        if self.NCG_handling:
            self.ncg_handling_power += self.brine_pump.work \
                                       + self.ncg_comp.work
            if self.liquefaction:
                self.ncg_handling_power += self.ncg_pump.work

        self.parasitic_power = self.coolingpump.work + self.ncg_handling_power
        self.net_power = self.cycle_power + self.parasitic_power

        self.cycle_power_elec = self.turbine.power_elec + self.feedpump.power_elec

        self.ncg_handling_power_elec = 0
        if self.NCG_handling:
            self.ncg_handling_power_elec += self.brine_pump.power_elec \
                                       + self.ncg_comp.power_elec
            if self.liquefaction:
                self.ncg_handling_power_elec += self.ncg_pump.power_elec

        self.parasitic_power_elec = self.coolingpump.power_elec + self.ncg_handling_power_elec
        self.net_power_elec = self.cycle_power_elec + self.parasitic_power_elec

        # calculate the heat flow into and out of the plant
        self.Q_in = self.geofluid.m * (self.geofluid_in.properties.H - self.geofluid_out.properties.H)
        self.Q_in_max = self.geofluid.m * self.geofluid_in.properties.H
        self.Q_out = self.coolant.m * (self.coolant_out.properties.H - self.coolant_in.properties.H)

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
        self.energy_balance = self.Q_in - self.Q_out + self.cycle_power  # this should be zero
        self.exergy_balance = self.Ein - self.Eout - self.Eloss - abs(self.cycle_power)  # this should be zero

        E_reinjected = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        E_rejected = self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        self.exergy_losses = [{"equip": "Reinjected", "val": E_reinjected},
                              {"equip": "Rejected", "val": E_rejected},
                              {"equip": "Superheater", "val": self.superheater.Eloss},
                              {"equip": "Evaporator", "val": self.evaporator.Eloss},
                              {"equip": "PreHeater", "val": self.preheater.Eloss},
                              {"equip": "Condenser", "val": self.condenser.Eloss},
                              {"equip": "Turbine", "val": self.turbine.Eloss},
                              {"equip": "Pump", "val": self.feedpump.Eloss}
                              ]
        if self.recuperated:
            self.exergy_losses.append({"equip": "Recuperator", "val": self.recuperator.Eloss})

        self.eta_I_cycle = -self.net_power / self.Q_in
        self.eta_I_recov = self.Q_in / self.Q_in_max
        self.eta_I_plant = self.eta_I_cycle * self.eta_I_recov

        self.eta_II_BF = -self.net_power / self.Ein
        self.eta_II_FUNC = -self.net_power / (self.Ein - self.Eout)

    def __calc_cost(self):

        cost = 0

        cost += self.feedpump.calc_cost()
        cost += self.superheater.calc_cost()
        cost += self.evaporator.calc_cost()
        cost += self.preheater.calc_cost()

        if self.recuperated:
            cost += self.recuperator.calc_cost()

        cost += self.condenser.calc_cost()
        cost += self.coolingpump.calc_cost()
        cost += self.turbine.calc_cost()

        if self.NCG_handling:
            cost += self.brine_pump.calc_cost()
            cost += self.ncg_comp.calc_cost()
            if self.liquefaction:
                cost += self.ncg_pump.calc_cost()
                cost += self.co2_liquefier.calc_cost()

        self.primary_equipment_cost = cost * 1e-6
        self.secondary_equipment_cost = 0.4 * cost * 1e-6  # control system, piping, etc.
        self.construction_cost = 0.7 * (self.primary_equipment_cost + self.secondary_equipment_cost)

        self.cost = self.primary_equipment_cost \
                    + self.secondary_equipment_cost \
                    + self.construction_cost \
                    + self.drilling_costs

        self.specific_cost = 1e3 * self.cost / abs(self.net_power_elec * 1e-6)  # $€/kW

        self.costs = [{"equip": "Superheater", "val": self.superheater.cost},
                      {"equip": "Evaporator", "val": self.evaporator.cost},
                      {"equip": "PreHeater", "val": self.preheater.cost},
                      {"equip": "Condenser", "val": self.condenser.cost},
                      {"equip": "Turbine", "val": self.turbine.cost},
                      {"equip": "Pump", "val": self.feedpump.cost},
                      {"equip": "Fan", "val": self.coolingpump.cost},
                      {"equip": "SecondaryEquip", "val": self.secondary_equipment_cost},
                      {"equip": "Construction", "val": self.construction_cost}
                      ]
        if self.NCG_handling:
            self.costs.append({"equip": "BrinePump", "val": self.brine_pump.cost})
            self.costs.append({"equip": "NCGComp", "val": self.ncg_comp.cost})

            if self.liquefaction:
                self.costs.append({"equip": "NCGPump", "val": self.ncg_pump.cost})
                self.costs.append({"equip": "NCGCondenser", "val": self.co2_liquefier.cost})

        if self.recuperated:
            self.costs.append({"equip": "Recuperator", "val": self.recuperator.cost})

    def calc(self, P_max, T_max, T_min, *args):

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

        geofluid_out = self.__calc_PHE(WF_preh_in, WF_evap_in, WF_sup_in, WF_turb_in)

        self.__calc_NCG_handling(geofluid_out)

        self.__calc_mass_rates()

        self.__calc_performance()

        self.__calc_cost()

        self.calc_economics()

        return self.net_power * 1.0

    def plot_TQ(self, show_plot=True):

        coolant = {"Duty": [], "Temperature": []}
        wf_heating = {"Duty": [], "Temperature": []}
        wf_cooling = {"Duty": [], "Temperature": []}
        geofluid = {"Duty": [], "Temperature": []}
        recu_low = {"Duty": [], "Temperature": []}
        recu_high = {"Duty": [], "Temperature": []}

        offset = 0.0

        duty = list(self.condenser.Duty_profile[1] * self.wfluid.m)
        coolant["Duty"] += duty
        coolant["Temperature"] += list(self.condenser.T_profile[1])
        wf_cooling["Duty"] += duty
        wf_cooling["Temperature"] += list(self.condenser.T_profile[0])

        if self.recuperated:
            offset += duty[-1]

            wf_cooling["Duty"] += list(self.recuperator.Duty_profile[1] * self.wfluid.m + offset)
            wf_cooling["Temperature"] += list(self.recuperator.T_profile[0])

            wf_heating["Duty"] += list(self.recuperator.Duty_profile[1] * self.wfluid.m)
            wf_heating["Temperature"] += list(self.recuperator.T_profile[1])

            recu_low["Duty"] = [0, offset]
            recu_low["Temperature"] = [wf_cooling["Temperature"][0], self.recuperator.T_profile[0][0]]

            recu_high["Duty"] = [wf_heating["Duty"][-1], wf_cooling["Duty"][-1]]
            recu_high["Temperature"] = [self.recuperator.T_profile[1][-1], self.recuperator.T_profile[0][-1]]

        offset = 0.0
        if self.recuperated:
            offset += wf_heating["Duty"][-1]

        duty = list(self.preheater.Duty_profile[1] * self.geofluid_out.m + offset)
        wf_heating["Duty"] += duty
        wf_heating["Temperature"] += list(self.preheater.T_profile[1])
        geofluid["Duty"] += duty
        geofluid["Temperature"] += list(self.preheater.T_profile[0])

        offset = duty[-1]

        duty = list(self.evaporator.Duty_profile[1] * self.geofluid_out.m + offset)
        wf_heating["Duty"] += duty
        wf_heating["Temperature"] += list(self.evaporator.T_profile[1])
        geofluid["Duty"] += duty
        geofluid["Temperature"] += list(self.evaporator.T_profile[0])

        offset = duty[-1]

        duty = list(self.superheater.Duty_profile[1] * self.geofluid_out.m + offset)
        wf_heating["Duty"] += duty
        wf_heating["Temperature"] += list(self.superheater.T_profile[1])
        geofluid["Duty"] += duty
        geofluid["Temperature"] += list(self.superheater.T_profile[0])

        if show_plot:
            plt.plot(coolant["Duty"], coolant["Temperature"])
            plt.plot(wf_cooling["Duty"], wf_cooling["Temperature"])
            plt.plot(wf_heating["Duty"], wf_heating["Temperature"])
            plt.plot(geofluid["Duty"], geofluid["Temperature"])

            if self.recuperated:
                plt.plot(recu_low["Duty"], recu_low["Temperature"])
                plt.plot(recu_high["Duty"], recu_high["Temperature"])

            plt.show()

        TQ_plot = {"coolant": coolant,
                   "wf_heating": wf_heating,
                   "wf_cooling": wf_cooling,
                   "geofluid": geofluid,
                   "recu_low": recu_low,
                   "recu_high": recu_high}

        return TQ_plot

    def plot_TQ2(self):

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

    # def plot_Eloss(self):
    #
    #     def sortFunc(e):
    #         return e["val"]
    #
    #     self.exergy_losses.sort(key=sortFunc, reverse=True)
    #
    #     labels = [x["equip"] for x in self.exergy_losses]
    #     values = [x["val"] for x in self.exergy_losses]
    #
    #     fig, ax = plt.subplots()
    #     ax.pie(values, labels=labels, autopct='%1.1f%%')
    #     plt.show()
    #
    # def plot_costs(self):
    #
    #     def sortFunc(e):
    #         return e["val"]
    #
    #     self.costs.sort(key=sortFunc, reverse=True)
    #
    #     labels = [x["equip"] for x in self.costs]
    #     values = [x["val"] for x in self.costs]
    #
    #     fig, ax = plt.subplots()
    #     ax.pie(values, labels=labels, autopct='%1.1f%%')
    #     plt.show()
