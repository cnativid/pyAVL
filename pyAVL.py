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
        self.inputlist = ''

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
    
    def load_opt_template(self,plane): # loads an optimization template
        opt_template = open('Planes/{}/{}.avlopt_template'.format(plane,plane)).read() # read the optimization file
        optVars = re.findall(r'\{.*?\}',opt_template) # find all the declared variables

        # optVars = [var.replace('{','').replace('}','').split(',') for var in optVars] # remove brackets in var list
  
        var_dict = {} # create dictionary
        var_index = {}
        var_count = 0
        for index, optVar in enumerate(optVars): # name variables in dictionary
            opt_template = opt_template.replace(optVar,'{{{}}}')
            optVar = optVar.replace('{','').replace('}','').split(',')
            # print(optVar)
            if len(optVar) > 1:
                var_name = optVar[1]
                if var_name in var_dict.keys():
                    var_dict[var_name].append(float(optVar[0]))
                    var_index[var_name].append(int(index))
                else:
                    # print(optVar[0])
                    var_dict[var_name] = [float(optVar[0])]
                    var_index[var_name] = [int(index)]
            else: # if name not declared, give general name
                var_count += 1
                var_name = 'var_{}'.format(var_count)
                var_dict[var_name] = [optVar[0]]
                var_index[var_name] = [int(index)]
            # print('{'+str(index)+'}')

        # rearranges formatting for vector binning

        var_index_flat = [i for var in list(var_index.values()) for i in var]
        # print(var_index_flat)
        opt_template = opt_template.format(*list(np.argsort(var_index_flat))) # do not ask
        # print(np.argsort(var_index_flat))
        # print(opt_template)
        # print(*[item for index in list(var_dict.values()) for item in index])
        self.opt_template = opt_template # stores template
        self.var_dict = var_dict # stores vars within itself

        # print(opt_template)
        # print(np.argsort(var_index_flat))
        # print(var_dict.values())

    def writeOptimize(self,plane): # writes new values into iteration

        # this needs fixing bruhhh
        with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'w') as file:
            file.write(self.opt_template.format(*[i for var in list(self.var_dict.values()) for i in var]))
        # self.updateRefs(plane)
        # with open('Planes/{}/{}.avlopt_iter'.format(plane,plane),'w') as file:
        #     file.write(self.opt_template.format(*self.var_dict.values()))   

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
            self.var_dict['Bref'] = [2*sum(section_lengths)]
            S_ref = sum(section_lengths*(planform_data[:-1,1]+planform_data[1:,1]))
            self.var_dict['Cref'] = [2/S_ref*sum( section_lengths*(planform_data[:-1,1]*planform_data[1:,1]+1/3*(planform_data[1:,1]-planform_data[:-1,1])**2) )]
            self.var_dict['Sref'] = [S_ref]

            # print([section_lengths])
            