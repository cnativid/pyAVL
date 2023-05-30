import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL
import openmdao.api as om
import numpy as np

class STARTG01_Model(om.ExplicitComponent):
    """
    STARTG01 AVL model
    """
    # define the i/o here 
    def setup(self):
        self.add_input('c', val=np.zeros(5))
        self.add_output('S', val=1)
        self.add_output('CDtot', val=1)

    # can define analytical diffs here, but we will use finite difference
    def setup_partials(self):
        # Finite difference all partials.
        self.declare_partials('*', '*', method='fd')

    # 
    def compute(self, inputs, outputs):
        # c = inputs['c'] # pull values from the inputs

        AVLsp = pyAVL.AVL()
        AVLsp.opt_template(planeName)

        AVLsp.optvarval[3:] = inputs['c']

        AVLsp.writeOptimize(planeName)
        AVLsp.updateRefs(planeName)
        AVLsp.writeOptimize(planeName)

        AVLsp.load_opt_plane(planeName)
        AVLsp.addInput('oper')
        AVLsp.addInput('A C {}'.format(.5*826.13454/AVLsp.optvarval[0]))
        AVLsp.addInput('X')
        AVLsp.saveOutput('FT','opt')
        

        AVLsp.runAVL()

        var_dict = AVLsp.readOutput('FT','opt')

        print(AVLsp.optvarval,'\n',var_dict['CDtot'])

        Sref = var_dict['Sref']
        
        wing_L = var_dict['Cref']
        rho = 0.1152e-02
        V = 275*1.6878099
        mu= 3.246e-7
        Re = (rho * V * wing_L) / mu
        Cf = 0.072/Re**(1/5)
        
        FF = 1 + 2.7*(.2)+100*(.2)**4
        
        f = 2.1*Sref*1*Cf*FF

        outputs['S'] = Sref
        outputs['CDtot'] = var_dict['CDtot'] + f/Sref
        print(outputs['CDtot'])


if __name__ == "__main__":
    planeName = 'STARTG01'
    # AVLsp = pyAVL.AVL()
    # AVLsp.loadOptimize(planeName)

    # AVLsp.writeOptimize(planeName)
    # AVLsp.updateRefs(planeName)
    # AVLsp.writeOptimize(planeName)

    # print(AVLsp.optvarval)
    
    

    # AVLsp.runAVL()

    model = om.Group() # a group instance. this is used to organize multiple groups 
    model.add_subsystem('Aeromodel', STARTG01_Model(),promotes_inputs=['c']) # each group can have a collection of subsystems. In this case, it's only one.

    # can actually define stuff in model before moving onto the problem setup
    # model.add_subsystem('constraint1', om.ExecComp('g = x + y'),promotes_inputs=['x','y'])

    # set default values
    model.set_input_defaults('c',[10.188, 9.3026, 6.512, 3.721, 0.9989])
    # model.set_input_defaults('y',-4)

    # now setup the optimization
    prob = om.Problem(model) # create a problem instance

    # select a driver
    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'

    prob.model.add_design_var('c',lower=0,upper=20)
    # prob.model.add_design_var('y',lower=-50,upper=50)
    prob.model.add_objective('Aeromodel.CDtot')

    # also add constraint
    prob.model.add_constraint('Aeromodel.S',lower=826.13454)

    prob.setup() # creates some data structures so the model can be ready for execution

    prob.run_driver()

    # # run ONCE
    # # repeat again
    # prob.set_val('parab.x', 6.667)
    # prob.set_val('parab.y', -7.333)

    # prob.run_model()
    # print(prob['parab.f_xy'])

