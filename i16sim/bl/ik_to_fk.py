"""
functinos for enabling and disabling inverse kinematics and saving the visual position
"""

import bpy
import i16sim.bl.read_visual_angle as ra
import i16sim.parameters as params

#constants
arm_name=params.arm_name
bone_name=params.ik_bone_name #"kphi"
motors=params.armature_motors #["kmu","kdelta","kgamma","ktheta","kappa","kphi"]
target_name=params.target_name #"sample coordinates"
offset=params.offset#[0,0,-pi/2] #rotation between sample and lab frame in rest position

#set IK
def set_IK(use_location=False, use_rotation=True, lock_kmu=True, target_name=target_name, bone_name=bone_name, arm_name=arm_name):
    """
    

    Parameters
    ----------
    use_location : bool, optional
        try to reach location of target. The default is False.
    use_rotation : bool, optional
        try to reach rotation of target. The default is True.
    lock_kmu : bool, optional
        removed. The default is True.
    target_name : str, optional
        target name. The default is params.target_name.
    bone_name : str, optional
        id of bone with ik constraint. The default is params.ik_bone_name.
    arm_name : str, optional
        armature name. The default is params.arm_name.

    Returns
    -------
    None.

    """
    #print(target_name,bone_name,arm_name)
    
    #glob_m=ra.global_matrix("kphi")
    #print(glob_m)
    #print(ra.rotation_from_m(glob_m,degrees=True),"This1")
    
    
    #shorthands
    Target=bpy.data.objects[target_name]
    Arm=bpy.data.objects[arm_name]
    
    #enable IK and show Target
    Arm.pose.bones[bone_name].constraints["IK"].weight = 0.01
    Arm.pose.bones[bone_name].constraints["IK"].use_location = use_location
    Arm.pose.bones[bone_name].constraints["IK"].use_rotation = use_rotation
    #Arm.pose.bones["kmu"].use_ik_limit_y = lock_kmu
    Target.hide_viewport = False
    Target.hide_set(False)
    
    #unparent from armature
    Target.modifiers[arm_name].use_vertex_groups = False

    #should set target to match current rotation
    glob_m=ra.global_matrix(bone_name)
    r = ra.rotation_from_m(glob_m,degrees=False)
    Target.rotation_euler=r[:3]
    #print (r)
    
    #Enable object mode to allow manual movement of the Target
    bpy.context.view_layer.objects.active = Target
    bpy.ops.object.mode_set(mode='OBJECT')
    Target.select_set(True)
    #bpy.context.space_data.context = 'OBJECT' # pick object properties tab. 
    #Need full address. might remove when ui available
    
#remove IK
def remove_IK( target_name=target_name, motors=motors, bone_name=bone_name, arm_name=arm_name, offset=offset):
    """
    

    Parameters
    ----------
    target_name : str, optional
        target name. The default is params.target_name.
    motors : [str]*6, optional
        names of motor bones in blender. The default is params.motors.
    bone_name : str, optional
        id of bone with ik constraint. The default is params.ik_bone_name.
    arm_name : str, optional
        armature name. The default is params.arm_name.
    offset : [float,float,float], optional
        Rotation between sample and lab frames in rest position. The default is params.offset.

    Returns
    -------
    None.

    """
    
    #shorthands
    Target=bpy.data.objects[target_name]
    Arm=bpy.data.objects[arm_name]
    
    
    #should save position
    for motor in motors:
        vis_m=ra.visual_matrix(motor)
        rot_y=ra.rotation_from_m(vis_m).y
        #print(rot_y,motor)
        Arm.pose.bones[motor].rotation_euler[1] = rot_y

    
    
    #removes constraint and hides target
    Arm.pose.bones[bone_name].constraints["IK"].use_location = False
    Arm.pose.bones[bone_name].constraints["IK"].use_rotation = False
    #Target.hide_viewport = True
    
    #reparent with appropriate rotation
    Target.modifiers[arm_name].use_vertex_groups = True
    for i in range(len(offset)): 
        Target.rotation_euler[i] = offset[i]

    #go back to general object mode
    #if (Arm.hide_viewport==False or Arm.visible_get()): #if armature visible
    if (Arm.visible_get()): #if armature visible
        bpy.context.view_layer.objects.active = Arm
        bpy.ops.object.mode_set(mode='OBJECT') #force object mode
        bpy.ops.object.select_all(action="DESELECT") #deselect armature 
     
    #return {'FINISHED'}
    
#remove_IK()
#set_IK()
#set_IK(lock_kmu=False)