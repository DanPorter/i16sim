"""
Reading and setting motor angles in the simulation
"""

import bpy
import i16sim.bl.read_visual_angle as ra
import i16sim.parameters as params
from math import degrees as deg
from math import radians as rad

#constants
arm_name=params.arm_name #"Armature"
motors=params.armature_motors #["kmu","kdelta","kgamma","ktheta","kappa","kphi"]

#returns all the motor angles in radians
def read_motor_angles(degrees=False, arm_name=arm_name, motors=motors):
    """
    

    Parameters
    ----------
    degrees : bool, optional
        if return angles in degrees. The default is False.
    arm_name : str, optional
        armature name. The default is params.arm_name.
    motors : str, optional
        motor bone names. The default is params.armature_motors.

    Returns
    -------
    angles : list [kmu:float, kdelta:float, kgamma:float, ktheta:float, kappa:float, kphi:float]
        rotations of each motor bone.
        
    example:
        print(read_motor_angles(degrees=True))
    """
    angles = {}
    for motor in motors:
        vis_m = ra.visual_matrix (motor)
        rot_y = ra.rotation_from_m (vis_m).y
        if degrees:
            angles[motor] = deg(rot_y)
        else:
            angles[motor] = rot_y

    return angles

def set_motor_angles(list, degrees=False, arm_name=arm_name, motors=motors):
    """
    

    Parameters
    ----------
    list : list [kmu:float, kdelta:float, kgamma:float, ktheta:float, kappa:float, kphi:float]
        rotations of each motor bone.
    degrees : bool, optional
        if given in degrees. The default is False.
    arm_name : str, optional
        armature name. The default is params.arm_name.
    motors : str, optional
        motor bone names. The default is params.armature_motors.

    Returns
    -------
    None.
    
    example:
        set_motor_angles([4,5,6,3,2,1],degrees=True)
    """
    #shorthand
    Arm=bpy.data.objects[arm_name]
    
    if degrees:
        list = [rad(float(x)) for x in list]
    
    for i,angle in enumerate(list):
        Arm.pose.bones[motors[i]].rotation_euler[1]=float(angle)

    
#print(read_motor_angles(degrees=True))
#set_motor_angles([0,0,0,0,0,0],degrees=True)
#set_motor_angles([4,5,6,3,2,1],degrees=True)
#print(read_motor_angles(degrees=True))