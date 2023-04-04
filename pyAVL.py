from ambiance import Atmosphere
import os
import sys
import re
import subprocess
import time

class Plane:
    def __init__(self,surfaces):
        self.surfaces = surfaces
        # print(range(0,len(self.surfaces[0].sections[:-1])-2))
        # print(len(self.surfaces[0].sections))
        self.Sref = 0
        for i in range(0,len(self.surfaces[0].sections)-1):

            # self.Sref += self.surfaces.sections
            self.Sref +=((self.surfaces[0].sections[i+1][1]+self.surfaces[0].sections[i][1])*(self.surfaces[0].sections[i+1][0][1]-self.surfaces[0].sections[i][0][1]))
        # for i = len(self.surfaces[0].sections[:-1])
        # self.Sref = self.surfaces[0].sections[:-1]

            
            
            
        # self.bodies = bodies

class Surface:
    def __init__(self, name, symmetry, component, translate, incidence, Nchord, Cspace, sections):
        """
        name: string
            Name of the Surface
        symmetry: boolean
            0 = no symmetry
            1 = symmetry over X-Z plane
        component: integer
            Component #
        translate: vector
            Location of LE at root chord
        incidence: float
            Incidence Angle
        Nchord: integer
            Number of chordwise points
        Cspace: integer
            Chordwise point distribution
        sections: array
            Section Array
        """
        self.name = name
        self.symmetry = symmetry
        self.component = component
        self.translate = translate
        self.incidence = incidence
        self.Nchord = Nchord
        self.Cspace = Cspace
        self.sections = sections
        
def WriteSection(section):
    # section = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
    sect = "SECTION\n{} {} {} {} {} {} {} \nAFIL\nAirfoils\\{}\n".format(section[0][0],section[0][1],section[0][2],section[1],section[2],section[3],section[4],section[5])
    return sect

def WriteSurface(surface):
    surf = "SURFACE\n{}\n{} {}\nCOMPONENT\n{}\n".format(surface.name,surface.Nchord, surface.Cspace,surface.component)
    if surface.symmetry == 1:
        surf = surf+"YDUPLICATE\n0.0\n"
    surf = surf + "TRANSLATE\n{} {} {}\nANGLE\n{}\n".format(surface.translate[0],surface.translate[1],surface.translate[2],surface.incidence)
    for section in surface.sections:
        surf = surf + WriteSection(section)
    # print(surf)
    return surf
    
# def ComponentHeader(text):
#     text = text.replace("", " ")[1: -1]
#     length = len(text)
#     header = ["\n"+"#" * (length+8)+"\n","#   {}   #\n".format(text),"#" * (length+8)+"\n"]
#     return header

# def SectionHeader(text):
#     header = "###  {}  ###\n".format(text.replace("", " ")[1: -1])
#     return header

def CreateAVLPlane(name,mach,plane):
    # print('AAA')
    cd = os.getcwd() # Get current location of python script
    if not os.path.exists('{}\\Planes'.format(cd)): # create folders if nonexistent
        os.mkdir('{}\\Planes'.format(cd))
        print("/Planes folder created")
    if not os.path.exists('{}\\Planes\\{}'.format(cd,name)):
        os.mkdir('{}\\Planes\\{}'.format(cd,name))
        print("Planes/{} folder created".format(name))

    
    Cref = 10
    Bref = 10
    
    with open('{}\\Planes\\{}\\{}.avl'.format(cd,name,name),'w') as file:
        file.write('{}\n{}\n0 0 0\n{} {} {}\n0 0 0\n0\n'.format(name,mach,plane.Sref,Cref,Bref))
        for surface in plane.surfaces:
            file.write(WriteSurface(surface))

        # file.writelines(ComponentHeader('MASS DEFINTION'))
        # file.write(SectionHeader('MASS DEFINTION'))

class AVL:
    def __init__(self):
        self.inputList = ''
        self.cd = os.getcwd()
        # print(self)
    def addInput(self,input):
        self.inputList += '{}\n'.format(input)
        # print(self.inputList)
    def clearInput(self):
        self.inputlist = ''
    def runAVL(self):
        self.AVLsp = subprocess.Popen('avl.exe',
            shell=False,
            stdin=subprocess.PIPE,
            stdout=open('AVLsession.log', 'w'),         # Put the output of this terminal into the open log file
            stderr=subprocess.PIPE)
        self.AVLsp.stdin.write(self.inputList.encode('utf-8'))
        self.AVLsp.stdin.flush()
        self.AVLsp.communicate()
    
        log = open('AVLsession.log').read()
        os.path.getsize('AVLsession.log')
        # print(len(log))
        start = log.rfind('  Alpha =')
        end = log.rfind('| Plane')
        caseOutput = log[start:end].replace('| Trefftz','').replace('=',' ').split()
        caseData = dict(zip(caseOutput[::2],list(map(float,caseOutput[1::2]))))
        return caseData
        
        
    # def readAVL(self,varlist):
    #     varlist = [var + ' = ' for var in varlist]
    #     with open("{}\\AVLsession.log".format(self.cd),'r') as f:
    #         print("{}\\AVLsession.log".format(self.cd))
    #         log = f.read()
    #         start = log.rfind(' Forces')+len(' Forces')
    #         end = log.rfind('| Plane')
    #         print(start,end)
    #         for var in varlist:
    #             print(var)
    #             print(log.rfind(var,start,end))

def alpha(plane,alphas):
    AVLsp = AVL()
    AVLsp.addInput('load Planes\\{}\\{}'.format(plane,plane))
    AVLsp.addInput('oper')
    for alpha in alphas:
        AVLsp.addInput('A')
        AVLsp.addInput('A')
        AVLsp.addInput('{}'.format(alpha))
        AVLsp.addInput('X')
        output = AVLsp.runAVL()
        CLCD = output['CLtot']/output['CDtot']
        print(CLCD)
        AVLsp.clearInput()
    # AVLsp.readAVL(['e','Alpha','CLtot'])

if __name__ == "__main__":
    name = 'TestPlane'
    # mach = 0
    # # sections = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
    # mainWing = Surface('MainWing',1,1,[0,0,0],0,10,1,
    #     [
    #     [[0,0,0],1,0,10,1,'S4022.dat'],
    #     [[.25,5,0],.5,0,10,1,'S4022.dat'],
    # ])
    # hStab = Surface('hStab',1,2,[5,0,.5],0,5,1,
    #                 [
    #     [[0,0,0],.5,0,10,1,'S4022.dat'],
    #     [[.125,2,0],.25,0,10,1,'S4022.dat'],
    #                 ])
    # TestPlane = Plane([mainWing,hStab])

    # # TestPlane = Plane(surfs,bodies)
    # CreateAVLPlane(name,mach,TestPlane)
    # AVLsp = AVL()
    # AVLsp.addInput('load Planes/{}/{}.avl'.format(name,name))
    # AVLsp.addInput('oper')
    # AVLsp.addInput('A')
    # AVLsp.addInput('C')
    # AVLsp.addInput('.6')
    # AVLsp.addInput('C1')
    # AVLsp.addInput('X')
    # AVLsp.addInput('1')
    # AVLsp.addInput('')
    # AVLsp.addInput('X')
    # AVLsp.runAVL()


    