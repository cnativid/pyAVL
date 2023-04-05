import sys
import openmdao.api as om
sys.path.append('path/to/pyAVL.py')
import pyAVL

PlaneName = 'TestPlane'


# sections = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
def taperstudy(span,chord):
    print(chord)
    mainWingSections = []
    croot = chord[0]
    sections = len(chord)
    for i, c in enumerate(chord):
        mainWingSections.append([[(croot-c)/2,i*span[0]/(2*(sections-1)),0],
        c,0,15,1,
        'SD7037-092-88.dat'])

    mainWing = pyAVL.Surface('mainWing',1,1,[0,0,0],0,15,1,mainWingSections)
    hStab = pyAVL.Surface('hStab',1,1,[4,0,0],0,10,1,
        [
        [[0,0,0],
         1,0,6,1,
         'NACA0012.dat'],
        [[.25,1,0],
         .5,0,6,1,
         'NACA0012.dat'],
    ])
    # print(span,chord[0])
    TestPlane = pyAVL.Plane([mainWing])
    pyAVL.CreateAVLPlane(PlaneName,0,TestPlane)
    alphas = [0]
    out = pyAVL.alpha(PlaneName,alphas)
    # CLs = [.5]
    # out = pyAVL.alpha('TestPlane',CLs)
    return out

class OptProblem(om.ExplicitComponent):
    """
    Computes the CL/CD of the wing
    """

    def setup(self):
        self.add_input('span',val=1)
        self.add_input('chord',val=[1,1,1])

        self.add_output('optFun',val=0)

    def setup_partials(self):
        self.declare_partials('*','*',method='fd')

    def compute(self, inputs, outputs):
        span = inputs['span']
        chord = inputs['chord']

        out = taperstudy(span,chord)
        # optFun = out['CLtot']/out['CDtot']
        optFun = out['e']
        print(optFun)
        outputs['optFun'] = optFun
    

if __name__ == "__main__":
    pyAVL.showGeom(PlaneName)
    prob = om.Problem()
    prob.model.add_subsystem('OptFun', OptProblem(), promotes_inputs=['span','chord'])

    prob.model.set_input_defaults('chord',[1,1,1])
    prob.model.set_input_defaults('span',5)

    prob.driver = om.ScipyOptimizeDriver()
    prob.driver.options['optimizer'] = 'COBYLA'
    prob.driver.options['maxiter'] = 1e5
    

    prob.model.add_design_var('chord',lower = 0.01, upper = 1)
    # prob.model.add_design_var('span',lower = 1, upper = 10)
    prob.model.add_objective('OptFun.optFun',scaler=-1)

    prob.setup()
    prob.run_driver();
    
    pyAVL.showGeom(PlaneName)

