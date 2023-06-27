"""
Blender Addon: i16sim
Simulation package for the I16 6-circle kappa diffractometer at Diamond Light Source Ltd.

commands:
    from i16sim.commands import * to enable the diffcalc namespace

parameters:
    All hard typed constants in the emulator code

diffcalc_emulator:
    The diffcalc emulator that brings all the modules together. 
    It moves the simulation in Blender and provides commands that mimic diffcalc in GDA. 

For more info, see: https://github.com/DanPorter/i16sim
Documentation: https://i16sim.readthedocs.io/

Installation of Addon:
 - In Blender, open Preferences (Menu > Edit > Preferences...)
 - In the Add-ons tab, click Install..
 - Select file : i16full/install/i16sim.zip > Click install
 - Ensure the i16 simulation Addon is selected.

Update instructions:
Changes to i16sim package should be included in the i16full/install/i16sim.zip file.
 - In Blender, remove i16 simulation Addon
 - Re-install Addon from i16full/install/i16sim.zip

Version: 1.1
Date: 27 June 2023

By Aurys Silinga & Dan Porter
Beamline I16
Diamond Light Source Ltd.
2021
"""

bl_info = {
    'name': 'i16 simulation',
    'author': 'Aurys Silinga and Diamond Light Source Ltd. - Scientific Software',
    'location': 'View3D > UI panel',
    'category': '3D View',
    "doc_url": 'https://github.com/DanPorter/i16sim',
    "version": (1, 1),
    "blender": (2, 93, 1),
    }
    
import i16sim.bl.ui as ui
import i16sim.bl.no_render_animate as animate


def register():
    ui.register()
    animate.register()


def unregister():
    ui.unregister()
    animate.unregister()

