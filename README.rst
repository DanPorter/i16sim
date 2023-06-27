========================================================================
i16sim readme
========================================================================
Simulation package for the I16 6-circle kappa diffractometer at Diamond Light Source Ltd.

Implements `diffcalc <https://github.com/DiamondLightSource/diffcalc>`_ functionality in  `Blender <https://www.blender.org/>`_ and uses it to animate a model of the  `diffractometer <https://www.diamond.ac.uk/Instruments/Magnetic-Materials/I16/Beamline-Guide/Beamline-Equipment.html>`_.


:Authors:
    Aurys Silinga,
    Dan Porter
:Beamline: I16
:Facility: Diamond Light Source Ltd
:Version: 1.1
:Date: 26/06/2023

If used for your research, please credit Aurys Silinga.

.. image:: https://github.com/DanPorter/i16sim/blob/efb6e1131af703a32e5d307d10f5f57c4fa213d6/i16sim.PNG?raw=true
   :width: 600pt

Features
=======================

- **3D model of the diffractometer with mesh error < 1 mm**
- **Collision testing**
- **User interface for visualisation of (pseudo-)motor rotations**
- **Crystal calculations and movements in hkl space via diffcalc commands**
- **Console and script editor for testing experiment scripts**
- **Reading nexus data or GDA state files to show diffractometer state during experiment**
- **Visualisation of reciprocal lattice vectors and azimuthal reference in the laboratory coordinate system**
- **Perspective view from beamline cameras or any point in space**

Introduction video
--------------------

You can watch step-by-step guides to installing the package and using the features.
The  `videos <https://github.com/AurysSilinga/i16sim/tree/main/videos>`_ are available on GitHub and on the I16 YouTube channel.

Videos:  `Installation <https://youtu.be/yQji8m3zBZY>`_ and `Introduction <https://youtu.be/80_1f4kFLF0>`_.


Installation
=======================

Download Software
-----------------

 1. Download and install Blender from `www.blender.org <https://www.blender.org/>`_

 2. Download this repository, specifically `i16 full.zip <https://github.com/DanPorter/i16sim/blob/main/i16%20full.zip>`_

 3. Unzip the "i16 full.zip" file into a location of your choosing.

Setup Blender python environment
--------------------------------
This step configure's the internal Blender python environment and installs required packages.

 4. Open the file *i16 full/diffractometer40.blend*

 5. In the Blender script editor, open the file *i16 full/install/install_i16sim_environment.py*

 6. Run the script (using "Run" right-arrow). Check results in Console, should say 'Finished installation'
    (Windows - use h-bars at top left > Window > Toggle console view)
    (Linux - look in terminal used to start Blender)

 7. Restart Blender

Install i16sim plugin
---------------------

 8. Open Preferences (Menu ☰ > Edit > Preferences...)

 9.  In the **Add-ons** tab, click **Install..**

 10. Select file: *i16 full/install/i16sim.zip*

 11. Ensure the **i16 simulation** Add-on is selected.

 12. Installation is complete!


Update i16sim plugin
--------------------

 1. Download new version of `i16full/install/i16sim.zip <https://github.com/DanPorter/i16sim/blob/main/i16%20full/install/i16sim.zip>`_

 2. In Blender, Open Preferences (Menu ☰ > Edit > Preferences...)

 3. Remove old Add-on **i16 simulation** (select and press **remove**)

 4. Install new version from downloaded file.


Documentation
=======================

 |Read the docs|


.. |Read the docs|  image:: https://readthedocs.org/projects/i16sim/badge/?version=latest
   :target: https://i16sim.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Full documentation can be found here:

https://i16sim.readthedocs.io/
