# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 18:56:29 2023

@author: lgalieti
"""

# TODO results reporting

import copy
import importlib
import sys

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
# from pymoo.termination import get_termination
from pymoo.termination.default import Termination
from pymoo.core.problem import StarmapParallelization
from pymoo.optimize import minimize
import multiprocessing
import numpy as np
import os
import itertools

import json

from . import ORCptimization_problem


def OptimizationManager(file_paths, Parallel, Restart, N_cores=[], logging=True):
    for file in file_paths:
        if not os.path.exists(file):
            msg = "the specified filepath \"{}\" does not exist! Aborted Optimization!!".format(file)
            raise ValueError(msg)

    for file in file_paths:
        print(file)
        sys.path.append(file)

        import input_file
        import input_function

        # this is needed when multiple optimization are queued. Otherwise it may skip reloading the inputscript
        importlib.reload(input_file)
        importlib.reload(input_function)

        SensitivityParameters = input_file.SensitivityParams
        n_Vars = input_file.N_var

        ObjectiveFunc = input_function.Objective_Function
        CaseParameters = []

        if SensitivityParameters:
            SensitivityVars = [i for i in SensitivityParameters]
            SensitivityValues = [SensitivityParameters[i] for i in SensitivityVars]
            SensitivityIDs = [list(range(len(SensitivityParameters[i]))) for i in SensitivityVars]

            case_ids = list(itertools.product(*SensitivityIDs))

            if logging:
                sensitivity_name = file + "/sensitivity.npy"
                np.save(sensitivity_name, case_ids)

            # update the Parameters
            for case in case_ids:
                case_params = copy.deepcopy(input_file.Parameters)

                for i, sens_var in enumerate(SensitivityVars):
                    case_params[sens_var] = SensitivityValues[i][case[i]]

                CaseParameters.append(case_params)

        else:
            CaseParameters.append(copy.deepcopy(input_file.Parameters))

        if not os.path.exists(file + '/results'):
            os.mkdir(file + '/results')
        if not os.path.exists(file + '/checkpoint'):
            os.mkdir(file + '/checkpoint')
        if not os.path.exists(file + '/inputs'):
            os.mkdir(file + '/inputs')

        # resets the sensitivity results for this sensitivity
        open(file + "/sensitivity_results.txt", "w").close()
        open(file + "/sensitivity_results.json", "w").close()

        CaseResults = ["" for case in CaseParameters]

        for i, case in enumerate(CaseParameters):
            ####### generate checkpoint name
            checkpoint_name = file + '/checkpoint/Checkpoint_{}.npy'.format(i)
            history_name = file + '/results/History_{}.npy'.format(i)
            inputs_name = file + "/inputs/Inputs_{}.npy".format(i)

            if Restart:

                if os.path.exists(checkpoint_name):
                    pop_init = np.load(checkpoint_name, allow_pickle=True)
                else:
                    continue
                if os.path.exists(history_name):
                    History = np.load(history_name, allow_pickle=True)
                else:
                    continue
            else:
                pop_init = FloatRandomSampling()
                History = np.empty(0)

            # for pop in pop_init:
            #     pop.F *= 10

            N_individuals_0 = input_file.N_individuals_0  ## size of the initial generation
            N_individuals = input_file.N_individuals  # size of all the subsequent generations
            N_gen = input_file.N_gen
            Seed_init = input_file.Seed_init  # change this number to change the distribution of the initial population
            cross_over_prob = input_file.cross_over_prob
            cross_over_eta = input_file.cross_over_eta
            mut_prob = input_file.mut_prob
            mut_eta = input_file.mut_eta

            algorithm = GA(
                pop_size=N_individuals_0,
                n_offsprings=N_individuals,
                sampling=pop_init,
                crossover=SBX(prob=cross_over_prob, eta=cross_over_eta),
                mutation=PM(prob=mut_prob, eta=mut_eta),
                eliminate_duplicates=True  # True
            )

            # termination = get_termination("n_gen", N_gen)
            termination = CustomTerminator(0.01, N_gen)  # set to 0.005 when resunning the techno-economic optimisation

            if Parallel and __name__ == "ORCptimization.ORCptimization_manager":
                pool = multiprocessing.Pool(N_cores)
                runner = StarmapParallelization(pool.starmap)

                problem = ORCptimization_problem.ORCptimization_Problem(ObjectiveFunc, case, file,
                                                                        elementwise_runner=runner)
            else:
                problem = ORCptimization_problem.ORCptimization_Problem(ObjectiveFunc, case, file)

            res = minimize(problem, algorithm, termination, save_history=True, seed=Seed_init, verbose=True, return_least_infeasible=False)

            try:
                X = res.X
                W_net_best = -res.F

                extra_res = input_function.PostProcessing(X, CaseParameters[i])

                fmin, fmax, favg = get_convergence_data(res.history)

                if logging:
                    History = np.append(History, res.history)
                    np.save(checkpoint_name, History[-1].pop)
                    np.save(history_name, History)

                if SensitivityParameters and logging:
                    np.save(inputs_name, case_ids[i])

                with open(file + "/sensitivity_results.txt", "a") as res_file:
                    results = ""

                    if i == 0:
                        header = ""
                        for key in CaseParameters[0]:
                            header += key + ";"
                        header += "ObjFunc;"
                        for j in range(n_Vars):
                            header += "Var {};".format(j)
                        for x_res in extra_res:
                            header += x_res + ";"
                        header += "fmin;fmax;favg;"
                        header += "\n"

                        results += header

                    for key in CaseParameters[i]:
                        results += str(CaseParameters[i][key]) + ";"
                    for res in W_net_best:
                        results += str(res) + ";"
                    for x_var in X:
                        results += str(x_var) + ";"
                    for x_res in extra_res:
                        results += str(extra_res[x_res]) + ";"

                    results += str(fmin) + ";"
                    results += str(fmax) + ";"
                    results += str(favg) + ";"

                    results += "\n"
                    res_file.write(results)

                CaseResults[i] = {key: CaseParameters[i][key] for key in CaseParameters[i]} | \
                               {"ObjFunc": list(W_net_best)} | \
                               {"Var {}".format(j): X[j] for j in range(n_Vars)} | \
                               extra_res | \
                               {"fmin": fmin, "fmax": fmax, "favg": favg}

                with open(file + "/sensitivity_results.json", "w") as res_file:
                    json.dump(CaseResults, res_file)

                print('Optimization Successful')

            except:

                print('Optimization Failed')

            if Parallel and __name__ == "ORCptimization.ORCptimization_manager":
                pool.close()



        while file in sys.path:
            sys.path.remove(file)


def get_convergence_data(History):

    best = []
    average = []
    worst = []

    for j in range(len(History)):

        H = History[j]
        F = []

        for k in range(len(H.pop)):
            # if H.pop[k].F < 0:
            #     F.append(H.pop[k].F[0])
            # else:
            #     F.append(0)

            F.append(H.pop[k].F[0])

        best.append(min(F))
        worst.append(max(F))
        average.append(sum(F) / len(F))

    return best, worst, average


class CustomTerminator(Termination):

    def __init__(self, f_tol, n_max_gen):
        super().__init__()

        self.f_tol = f_tol
        self.n_max_gen = n_max_gen

    def _update(self, algorithm):

        progress = 0.0

        if algorithm.history:
            f_avg = algorithm.history[-1].output.f_avg.value
            f_min = algorithm.history[-1].output.f_min.value

            if abs(f_min-f_avg)/abs(f_min + 1e-6) <= self.f_tol:
                progress = 1.1

        if algorithm.n_gen >= self.n_max_gen:
            progress = 1.1

        return progress
