========================================================================
i16sim readme
========================================================================
Simulation package for the I16 6-circle kappa diffractometer at Diamond Light Source Ltd

Implements `diffcalc <https://github.com/DiamondLightSource/diffcalc>`_ functionality in  `Blender <https://www.blender.org/>`_ and uses it to animate a model of the  `diffractometer <https://www.diamond.ac.uk/Instruments/Magnetic-Materials/I16/layout.html>`_.

If used for your research, please credit Aurys Silinga.

.. image:: https://github.com/DanPorter/i16sim/blob/efb6e1131af703a32e5d307d10f5f57c4fa213d6/i16sim.PNG
   :width: 600pt

.. contents::

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
#. Install `Blender <https://www.blender.org/download/>`_ 2.93.1 or newer.
#. Download ``i16sim full.zip`` from GitHub and extract.
#. Open ``diffractometerXX.blend`` in Blender.
#. Bring up the terminal so script output can be viewed. On Windows, open it via the menu ``Window > Toggle System Console``. On Linux, it should already be open in the background.
#. Open ``./i16sim full/install/install_i16sim_environment.py`` in Blender's internal script editor.
#. Run the script and wait until it prints 'Installation finished' in the terminal.
#. Restart Blender.
#. Navigate via the menu to ``Edit > Preferences > Add-ons``.
#. Install the ``./i16sim full/install/i16sim.zip`` addon and enable it.
#. To access diffcalc commands in the console, run ``from i16sim.commands import *``.

Troubleshooting
----------------------
If steps 5-7 do not work, try installing the ``./i16sim full/install/install_environment.zip`` addon. Enable it via the menu. When it finishes executing and is fully enabled, disable it. Installing this addon forces Blender to create a folder it can write to and installs all necessary modules to that folder.

If neither of the above methods worked, you need to manually install the python packages ``numpy``, ``scipy``, and ``h5py`` in a directory that Blender's internal python environment has a path to. Also, copy ``./i16sim full/install/userpref.blend`` to Blender's config folder.


Using the Features
====================
Starting the simulation
---------------------------
Enable the ``i16sim`` addon and open up the i16sim tab in the top right corner of the user interface.

Run ``from i16sim.commands import *`` in the console and at the start of every script


At the beamline
---------------------------
In GDA run the command ``simbl(hkl, [k,h,l])``. It is an extension of the usual ``sim()`` command
that also writes the position the diffractometer would go to into a file.

Start the simulation by running the script on the desktop of 'i16user' and press the ``import from file`` 
button to display the diffractometer state you saved with the ``simbl()`` command. This also checks for collisions.


Each feature
-------------------
- Collision testing
    Press ``Check for collisions`` button or run ``intersect()`` command.
    If collisions are detected, highlights colliding objects and returns a list of colliding meshes. 
    Collisions are only tested for meshes that are visible in 3D view. Hidden meshes will not be tested.

- User interface for visualisation of (pseudo-)motor rotations
    Move the sliders in the UI, run ``pos(...)`` commands, or unhide axes of rotation by clicking the 'eye' icon in the outliner.
    The simulation moves in real-time.
    
- Crystal calculations and movements in hkl space via diffcalc commands
    See examples folder, `diffcalc <https://github.com/DiamondLightSource/diffcalc>`_ documentation, `diffcalc-core <https://github.com/DiamondLightSource/diffcalc-core>`_ documentation, commands section below, or import nexus data and GDA state files.
    All calculations present in diffcalc are possible, but some can require accessing internal diffcalc-core objects.
    
- Console and script editor for testing experiment scripts
    Start each script with the command
    ``enable_lm(True)``.
    The scripting environment at the beamline detects syntax errors but cannot predict runtime errors, such as moving the diffractometer to a forbidden position.
    If limits are enabled, all diffcalc commands should throw the same errors as in GDA. If you wish to show diffractometer movements while the script is running, 
    you can pass the ``animate`` parmeter to ``scan`` functions. Also, to show all available scannables run ``pos()`` without parameters, and to move a scannable 
    run ``pos(scannable, value)``.
    
- Reading nexus data or GDA state files to show diffractometer state during experiment
    Select the file with the ``file`` widget in the UI and press the ``import from file`` button.
    If the data is present in a file, importing it sets position, diffcalc constraints, crystal lattice, UB matrix, azimuthal reference, and energy. 
    Then it tests for collisions.
    
- Visualisation of reciprocal lattice vectors and azimuthal reference in the laboratory coordinate system
    Unhide reciprocal vectors by clicking the 'eye' icon in the outliner. Reciprocal vectors are shown if a UB matrix is set.

- Perspective view from beamline cameras or any point in space
    Select the camera in the UI 'cameras' tab and click the ``Toggle the camera view`` button.


Commands
====================
Orientation Commands
--------------------

+-----------------------------+---------------------------------------------------+
| **STATE**                                                                       |
+-----------------------------+---------------------------------------------------+
| **-- newub** ({'name'})     | start a new ub calculation, name                  |
+-----------------------------+---------------------------------------------------+
| **-- loadub** ('name'|num)  | load an existing ub calculation                   |
+-----------------------------+---------------------------------------------------+
| **-- lastub** ()            | load the last used ub calculation                 |
+-----------------------------+---------------------------------------------------+
| **-- listub** ()            | list the ub calculations available to load        |
+-----------------------------+---------------------------------------------------+
| **LATTICE**                                                                     |
+-----------------------------+---------------------------------------------------+
| **-- setlat** ()            | interactively enter lattice parameters (Angstroms |
|                             | and Deg)                                          |
+-----------------------------+---------------------------------------------------+
| **-- setlat** (name, a)     | assumes cubic                                     |
+-----------------------------+---------------------------------------------------+
| **-- setlat** (name, a, b)  | assumes tetragonal                                |
+-----------------------------+---------------------------------------------------+
| **-- setlat** (name, a, b,  | assumes ortho                                     |
| c)                          |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- setlat** (name, a, b,  | assumes mon/hex with gam not equal to 90          |
| c, gamma)                   |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- setlat** (name, a, b,  | arbitrary                                         |
| c, alpha, beta, gamma)      |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- c2th** ([h, k, l])     | calculate two-theta angle for reflection          |
+-----------------------------+---------------------------------------------------+
| **REFERENCE (SURFACE)**                                                         |
+-----------------------------+---------------------------------------------------+
| **-- setnphi** ({[x, y, z]})| sets or displays n_phi reference                  |
+-----------------------------+---------------------------------------------------+
| **-- setnhkl** ({[h, k, l]})| sets or displays n_hkl reference                  |
+-----------------------------+---------------------------------------------------+
| **REFLECTIONS**                                                                 |
+-----------------------------+---------------------------------------------------+
| **-- showref** ()           | shows full reflection list                        |
+-----------------------------+---------------------------------------------------+
| **-- addref**  ()           | add reflection interactively                      |
+-----------------------------+---------------------------------------------------+
| **-- addref** ([h, k, l],   | add reflection with current position and energy   |
| {'tag'})                    |                                                   |
+-----------------------------+---------------------------------------------------+
| **CRYSTAL ORIENTATIONS**                                                        |
+-----------------------------+---------------------------------------------------+
| **-- showorient** ()        | shows full list of crystal orientations           |
+-----------------------------+---------------------------------------------------+
| **-- addorient** ()         | add crystal orientation interactively             |
+-----------------------------+---------------------------------------------------+
| **-- addorient** ([h, k, l],| add crystal orientation in laboratory frame       |
| [x y z], {'tag'})           |                                                   |
+-----------------------------+---------------------------------------------------+
| **UB MATRIX**                                                                   |
+-----------------------------+---------------------------------------------------+
| **-- checkub** ()           | show calculated and entered hkl values for        |
|                             | reflections                                       |
+-----------------------------+---------------------------------------------------+
| **-- calcub**               | (re)calculate u matrix from ref1 and ref2         |
| (num1|'tag1', num2|'tag2')  |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- trialub** ()           | (re)calculate u matrix from ref1 only (check      |
|                             | carefully)                                        |
+-----------------------------+---------------------------------------------------+

Motion Commands
---------------

+-----------------------------+---------------------------------------------------+
| **CONSTRAINTS**                                                                 |
+-----------------------------+---------------------------------------------------+
| **-- con** ()               | list available constraints and values             |
+-----------------------------+---------------------------------------------------+
| **-- con** (<name>, {val})  | constrains and optionally sets one constraint     |
+-----------------------------+---------------------------------------------------+
| **-- con** (<name>,{val},   | clears and then fully constrains                  |
| <name>,{val}, <name>,{val}) |                                                   |
+-----------------------------+---------------------------------------------------+
| **HKL**                                                                         |
+-----------------------------+---------------------------------------------------+
| **-- allhkl** ([h, k, l])   | print all hkl solutions ignoring limits           |
+-----------------------------+---------------------------------------------------+
| **HARDWARE**                                                                    |
+-----------------------------+---------------------------------------------------+
| **-- showlm** ()            | show diffcalc limits and cuts                     |
+-----------------------------+---------------------------------------------------+
| **-- enable_lm** (bool)     | enable or disable all limits                      |
+-----------------------------+---------------------------------------------------+
| **MOTION**                                                                      |
+-----------------------------+---------------------------------------------------+
| **-- sim** (scn, val)       | simulates moving scannable (hkl or sixc)          |
+-----------------------------+---------------------------------------------------+
| **-- sixc** ()              | get Eulerian position                             |
+-----------------------------+---------------------------------------------------+
| **-- pos** (sixc [phi, chi, | move to Eularian position(None holds an axis      |
| eta, mu, delta, gam]        | still)                                            |
+-----------------------------+---------------------------------------------------+
| **-- sim** (sixc, [phi, chi,| simulate move to Eulerian position sixc           |
| eta, mu, delta, gam])       |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- hkl** ()               | get hkl position                                  |
+-----------------------------+---------------------------------------------------+
| **-- pos** (hkl, [h, k, l]) | move to hkl position                              |
+-----------------------------+---------------------------------------------------+
| **-- pos** ({h  |k | l},    | move h, k or l to val                             |
| val)                        |                                                   |
+-----------------------------+---------------------------------------------------+
| **-- sim** (hkl, [h, k, l]) | simulate move to hkl position                     |
+-----------------------------+---------------------------------------------------+



