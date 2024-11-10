from pymoo.core.problem import ElementwiseProblem
import importlib
import sys

class ORCptimization_Problem(ElementwiseProblem):

    def __init__(self, Function, Parameters, input_file_path, **kwargs):
        sys.path.append(input_file_path)
        import input_file
        # this is needed when multiple optimization are queued. Otherwise it may skip reloading the inputscript
        importlib.reload(input_file)

        ####### setting the input function as a class attribute. It is supposed to return both objectives and constraints

        self.Function = Function
        self.Parameters = Parameters

        ####### setting here the number of variables, objectives and constraints

        super().__init__(n_var=input_file.N_var,
                         n_obj=input_file.N_obj,
                         n_constr=input_file.N_constr,
                         xl=input_file.Variables_low_bound,
                         xu=input_file.Variables_up_bound, **kwargs)

        while input_file in sys.path:
            sys.path.remove(input_file)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"], out["G"] = self.Function(x, self.Parameters)
        
           
        
      
            
            
            
            
        
        
            
            
            
        
    
    