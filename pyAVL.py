from ambiance import Atmosphere
import os
import sys
import re
import subprocess
import time
import numpy as np
import re

'''
# class Plane:
#     def __init__(self,surfaces):
#         self.surfaces = surfaces
#         # print(range(0,len(self.surfaces[0].sections[:-1])-2))
#         # print(len(self.surfaces[0].sections))
#         self.Sref = 0
#         for i in range(0,len(self.surfaces[0].sections)-1):

#             # self.Sref += self.surfaces.sections
#             self.Sref +=((self.surfaces[0].sections[i+1][1]+self.surfaces[0].sections[i][1])*(self.surfaces[0].sections[i+1][0][1]-self.surfaces[0].sections[i][0][1]))
#         self.Bref = 2*self.surfaces[0].sections[-1][0][1]
#         self.Cref = self.Sref/self.Bref
#         # for i = len(self.surfaces[0].sections[:-1])
#         # self.Sref = self.surfaces[0].sections[:-1]

            
            
            
#         # self.bodies = bodies

# class Surface:
#     def __init__(self, name, symmetry, component, translate, incidence, Nchord, Cspace, sections):
#         """
#         name: string
#             Name of the Surface
#         symmetry: boolean
#             0 = no symmetry
#             1 = symmetry over X-Z plane
#         component: integer
#             Component #
#         translate: vector
#             Location of LE at root chord
#         incidence: float
#             Incidence Angle
#         Nchord: integer
#             Number of chordwise points
#         Cspace: integer
#             Chordwise point distribution
#         sections: array
#             Section Array
#         """
#         self.name = name
#         self.symmetry = symmetry
#         self.component = component
#         self.translate = translate
#         self.incidence = incidence
#         self.Nchord = Nchord
#         self.Cspace = Cspace
#         self.sections = sections
        
# def WriteSection(section):
#     # section = [[Xle,Yle,Zle],chord,angle,Nspan,Sspace,airfoil]
#     sect = "SECTION\n{} {} {} {} {} {} {} \nAFIL\nAirfoils\\{}\n".format(section[0][0],section[0][1],section[0][2],section[1],section[2],section[3],section[4],section[5])
#     return sect

# def WriteSurface(surface):
#     surf = "SURFACE\n{}\n{} {}\nCOMPONENT\n{}\n".format(surface.name,surface.Nchord, surface.Cspace,surface.component)
#     if surface.symmetry == 1:
#         surf = surf+"YDUPLICATE\n0.0\n"
#     surf = surf + "TRANSLATE\n{} {} {}\nANGLE\n{}\n".format(surface.translate[0],surface.translate[1],surface.translate[2],surface.incidence)
#     for section in surface.sections:
#         surf = surf + WriteSection(section)
#     # print(surf)
#     return surf
    
# def ComponentHeader(text):
#     text = text.replace("", " ")[1: -1]
#     length = len(text)
#     header = ["\n"+"#" * (length+8)+"\n","#   {}   #\n".format(text),"#" * (length+8)+"\n"]
#     return header

# def SectionHeader(text):
#     header = "###  {}  ###\n".format(text.replace("", " ")[1: -1])
#     return header

# def CreateAVLPlane(name,mach,plane):
#     # print('AAA')
#     cd = os.getcwd() # Get current location of python script
#     if not os.path.exists('{}\\Planes'.format(cd)): # create folders if nonexistent
#         os.mkdir('{}\\Planes'.format(cd))
#         print("/Planes folder created")
#     if not os.path.exists('{}\\Planes\\{}'.format(cd,name)):
#         os.mkdir('{}\\Planes\\{}'.format(cd,name))
#         print("Planes/{} folder created".format(name))

    
#     # Cref = 10/
    
#     with open('{}\\Planes\\{}\\{}.avl'.format(cd,name,name),'w') as file:
#         file.write('{}\n{}\n0 0 0\n{} {} {}\n0 0 0\n0\n'.format(name,mach,plane.Sref,plane.Cref,plane.Bref))
#         for surface in plane.surfaces:
#             file.write(WriteSurface(surface))

#         # file.writelines(ComponentHeader('MASS DEFINTION'))
#         # file.write(SectionHeader('MASS DEFINTION'))
'''

def IsItWindows():
    """Return true if os is windows"""
    return True if os.name == 'nt' else False

class AVL:
    def __init__(self):
        self.inputList = '' 
        self.cd = os.getcwd()
        # print(self)

        self.win = IsItWindows()
        if self.win:
            self.avlpath = '{}/avl.exe'.format(self.cd)
        else:
            self.avlpath = '{}/avl3.35'.format(self.cd)


    def addInput(self,input):
        self.inputList += '{}\n'.format(input)
        # print(self.inputList)
    def clearInput(self):
        self.inputlist = ''
    def runAVL(self): # opens avl and runs all of the stored commands
        self.AVLsp = subprocess.Popen(self.avlpath,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=open('AVLsession.log', 'w'),         # Put the output of this terminal into the open log file
            stderr=subprocess.PIPE)
        self.AVLsp.stdin.write(self.inputList.encode('utf-8'))
        self.AVLsp.stdin.flush()
        self.AVLsp.communicate()

    def oper(self):
        self.addInput('\n \n \n')
        self.addInput('oper')

    def loadPlane(self,plane):
        self.addInput('load Planes/{}/{}.avl'.format(plane,plane))


    def loadMass(self,plane):
        self.addInput('mass Planes/{}/{}.mass'.format(plane,plane))
        self.addInput('mset\n0')

    def setAtmosphere(self,altitude=0,temp_offset=0):
        # convert to imperial units
        altitude = altitude/3.28084 # ft to m
        temp_offset = 5/9*temp_offset # F to C
        self.addInput('oper')
        self.addInput('M')
        self.addInput('G 32.17')
        atmo = Atmosphere(altitude)
        self.addInput('D {}'.format((atmo.temperature[0]/(atmo.temperature[0]+temp_offset))*atmo.density[0]/515.378819))
        self.addInput('\n')

    def setVelocity(self,velocity):
        self.addInput('oper')
        self.addInput('M')
        self.addInput('G 32.17')  
        self.addInput('V {}'.format(velocity))
        self.addInput('\n')
        
    def saveOutput(self,output,name=0):
        self.addInput('MRF')
        self.addInput(output)
        if name == 0:
            self.addInput('output.{}'.format(output))
        else:
            self.addInput('{}.{}'.format(name,output))
        self.addInput('O\n')

    def readOutput(self,output,name=0):
        # load output file
        if name == 0:
            fname = ('output.{}'.format(output))
        else:
            fname = ('{}.{}'.format(name,output))
        
        out = np.array(open(fname).readlines()) # read the output file
        out = out[np.array(['|' in line for line in out])]


        var_dict = {}
        for line in out:
            line = line.replace('\n','').replace(':',',').split('|')
            line[0] = line[0].split()
            line[1] = [var.strip() for var in line[1].split(',')]
            for j in range(1,len(line[0])+1):
                var_dict[line[1][-j]] = float(line[0][-j])
        return var_dict
    
    def loadOptimize(self,plane): # loads an optimization template

        optTemplate = open('Planes/{}/{}.avlopt_template'.format(plane,plane)).read() # read the optimization file
        optVars = re.findall(r'\{.*?\}',optTemplate) # find all the declared variables
        for optVar in optVars: # replace all variables w/ format brackets
            optTemplate = optTemplate.replace(optVar,'{}')
        
        optVars = [var.replace('{','').replace('}','').split(',') for var in optVars] # remove brackets in var list
        # print(optTemplate) 

        var_dict = {} # create dictionary
        var_count = 0
        for optVar in optVars: # name variables in dictionary
            if len(optVar) > 1:
                var_dict[optVar[1]] = optVar[0]
            else: # if name not declared, give general name
                var_count += 1
                var_dict['var_{}'.format(var_count)] = optVar[0]
        # print(list(var_dict.values()))

        self.optTemplate = optTemplate
        self.var_dict = var_dict
        # return optTemplate,var_dict

    def writeOptimize(self,plane):
        with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'w') as file:
            file.write(self.optTemplate.format(*self.var_dict.values()))
            
        



    # def readFT(self,name=0):
    #     if name == 0:
    #         FT = open('FT.out')
    #     else:
    #         FT = open(name)
    #     FTout = FT.readlines()
    #     out = {}
    #     for i in [7,8,11,12,13,14,15,16,17,18,19,20]:
    #         newLine = FTout[i].replace('\n','').replace(',',' ').replace('|',' ').replace('Trefftz Plane: ','').split()
    #         h = int(len(newLine)/2) # get half length
    #         for j in range(h):
    #             out[newLine[j+h]] = float(newLine[j])
    #     FT.close()
    #     return out


