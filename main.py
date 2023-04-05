import sys
import openmdao.api as om
sys.path.append('path/to/pyAVL.py')
import pyAVL

# sections = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
def taperstudy(span,taper1,taper2,taper3):
    mainWing = pyAVL.Surface('mainWing',1,1,[0,0,0],0,10,1,
        [
        [[0,0,0],
         1,0,10,1,
         'SD7037-092-88.dat'],
        [[(1-taper1[0])/2,span[0]/4,0],
         taper1[0],0,10,1,
         'SD7037-092-88.dat'],
        [[(1-taper2[0])/2,3*span[0]/8,0],
        taper2[0],0,5,1,
        'SD7037-092-88.dat'],
                [[(1-taper3[0])/2,span[0]/2,0],
        taper3[0],0,5,1,
        'SD7037-092-88.dat']
    ])
    hStab = pyAVL.Surface('hStab',1,1,[4,0,0],0,10,1,
        [
        [[0,0,0],
         1,0,6,1,
         'NACA0012.dat'],
        [[.25,1,0],
         .5,0,6,1,
         'NACA0012.dat'],
    ])
    print(span,taper1,taper2,taper3)
    TestPlane = pyAVL.Plane([mainWing])
    pyAVL.CreateAVLPlane('TestPlane',0,TestPlane)
    alphas = [0]
    out = pyAVL.alpha('TestPlane',alphas)
    # CLs = [.5]
    # out = pyAVL.alpha('TestPlane',CLs)
    return out

class OptProblem(om.ExplicitComponent):
    """
    Computes the CL/CD of the wing
    """

    def setup(self):
        self.add_input('span',val=1)
        self.add_input('taper1',val=1)
        self.add_input('taper2',val=1)
        self.add_input('taper3',val=1)

        self.add_output('optFun',val=0)

    def setup_partials(self):
        self.declare_partials('*','*',method='fd')

    def compute(self, inputs, outputs):
        span = inputs['span']
        taper1 = inputs['taper1']
        taper2 = inputs['taper2']
        taper3 = inputs['taper3']

        out = taperstudy(span,taper1,taper2,taper3)
        # optFun = out['CLtot']/out['CDtot']
        optFun = out['e']
        print(optFun)
        outputs['optFun'] = optFun
    
    

if __name__ == "__main__":
    prob = om.Problem()
    prob.model.add_subsystem('OptFun', OptProblem(), promotes_inputs=['span','taper1','taper2','taper3'])

    prob.model.set_input_defaults('taper1',1)
    prob.model.set_input_defaults('taper2',1)
    prob.model.set_input_defaults('taper3',1)
    prob.model.set_input_defaults('span',5)

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'

    prob.model.add_design_var('taper1',lower = 0.01, upper = 1)
    prob.model.add_design_var('taper2',lower = 0.01, upper = 1)
    prob.model.add_design_var('taper3',lower = 0.01, upper = 1)
    # prob.model.add_design_var('span',lower = 1, upper = 10)
    prob.model.add_objective('OptFun.optFun',scaler=-1)

    prob.setup()
    prob.run_driver();