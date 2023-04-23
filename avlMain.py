import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL

if __name__ == "__main__":
    planeName = 'STARTG01'
    AVLsp = pyAVL.AVL()
    AVLsp.loadPlane(planeName)
    AVLsp.loadMass(planeName)

    AVLsp.setAtmosphere(25e3,20)
    AVLsp.setVelocity(275*1.6878099)
    AVLsp.addInput('oper')
    AVLsp.addInput('C1')
    AVLsp.addInput('\nX\nG\nLO\nH')
    AVLsp.runAVL()

