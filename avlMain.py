import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL
import openmdao.api as om
import numpy as np
import time

class STARTG01_Model(om.ExplicitComponent):
    """
    STARTG01 AVL model
    """
    # define the i/o here 
    def setup(self):
        self.add_input('c_i', val=np.zeros(5))
        self.add_input('b', val=1)

        self.add_output('S', val=1)
        self.add_output('CDtot', val=1)
        self.add_output('Dtot', val=1)

        # setup AVL
        self.t_start = time.time()

        self.AVLsp_init = pyAVL.AVL()
        self.AVLsp_init.load_opt_template(planeName)
        self.b_init = self.AVLsp_init.var_dict['b_i']
        print(self.b_init)

    # can define analytical diffs here, but we will use finite difference
    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    # 
    def compute(self, inputs, outputs):
        # c = inputs['c'] # pull values from the inputs
        t = time.time()

        # AVLsp = self.AVLsp
        self.AVLsp = pyAVL.AVL()
        self.AVLsp.load_opt_template(planeName)

        self.AVLsp.var_dict['c_i'] = inputs['c_i']
        # print(inputs['b'],inputs['b']*self.b_init/115.77869)
        self.AVLsp.var_dict['b_i'] = inputs['b']*self.b_init/115.77869

        self.AVLsp.writeOptimize(planeName)
        self.AVLsp.updateRefs(planeName)
        self.AVLsp.writeOptimize(planeName)

        self.AVLsp.load_opt_plane(planeName)
        self.AVLsp.addInput('oper')
        self.AVLsp.addInput('A C {}'.format(.5*826.13454/self.AVLsp.var_dict['Sref'][0]))
        self.AVLsp.addInput('X')
        self.AVLsp.saveOutput('FT','opt')
        self.AVLsp.saveOutput('\n')
        

        self.AVLsp.runAVL()
        self.AVLsp.clearInput()

        out_dict = self.AVLsp.readOutput('FT','opt')

        print(self.AVLsp.var_dict,'\n',out_dict['CDtot'])

        Sref = out_dict['Sref']
        
        wing_L = out_dict['Cref']
        rho = 0.1152e-02
        V = 275*1.6878099
        mu= 3.246e-7
        Re = (rho * V * wing_L) / mu
        Cf = 0.072/Re**(1/5)
        
        FF = 1 + 2.7*(.2)+100*(.2)**4
        
        f = 2.1*Sref*1*Cf*FF

        outputs['S'] = Sref
        outputs['CDtot'] = out_dict['CDtot'] + f/Sref
        outputs['Dtot'] = outputs['CDtot']*0.5*rho*V**2*Sref
        print(outputs['CDtot'],outputs['Dtot'])
        print('Total time: {} s, Last iteration: {} s'.format(time.time() - self.t_start,time.time() - t))


if __name__ == "__main__":
    planeName = 'STARTG01'

    # AVLsp = pyAVL.AVL()
    # AVLsp.load_opt_template(planeName)

    # AVLsp.writeOptimize(planeName)
    # AVLsp.updateRefs(planeName)
    # AVLsp.writeOptimize(planeName)

    # print(AVLsp.opt_template)
    
    

    # AVLsp.runAVL()


    model = om.Group() # a group instance. this is used to organize multiple groups 
    model.add_subsystem('Aeromodel', STARTG01_Model(),promotes_inputs=['c_i','b']) # each group can have a collection of subsystems. In this case, it's only one.

    # can actually define stuff in model before moving onto the problem setup
    # model.add_subsystem('constraint1', om.ExecComp('g = x + y'),promotes_inputs=['x','y'])

    # set default values
    model.set_input_defaults('c_i',[10.188, 9.3026, 6.512, 3.721, 0.9989])
    model.set_input_defaults('b',115.77869)
    # model.set_input_defaults('y',-4)

    # now setup the optimization
    prob = om.Problem(model) # create a problem instance

    # select a driver
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'

    prob.model.add_design_var('c_i',lower=0,upper=20)
    prob.model.add_design_var('b',lower=0,upper=115.77869)
    # prob.model.add_design_var('y',lower=-50,upper=50)
    prob.model.add_objective('Aeromodel.Dtot')

    # also add constraint
    prob.model.add_constraint('Aeromodel.S',lower=826.13454)

    prob.setup() # creates some data structures so the model can be ready for execution

    prob.run_driver()



