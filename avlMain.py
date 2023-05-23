import sys
sys.path.append('path/to/pyAVL.py')
import pyAVL

if __name__ == "__main__":
    planeName = 'STARTG01'
    AVLsp = pyAVL.AVL()
    AVLsp.loadOptimize(planeName)
    AVLsp.writeOptimize(planeName)
    

    AVLsp.runAVL()


