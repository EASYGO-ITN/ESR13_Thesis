import Simulator
from Simulator.cycle import Cycle
from Simulator import Tref
from Simulator.streams import MaterialStream
from FluidProperties.fluid import Fluid
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

"""

      *--------------> Turb ----*
      |                         |
      |             *---------- Recup <---- Pump <----*
      |             |               |                 |
----> Evap ----> PreH ---->         *----> Cond ------*
         |       |
         *-------*

"""


class DirectCycle(Cycle):

    def __init__(self):

        super().__init__()

        self.flash_sep = Simulator.separator()
        # self.ncg_sep = Simulator.separator()

        self.turbine = Simulator.turbine(0.85, BaumannCorrection=True, cost_model="thermoflex")

        self.condenser = Simulator.heat_exchanger(deltaT_pinch=self.deltaT_pinch_liq, deltaP_hot=0, cost_model="condenser-GETEM")

        self.coolingpump = Simulator.pump(0.6, cost_model="fan")
        #
        #
        # self.brine_pump = Simulator.pump(0.75, cost_model="default")
        # self.condensate_pump = Simulator.pump(0.75, cost_model="default")

        self.ncg_sep_lp = Simulator.separator()
        self.brine_pump_lP = Simulator.pump(0.75, cost_model="astolfi")
        self.condensate_pump_lP = Simulator.pump(0.75, cost_model="astolfi")
        self.ncg_comp_lp = Simulator.multistage_compression(0.7, 1, cost_model="default")

        self.absorption = Simulator.mixer()
        self.ncg_sep_hp = Simulator.separator()

        self.brine_pump_hp = Simulator.pump(0.75, cost_model="astolfi")
        self.ncg_comp_hp = Simulator.multistage_compression(0.7, 1, cost_model="default")
        self.ncg_pump_hp = Simulator.pump(0.75, cost_model="astolfi")

        self.co2_liquefier = Simulator.heat_exchanger(deltaT_pinch=0.5, deltaP_hot=0, deltaP_cold=0,
                                                      cost_model="condenser-GETEM")

        self.mixer = Simulator.mixer()

        self.geofluid_P_out = 75e5

        self.drilling_costs = 0

    def __calc_flash_sep(self, flash, gfluid):

        P_in = self.geofluid_in.properties.P * 1.0

        P_flash = flash * P_in
        self.P_flash = P_flash

        self.flash_sep.set_inputs(gfluid, InputSpec="PH", Input1=P_flash, Input2=gfluid.properties.H)
        brine, vapour = self.flash_sep.calc()

        return brine, vapour

    def __calc_condenser(self, vap_turb_out):

        # switch the geofluid to the interpolation fluid
        if self.interpolation:
            vap_cond_in = self.geofluid_table.copy()
            vap_cond_in.fluid.update_composition(vap_turb_out.fluid.composition)
            vap_cond_in._update_quantity(vap_turb_out.m)
            vap_cond_in.update("PH", vap_turb_out.properties.P, vap_turb_out.properties.H)
        else:
            vap_cond_in = vap_turb_out.copy()

        # calculate the condensation temperature
        try:
            temp_vap = vap_cond_in.copy()
            temp_vap.update("PQ", self.Pmin, 0)
            T_min = temp_vap.properties.T - self.deltaT_subcool

            if T_min < self.T_ambient + self.deltaT_pinch_liq:
                T_min = self.T_ambient + self.deltaT_pinch_liq
        except:
            T_min = self.T_ambient + self.deltaT_pinch_liq + 1

        self.Tmin = T_min

        vap_cond_out = vap_cond_in.copy()
        vap_cond_out.update("PT", self.Pmin, T_min)

        # calculate the condenser
        P_cool_in = self.coolant.properties.P + self.condenser.deltaP_cold
        self.coolingpump.set_inputs(self.coolant, P_cool_in)
        self.coolant_in = self.coolingpump.calc()

        self.condenser.set_inputs(MassRatio=-1, Inlet_hot=vap_cond_in, Inlet_cold=self.coolant_in,
                                  Outlet_hot=vap_cond_out)
        vap_cond_out, self.coolant_out = self.condenser.calc()

        if self.interpolation:
            temp_vapour_out = vap_turb_out.copy()
            temp_vapour_out.update("PH", vap_cond_out.properties.P, vap_cond_out.properties.H)
        else:
            temp_vapour_out = vap_cond_out.copy()
        vap_cond_out = temp_vapour_out

        return vap_cond_out

    def update_mass_rate(self, m):

        ratio = m / self.geofluid.m

        self.geofluid._update_quantity(m)

        vapour = self.turbine.inlet.copy()
        vapour._update_quantity(vapour.m * ratio)

        brine = self.brine_pump_lP.inlet.copy()
        brine._update_quantity(brine.m * ratio)

        ncg = self.ncg_comp_lp.inlet.copy()
        ncg._update_quantity(ncg.m * ratio)

        condensate = self.condensate_pump_lP.inlet.copy()
        condensate._update_quantity(condensate.m * ratio)

        self.geofluid_in._update_quantity(m)
        self.geofluid_out._update_quantity(m)

        self.coolant._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(vapour.m * self.condenser.MassRatio)

        self.flash_sep.update_inlet_rate(vapour.m + brine.m)
        self.ncg_sep_lp.update_inlet_rate(vapour.m)

        self.turbine.update_inlet_rate(vapour.m)

        self.condenser.update_inlet_rate(vapour.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

        lp_brine_m = self.flash_sep.outlet[0].m
        lp_cond_m = self.ncg_sep_lp.outlet[0].m
        lp_ncg_m = self.ncg_sep_lp.outlet[1].m

        self.brine_pump_lP.update_inlet_rate(lp_brine_m)
        self.condensate_pump_lP.update_inlet_rate(lp_cond_m)
        self.ncg_comp_lp.update_inlet_rate(lp_ncg_m)

        self.absorption.update_inlet_rate([lp_brine_m, lp_cond_m, lp_ncg_m])
        self.ncg_sep_hp.update_inlet_rate(self.geofluid.m)

        mp_brine_m = self.ncg_sep_hp.outlet[0].m
        mp_ncg_m = self.ncg_sep_hp.outlet[1].m

        self.brine_pump_hp.update_inlet_rate(mp_brine_m)
        self.ncg_comp_hp.update_inlet_rate(mp_ncg_m)
        self.ncg_pump_hp.update_inlet_rate(mp_brine_m)

        ncg_coolant_m = mp_ncg_m * self.co2_liquefier.MassRatio
        self.co2_liquefier.update_inlet_rate(mp_ncg_m, ncg_coolant_m)

        self.mixer.update_inlet_rate([mp_brine_m, mp_ncg_m])

        self.__calc_performance()
        self.__calc_cost()

        self.calc_economics()

    def __calc_mass_rates(self, vapour, brine, ncg, condensate):

        vapour._update_quantity(self.geofluid.m*vapour.m)
        brine._update_quantity(self.geofluid.m*brine.m)
        ncg._update_quantity(self.geofluid.m * ncg.m)
        condensate._update_quantity(self.geofluid.m * condensate.m)

        self.geofluid_in._update_quantity(self.geofluid.m)
        self.geofluid_out._update_quantity(self.geofluid.m*self.geofluid_out.m)

        self.coolant._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_in._update_quantity(vapour.m * self.condenser.MassRatio)
        self.coolant_out._update_quantity(vapour.m * self.condenser.MassRatio)

        self.flash_sep.update_inlet_rate(vapour.m + brine.m)
        self.ncg_sep_lp.update_inlet_rate(vapour.m)

        self.turbine.update_inlet_rate(vapour.m)

        self.condenser.update_inlet_rate(vapour.m, self.coolant.m)
        self.coolingpump.update_inlet_rate(self.coolant.m)

        lp_brine_m = self.flash_sep.outlet[0].m
        lp_cond_m = self.ncg_sep_lp.outlet[0].m
        lp_ncg_m = self.ncg_sep_lp.outlet[1].m

        # print(lp_cond_m + lp_brine_m + lp_ncg_m, self.geofluid.m)

        self.brine_pump_lP.update_inlet_rate(lp_brine_m)
        self.condensate_pump_lP.update_inlet_rate(lp_cond_m)
        self.ncg_comp_lp.update_inlet_rate(lp_ncg_m)

        self.absorption.update_inlet_rate([lp_brine_m, lp_cond_m, lp_ncg_m])
        self.ncg_sep_hp.update_inlet_rate(self.geofluid.m)

        mp_brine_m = self.ncg_sep_hp.outlet[0].m
        mp_ncg_m = self.ncg_sep_hp.outlet[1].m

        self.brine_pump_hp.update_inlet_rate(mp_brine_m)
        self.ncg_comp_hp.update_inlet_rate(mp_ncg_m)
        self.ncg_pump_hp.update_inlet_rate(mp_brine_m)

        ncg_coolant_m = mp_ncg_m * self.co2_liquefier.MassRatio
        self.co2_liquefier.update_inlet_rate(mp_ncg_m, ncg_coolant_m)

        self.mixer.update_inlet_rate([mp_brine_m, mp_ncg_m])

        #
        # self.brine_pump.update_inlet_rate(brine.m)
        # self.condensate_pump.update_inlet_rate(condensate.m)
        # self.ncg_pump.update_inlet_rate(ncg.m)
        #
        # self.geo_mix.update_inlet_rate([brine.m, condensate.m, ncg.m])

    def __calc_performance(self):

        self.cycle_power = self.turbine.work
        self.ncg_handling_power = self.brine_pump_lP.work \
                                  + self.brine_pump_hp.work \
                                  + self.ncg_comp_lp.work \
                                  + self.ncg_comp_hp.work \
                                  + self.ncg_pump_hp.work
        self.parasitic_power = self.coolingpump.work + self.ncg_handling_power
        self.net_power = self.cycle_power + self.parasitic_power

        self.cycle_power_elec = self.turbine.power_elec
        self.ncg_handling_power_elec = self.brine_pump_lP.power_elec \
                                  + self.brine_pump_hp.power_elec \
                                  + self.ncg_comp_lp.power_elec \
                                  + self.ncg_comp_hp.power_elec \
                                  + self.ncg_pump_hp.power_elec
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
        self.flash_sep.calc_exergy_balance()
        self.turbine.calc_exergy_balance()
        self.condenser.calc_exergy_balance()
        # self.brine_pump.calc_exergy_balance()
        # self.condensate_pump.calc_exergy_balance()
        # self.ncg_sep.calc_exergy_balance()
        # self.ncg_pump.calc_exergy_balance()
        # self.geo_mix.calc_exergy_balance()

        self.Eloss = self.flash_sep.Eloss + self.turbine.Eloss + self.condenser.Eloss

        # self.Eloss = self.flash_sep.Eloss + self.ncg_sep.Eloss \
        #              + self.turbine.Eloss + self.condenser.Eloss \
        #              + self.brine_pump.Eloss + self.condensate_pump.Eloss\
        #              + self.ncg_pump.Eloss + self.geo_mix.Eloss

        # this is to QC the results
        self.energy_balance = self.Q_in - self.Q_out + self.cycle_power  # this should be zero, though not necessarily in the case of direct cycles

        net_cycle_power = self.cycle_power # + self.brine_pump.work + self.condensate_pump.work + self.ncg_pump.work  # need to use the net cycle power for the exergy calculation
        self.exergy_balance = self.Ein - self.Eout - self.Eloss - abs(net_cycle_power)  # this should be zero

        E_reinjected = self.geofluid.m * (self.geofluid_out.properties.H - Tref * self.geofluid_out.properties.S)
        E_rejected = self.coolant.m * (self.coolant_out.properties.H - Tref * self.coolant_out.properties.S)

        self.exergy_losses = [{"equip": "Reinjected", "val": E_reinjected},
                              {"equip": "Rejected", "val": E_rejected},
                              {"equip": "FlashSep", "val": self.flash_sep.Eloss},
                              # {"equip": "NCGSep", "val": self.ncg_sep.Eloss},
                              {"equip": "Turbine", "val": self.turbine.Eloss},
                              {"equip": "Condenser", "val": self.condenser.Eloss},
                              # {"equip": "BrinePump", "val": self.brine_pump.Eloss},
                              # {"equip": "CondensatePump", "val": self.condensate_pump.Eloss},
                              # {"equip": "NCGComp", "val": self.ncg_pump.Eloss},
                              # {"equip": "Mixer", "val": self.geo_mix.Eloss},
                              ]

        self.eta_I_cycle = -self.net_power / self.Q_in
        self.eta_I_recov = self.Q_in / self.Q_in_max
        self.eta_I_plant = self.eta_I_cycle * self.eta_I_recov

        self.eta_II_BF = -self.net_power / self.Ein
        self.eta_II_FUNC = -self.net_power / (self.Ein - self.Eout)

    def __calc_cost(self):

        cost = 0

        cost += self.flash_sep.calc_cost()
        cost += self.turbine.calc_cost()
        cost += self.condenser.calc_cost()
        cost += self.coolingpump.calc_cost()

        cost += self.brine_pump_lP.calc_cost()
        cost += self.brine_pump_hp.calc_cost()
        cost += self.ncg_comp_lp.calc_cost()
        cost += self.ncg_comp_hp.calc_cost()
        cost += self.ncg_pump_hp.calc_cost()

        cost += self.ncg_sep_lp.calc_cost()
        cost += self.absorption.calc_cost()
        cost += self.ncg_sep_hp.calc_cost()
        cost += self.mixer.calc_cost()


        self.primary_equipment_cost = cost * 1e-6
        self.secondary_equipment_cost = 0.4 * cost * 1e-6  # control system, piping, etc.
        # self.construction_cost = 0.7 * (0.4 * cost) * 1e-6  # construction & materials
        self.construction_cost = 0.7 * (self.primary_equipment_cost + self.secondary_equipment_cost)

        self.cost = self.primary_equipment_cost \
                    + self.secondary_equipment_cost \
                    + self.construction_cost \
                    + self.drilling_costs

        self.specific_cost = 1e3 * self.cost / abs(self.net_power_elec * 1e-6)  # $€/kW

        self.costs = [{"equip": "FlashSep", "val": self.flash_sep.cost},
                      {"equip": "Turbine", "val": self.turbine.cost},
                      {"equip": "Condenser", "val": self.condenser.cost},
                      {"equip": "CoolingPump", "val": self.coolingpump.cost},
                      {"equip": "SecondaryEquip", "val": self.secondary_equipment_cost},
                      {"equip": "Construction", "val": self.construction_cost},
                      {"equip": "LP_BrinePump", "val": self.brine_pump_lP.cost},
                      {"equip": "HP_BrinePump", "val": self.brine_pump_hp.cost},
                      {"equip": "LP_NCGComp", "val": self.ncg_comp_lp.cost},
                      {"equip": "HP_NCGComp", "val": self.ncg_comp_hp.cost},
                      {"equip": "HP_NCGPump", "val": self.ncg_pump_hp.cost}
                      ]

    def __calc_NCG_handling(self, brine_out, condensate_out, ncg_out, P_absorb):

        self.brine_pump_lP.set_inputs(brine_out, P_absorb)
        brine_mp = self.brine_pump_lP.calc()

        self.condensate_pump_lP.set_inputs(condensate_out, P_absorb)
        condensate_mp = self.condensate_pump_lP.calc()

        self.ncg_comp_lp.set_inputs(ncg_out, P_absorb, findN=True)
        ncg_mp = self.ncg_comp_lp.calc()

        self.absorption.set_inputs(brine_mp, condensate_mp, ncg_mp)
        gf_mp = self.absorption.calc()

        self.ncg_sep_hp.set_inputs(gf_mp)
        ncg_brine_mp, co2_mp = self.ncg_sep_hp.calc()

        self.brine_pump_hp.set_inputs(ncg_brine_mp, self.geofluid_P_out)
        ncg_brine_hp = self.brine_pump_hp.calc()

        co2_mp.fluid.update_composition([0, 1])
        temp_co2 = co2_mp.copy()
        temp_co2.update("TQ", 300, 1)
        Psat = temp_co2.properties.P

        self.ncg_comp_hp.set_inputs(co2_mp, Psat, findN=True)
        co2_vap_hp = self.ncg_comp_hp.calc()

        temp_co2.update("TQ", 300, 0)
        co2_liq_mp = temp_co2.copy()

        self.ncg_coolant_in = self.coolant_in.copy()
        self.co2_liquefier.set_inputs(MassRatio=-1, Inlet_hot=co2_vap_hp, Inlet_cold=self.ncg_coolant_in, Outlet_hot=co2_liq_mp)
        co2_liq_mp, self.ncg_coolant_out = self.co2_liquefier.calc()

        self.ncg_pump_hp.set_inputs(co2_liq_mp, self.geofluid_P_out)
        co2_liq_hp = self.ncg_pump_hp.calc()

        self.mixer.set_inputs(co2_liq_hp, ncg_brine_hp)
        self.geofluid_out = self.mixer.calc()

    def calc(self, flash, P_min, P_absorb, *args):

        self.Pmin = P_min
        self.Pabsorb = P_absorb

        self.geofluid_in = self.geofluid.copy()
        self.coolant_in = self.coolant.copy()

        # (re)initialise the stream mass rates
        gfluid = self.geofluid.copy()
        gfluid._update_quantity(1.0)
        if self.interpolation:
            gfluid_table = self.geofluid_table.copy()
            gfluid_table._update_quantity(1.0)
        cfluid = self.coolant.copy()
        cfluid._update_quantity(1.0)

        brine_in, vapour_in = self.__calc_flash_sep(flash, gfluid)

        P_turb_out = P_min + self.condenser.deltaP_hot
        self.turbine.set_inputs(vapour_in, P_turb_out)
        vap_turb_out = self.turbine.calc()

        vap_cond_out = self.__calc_condenser(vap_turb_out)

        self.ncg_sep_lp.set_inputs(vap_cond_out)
        condensate, ncg = self.ncg_sep_lp.calc()

        self.__calc_NCG_handling(brine_in, condensate, ncg, P_absorb)

        self.__calc_mass_rates(vapour_in, brine_in, ncg, condensate)

        self.__calc_performance()

        self.__calc_cost()

        self.calc_economics()

        return self.net_power * 1.0

    def plot_TS(self):

        # the geofluid separation
        h_tot = self.geofluid_in.properties.H
        h_liq = self.flash_sep.outlet[0].properties.H
        h_vap = self.flash_sep.outlet[1].properties.H
        x = (h_tot - h_liq) / (h_vap - h_liq)

        s_liq = self.flash_sep.outlet[0].properties.S
        s_vap = self.flash_sep.outlet[1].properties.S
        s_tot = (1 - x) * s_liq + x * s_vap

        s = [self.geofluid_in.properties.S, s_tot]
        T = [self.geofluid_in.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="flash_sep")

        s = [s_tot, s_liq]
        T = [self.flash_sep.inlet.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="brine")

        s = [s_tot, s_vap]
        T = [self.flash_sep.inlet.properties.T, self.flash_sep.outlet[1].properties.T]
        plt.plot(s, T, label="vapour")

        # the brine repressurisation
        s = [self.brine_pump.inlet.properties.S, self.brine_pump.outlet.properties.S]
        T = [self.brine_pump.inlet.properties.T, self.brine_pump.outlet.properties.T]
        plt.plot(s, T, label="brine pump")

        # the vapour expansion
        s = [self.turbine.inlet.properties.S, self.turbine.outlet.properties.S]
        T = [self.turbine.inlet.properties.T, self.turbine.outlet.properties.T]
        plt.plot(s, T, label="turbine")

        s = self.condenser.S_profile[0]
        T = self.condenser.T_profile[0]
        plt.plot(s, T, label="condenser")

        # the ncg separator
        s_cond = self.ncg_sep.outlet[0].properties.S
        s_ncg = self.ncg_sep.outlet[1].properties.S
        s_tot = self.condenser.outlet[0].properties.S

        s = [s_tot, s_cond]
        T = [self.condenser.outlet[0].properties.T, self.ncg_sep.outlet[0].properties.T]
        plt.plot(s, T, label="condensate")

        s = [s_tot, s_ncg]
        T = [self.condenser.outlet[0].properties.T, self.ncg_sep.outlet[1].properties.T]
        plt.plot(s, T, label="ncg")

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Specific Entropy, J/kg/K")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power / 1000))

        plt.show()

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

if __name__ == "__main__":

    from FluidProperties.fluid import Fluid
    from Simulator.streams import MaterialStream
    from time import perf_counter

    Cycle = DirectCycle()
    Cycle.condenser.deltaP_cold = 120
    Cycle.coolingpump.eta_isentropic = 0.6

    Tin = 200 + 273.15
    Qin = 0.15
    Min = 50

    interp = False

    water = Fluid(["water", 1])
    water.update("TQ", Tin, Qin)

    hot_fluid = Fluid(["water", 0.95, "carbondioxide", 0.05], engine="geoprop")

    def q_wat(P):
        hot_fluid.update("PT", P, Tin)
        zH2O = hot_fluid.composition[0]
        yH2O = hot_fluid.properties.VapProps.composition[0]
        X = hot_fluid.properties.Q

        Q_wat = X * yH2O / zH2O

        return Q_wat

    def q_search(P):

        error = q_wat(P) - Qin

        return error

    P_min = water.properties.P
    P_max = P_min * (1 + hot_fluid.composition[1])
    iter = 0

    while q_wat(P_max) > Qin and iter < 10:
        P_min = P_max * 1.0
        P_max *= (1 + hot_fluid.composition[1])

        iter += 1

    res = root_scalar(q_search, method="brentq", bracket=[P_min, P_max], rtol=1e-4)
    hot_fluid.update("PT", res.root, Tin)

    m = Min * water.properties.H / hot_fluid.properties.H

    print(m/Min)

    hot_fluid_stream = MaterialStream(hot_fluid, m=m)
    hot_fluid_stream.update("PT", res.root, Tin)

    if interp:
        hot_fluid_tab = Fluid(["water", 0.95, "carbondioxide", 0.5], engine="tables", filename="../../propertyengine_plugins/LookUpTables/SuperDuperTable")
        hot_fluid_tab_stream = MaterialStream(hot_fluid_tab, m=m)

        Cycle.set_geofluid(hot_fluid_stream, interpolation=hot_fluid_tab_stream)
    else:
        Cycle.set_geofluid(hot_fluid_stream)


    Cycle.set_geofluid(hot_fluid_stream)

    cold_fluid = Fluid(["air", 1])
    cold_fluid_stream = MaterialStream(cold_fluid, m=1)
    Cycle.set_coolant(cold_fluid_stream)

    flash1 = 0.66
    Pcond = 0.6e5


    START=perf_counter()
    Cycle.calc(flash1, Pcond, 30e5)
    END = perf_counter()

    print(END - START)

    print()


