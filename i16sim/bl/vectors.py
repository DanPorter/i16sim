"""
Functions for setting reciprocal lattice vectors, 
showing the scattering vector q = k_f - k_i,
and rotating vectors in either sample or lab frames.
"""

from i16sim.diffcalc.hkl.geometry import get_q_phi
from i16sim.diffcalc.ub.calc import ReferenceVector
from i16sim.diffcalc.hkl.geometry import Position
import i16sim.parameters as params
import bpy
import numpy as np


#IDs
scattering_vector=params.scattering_vector
reciprocal_lattice_vectors=params.reciprocal_lattice_vectors


def rotate_vector(name,vector,scale=1,small=10**(-10)):
    """roatates a vector in the lab frame
    

    Parameters
    ----------
    name : str
        vector object id.
    vector : [float,float,float]
        a vector in the lab frame.
    scale : float, optional
        vector mesh scale. The default is 1.
    small : float, optional
        numerical error threshold. The default is 10**(-10).

    Returns
    -------
    None.

    """
    vector=list(vector)
    arrow=bpy.data.objects[name]
    for i in range(len(vector)):
        if abs(vector[i])<small:
            vector[i]=0
    #print(vector)
    xrot=np.arctan2(-vector[1],np.sqrt(vector[2]**2+vector[0]**2))
    yrot=np.arctan2(vector[0],vector[2])
    arrow.rotation_euler[0]=xrot
    arrow.rotation_euler[1]=yrot
    arrow.scale[2]=scale
    #print(xrot,yrot)
    
#for rest position in phi frame
def phi_to_lab (vector):
    """convert between sample and lab frame vectors
    

    Parameters
    ----------
    vector : [float,float,float]
        a vector in the sample (phi) frame.

    Returns
    -------
    vector : [float,float,float]
        a vector in the lab frame.

    """
    return (vector[2],vector[0],vector[1])

def set_q(position,name=scattering_vector):
    """sets the scattering vector to the correct position and scale in units 2*pi/wavelength
    

    Parameters
    ----------
    position : Position
        eulerian rotations in a diffcalc Position object
    name : str, optional
        scattering vector object id in Blender. The default is scattering_vector.

    Returns
    -------
    None.

    """
    q=get_q_phi(position)
    #print('q',q,position.asdict)
    rotate_vector(name,phi_to_lab(q),scale=np.linalg.norm(q))
    #rotate_vector(name,q,scale=np.linalg.norm(q))

def set_reciprocal_lattice(UB, wl=None,rvector_names=reciprocal_lattice_vectors):
    """Finds reciprocal lattice vectors and displays them in correct positions in the lab frame. 
    Scaled to units in units 2*pi/wavelength
    

    Parameters
    ----------
    UB : numpy matrix (3,3)
        UB matrix.
    wl : float, optional
        wavelength. The default is None.
    rvector_names : [str,str,str], optional
        reciprocal vector mesh ids in Blender. The default is params.reciprocal_lattice_vectors.

    Returns
    -------
    None.

    """
    #rv=ReferenceVector(None,True)
    rvectors=[[1,0,0],[0,1,0,],[0,0,1]]
    #labvectors=[]
    for i,vector in enumerate(rvectors):
        vector=np.array(vector,ndmin=2).transpose()
        vector_phi=UB @ vector
        
        if wl==None:
            scale=0.5
        else:
            scale=np.linalg.norm(vector_phi)*wl/(2*np.pi)
        
        #print("q",vector_phi,scale)
        rotate_vector(rvector_names[i],phi_to_lab(vector_phi),scale=scale)
        
def set_vector(name,vector):
    """sets a vector in the sample (phi) frame
    

    Parameters
    ----------
    name : str
        vector object id in Blender.
    vector : [float,float,float]
        a vector in the phi (sample) frame.

    Returns
    -------
    None.

    """
    if vector is None:
        scale=0
        vector=[0]*3
    else:
        scale=1
    rotate_vector(name, phi_to_lab(vector), scale=scale)
    
#rotate_vector('arrow',[float('inf'),0,0])

#rotate_vector('arrow', phi_to_lab([0,1,0]))
#print("start")
#pos=Position(0,10,0,0,90,0)
#set_q(pos)
#print(np.arctan2(-0.78,2))
