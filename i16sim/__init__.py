bl_info = {
    'name': 'i16 simulation',
    'author': 'Aurys Silinga and Diamond Light Source Ltd. - Scientific Software',
    'location': 'View3D > UI panel',
    'category': '3D View',
    "blender": (2, 93, 1),
    }

"""
commands:
    from i16sim.commands import * to enable the diffcalc namespace

parameters:
    All hard typed constants in the emulator code
    
diffcalc_emulator:
    The diffcalc emulator that brings all the modules together. 
    It moves the simulation in Blender and provides commands that mimic diffcalc in GDA. 

"""
    
import i16sim.bl.ui as ui
import i16sim.bl.no_render_animate as animate


def register():
    ui.register()
    animate.register()


def unregister():
    ui.unregister()
    animate.unregister()

