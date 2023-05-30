from ambiance import Atmosphere
import os
import sys
import re
import subprocess
import time
import numpy as np
import re


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

    def load_opt_plane(self,plane):
        self.addInput('load Planes/{}/{}.avlopt_iter'.format(plane,plane))

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
    
    def opt_template(self,plane): # loads an optimization template
        optTemplate = open('Planes/{}/{}.avlopt_template'.format(plane,plane)).read() # read the optimization file
        optVars = re.findall(r'\{.*?\}',optTemplate) # find all the declared variables
        for optVar in optVars: # replace all variables w/ format brackets
            optTemplate = optTemplate.replace(optVar,'{}')
        
        optVars = [var.replace('{','').replace('}','').split(',') for var in optVars] # remove brackets in var list
        # print(optTemplate) 

        optvarval = [] 
        # var_count = 0
        for optVar in optVars: # name variables in dictionary
            optvarval.append(float(optVar[0]))

        # # var_dict = {} # create dictionary
        # # var_count = 0
        # for optVar in optVars: # name variables in dictionary
        #     if len(optVar) > 1:
        #         var_dict[optVar[1]] = optVar[0]
        #     else: # if name not declared, give general name
        #         var_count += 1
        #         var_dict['var_{}'.format(var_count)] = optVar[0]
        # print(list(var_dict.values()))

        self.optTemplate = optTemplate # stores template
        # self.var_dict = var_dict # stores vars within itself
        self.optvarval = optvarval
        # return optTemplate,var_dict

    def writeOptimize(self,plane): # writes new values into iteration

        # this needs fixing bruhhh
        with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'w') as file:
            file.write(self.optTemplate.format(*self.optvarval))
        # self.updateRefs(plane)
        # with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'w') as file:
        #     file.write(self.optTemplate.format(*self.var_dict.values()))   

    def updateRefs(self,plane): # calculates new reference values
        with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'r') as file:
            fstring = np.array(file.readlines()) # reads line by line
            # print(fstring)
            surfref = []    
            for index, line in enumerate(fstring):
                if 'SURFACE' in line:
                    surfref.append(index)
                    if len(surfref) > 1:
                        break
            sectionindex = []
            for index, line in enumerate(fstring[:surfref[1]]):
                if 'SECTION' in line:
                    sectionindex.append(index)

            planform_data = []
            for i in range(len(sectionindex)):
                planform_data.append([float(line) for line in np.array(fstring[sectionindex[i]+1].split())[[1,3]]]) # disgusting python one liner
            planform_data = np.array(planform_data)
            # print(planform_data)
            
            section_lengths = planform_data[1:,0]-planform_data[:-1,0]
            b_ref = 2*sum(section_lengths)
            # print(span,section_lengths)
            S_ref = sum(section_lengths*(planform_data[:-1,1]+planform_data[1:,1]))
            c_ref = 2/S_ref*sum( section_lengths*(planform_data[:-1,1]*planform_data[1:,1]+1/3*(planform_data[1:,1]-planform_data[:-1,1])**2) )
            # print(S_ref,c_ref,b_ref)
            self.optvarval[0] = S_ref
            self.optvarval[1] = c_ref
            self.optvarval[2] = b_ref