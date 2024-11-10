
########### Genetic algorithm settings #################

N_var = 3
# flashing, Pmin, Pabsorb
Variables_low_bound  = [0.1, 0.1e5, 0]
Variables_up_bound   = [0.99, 5e5, 1]

N_obj = 1
N_constr = 0

N_species = N_var * 10

N_individuals_0 = 3*N_species  ## size of the initial generation
N_individuals = N_species  # size of all the subsequent generations
N_gen = N_var * 10

Seed_init = 1 # change this number to change the distribution of the initial population
cross_over_prob = 0.8
cross_over_eta  = 15
mut_prob = 0.2
mut_eta  = 0.3

SensitivityParams = {
"Hot fluid input2"         : [0.25],  # because at this steam quality the ORC and DSC have simular net power and specific cost
"Hot fluid input1"         : [200+273.15],
"Hot fluid comp"           : [["water", 0.99, "carbondioxide", 0.01],
                              ["water", 0.98, "carbondioxide", 0.02],
                              ["water", 0.97, "carbondioxide", 0.03],
                              ["water", 0.96, "carbondioxide", 0.04],
                              ["water", 0.95, "carbondioxide", 0.05],
                              ["water", 0.93, "carbondioxide", 0.07],
                              ["water", 0.91, "carbondioxide", 0.09],
                              ["water", 0.89, "carbondioxide", 0.11],
                              ["water", 0.87, "carbondioxide", 0.13],
                              ["water", 0.85, "carbondioxide", 0.15]
                              ]
}

Parameters = {
"is Cycle regenerated"     : False,
"Hot fluid comp"           : ["water", 0.95, "carbondioxide", 0.05],
"Hot fluid engine"         : "geoprop",
"Hot fluid table path"     : "../../propertyengine_plugins/LookUpTables/SuperDuperTable",
"Hot fluid tables"         : True,
# "Hot fluid comp"           : ["water", 1],
# "Hot fluid engine"         : "default",
"Hot fluid input spec"     : 'TQ',
"Hot fluid input1"         : 450,
"Hot fluid input2"         : 0.15,
"Hot fluid mass flow"      : 50,
"Cold fluid comp"          : ["air", 1],
"Cold fluid engine"        : "default",
"Condenser dP"             : 120,
"Cooling Pump IsenEff"     : 0.6,
"Working fluid comp"       : ["nButane", 1],
"Working fluid engine"     : "default",
"MaxSuperheat"             : 15,
"MinSuperheat"     : 2,
"TestMassRates"            : [1, 2.5, 5, 10, 25, 50, 100, 150, 200],
"Geofluid_P_out"           : 75e5
}






