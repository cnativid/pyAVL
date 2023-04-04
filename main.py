import sys
import openmdao.api as om
sys.path.append('path/to/pyAVL.py')
import pyAVL

# sections = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
mainWing = pyAVL.Surface('mainWing',1,1,[0,0,0],0,10,1,
    [
    [[0,0,0],1,0,10,1,'SD7037-092-88.dat'],
    [[.25,5,0],.5,0,10,1,'SD7037-092-88.dat'],
])
TestPlane = pyAVL.Plane([mainWing])
pyAVL.CreateAVLPlane('TestPlane',0,TestPlane)
alphas = [1,2,3,4,5]
pyAVL.alpha('TestPlane',alphas)




# # build the model
# prob = om.Problem()

# prob.model.add_subsystem('Aerodynamics', om.ExecComp('f = (x-3)**2 + x*y + (y+4)**2 - 3'))

# # setup the optimization
# prob.driver = om.ScipyOptimizeDriver()
# prob.driver.options['optimizer'] = 'SLSQP'

# prob.model.add_design_var('paraboloid.x', lower=-50, upper=50)
# prob.model.add_design_var('paraboloid.y', lower=-50, upper=50)
# prob.model.add_objective('paraboloid.f')

# prob.setup()

# # Set initial values.
# prob.set_val('paraboloid.x', 3.0)
# prob.set_val('paraboloid.y', -4.0)

# # run the optimization
# prob.run_driver();