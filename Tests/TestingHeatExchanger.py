from FluidProperties.fluid import Fluid
import Simulator
from Simulator.streams import MaterialStream


class TESTS:


    def __init__(self, plot=True):

        self.test_counter = 0
        self.fail_counter = 0
        self.pass_counter = 0

        tests = [TESTING_HX_calcs]

        for test in tests:
            t = test(plot=plot)
            t.run_all()

            self.test_counter += t.test_counter
            self.pass_counter += t.pass_counter
            self.fail_counter += t.fail_counter

        print("\nTest Summary ALL:\n - Tests: {}\n - Pass: {}\n - Fail: {}".format(self.test_counter, self.pass_counter, self.fail_counter))

class TESTING_HX_calcs:

    def __init__(self, plot=True):

        self.tolerance = 0.001

        hot = Fluid(["water", 1])
        hot_stream = MaterialStream(hot, 1.0)

        self.hot_stream_in = hot_stream.copy()
        self.hot_stream_in.update("PT", 2e6, 400)

        self.hot_stream_out = hot_stream.copy()
        self.hot_stream_out.update("PT", 2e6 - 1e4, 305)

        cold = Fluid(["water", 1])
        cold_stream = MaterialStream(cold, 3.0)

        self.cold_stream_in = cold_stream.copy()
        self.cold_stream_in.update("PT", 1e6, 300)

        self.cold_stream_out = cold_stream.copy()
        self.cold_stream_out.update("PT", 9e5 - 1e4, 331.8)

        self.heat_exchanger = Simulator.heat_exchanger()

        self.MassRatio = 3.0

        self.tests = [self.calc_R,
                      self.calc_Tih,
                      self.calc_Toh,
                      self.calc_Tic,
                      self.calc_Toc,
                      self.calc_Toh_Toc,
                      self.calc_Toh_Tic,
                      ]

        self.ignore = [self.calc_Tih_Tic,
                       self.calc_Tih_Toc
                       ]

        self.test_counter = 0
        self.fail_counter = 0
        self.pass_counter = 0

        self.plot = plot

    def run_all(self):

        print("\n\tTest for HX Calcs")

        T_in_H = self.hot_stream_in.properties.T
        T_out_H = self.hot_stream_out.properties.T
        T_in_C = self.cold_stream_in.properties.T
        T_out_C = self.cold_stream_out.properties.T

        for test in self.tests:
            self.test_counter += 1
            try:
                test()
                fail_flag = False
                if abs(T_in_H - self.heat_exchanger.inlet_T[0])/T_in_H > self.tolerance:
                    fail_flag = True
                    print("\t\tTest {}: Inconsistent Hot Inlet Temperature calculated".format(self.test_counter))
                if abs(T_out_H - self.heat_exchanger.outlet_T[0])/T_out_H > self.tolerance:
                    fail_flag = True
                    print("\t\tTest {}: Inconsistent Hot Outlet Temperature calculated".format(self.test_counter))

                if abs(T_in_C - self.heat_exchanger.inlet_T[1]) / T_in_C > self.tolerance:
                    fail_flag = True
                    print("\t\tTest {}: Inconsistent Cold Inlet Temperature calculated".format(self.test_counter))
                if abs(T_out_C - self.heat_exchanger.outlet_T[1]) / T_out_C > self.tolerance:
                    fail_flag = True
                    print("\t\tTest {}: Inconsistent Cold Outlet Temperature calculated".format(self.test_counter))

                if fail_flag:
                    self.fail_counter += 1
                else:
                    self.pass_counter += 1

            except:
                self.fail_counter += 1

        print("\n\tTest Summary HX Calcs:\n - Tests: {}\n - Pass: {}\n - Fail: {}".format(self.test_counter, self.pass_counter, self.fail_counter))

    def calc_R(self):

        self.heat_exchanger.set_inputs(MassRatio=-1,
                                       Inlet_hot=self.hot_stream_in.copy(),
                                       Outlet_hot=self.hot_stream_out.copy(),
                                       Inlet_cold=self.cold_stream_in.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())

        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Tih(self):

        self.heat_exchanger.set_inputs(MassRatio=self.MassRatio,
                                       Outlet_hot=self.hot_stream_out.copy(),
                                       Inlet_cold=self.cold_stream_in.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())

        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Toh(self):

        self.heat_exchanger.set_inputs(MassRatio=self.MassRatio,
                                       Inlet_hot=self.hot_stream_in.copy(),
                                       Inlet_cold=self.cold_stream_in.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())

        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Tic(self):

        self.heat_exchanger.set_inputs(MassRatio=self.MassRatio,
                                       Inlet_hot=self.hot_stream_in.copy(),
                                       Outlet_hot=self.hot_stream_out.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())

        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Toc(self):

        self.heat_exchanger.set_inputs(MassRatio=self.MassRatio,
                                       Inlet_hot=self.hot_stream_in.copy(),
                                       Outlet_hot=self.hot_stream_out.copy(),
                                       Inlet_cold=self.cold_stream_in.copy())

        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Toh_Toc(self):

        self.heat_exchanger.set_inputs(Inlet_hot=self.hot_stream_in.copy(),
                                       Inlet_cold=self.cold_stream_in.copy())
        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Toh_Tic(self):

        self.heat_exchanger.set_inputs(Inlet_hot=self.hot_stream_in.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())
        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Tih_Tic(self):

        self.heat_exchanger.set_inputs(Outlet_hot=self.hot_stream_out.copy(),
                                       Outlet_cold=self.cold_stream_out.copy())
        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()

    def calc_Tih_Toc(self):

        self.heat_exchanger.set_inputs(Outlet_hot=self.hot_stream_out.copy(),
                                       Inlet_cold=self.cold_stream_in.copy())
        self.heat_exchanger.calc()

        if self.plot:
            self.heat_exchanger.plot()


TESTS(plot=False)

# test = TESTING_HX_calcs()
# test.calc_Toh_Toc()
