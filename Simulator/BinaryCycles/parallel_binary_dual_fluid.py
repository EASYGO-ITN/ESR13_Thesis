from ..cycle import BinaryCycle
import Simulator
import matplotlib.pyplot as plt
from Simulator.BinaryCycles.simple_binary import ORC as SimpleORC


"""

                *-------*
                |       |
      *----> Evap ----> PreH ---->         *----- Cond <----*       
      |      |             |               |                |
      |      |             *----------- Recu <---- Pump ----*
      |      |                          |
      |      *----> HTurb --------------* 
----> Sep
      |      *----> LTurb --------------*
      |      |                          |
      |      |          *-------------- Recu <---- Pump <----*
      |      |          |                  |                 |
      *----> Evap ----> PreH ---->         *----> Cond ------*
                |       |
                *-------*

"""


class ORC(BinaryCycle):

    def __init__(self, recu=True):

        super().__init__()

        self.recuperated = recu

        self.separator = Simulator.separator()

        self.brine_ORC = SimpleORC()
        self.brine_ORC.evaporator.deltaT_pinch = self.deltaT_pinch_liq
        self.vapour_ORC = SimpleORC()

        self.geo_mixer = Simulator.mixer()
        self.cond_mixer = Simulator.mixer()

        self.wfluidV = None
        self.wfluidB = None

        self.coolantV = None
        self.coolantB = None

    def set_workingfluid(self, streamB, streamV):
        self.wfluidV = streamV
        self.wfluidB = streamB

    def set_coolant(self, stream):
        self.coolant = stream.copy()
        self.coolant.update("PT", self.P_ambient, self.T_ambient)

        self.coolantB = self.coolant.copy()
        self.coolantV = self.coolant.copy()

    def _init_streams(self):
        # (re)initialise the stream mass rates
        self.wfluidV._update_quantity(1.0)
        self.wfluidB._update_quantity(1.0)

        self.geofluid._update_quantity(1.0)

        self.coolantV._update_quantity(1.0)
        self.coolantB._update_quantity(1.0)

        if self.interpolation:
            self.geofluid_table._update_quantity(1.0)

    def calc(self, BP_max, BT_max, BT_min, VP_max, VT_max, VT_min, BP_min=None, VP_min=None):

        self.geofluid_in = self.geofluid.copy()
        self.coolant_in = self.coolant.copy()

        self._init_streams()

        # separate the geofluid liquid and vapour phases
        self.separator.set_inputs(self.geofluid)
        brine, vapour = self.separator.calc()

        self.brine_ORC.set_geofluid(brine.copy())
        self.brine_ORC.set_workingfluid(self.wfluidB)
        self.brine_ORC.set_coolant(self.coolantB)
        self.brine_ORC.calc(BP_max, BT_max, BT_min, P_min=BP_min)

        # self.brine_ORC.net_power *= brine.m

        self.vapour_ORC.set_geofluid(vapour.copy())
        self.vapour_ORC.set_workingfluid(self.wfluidV)
        self.vapour_ORC.set_coolant(self.coolantV)
        self.vapour_ORC.calc(VP_max, VT_max, VT_min, P_min=VP_min)

        # self.vapour_ORC.net_power *= vapour.m

        self.geo_mixer.set_inputs(self.brine_ORC.geofluid_out.copy(), self.vapour_ORC.geofluid_out.copy())
        self.geofluid_out = self.geo_mixer.calc()

        self.cond_mixer.set_inputs(self.brine_ORC.coolant_out.copy(), self.vapour_ORC.coolant_out.copy())
        self.coolant_out = self.cond_mixer.calc()

        # calculate the stream mass rates
        self.brine = self.brine_ORC.geofluid_out
        self.vapour = self.vapour_ORC.geofluid_out

        self.wfluidB._update_quantity(brine.m * self.brine_ORC.preheater.MassRatio)
        self.wfluidV._update_quantity(vapour.m * self.vapour_ORC.preheater.MassRatio)
        self.coolant._update_quantity(self.coolant_out.m)
        self.coolant_in._update_quantity(self.coolant_out.m)

        self.cycle_power = self.brine_ORC.net_power + self.vapour_ORC.net_power
        self.parasitic_power = 0
        self.net_power = self.cycle_power

        self.calc_energy_balance()

        return self.net_power * 1.0

    def plot_TQ(self):

        wf_style_B = {"color": "green", "label": "BB working fluid"}
        wf_style_V = {"color": "black", "label": "VB working fluid"}
        geo_style = {"color": "red", "label": "geofluid"}
        cool_style = {"color": "blue", "label": "coolant"}
        recu_style_B = {"linestyle": "--", "color": "black"}
        recu_style_V = {"linestyle": "--", "color": "green"}


        # BRINE ORC
        offset = 0.0

        duty = self.brine_ORC.condenser.Duty_profile[1] * self.brine_ORC.wfluid.m
        T_hot = self.brine_ORC.condenser.T_profile[0]
        T_cold = self.brine_ORC.condenser.T_profile[1]

        plt.plot(duty, T_hot, **wf_style_B)
        plt.plot(duty, T_cold, **cool_style)

        offset += duty[-1]

        if self.recuperated:
            duty = self.brine_ORC.recuperator.Duty_profile[1] * self.brine_ORC.wfluid.m
            T_hot = self.brine_ORC.recuperator.T_profile[0]
            T_cold = self.brine_ORC.recuperator.T_profile[1]
            recu_offset = duty[-1]

            plt.plot(duty, T_cold, **wf_style_B)
            plt.plot(duty + offset, T_hot, **wf_style_B)

            duty_cold = [self.brine_ORC.recuperator.Duty_profile[1][0], offset]
            T_cold = [self.brine_ORC.recuperator.T_profile[1][0], self.brine_ORC.recuperator.T_profile[0][0]]
            plt.plot(duty_cold, T_cold, **recu_style_B)

            duty_hot = [recu_offset, recu_offset + offset]
            T_hot = [self.brine_ORC.recuperator.T_profile[1][-1], self.brine_ORC.recuperator.T_profile[0][-1]]
            plt.plot(duty_hot, T_hot, **recu_style_B)

        offset = 0.0
        if self.recuperated:
            offset += duty[-1]

        duty = self.brine_ORC.preheater.Duty_profile[1] * self.brine_ORC.geofluid_out.m
        T_hot = self.brine_ORC.preheater.T_profile[0]
        T_cold = self.brine_ORC.preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style_B)

        offset += duty[-1]

        duty = self.brine_ORC.evaporator.Duty_profile[1] * self.brine_ORC.geofluid_out.m
        T_hot = self.brine_ORC.evaporator.T_profile[0]
        T_cold = self.brine_ORC.evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style_B)

        # VAPOUR ORC
        vap_offset = duty[-1] + offset
        offset = vap_offset * 1.0

        duty = self.vapour_ORC.condenser.Duty_profile[1] * self.vapour_ORC.wfluid.m
        T_hot = self.vapour_ORC.condenser.T_profile[0]
        T_cold = self.vapour_ORC.condenser.T_profile[1]

        plt.plot(duty + offset, T_hot, **wf_style_V)
        plt.plot(duty + offset, T_cold, **cool_style)

        offset += duty[-1]

        if self.recuperated:
            duty = self.vapour_ORC.recuperator.Duty_profile[1] * self.vapour_ORC.wfluid.m
            T_hot = self.vapour_ORC.recuperator.T_profile[0]
            T_cold = self.vapour_ORC.recuperator.T_profile[1]
            recu_offset = duty[-1]

            plt.plot(duty + vap_offset, T_cold, **wf_style_V)
            plt.plot(duty + offset, T_hot, **wf_style_V)

            duty_cold = [self.vapour_ORC.recuperator.Duty_profile[1][0] + vap_offset, offset]
            T_cold = [self.vapour_ORC.recuperator.T_profile[1][0], self.vapour_ORC.recuperator.T_profile[0][0]]
            plt.plot(duty_cold, T_cold, **recu_style_V)

            duty_hot = [recu_offset + vap_offset, recu_offset + offset]
            T_hot = [self.vapour_ORC.recuperator.T_profile[1][-1], self.vapour_ORC.recuperator.T_profile[0][-1]]
            plt.plot(duty_hot, T_hot, **recu_style_V)

        offset = vap_offset * 1.0
        if self.recuperated:
            offset += duty[-1]

        duty = self.vapour_ORC.preheater.Duty_profile[1] * self.vapour_ORC.geofluid_out.m
        T_hot = self.vapour_ORC.preheater.T_profile[0]
        T_cold = self.vapour_ORC.preheater.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style_V)

        offset += duty[-1]

        duty = self.vapour_ORC.evaporator.Duty_profile[1] * self.vapour_ORC.geofluid_out.m
        T_hot = self.vapour_ORC.evaporator.T_profile[0]
        T_cold = self.vapour_ORC.evaporator.T_profile[1]

        plt.plot(duty + offset, T_hot, **geo_style)
        plt.plot(duty + offset, T_cold, **wf_style_V)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Heat Transferred, J/(kg/s)")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power / 1000))

        plt.show()

    def plot_TS(self):

        wf_style_B = {"color": "green", "label": "Brine cycle WF"}
        env_style_B = {"color": "black", "linewidth": 0.5}

        wf_style_V = {"color": "blue", "label": "Vapour cycle WF"}
        env_style_V = {"color": "red", "linewidth": 0.5}

        # BRINE ORC
        s = [self.brine_ORC.feedpump.inlet.properties.S, self.brine_ORC.feedpump.outlet.properties.S]
        T = [self.brine_ORC.feedpump.inlet.properties.T, self.brine_ORC.feedpump.outlet.properties.T]
        plt.plot(s, T, **wf_style_B)

        if self.recuperated:
            s = self.brine_ORC.recuperator.S_profile[1]
            T = self.brine_ORC.recuperator.T_profile[1]
            plt.plot(s, T, **wf_style_B)

        s = self.brine_ORC.preheater.S_profile[1]
        T = self.brine_ORC.preheater.T_profile[1]
        plt.plot(s, T, **wf_style_B)

        s = self.brine_ORC.evaporator.S_profile[1]
        T = self.brine_ORC.evaporator.T_profile[1]
        plt.plot(s, T, **wf_style_B)

        s = [self.brine_ORC.turbine.inlet.properties.S, self.brine_ORC.turbine.outlet.properties.S]
        T = [self.brine_ORC.turbine.inlet.properties.T, self.brine_ORC.turbine.outlet.properties.T]
        plt.plot(s, T, **wf_style_B)

        if self.recuperated:
            s = self.brine_ORC.recuperator.S_profile[0]
            T = self.brine_ORC.recuperator.T_profile[0]
            plt.plot(s, T, **wf_style_B)

        s = self.brine_ORC.condenser.S_profile[0]
        T = self.brine_ORC.condenser.T_profile[0]
        plt.plot(s, T, **wf_style_B)

        ss, ts = self._calc_TS_envelope(fluid=self.wfluidB)
        plt.plot(ss, ts, **env_style_B)

        # Vapour ORC
        s = [self.vapour_ORC.feedpump.inlet.properties.S, self.vapour_ORC.feedpump.outlet.properties.S]
        T = [self.vapour_ORC.feedpump.inlet.properties.T, self.vapour_ORC.feedpump.outlet.properties.T]
        plt.plot(s, T, **wf_style_V)

        if self.recuperated:
            s = self.vapour_ORC.recuperator.S_profile[1]
            T = self.vapour_ORC.recuperator.T_profile[1]
            plt.plot(s, T, **wf_style_V)

        s = self.vapour_ORC.preheater.S_profile[1]
        T = self.vapour_ORC.preheater.T_profile[1]
        plt.plot(s, T, **wf_style_V)

        s = self.vapour_ORC.evaporator.S_profile[1]
        T = self.vapour_ORC.evaporator.T_profile[1]
        plt.plot(s, T, **wf_style_V)

        s = [self.vapour_ORC.turbine.inlet.properties.S, self.vapour_ORC.turbine.outlet.properties.S]
        T = [self.vapour_ORC.turbine.inlet.properties.T, self.vapour_ORC.turbine.outlet.properties.T]
        plt.plot(s, T, **wf_style_V)

        if self.recuperated:
            s = self.vapour_ORC.recuperator.S_profile[0]
            T = self.vapour_ORC.recuperator.T_profile[0]
            plt.plot(s, T, **wf_style_V)

        s = self.vapour_ORC.condenser.S_profile[0]
        T = self.vapour_ORC.condenser.T_profile[0]
        plt.plot(s, T, **wf_style_V)

        ss, ts = self._calc_TS_envelope(fluid=self.wfluidV)
        plt.plot(ss, ts, **env_style_V)

        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc=0)

        plt.xlabel("Specific Entropy, J/kg/K")
        plt.ylabel("Temperature, K")

        plt.title("NetPower: {:.2f} kW/(kg/s)".format(-self.net_power/1000))

        plt.show()