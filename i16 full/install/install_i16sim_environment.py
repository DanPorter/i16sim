"""
If run from Blender's script editor, this script installs the modules and settings 
needed for the i16sim addon.
If this does not work, use the 'install_environment.zip' addon by installing and enabling it
via the 'preferences > add-ons > install' menu
"""

import subprocess
import sys
import os
import shutil
import bpy

packages = ['numpy', 'scipy', 'h5py']
python_path = sys.executable

# install modules
module_path = os.path.join(bpy.utils.user_resource('SCRIPTS'), 'addons', 'modules')

if module_path in sys.path:
    print('Installing packages for Blender in', module_path)

    # enable pip
    subprocess.check_call([python_path, "-m", "ensurepip", ])

    # install packages
    subprocess.check_call([python_path, "-m", "pip", 'install', '--target', module_path] + packages)
    print("Done installing modules")
else:
    raise Exception("Blender does not have a path to its 'modules' folder")

# install settings
this_file = os.path.realpath(__file__)
directory = os.path.dirname(this_file)
settings_file = os.path.join(directory, 'userpref.blend')
config_folder = bpy.utils.user_resource('CONFIG')

if os.path.isfile(settings_file):
    print("Installing user preferences at", config_folder)
    shutil.copy(settings_file, config_folder)
else:
    raise Exception("Settings file not found")

print("----------------------")
print("Finished installation")
print("Please restart Blender")
print("----------------------")
print()
