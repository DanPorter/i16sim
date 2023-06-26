"""
Functions for getting visual matrix and extracting bone rotations
blender: (2, 93, 1),

Examples:
    #to get the motor rotation angle, as seen on screen
    vis_m=visual_matrix("kphi")
    print(vis_m)
    print(rotation_from_m(vis_m).y)
    
    #to get bone rotation in lab frame
    glob_m=global_matrix("kphi")
    print(glob_m)
    print(rotation_from_m(glob_m,degrees=True))
"""

import bpy
import numpy as np
import mathutils
from math import degrees as deg

import i16sim.parameters as params


arm_name=params.arm_name

#obtain the visual transform matrix
def visual_matrix(bone_name, arm_name=arm_name):
    """ Return a local transformation matrix that 
    captures the visual transformation including
    IK chain etc
    

    Parameters
    ----------
    bone_name : str
        bone id.
    arm_name : str, optional
        armature name. The default is params.arm_name.

    Returns
    -------
    numpy matrix (3,3)
        matrix describing visual location, rotation, and scale changes of bone.

    """
    armature=bpy.data.objects[arm_name]
    
    pose_bone = armature.pose.bones[bone_name]
    data_bone = armature.data.bones[bone_name]
    
    M_pose = pose_bone.matrix
    M_data = data_bone.matrix_local
    
    #print(M_pose)
    #print(M_data)

    # grab the parent's world pose and rest matrices
    if data_bone.parent:
        M_parent_data = data_bone.parent.matrix_local.copy()
        M_parent_pose = pose_bone.parent.matrix.copy()
    else:
        M_parent_data = mathutils.Matrix()
        M_parent_pose = mathutils.Matrix()

    M1 = M_data.copy()
    M1.invert()

    M2 = M_parent_pose.copy()
    M2.invert()

    visual_matrix = M1 @ M_parent_data @ M2 @ M_pose

    return visual_matrix

#return global position matrix
def global_matrix(bone_name, arm_name=arm_name):
    """Return the global transfromation matrix of a bone
    

    Parameters
    ----------
    bone_name : str
        bone id.
    arm_name : str, optional
        armature name. The default is params.arm_name.

    Returns
    -------
    global_m : numpy matrix (3,3)
        matrix describing global location, rotation, and scale of bone.

    """
    
    #print(bone_name,arm_name)
    armature=bpy.data.objects[arm_name]
    
    pose_bone = armature.pose.bones[bone_name]
    
    global_m = armature.matrix_world @ pose_bone.matrix
    
    return global_m

#get the rotation in radians represented as an euler object from a visual transform matrix
#r.y is the value that is supposed to change upon rotation in radians
def rotation_from_m (vis_m, degrees=False):
    """
    

    Parameters
    ----------
    vis_m : numpy matrix (3,3)
        Transformation matrix.
    degrees : bool, optional
        if output should be in degrees. The default is False.

    Returns
    -------
    r : [x_rot:float, y_rot:float, z_rot:float]
        rotation tuple.

    """
    loc, rot, sca = vis_m.decompose()
    r=rot.to_euler('XYZ')
    
    if degrees:
        for i in range(len(r)):
            r[i]=deg(r[i])

    return (r)


#to get the motor rotation angle, as seen on screen
#vis_m=visual_matrix("kphi")
#print(vis_m)
#print(rotation_from_m(vis_m).y)

#to get bone rotation in lab frame
#glob_m=global_matrix("kphi")
#print(glob_m)
#print(rotation_from_m(glob_m,degrees=True))

