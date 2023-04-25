import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL

if __name__ == "__main__":
    planeName = 'STARTG01'
    AVLsp = pyAVL.AVL()
    AVLsp.loadPlane(planeName)
    AVLsp.loadMass(planeName)

    AVLsp.setAtmosphere(25e3,0)
    AVLsp.setVelocity(275*1.6878099)
    AVLsp.addInput('oper')
    AVLsp.addInput('C1\n')
    AVLsp.addInput('D5\nPM\n0')
    AVLsp.addInput('X')
    AVLsp.saveOutput('FT','cruise')

    AVLsp.addInput('oper')
    AVLsp.addInput('C1\n')
    # AVLsp.addInput('D1 D1 0')
    AVLsp.addInput('A C 3.3')
    AVLsp.addInput('D2 D2 45')
    # AVLsp.addInput('D3 D3 0')
    AVLsp.addInput('D4 D4 45')
    # AVLsp.addInput('D5 PM 0')
    AVLsp.addInput('X')
    AVLsp.saveOutput('FT','landing')

    AVLsp.addInput('X')

    AVLsp.runAVL()

