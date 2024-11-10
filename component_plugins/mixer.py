from typing import NoReturn

from .base_component import Component
from Simulator import factory
from Simulator.streams import MaterialStream, HeatStream, WorkStream
from FluidProperties.fluid import Fluid
from FluidProperties import Tref


class mixer(Component):
    """
    The mixer component

    Attributes
    ----------
    inlet: list[MaterialStream | HeatStream | WorkStream]
        the inlet streams
    outlet: MaterialStream | HeatStream | WorkStream
        the outlet stream

    stream_type: MaterialStream | HeatStream | WorkStream
    """

    def __init__(self):
        """
        Instantiates the Mixer
        """

        super().__init__()

    def set_inputs(self, *args: tuple[MaterialStream] | tuple[HeatStream] | tuple[WorkStream]) -> NoReturn:
        """
        set the inputs for the mixer calculations

        Parameters
        ----------
        *args: tuple[MaterialStream] | tuple[HeatStream] | tuple[WorkStream]
            the streams to be mixed

        Returns
        -------
        NoReturn

        Raises
        ------
        ValueError
            the inlet streams are not of the same type
        """

        self.inlet = [i.copy() for i in args]
        self.stream_type = type(args[0])

        for stream in self.inlet:
            if type(stream) != self.stream_type:
                msg = "\nOnly like streams can be mixed. Stream type {} and {} cannot be mixed".format(self.stream_type, type(stream))
                raise ValueError(msg)

    def calc(self) -> MaterialStream | HeatStream | WorkStream:

        """
        mix the inlet streams

        Returns
        -------
        MaterialStream | HeatStream | WorkStream
        """

        if self.stream_type == MaterialStream:

            return self.__mix_material_stream()

        elif self.stream_type == MaterialStream:

            return self.__mix_heat_stream()

        elif self.stream_type == WorkStream:

            return self.__mix_work_stream()

    def __mix_material_stream(self) -> MaterialStream:
        """
        Helper function to mix two or more MaterialStreams

        Returns
        -------
        MaterialStream

        Raises
        ------
        ValueError
            streams do not use the same fluid engine
        """

        m_tot = 0.0
        P_min = 1e15
        H_tot = 0.0
        engine = self.inlet[0].fluid.engine

        moles = [stream.m/stream.properties.Mr for stream in self.inlet]

        comps_compo = {}

        for i, stream in enumerate(self.inlet):

            if stream.fluid.engine != engine:

                if stream.fluid.engine in ["default", "coolprop"] and engine in ["default", "coolprop"]:
                    pass
                else:
                    msg = "Only like streams can be mixed. Engine type {} and {} cannot be mixed".format(engine, stream.fluid.engine)
                    raise ValueError(msg)

            m_tot += stream.m + 1e-6
            H_tot += stream.m * stream.properties.H

            if stream.properties.P < P_min:
                P_min = stream.properties.P * 1.0

            for j, comp in enumerate(stream.fluid.components):
                if comp in comps_compo:
                    comps_compo[comp] += stream.fluid.composition[j] * moles[i]
                else:
                    comps_compo[comp] = stream.fluid.composition[j] * moles[i]

        components = []
        for comp in comps_compo:
            components.append(comp)
            components.append(comps_compo[comp])

        temp_fluid = Fluid(components, engine=engine)
        temp_stream = MaterialStream(temp_fluid, m=m_tot)
        H = H_tot / m_tot

        temp_stream.update("PH", P_min, H)

        self.outlet = temp_stream.copy()

        return temp_stream

    def __mix_heat_stream(self) -> HeatStream:
        """
        Helper function to mix two or more HeatStreams

        Returns
        -------
        HeatStream
        """

        Q_tot = 0.0
        for i, stream in enumerate(self.inlet):
            Q_tot += stream.Q

        return HeatStream(Q_tot)

    def __mix_work_stream(self) -> WorkStream:
        """
        Helper function to mix two or more WorkStreams

        Returns
        -------
        WorkStream
        """

        W_tot = 0.0
        for i, stream in enumerate(self.inlet):
            W_tot += stream.W

        return WorkStream(W_tot)

    def calc_exergy_balance(self):

        self.Ein = 0
        for i, stream in enumerate(self.inlet):
            self.Ein += stream.m * (stream.properties.H - Tref * stream.properties.S)

        self.Eout = self.outlet.m * (self.outlet.properties.H - Tref * self.outlet.properties.S)

        self.Eloss = self.Ein - self.Eout

        # print(self.Ein, self.Eout, self.Eloss)

    def update_inlet_rate(self, ms):

        for i, m in enumerate(ms):
            self.inlet[i]._update_quantity(m)

        self.outlet._update_quantity(sum(ms))

    def calc_cost(self):

        cost = 0

        self.cost = cost * 1.0

        return cost


def register() -> NoReturn:
    """
    Registers the mixer component

    Returns
    -------
    NoReturn
    """

    factory.register("mixer", mixer)