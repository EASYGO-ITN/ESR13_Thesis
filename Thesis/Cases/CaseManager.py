# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 14:24:25 2023

@author: lgalieti
"""

import sys

# sys.path.append(r'C:/Users/Moana/Documents/GitHub/PowerCycle')

from ORCptimization import ORCptimization_manager as Optimizer
# from Tests.OptimizationTests.test1.input_function import Objective_Function
import time
import numpy as np


if __name__ == "__main_":

    input_file_path = [
        # "./00_SimpleORC",
        # "Thesis/Cases/00_SimpleORC_high_def",
        #"Thesis/Cases/00_SimpleORC_turbine_stages",
        #"Thesis/Cases/01_SimpleORC_recuperated",
        #"Thesis/Cases/02_SimpleORC_superheated",
        #"Thesis/Cases/03_SimpleORC_transcritical",
        #"Thesis/Cases/04_SimpleORC_superheated_recuperated/Part_a", 
        #"Thesis/Cases/04_SimpleORC_superheated_recuperated/Part_b",
        #"Thesis/Cases/04_SimpleORC_superheated_recuperated/Part_c",
        #"Thesis/Cases/05_SimpleORC_transcritical_recuperated",
        # "./06_DSC_single_flash",
        # "./07_DSC_double_flash",
        #"Thesis/Cases/08_SimpleORC_techno_specCost/Part_a",
        #"Thesis/Cases/08_SimpleORC_techno_specCost/Part_b",
        #"Thesis/Cases/08_SimpleORC_techno_specCost/Part_c",
        #"Thesis/Cases/09_SimpleORC_techno_LCOE/Part_a",
        #"Thesis/Cases/09_SimpleORC_techno_LCOE/Part_b",
        #"Thesis/Cases/09_SimpleORC_techno_LCOE/Part_c",
        #"Thesis/Cases/10_DSC_single_flash_techno_specCost",
        #"Thesis/Cases/11_DSC_single_flash_techno_LCOE",
        # "./12_SimpleORC_thermo_specCost_drillingCost",
        # "./16_SimpleORC_NCG_Venting_final",
        "./17_SimpleORC_NCG_Reinjection_final",
        # "./14_SimpleORC_NCG_CarbFix",
        # "./18_DSC_single_flash_NCG_Venting_final",
        # "./19_DSC_single_flash_NCG_Reinjection",
        # "./15_DSC_single_flash_NCG_CarbFix"
        "./19_DSC_single_flash_NCG_Reinjection_final",
        "./21_DSC_single_flash_NCG_Reinjection_no_liq",
        "./17_SimpleORC_NCG_Reinjection_final",
        "./20_SimpleORC_NCG_Reinjection_no_liq",
    ]

    Restart = True
    Parallel = False
    N_cores = 4
    start_time = time.time_ns()
    Optimizer.OptimizationManager(input_file_path, Parallel, Restart, N_cores, logging=False)
    run_time = time.time_ns() - start_time
    print('run time:', "{:.3f}".format(run_time*10**-9),'s')
