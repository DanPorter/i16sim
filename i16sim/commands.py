"""
Run 'from i16sim.commands import *' to enable shorthand sytax in your script.

Sets up diffcalc emulator namespace for importing and sets up the simulation.
For example dc.pos(dc.scannables['hkl']) could be called as pos(hkl) after importing this module
"""

import bpy
    
diffractometer=bpy.context.scene.diffractometer
dc=diffractometer
globals().update(diffractometer.get_namespace())
update_pos()