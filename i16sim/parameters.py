# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 12:52:09 2021
@author: axw86756

All hard typed constants in the emulator code
"""
from math import pi


#scannable identifiers. 
simple_scannables=['wait','collision','animate','zp','dettrans','base_y','base_z'] #no movement
renamed={
        'gam': 'nu', 'gamma': 'nu', 'kgam': 'nu',
        'kth': 'ktheta',
        'kmu': 'mu',
        'kdelta': 'delta',
        'sixcircle': 'sixc',
        'energy':'en',
        'k_angles':'kang'}
limitsets={
        'mu':[-1,80,-180], #min, max, cut
        'delta':[-1,120,-90],
        'nu':[-1,120,-180],
        'eta':[-22,90,-180],
        'chi':[-90,99,-180],
        'phi':[-90,270,-90],
        'kphi':[-90,270,-90],
        'kappa':[-90,270,-90],
        'ktheta':[-90,212,-90],
        'ktheta-delta':77.5,
        'gamma-mu':-1,
        'sx':[-5,5,None],
        'sy':[-5,5,None],
        'sz':[-50,50,None],
        }
#Needed to initialise as diffcalc core prevents getting pseudo angle ids before UB is set
virtual_angle_keys=['theta', 'ttheta', 'qaz', 'alpha', 'naz', 'tau', 'psi', 'beta', 'betain', 'betaout']

#vector parameters
scattering_vector='scattering vector'
azi_vector='reference azimuthal'
reciprocal_lattice_vectors=['a*','b*','c*']

#emulator identifiers
chi_axis="chi axis"
collision_exceptions=[["delta","detector arm"]]
#collections of objects that touch
intersect_collections=[['Sample environments',['phi']],['Environment',['base']],['nozzles',['detector arm']],['pipe',[]]]

#nexus file paths
motor_names=['mu','delta','gam','eta','chi','phi']
motor_path='entry1/before_scan/diffractometer_sample/'
ub_path='entry1/before_scan/xtlinfo/'
scan_id_path='entry1/entry_identifier'
cell_path='entry1/sample/unit_cell/'
azi_names=['azih','azik','azil']

#blender ids
armature_motors=["kmu","kdelta","kgamma","ktheta","kappa","kphi"]
arm_name='Armature'
target_name="sample coordinates"
offset=[0,0,-pi/2] #rotation between sample and lab frame in rest position
ik_bone_name = "kphi"
# a minimal list of meshes in case automatic detection does not work
mesh_names = ["base","detector arm","mu","delta","gamma","theta","kappa","phi","detector arm back","detector carriage"]


#blender ui initialisation constants
constraints_ui=[['vertical_con','horizontal_con'],['phi_con','psi_con','bisect']] 

#detector arm motor names
detector_motors=['stokes','thp','tthp','mtthp']
