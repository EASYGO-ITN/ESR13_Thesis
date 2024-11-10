# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:54:50 2023

@author: lgalieti
"""
import time
import numpy as np
import multiprocessing
import Parallel_CoolProp_Test as PCT

if __name__ == '__main__':
    
   
    Npoint = 1
    T = np.linspace(300,500, Npoint)
    P = 0.1e5
    fluid = 'nButane'
    N_Proc = [1,2,3,4]
    # print(T,P)
    start_time = time.time_ns()
    
    for i in range(len(T)):
        
        PCT.CalcProp(P, T[i], fluid)
    run_time = time.time_ns() - start_time
    print('Bare CoolProp serial run time: ' "{:.3f}".format(run_time*10**-9),'s')
        
        
    
    for ncores in N_Proc:
        
        pool = multiprocessing.Pool(ncores)
        
        start_time = time.time_ns()
        
        packinput = []
        for i in range( Npoint):
            packinput.append([ P,T[i], fluid])
        
        
        
        
    
        
        PackOutput = pool.starmap(PCT.CalcProp, packinput)
        
        
    
        run_time = time.time_ns() - start_time
        print('Bare CoolProp parallel run time',ncores, 'cores: ' "{:.3f}".format(run_time*10**-9),'s')
        
        pool.close()
        
    
    
    
    start_time = time.time_ns()
    
    for i in range(len(T)):
       
        PCT.CalcTristanProp(P, T[i], fluid)
    
    run_time = time.time_ns() - start_time
    print('Tristan CoolProp serial run time: ' "{:.3f}".format(run_time*10**-9),'s')
    
        
    for ncores in N_Proc:
        
        pool = multiprocessing.Pool(ncores)
        
        start_time = time.time_ns()
        
        packinput = []
        
        
        for i in range( Npoint):
            packinput.append([P,T[i], fluid])
        
    
        
        
        
        PackOutput = pool.starmap(PCT.CalcTristanProp, packinput)
           
    
        run_time = time.time_ns() - start_time
        print('Tristan CoolProp parallel run time',ncores, 'cores: ' "{:.3f}".format(run_time*10**-9),'s')
    
        pool.close()
    
    
    
    