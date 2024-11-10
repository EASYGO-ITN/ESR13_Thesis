import numpy as np

from FluidProperties import engines
from FluidProperties.fluid import Fluid
from FluidProperties import Pref, Tref


class TESTS:

    def __init__(self):

        self.test_counter = 0
        self.fail_counter = 0
        self.pass_counter = 0


        print(engines)
        print()

        pure = TESTING_PURE_FLUIDS()
        self.test_counter += pure.test_counter
        self.fail_counter += pure.fail_counter
        self.pass_counter += pure.pass_counter

        mixtures = TESTING_MIXTURE_FLUIDS()
        self.test_counter += mixtures.test_counter
        self.fail_counter += mixtures.fail_counter
        self.pass_counter += mixtures.pass_counter

        print("\nTest Summary ALL:\n - Tests: {}\n - Pass: {}\n - Fail: {}".format(self.test_counter, self.pass_counter,
                                                                               self.fail_counter))

class TESTING_PURE_FLUIDS:

    def __init__(self):

        self.test_counter = 0
        self.fail_counter = 0
        self.pass_counter = 0

        self.test_fluids = []

        print("\n##### PURE FLUID CREATION - WATER #####\n")
        self.test_fluid_pure_creation("")
        self.test_fluid_pure_creation("coolprop")
        self.test_fluid_pure_creation("geoprop")
        self.test_fluid_pure_creation("error", fail_is_pass=True)

        print("\n##### PT CALCULATION #####\n")
        for fluid in self.test_fluids:
            self.test_PT_calculation(fluid, Pref, Tref)

        print("\n##### PT RESULTS COMPARISON #####\n")
        self.test_results_comparison("P")
        self.test_results_comparison("T")
        self.test_results_comparison("H")
        self.test_results_comparison("S")
        self.test_results_comparison("D")
        self.test_results_comparison("V")
        self.test_results_comparison("Q")

        print("\n##### PH CALCULATION #####\n")
        pres = 101325
        h = 1500000

        for fluid in self.test_fluids:
            self.test_PVT_calculation(fluid, "PH", pres, h)

        print("\n##### PH RESULTS COMPARISON #####\n")
        self.test_results_comparison("P")
        self.test_results_comparison("T")
        self.test_results_comparison("H")
        self.test_results_comparison("S")
        self.test_results_comparison("D")
        self.test_results_comparison("V")

        print("\n##### PURE FLUID CREATION - CARBONDIOXIDE #####\n")
        self.reset_test_fluids()

        self.test_fluid_pure_creation("", species="carbondioxide")
        self.test_fluid_pure_creation("coolprop", species="carbondioxide")
        self.test_fluid_pure_creation("geoprop", species="carbondioxide")
        self.test_fluid_pure_creation("error", species="carbondioxide", fail_is_pass=True)

        print("\n##### PT CALCULATION #####\n")
        for fluid in self.test_fluids:
            self.test_PT_calculation(fluid, Pref, Tref)

        print("\n##### PT RESULTS COMPARISON #####\n")
        self.test_results_comparison("H")
        self.test_results_comparison("S")
        self.test_results_comparison("D")
        self.test_results_comparison("V")
        self.test_results_comparison("Q")

        print("\nTest Summary PURE FLUIDS:\n - Tests: {}\n - Pass: {}\n - Fail: {}".format(self.test_counter, self.pass_counter,
                                                                               self.fail_counter))


    def reset_test_fluids(self):
        self.test_fluids = []

    def test_fluid_pure_creation(self, engine, species="water", fail_is_pass=False):
        self.test_counter += 1

        try:
            if engine:
                fluid = Fluid([species, 1], engine=engine)
            else:
                fluid = Fluid([species, 1])

            self.test_fluids.append(fluid)

            if fail_is_pass:
                self.fail_counter += 1
                print("FAILED - fluid with erroreous engine was created")
            else:
                self.pass_counter += 1
                print("PASS - fluid with \"{}\" engine was created".format(engine))
        except:

            if fail_is_pass:
                self.pass_counter += 1
                print("PASS - fluid with erroreous engine was NOT created")
            else:
                self.fail_counter += 1
                print("FAILED - fluid with \"{}\" engine was NOT created".format(engine))
            pass

    def test_PT_calculation(self, fluid, P, T):
        self.test_counter += 1

        try:
            fluid.update("PT", P, T)

            self.pass_counter += 1
            print("PASS - PT calculation with \"{}\" engine with components {} and composition {} for P: {:.2e} Pa and T: {:.2f} K".format(fluid.engine, fluid.components, fluid.composition, P, T))
        except:
            self.fail_counter += 1
            print("FAILED - PT calculation with \"{}\" engine with components {} and composition {} for P: {:.2e} Pa and T: {:.2f} K failed unexpectedly".format(fluid.engine, fluid.components, fluid.composition, P, T))

    def test_results_comparison(self, prop, tol=0.001):

        self.test_counter += 1

        n_fluid = len(self.test_fluids)

        arr = np.array([fluid.properties[prop] for fluid in self.test_fluids])
        mat = np.zeros((n_fluid, n_fluid))

        for i, x in enumerate(arr):
            for j, y in enumerate(arr):
                mat[i, j] = abs((x - y) / (x + 1e-20))

        if mat.max() < tol:
            self.pass_counter += 1
            print("PASS - PT calculated \"{}\" are consistent".format(prop))
        else:
            self.fail_counter += 1
            print("FAILED - PT calculated \"{}\" are inconsistent".format(prop))

        print("\tFluids:", self.test_fluids, "\n")
        with np.printoptions(precision=3, suppress=True):
            print("\tProperties:", arr, "\n")
            print("\tDiffMap:\n", mat, "\n")

    def test_PVT_calculation(self, fluid, InputSpec, Input1, Input2):
        self.test_counter += 1

        try:
            fluid.update(InputSpec, Input1, Input2)

            self.pass_counter += 1
            print("PASS - {} calculation with \"{}\" engine with components {} and composition {} for {}: {:.2e} and {}: {:.2e}".format(InputSpec, fluid.engine, fluid.components, fluid.composition, InputSpec[0], Input1, InputSpec[1], Input2))
        except:
            self.fail_counter += 1
            print("FAILED - {} calculation with \"{}\" engine with components {} and composition {} for {}: {:.2e} and {}: {:.2e} failed unexpectedly".format(InputSpec, fluid.engine, fluid.components, fluid.composition, InputSpec[0], Input1, InputSpec[1], Input2))



class TESTING_MIXTURE_FLUIDS:

    def __init__(self):

        self.test_counter = 0
        self.fail_counter = 0
        self.pass_counter = 0

        self.test_fluids = []

        self.run_all()

    def run_all(self):

        print("\n##### FLUID CREATION #####\n")
        self.test_fluid_creation("")
        self.test_fluid_creation("coolprop")
        self.test_fluid_creation("geoprop")
        self.test_fluid_creation("error", fail_is_pass=True)

        print("\n##### PT CALCULATION #####\n")
        for fluid in self.test_fluids:
            self.test_PT_calculation(fluid, Pref, Tref)

        print("\n##### PT RESULTS COMPARISON #####\n")
        self.test_results_comparison("P")
        self.test_results_comparison("T")
        self.test_results_comparison("H")
        self.test_results_comparison("S")
        self.test_results_comparison("D")
        self.test_results_comparison("V")
        self.test_results_comparison("Q")

        #
        # print("\n##### PH CALCULATION #####\n")
        # pres = 101325
        # h = 1500000
        #
        # for fluid in self.test_fluids:
        #     self.test_PVT_calculation(fluid, "PH", pres, h)
        #
        # print("\n##### PH RESULTS COMPARISON #####\n")
        # self.test_results_comparison("P")
        # self.test_results_comparison("T")
        # self.test_results_comparison("H")
        # self.test_results_comparison("S")
        # self.test_results_comparison("D")
        # self.test_results_comparison("V")

        print("\nTest Summary MIXTURE FLUIDS:\n - Tests: {}\n - Pass: {}\n - Fail: {}".format(self.test_counter, self.pass_counter,
                                                                               self.fail_counter))

    def test_fluid_creation(self, engine, fail_is_pass=False):
        self.test_counter += 1

        try:
            if engine:
                fluid = Fluid(["water", 0.0098, "carbondioxide", 0.002], engine=engine)
            else:
                fluid = Fluid(["water", 0.0098, "carbondioxide", 0.002])

            self.test_fluids.append(fluid)

            if fail_is_pass:
                self.fail_counter += 1
                print("FAILED - fluid with erroreous engine was created")
            else:
                self.pass_counter += 1
                print("PASS - fluid with \"{}\" engine was created".format(engine))
        except:

            if fail_is_pass:
                self.pass_counter += 1
                print("PASS - fluid with erroreous engine was NOT created")
            else:
                self.fail_counter += 1
                print("FAILED - fluid with \"{}\" engine was NOT created".format(engine))
            pass

    def test_PT_calculation(self, fluid, P, T):
        self.test_counter += 1

        try:
            fluid.update("PT", P, T)

            self.pass_counter += 1
            print(
                "PASS - PT calculation with \"{}\" engine with components {} and composition {} for P: {:.2e} Pa and T: {:.2f} K".format(
                    fluid.engine, fluid.components, fluid.composition, P, T))
        except:
            self.fail_counter += 1
            print(
                "FAILED - PT calculation with \"{}\" engine with components {} and composition {} for P: {:.2e} Pa and T: {:.2f} K failed unexpectedly".format(
                    fluid.engine, fluid.components, fluid.composition, P, T))

    def test_results_comparison(self, prop, tol=0.001):

        self.test_counter += 1

        n_fluid = len(self.test_fluids)

        arr = np.array([fluid.properties[prop] for fluid in self.test_fluids])
        mat = np.zeros((n_fluid, n_fluid))

        for i, x in enumerate(arr):
            for j, y in enumerate(arr):
                mat[i, j] = abs((x - y) / (x + 1e-20))

        if mat.max() < tol:
            self.pass_counter += 1
            print("PASS - PT calculated \"{}\" are consistent".format(prop))
        else:
            self.fail_counter += 1
            print("FAILED - PT calculated \"{}\" are inconsistent".format(prop))

        print(self.test_fluids, "\n")
        with np.printoptions(precision=3, suppress=True):
            print(arr, "\n")
            print(mat, "\n")


if __name__ == "__main__":
    TESTS()
