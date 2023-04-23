import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL

if __name__ == "__main__":
    planeName = 'STARTG01'
    AVLsp = pyAVL.AVL()
    AVLsp.loadPlane(planeName)
    AVLsp.loadMass(planeName)

    AVLsp.setAtmosphere()
    AVLsp.setVelocity(275*1.6878099)
    AVLsp.addInput('oper')
    AVLsp.addInput('C1')
    AVLsp.runAVL()

