# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 19:11:43 2021

@author: Aurys Silinga

function for processing nexus files

"""

import h5py
import i16sim.parameters as params

def interpret(filename,
              motor_names=params.motor_names,
              motor_path=params.motor_path,
              ub_path=params.ub_path,
              scan_id_path=params.scan_id_path,
              cell_path=params.cell_path,
              azi_names=params.azi_names
              ):
    """
    in: filename
    out: creates a '.txt' file that i16sim Blender simulation can import
    Takes a nexus file from i16 and extracts the UB matrix and position at the start of the scan.

    N.B. Blender does not ship with h5py installed, so this module might not run in Blender.
    Consider pip installing h5py in the Blender directory or 
    interpreting the files with an external version of Python
    """
    
    h=h5py.File(filename, 'r')
    
    ub=[[0 for j in range(3)] for i in range(3)]
    pos=[0]*6
    lattice=[]
    azi_hkl=[0]*3
    
    #get the pseudomotor rotations before scan
    try:
        for i in range(len(motor_names)):
            pos[i]=h[motor_path+motor_names[i]][()]
    except:
        pos=None
        print("pseudomotor rotations not found")

    
    #copy UB elements 
    try:
        for i in range(3):
            for j in range(3):
                # The indices are (probably) switched in the Nexus files
                ub[i][j]=h[ub_path+'UB'+str(j+1)+str(i+1)][()]
    except:
        ub=None
        print("UB elements not found")
        
    #get energy
    try:
        en=h[motor_path+'en'][()]
    except:
        en=None
        print("energy not found")
        
    #get unit cell
    try:
        lattice_name=h[scan_id_path][()]
        lattice=list(h[cell_path][0])
    except:
        lattice=None
        print("unit cell not found")
        
    #get azimulthal reference
    try:
        for i in range(len(azi_names)):
            azi_hkl[i]=h[motor_path+azi_names[i]][()]
    except:
        azi_hkl=None
        print("azimulthal reference not found")
    
    h.close()
    
    with open (filename+'.i16sim.txt','w') as f:
        
        if ub is not None:
            f.write('ub\n')
            for row in ub:
                for el in row:
                    f.write(str(el)+' ')
                f.write('\n')
        
        if pos is not None:
            f.write('sixc\n')
            for el in pos:
                f.write(str(el)+' ')
            f.write('\n')
        
        if en is not None:
            f.write('en\n')
            f.write(str(en)+'\n')
        
        if lattice is not None:
            f.write('lattice\n')
            f.write(str(int(lattice_name))+'\n')
            for el in lattice:
                f.write(str(el)+' ')
            f.write('\n')
        
        if azi_hkl is not None:
            f.write('azi_hkl\n')
            for el in azi_hkl:
                f.write(str(el)+' ')
            f.write('\n')
        
    print("Interpreting finished")
    
#interpret(r'C:\Unsorted Stuff\Work Files\Blender tests\Diffrac\scripts\892941.nxs')