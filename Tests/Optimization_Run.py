# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 14:24:25 2023

@author: lgalieti
"""

from ORCptimization import ORCptimization_manager as Optimizer
# from Tests.OptimizationTests.test1.input_function import Objective_Function
import time
import numpy as np

if __name__ == "__main__":

    input_file_path = [
        # "../Tests/OptimizationTests/TechnoEconomicComparison/00_SimpleORC_vs_SteamQuality_Thermodynamic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/00_SimpleORC_vs_SteamQuality_Thermodynamic_CO2",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/00B_SimpleORC_vs_SteamQuality_Thermodynamic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/01_SimpleORC_vs_SteamQuality_Economic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/10_SingleFlash_vs_SteamQuality_Thermodynamic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/10_SingleFlash_vs_SteamQuality_Thermodynamic_CO2",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/11_SingleFlash_vs_SteamQuality_Economic"
        # "../Tests/OptimizationTests/TechnoEconomicComparison/02_SimpleORC_vs_CO2_Thermodynamic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/20_SingleFlash_vs_CO2_Reinj_Thermodynamic",
        # "../Tests/OptimizationTests/TechnoEconomicComparison/21_SingleFlash_vs_CO2_Venting_Thermodynamic"
        "../Tests/OptimizationTests/TechnoEconomicComparison/22_SingleFlash_vs_CO2_Nothing_Thermodynamic"

    ]

    Restart = True
    Parallel = True
    N_cores = 6
    start_time = time.time_ns()
    Optimizer.OptimizationManager(input_file_path, Parallel, Restart, N_cores, logging=True)
    run_time = time.time_ns() - start_time
    print('run time:', "{:.3f}".format(run_time*10**-9),'s')

