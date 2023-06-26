bl_info = {
    "name": "i16sim UI",
    "blender": (2, 93, 1),
    "category": '3D View',
}


"""
Created on Mon Aug  9 16:16:47 2021
The i16sim UI in Blender
"""

#import importlib
import bpy
import pathlib
import math
import i16sim.diffcalc_emulator as dc_module
import i16sim.util.eulerian_conversion as etok
import i16sim.parameters as params
#from bpy.app.handlers import persistent
#import numpy as np
import traceback
#import warnings
#import sys
#import os
    



#operators
Operator = bpy.types.Operator

class I16_OT_ui_update(Operator):
    bl_idname = 'i16.ui_update'
    bl_description = 'Updates UI to match motor angles in diffcalc'
    bl_label = 'Update UI'
    bl_options = {"REGISTER", "UNDO"}
        
    def execute(self,context):
        dc=context.scene.diffractometer
        motors=list(dc.position.asdict.keys())
        angles=list(dc.position.asdict.values())
        
        for i in range(len(motors)):
            context.scene.i16_angles[motors[i]]=math.radians(angles[i])
            
        setattr(context.scene.i16_angles,motors[0],math.radians(angles[0]))#force update    
        return {'FINISHED'}

class I16_OT_import_file(Operator):
    bl_idname = 'i16.import_file'
    bl_description = "Read diffractometer state from '.i16sim.txt' or '.nxs file'. Then apply the state and check for collisions"
    bl_label = 'Import from file'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self,context):

        file=pathlib.Path(bpy.path.abspath(context.scene.import_file))
        dc=context.scene.diffractometer
        
        dc.loadub(str(file))
        self.report({'OPERATOR'}, "Reading "+str(file))
        intersections=context.scene.diffractometer.intersect()
        
        if intersections==[]:
            self.report({'INFO'}, "No collisions")  
        else:
            self.report({'ERROR'}, "Intersectinos between: "+str(intersections))  
            
        return {'FINISHED'}
    
class I16_OT_intersect(Operator):
    bl_idname = 'i16.intersect'
    bl_description = 'Check if any meshes intersect and highlight ones that do'
    bl_label = 'Check for collisions'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self,context):
        intersections=context.scene.diffractometer.intersect()
        
        if intersections==[]:
            self.report({'INFO'}, "No collisions")  
        else:
            self.report({'ERROR'}, "Intersectinos between: "+str(intersections))    
                
        return {'FINISHED'}
        




#shorthands
Panel=bpy.types.Panel

class View3DPanel_i16sim:
    """Parent UI panel"""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "i16sim"


class VIEW3D_PT_i16_top(View3DPanel_i16sim,Panel):
    """The top most UI panel"""
    bl_label = "I16 Simulation"
    
    def draw(self, context):
        layout = self.layout

        layout.operator("i16.intersect",icon="MOD_PHYSICS")
        layout.separator()
        
        col=layout.column()

        col.operator('i16.import_file',icon='IMPORT')
        
        col.prop(context.scene,'import_file')


class I16_angles(bpy.types.PropertyGroup):
    """
    A property group that stores all custom properties used in the Blender UI.
    """
    def update_ui(self,context):
        """Updates all the slider values and booleans in the UI.
        Triggers when something moves"""
        dc=context.scene.diffractometer
        motors=dc.position.asdict
        k_motors=dc.k_angles
        
        #update eulerian angles
        for name in motors:
            self[name]=math.radians(motors[name])
        #update real motors
        for name in k_motors:
            self[name]=math.radians(k_motors[name])
        
        #update hkl values
        if not (dc.ubcalc.UB is None):
            try:
                hkl=dc.scannables['hkl']()
                if hkl[0]==None:
                    hkl=[0,0,0]
                    print('hkl not found')
            except Exception as e:
                traceback.print_exc()
                print(e)
                print('hkl not found and caused error')
                hkl=[0,0,0]
        else:
            hkl=[0,0,0]
        
        for i in range(3):
            self['hkl'[i]]=hkl[i]
            
        #update constraints  
        constraint_modes,constraint_list=context.scene.constraints_ui
        all_cons=constraint_modes+constraint_list
            
        for key in all_cons:
            self[key]=False

        cons=dc.get_constraints()
        if (cons.mu==0 and cons.nu==0):
            self['vertical_con']=True
        elif (cons.eta==0 and cons.delta==0):
            self['horizontal_con']=True
        
        if cons.phi==0:
            self['phi_con']=True
        elif cons.psi==0:
            self['psi_con']=True
        elif cons.bisect==True:
            self['bisect']=True
        
        #update limits
        self['limits']=dc.limits
        
    def update_e(self,context):
        """When eulerian angle sliders are dragged"""
        dc=context.scene.diffractometer
        motors=list(dc.position.asdict.keys())
        new_e=[]
        #print(motors)
        #print(context.scene.i16_angles.keys())
        for name in motors:
            new_e.append(math.degrees(context.scene.i16_angles.get(name)))
        if new_e[4]>=100:
            new_e[4]=100-10**(-4)
        elif new_e[4]<=-100:
            new_e[4]=-(100-10**(-4))
        
        if self.ik_on==False: 
            #old_pos=dc.position.astuple
            try:
                dc.moveto(new_e,use_limits=True,UI_call=False)
            except Exception as e:
                print(e)
                #dc.moveto(old_pos,use_limits=False,UI_call=False)
        
            self.update_ui(context)
            
    def update_k(self,context):
        """When real motor sliders are dragged"""
        dc=context.scene.diffractometer
        motor_names=list(dc.k_angles.keys())
        
        new_k=[]
        for name in motor_names:
            new_k.append(math.degrees(context.scene.i16_angles.get(name)))
        
        if self.ik_on==False: 
            #old_pos=dc.position.astuple
            try:
                dc.moveto([*dc.position.astuple[:3],*etok.KtoE(new_k)],use_limits=True,UI_call=False)
            except Exception as e:
                print(e)
                #print('kang ui error')
                #dc.moveto(old_pos,use_limits=False,UI_call=False)
        #dc.moveto([*dc.position.astuple[:3],*etok.KtoE(new_k)],use_limits=False,UI_call=False)
        #print(self.k_angles)   
            self.update_ui(context)
    
    pi=math.pi
    phi: bpy.props.FloatProperty(
        name="phi",
        description=("Rotation from the 0 position of phi"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )
    chi: bpy.props.FloatProperty(
        name="chi",
        description=("Rotation from the 0 position of chi"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )
    eta: bpy.props.FloatProperty(
        name="eta",
        description=("Rotation from the 0 position of eta"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )
    delta: bpy.props.FloatProperty(
        name="delta",
        description=("Rotation from the 0 position of delta"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )

    nu: bpy.props.FloatProperty(
        name="gamma",
        description=("Rotation from the 0 position of gamma"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )
      
    mu: bpy.props.FloatProperty(
        name="mu",
        description=("Rotation from the 0 position of mu"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_e
    )
    
    kphi: bpy.props.FloatProperty(
        name="kphi",
        description=("Rotation from the 0 position of kphi"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_k
    )
    kappa: bpy.props.FloatProperty(
        name="kappa",
        description=("Rotation from the 0 position of kappa"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_k
    )
    ktheta: bpy.props.FloatProperty(
        name="ktheta",
        description=("Rotation from the 0 position of ktheta"),
        soft_min=-pi, soft_max=pi,
        default=0,
        subtype='ANGLE',
        unit='ROTATION',
        update=update_k
    )
        
    def ik_callback(self,context):
        """Continuous updating of disabled sliders"""
        dc=context.scene.diffractometer
        motors=list(dc.position.asdict.keys())
        angles=dc.read_visual_pos()
        k_motors=list(dc.k_angles.keys())
        k_angles=etok.EtoK(angles[3:])
        #print("active")
        
        for i in range(len(motors)):
            context.scene.i16_angles[motors[i]]=math.radians(angles[i])
        for i in range(len(k_motors)):
            context.scene.i16_angles[k_motors[i]]=math.radians(k_angles[i])
        
        if not (dc.ubcalc.UB is None):
            try:
                hkl=dc.hklcalc.get_hkl(dc.init_position_ob(angles), dc.wl)
                if hkl[0]==None:
                    hkl=[0,0,0]
                    print('hkl not found')
            except Exception as e:
                traceback.print_exc()
                print(e)
                print('hkl not found and caused error')
                hkl=[0,0,0]
        else:
            hkl=[0,0,0]
        
        for i in range(3):
            self['hkl'[i]]=hkl[i]
        
        
    
    def update_ik(self,context):
        """If boolean box is ticked"""
        dc=context.scene.diffractometer
        if (self.ik_on):
            bpy.types.Scene.i16_handler=bpy.types.SpaceView3D.draw_handler_add(self.ik_callback,
              (context,),
              'WINDOW',
              'POST_PIXEL')
            context.scene.objects['sample coordinates'].hide_set(False)
            context.scene.objects['scattering vector'].hide_set(True)
            dc.ik()
            context.scene.objects['sample coordinates'].select_set(True)
        else:
            bpy.types.SpaceView3D.draw_handler_remove(bpy.types.Scene.i16_handler,'WINDOW')
            dc.fk()
            context.scene.objects['scattering vector'].hide_set(False)
    
    ik_on: bpy.props.BoolProperty(
        name="IK enabled",
        description=("If inverse kinematics are enabled"),
        default=False,
        update=update_ik
    
    )
    
    def update_hkl(self,context):
        """If hkl sliders are dragged"""
        dc=context.scene.diffractometer
        hkl=[self.h,self.k,self.l]
        pos_old=dc.position.astuple
        if ((dc.ubcalc.UB is not None) and dc.cons.is_fully_constrained() and self.ik_on==False):
            
            try:
                pos_now,va=dc.pos_from_hkl(hkl)
                pos_now=pos_now.astuple
                #print("here1",pos_now)
                if pos_now[0]==None:
                    raise Exception("No solution to hkl found")
            except Exception as e:
                #traceback.print_exc()
                print(e)
                pos_now=pos_old
                #print("here2",pos_now)
        else:
            pos_now=pos_old
            #print("here3",pos_now)
            
        #print("here4",pos_now)
        if self.ik_on==False: 
            #print("here5",pos_now)
            try:
                dc.moveto(pos_now,use_limits=True,UI_call=False)
            except Exception as e:
                print(e)
                #print(pos_now,pos_old)
                dc.moveto(pos_old,use_limits=False,UI_call=False)
                
            self.update_ui(context)
    
    h: bpy.props.FloatProperty(
        name="h",
        description=("Scattering vector Q = h a* + k b* + l c*"),
        soft_min=-20, soft_max=20,
        default=0,
        update=update_hkl
    )
    
    k: bpy.props.FloatProperty(
        name="k",
        description=("Scattering vector Q = h a* + k b* + l c*"),
        soft_min=-20, soft_max=20,
        default=0,
        update=update_hkl
    )
    
    l: bpy.props.FloatProperty(
        name="l",
        description=("Scattering vector Q = h a* + k b* + l c*"),
        soft_min=-20, soft_max=20,
        default=0,
        update=update_hkl
    )
    
    #constraints
    def update_con(self,context,key):
        """If boolean markers are pressed"""
        dc=context.scene.diffractometer
        constraint_modes,constraint_list=context.scene.constraints_ui
        
        mutually_exclusive_list=[] 
        if key in constraint_modes:
            mutually_exclusive_list=constraint_modes
        elif key in constraint_list:
            mutually_exclusive_list=constraint_list
            
        for con in mutually_exclusive_list:
            self[con]=False
        self[key]=True
        
        #find the contraint set
        cons_list=[]
        cons_names=constraint_modes+constraint_list
        for key in (cons_names):
            if self[key]==True:
                if key=='horizontal_con':
                    cons_list.extend(['eta',0,'delta',0])
                elif key=='vertical_con':
                    cons_list.extend(['mu',0,'nu',0])
                elif key=='phi_con':
                    cons_list.extend(['phi',0])
                elif key=='psi_con':
                    cons_list.extend(['psi',0])
                elif key=='bisect':
                    cons_list.extend(['bisect',True])
        dc.con(*cons_list)

    def update_hor(self,context):
        self.update_con(context,'horizontal_con')
    def update_ver(self,context):
        self.update_con(context,'vertical_con')
    def update_phi(self,context):
        self.update_con(context,'phi_con')
    def update_psi(self,context):
        self.update_con(context,'psi_con')
    def update_bisect(self,context):
        self.update_con(context,'bisect')
    
    
    horizontal_con: bpy.props.BoolProperty(
        name="horizontal four-circle",
        description=("eta = delta = 0. Enable diffcalc constraints for horizontal operation"),
        default=False,
        update=update_hor
    )
    
    vertical_con: bpy.props.BoolProperty(
        name="vertical four-circle",
        description=("mu = gam = 0. Enable diffcalc constraints for vertical operation"),
        default=False,
        update=update_ver
    )
    
    phi_con: bpy.props.BoolProperty(
        name="phi = 0",
        description=("phi is constrained to 0 when calculating hkl movements"),
        default=False,
        update=update_phi
    )
    
    psi_con: bpy.props.BoolProperty(
        name="psi = 0",
        description=("azimuthal rotation about scattering vector of reference vector (from scattering plane)"),
        default=False,
        update=update_psi
    )
    
    bisect: bpy.props.BoolProperty(
        name="bisect",
        description=("bisecting mode with scattering vector in chi-circle plane"),
        default=False,
        update=update_bisect
    )
    
    
    def update_limits(self,context):
        """If boolean box is ticked"""
        dc=context.scene.diffractometer
        dc.limits = self['limits']
        
        if self.limits:
            #print('limit check1')
            if not dc.inlimits():
                #print('limit check2')
                dc.update_pos(0)
        

    
    limits: bpy.props.BoolProperty(
        name="Use safety limits",
        description=("Check every movement against current set of limits. To see limits call showlm()"),
        default=False,
        update=update_limits
    )
    
    
    
    

class VIEW3D_PT_i16_motors(View3DPanel_i16sim,Panel):
    bl_label = "Motors"

    #def upd(self,context):
    #    print(self.eta)
    """
    eta: bpy.props.FloatProperty(name='Eta', description='kkk', default=0.0, soft_min=-180, soft_max=180)
    ktheta: bpy.props.FloatProperty(name='ktheta', description='kkk', default=50, soft_min=-180, soft_max=180)
    """
    #motors=[]
    def draw(self, context):
        dc=context.scene.diffractometer
        motors=list(dc.position.asdict.keys())
        motors=[*motors[3:][::-1],*motors[:3]] #intuitive order
        layout = self.layout
        col=layout.column(align=True)
        
        #print("draw",context.scene.i16_angles.keys())
        for motor in motors:
            col.prop(context.scene.i16_angles,motor,slider=True,emboss= not context.scene.i16_angles.ik_on)
            

        
        
class VIEW3D_PT_i16_real_motors(View3DPanel_i16sim,Panel):
    bl_label = "Real motors"
    bl_parent_id = "VIEW3D_PT_i16_motors"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):            
        dc=context.scene.diffractometer
        k_motors=list(dc.k_angles.keys())
        #k_angles=list(dc.k_angles.values())
        layout = self.layout
        col=layout.column(align=True)
        for motor in k_motors[::-1]:
            col.prop(context.scene.i16_angles,motor,slider=True,emboss= not context.scene.i16_angles.ik_on)
    
class VIEW3D_PT_i16_hkl(View3DPanel_i16sim,Panel):
    bl_label = "Miller Indices"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):            
        dc=context.scene.diffractometer
        layout = self.layout
        col=layout.column(align=True)
        
        if (dc.ubcalc.UB is None):
            col.label(text="UB matrix not defined")
        else:
            can_move=(
            dc.cons.is_fully_constrained() and 
            context.scene.i16_angles.ik_on==False and 
            (dc.ubcalc.crystal is not None)
            )
            
            for index in 'hkl':
                col.prop(context.scene.i16_angles,index,slider=True,emboss=can_move)
                
        if (dc.ubcalc.crystal is None):
            col.label(text="Real lattice not defined")
        if (not dc.cons.is_fully_constrained()):
            col.label(text="Diffcalc not constrained")
            
            
class VIEW3D_PT_i16_con(View3DPanel_i16sim,Panel):
    bl_label = "Diffcalc constraints"
    bl_parent_id = "VIEW3D_PT_i16_hkl"
    bl_options = {'DEFAULT_CLOSED'}
    
    
    def draw(self, context):            
        #dc=context.scene.diffractometer
        constraint_modes,constraint_list=context.scene.constraints_ui
        layout = self.layout
        col=layout.column(align=True)
        
        col.label(text='modes:')
        
        for mode in constraint_modes:
            col.prop(context.scene.i16_angles,mode,toggle=1)
        
        col.separator()
        col.label(text='third constraint:')
        
        for con in constraint_list:
            col.prop(context.scene.i16_angles,con,toggle=1)
            
        col.separator()
        col.separator()
        col.label(text='optional constraints:')
        col.prop(context.scene.i16_angles,'limits')


class VIEW3D_PT_i16_ik(View3DPanel_i16sim,Panel):
    bl_label = "Inverse Kinematics"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        col=layout.column(align=True)
        col.prop(context.scene.i16_angles,'ik_on')
        if (context.scene.i16_angles.ik_on):
            target_name="sample coordinates"
            col.prop(context.scene.objects[target_name],'rotation_euler',text="Sample Rotation:")
            col.prop(context.scene.objects['Armature'].pose.bones['kmu'],'use_ik_limit_y',text='Lock mu at 0',slider=True)
            
            
class VIEW3D_PT_i16_cameras(View3DPanel_i16sim,Panel):
    bl_label = "Beamline Cameras"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        col=layout.column(align=True)
        col.label(text='select camera:')
        col.prop(context.scene,'camera',text='')

            
            
#check collision, load from gda



classlist=[VIEW3D_PT_i16_top, 
           VIEW3D_PT_i16_motors, 
           VIEW3D_PT_i16_real_motors, 
           VIEW3D_PT_i16_hkl,
           VIEW3D_PT_i16_con,
           VIEW3D_PT_i16_ik,
           I16_OT_import_file,
           I16_OT_intersect,
           I16_OT_ui_update,
           VIEW3D_PT_i16_cameras]

#@persistent
#def load_handler(dummy):


def register():
    #global variables
    bpy.types.Scene.diffractometer=dc_module.dc
    bpy.types.Scene.import_file=bpy.props.StringProperty(
        name='File',
        default='//testfile.txt',
        subtype='FILE_PATH'
    )
    bpy.types.Scene.constraints_ui=params.constraints_ui #[['vertical_con','horizontal_con'],['phi_con','psi_con','bisect']]
    
    #variable collection object
    bpy.utils.register_class(I16_angles)
    bpy.types.Scene.i16_angles=bpy.props.PointerProperty(type=I16_angles)
    
    for cls in classlist:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.diffractometer.ui_call=bpy.ops.i16.ui_update

    
        
def unregister():
    
    #varible collection object
    del bpy.types.Scene.i16_angles
    bpy.utils.unregister_class(I16_angles)
    
    #global variales
    del bpy.types.Scene.constraints_ui
    del bpy.types.Scene.import_file
    del bpy.types.Scene.diffractometer
    
    
    for cls in classlist:
        bpy.utils.unregister_class(cls)

        
if __name__ == "__main__":
    register()
    #unregister()
    pass