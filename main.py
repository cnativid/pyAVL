import sys
import openmdao.api as om
sys.path.append('path/to/pyAVL.py')
import pyAVL

# sections = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
def taperstudy(taper):
    mainWing = pyAVL.Surface('mainWing',1,1,[0,0,0],0,20,1,
        [
        [[0,0,0],1,0,20,1,'SD7037-092-88.dat'],
        [[.25*taper[0],5,0],taper[0],0,20,1,'SD7037-092-88.dat'],
    ])
    print(mainWing.sections)
    TestPlane = pyAVL.Plane([mainWing])
    pyAVL.CreateAVLPlane('TestPlane',0,TestPlane)
    alphas = [0]
    CLCD = pyAVL.alpha('TestPlane',alphas)
    print(CLCD)
    return CLCD


class OptProblem(om.ExplicitComponent):
    """
    Computes the CL/CD of the wing
    """

    def setup(self):
        self.add_input('taper',val=1)

        self.add_output('CLCD',val=0)

    def setup_partials(self):
        self.declare_partials('*','*',method='fd')

    def compute(self, inputs, outputs):
        taper = inputs['taper']

        outputs['CLCD'] = taperstudy(taper)
    
    

if __name__ == "__main__":
    prob = om.Problem()
    prob.model.add_subsystem('CLCDOpt', OptProblem(), promotes_inputs=['taper'])

    prob.model.set_input_defaults('taper',.5)

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'

    prob.model.add_design_var('taper',lower = 0.01, upper = 2)
    prob.model.add_objective('CLCDOpt.CLCD',scaler=-1)

    prob.setup()
    prob.run_driver();