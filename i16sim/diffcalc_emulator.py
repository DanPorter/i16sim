# -*- coding: utf-8 -*-
"""
Created on 19/07/2021

@author: Aurys Silinga

Diffcalc emulator for the Python console in Blender.

bugs and todos:
    
add lattice fixing commands. e.g. get real vectors from UB

add delta offsets. e.g. do do.pil

#documentation
mention what happens if lattice is wrong

implement con command with dynamic parameters. 

intesect and animate parameters for scans. Scans should be able to 
create animations or check for collisions at every point

sphere error of 1 micron

falls asleep crash. 

hkl scan should varify each h,k,l value separately and stop incrementing some 
while others still increase.

Directory problems

"""

from i16sim.diffcalc.hkl.calc import HklCalculation
from i16sim.diffcalc.hkl.constraints import Constraints
from i16sim.diffcalc.hkl.geometry import Position
from i16sim.diffcalc.ub.calc import UBCalculation

from math import degrees, radians, sqrt
import numpy as np
from time import sleep
import traceback
import os

import i16sim.bl.io_angles as motors
import i16sim.util.eulerian_conversion as etok
import i16sim.bl.ik_to_fk as ikfk
from i16sim.bl.intersect_test import is_intersect
import i16sim.bl.vectors as vectors
import i16sim.bl.read_visual_angle as ra
import i16sim.util.scannables as scannables

setrange = scannables.setrange
import i16sim.parameters as params
import i16sim.user.additional_scannables as additional_scannables
import i16sim.user.additional_functions as additional_functions

import bpy


class DiffcalcEmulator:
    """Moves the simulation in Blender and provides commands that mimic diffcalc in GDA"""

    def __init__(self,
                 position=None,  # [mu, delta, gamma, eta, chi, phi]
                 ubcalc=None,
                 cons=None,
                 hklcalc=None,
                 wl=1,
                 k_angles=[0, 0, 0],
                 ubname='test',
                 limits=False,  # if you want to restrict the range of allowed movements
                 collision_test=False,  # if test for collisions every time diffractometer moves
                 verbose=False  # if print location every time diffractometer moves
                 ):

        # internal state
        if ubcalc is None: self.ubcalc = UBCalculation(ubname)  # UB calculation class
        if cons is None: self.cons = Constraints()  # constraint object for hkl calculations. N.B. gamma is nu
        if hklcalc is None: self.hklcalc = HklCalculation(self.ubcalc,
                                                          self.cons)  # hkl calculation object. Initialised after UB and contraints are set.
        self.wl = 1  # wavelength in angstroms
        self.k_angles = {'ktheta': 0, 'kappa': 0, 'kphi': 0}  # real motors
        self.renamed = params.renamed
        self.limitsets = params.limitsets
        self.ui_call = None

        if position is None:
            # self.update_pos() # disabled beacause it cannot access the simulation while this module is being registered
            self.position = Position(0, 0, 0, 0, 0, 0)
        else:
            self.position = Position(*position)  # Eulerian angles

        self.scannables = scannables.base_scannables(self)
        try:
            additional_scs = additional_scannables.get_additional_scannables(self, scannables.Scannable)
            self.scannables.update(additional_scs)
        except:
            traceback.print_exc()
            print("Could not import non-essential scannables")

        try:
            self.composite_limits = scannables.create_composite_limits(self)
        except:
            traceback.print_exc()
            print("Could not import composite limits")

        # blender object identifiers
        self.armature_motors = params.armature_motors
        self.collision_exceptions = params.collision_exceptions

        # boolean modifiers for output
        self.limits = limits  # if you want to restrict the range of allowed movements
        self.collision_test = collision_test  # if test for collisions every time diffractometer moves
        self.verbose = verbose  # if print location every time diffractometer moves
        # if reciprocal lattice vectors and scattering vector should have accurate relative sizes
        self.scale_reciprocal_vectors = True

    def clear(self, keep_scannables=True):
        """Clear previous calculations
        
        Example::
            
            clear()

        Parameters
        ----------
        keep_scannables : bool, optional
             | Copies scannables over.
             | if keep==false, need to reload namespace afterwards.
             | The default is True.

        """
        old_sc = self.scannables
        self.__init__()
        if keep_scannables:
            self.scannables = old_sc
        self.update_pos()

    def intersect(self, popups=False, **kwargs):
        """Check if meshes in the simulation are intersecting
        
        Example::
            
            coliding_meshes=intersect()
        
        Parameters
        ----------
        popups : bool, optional
            Draw popup window if collision is detected. The default is False.
        verbose : bool, optional
            print every check. The default is False.


        Returns
        -------
        intersections : list [[str:mesh1, str:mesh2],...,[mesh69, mesh420]]
            list of intersecting mesh name pairs.

        """

        exceptions = self.collision_exceptions.copy()
        intersect_collections = params.intersect_collections

        for collection in intersect_collections:  # collections where all included objects should touch
            initial_list = collection[1]
            for name in bpy.data.collections[collection[0]].all_objects.keys():
                initial_list.append(name)
            exceptions.append(initial_list)
        return (is_intersect(popups=popups, exceptions=exceptions, **kwargs))

    def moveto(self, e_angles, use_limits=True, UI_call=True):
        """Move the simulation and update the global state
        
        Example::
            
            moveto([0,0,0,0,90,0]) #chi 90
        

        Parameters
        ----------
        e_angles : list [mu:float, delta:float, gamma:float, eta:float, chi:float, phi:float]
            eulerian rotations.
        use_limits : bool, optional
            if safety limits should be used if they are enabled. The default is True.
        UI_call : bool, optional
            If UI update call should be tried. The default is True.

        """
        test_pos = Position(*e_angles)
        if (self.limits and use_limits):
            if not (self.inlimits(test_pos, raise_error=True)):
                raise Exception('Would move outside limits')

        # calculate real motor angles
        k_angles_new = etok.EtoK([test_pos.eta, test_pos.chi, test_pos.phi])
        if k_angles_new[0] is None:
            raise Exception('Eulerian to K conversion not possible in this mode')

        self.position = test_pos
        self.k_angles = dict(zip(self.k_angles.keys(), k_angles_new))
        # convert to blender coordinate system
        b_angles = etok.KtoB([*list(e_angles)[:3], *k_angles_new])

        # move it
        motors.set_motor_angles(b_angles)

        # print values
        if self.verbose:
            print("Moved to:")
            print(self.position.asdict)
            print()

        if self.collision_test:
            self.intersect(popups=True)
        # print(self.k_angles)

        bpy.context.view_layer.update()
        vectors.set_q(self.position)
        self.set_reciprocal_vectors()
        vectors.set_vector('reference azimuthal', self.setnphi())
        bpy.data.objects["chi axis"].rotation_euler[0] = -radians(self.position.eta)  # adjust chi axis

        if (UI_call):
            # print('ui was called')
            if self.ui_call is None:
                # print('lost the call function')
                # if UI has not given a function pointer for updating it,
                # try overiding the UI
                try:
                    bpy.ops.i16.ui_update()
                    bpy.types.Scene.diffractometer = self
                    self.ui_call = bpy.ops.i16.ui_update
                except Exception as e:
                    traceback.print_exc()
                    print(e)
            else:
                self.ui_call()

    def read_visual_pos(self):
        """Calculate motor rotations from visual roatation of meshes
        
        Returns
        -------
        position_tuple : [mu:float, delta:float, gamma:float, eta:float, chi:float, phi:float]
            eulerian angles as seen on screen. 
            Might be different from emulator position if desynced.

        """
        visual_angles = []
        for motor in self.armature_motors:
            vis_m = ra.visual_matrix(motor)
            rot_y = ra.rotation_from_m(vis_m).y
            visual_angles.append(rot_y)
        k_angles = etok.BtoK(visual_angles)
        e_angles = [*k_angles[:3], *etok.KtoE(k_angles[3:])]
        return (e_angles)
        # print(rot_y,motor)

    def set_reciprocal_vectors(self, *args):
        """Calculates and displays reciprocal lattice vectors in the lab frame
        
        Example::
            
            set_reciprocal_vectors()

        """
        if (self.scale_reciprocal_vectors):
            scale = self.wl
        else:
            scale = None
        if (self.ubcalc.UB is None):
            ub = np.zeros((3, 3))
        else:
            ub = self.ubcalc.UB

        vectors.set_reciprocal_lattice(ub, wl=scale)

    def varifykey(self, key):
        """Get the id of a scannable after comparing to alternative names
        and checking if this is not the object itself.
        
        Example::
            
            varifykey('sixcircle') #returns 'sixc' - the real scannable id

        Parameters
        ----------
        key : str or Scannable
            The scannable id or the scannable itself.

        Returns
        -------
        key : str
             The scannable id.

        """
        if hasattr(key, 'key'):
            key = key.key

        if key in self.renamed.keys():
            key = self.renamed[key]

        return key

    def inlimits(self, position=None, raise_error=False):
        """If given position is within safety limits. If no parameters given, checks current position.
        
        Example::
            
            inlimits(init_position_ob([0,0,0,0,90,0])) #check if chi 90 is allowed by the limits
        

        Parameters
        ----------
        position : Position, optional
            A position object describing Eulerian angles. The default is current position.
        raise_error : bool, optional
            if function should raise error instead of returning false if 
            position is outside the safety limits. 
            The default is False.

        Returns
        -------
        ret : bool
            if position is within safety limits.

        """
        if position is None:
            position = self.position

        ret = True
        if self.limits:
            if not self.scannables['sixc'].inlimits(position.astuple, raise_error):
                ret = False
            if not scannables.in_composite_limits(self.composite_limits, position.astuple, raise_error):
                ret = False

        return (ret)

    def get_dist(self, pos1, pos2):
        """Get estimate of how far away two position are in eulerian space
        

        Parameters
        ----------
        pos1 : Position
            A position object describing eulerian angles.
        pos2 : Position
            A position object describing eulerian angles.

        Returns
        -------
        dist : float
            Geometric sum of all eulerian rotations if going from pos1 to pos2.

        """
        tpos1 = pos1.astuple
        tpos2 = pos2.astuple
        distsq = 0
        for i in range(len(tpos1)):
            distsq += (setrange(tpos2[i]) - setrange(tpos1[i])) ** 2
        dist = sqrt(distsq)
        return dist

    def pos_from_hkl(self, hkl):
        """
        Get the closest position and virtual angles corresponding to a certain hkl. 
        If limits are enabled, makes sure the position is within limits.
        Raises an exception if there are no allowed positions.
        
        Example::
            
            position_ob, virtual_angles = pos_from_hkl([1,1,1])
        

        Parameters
        ----------
        hkl : [float,float,float]
            Miller idex list.

        Returns
        -------
        pos_best : Position
            the optimal position for this hkl.
        va_best : dict{ str:float }cal
            the corresponding virtual angles.

        """

        pos_now = self.position

        pos_best = None
        va_best = None
        dist_best = None

        for pos, virtual_angles in self.hklcalc.get_position(hkl[0], hkl[1], hkl[2], self.wl):

            # print("choice", pos.asdict)
            if self.inlimits(pos):
                # print("suiteble",pos.asdict)
                if pos_best is None:  # find starting point
                    pos_best = pos
                    va_best = virtual_angles
                    dist_best = self.get_dist(pos_now, pos)

                elif dist_best > self.get_dist(pos_now, pos):  # compare to the rest
                    pos_best = pos
                    va_best = virtual_angles
                    dist_best = self.get_dist(pos_now, pos)

        if pos_best is None:
            raise Exception('No solutions found for this hkl')
        # print("chosen",pos_best.asdict)
        return (pos_best, va_best)

    def pos(self, *args):
        """The diffcalc pos command.
        | If no arguments given, print the values of all scannables.
        | elif the the only argument is a scannable, print its value.
        | elif there are two arguments, a scannable and a value, set the scannable to that value.
        | elif there are multiple scannable and value pairs, 
        set each scannable to the corresponding value.
        
        Examples::
            
            pos() #prints everything
            pos(sixc) #prints [phi,chi,eta,mu,delta,gamma]
            pos(hkl,[1,1,1]) #moves simulation to position hkl = [1,1,1]
        

        Parameters
        ----------
        *args : [scannable1, value1, scannable2, value2, ....], optional
            Scannables and values.

        """

        # if print all
        if len(args) == 0:
            for name in self.scannables:
                if name != self.varifykey(name):
                    sc_str = self.scannables[name].key
                else:
                    sc_str = repr(self.scannables[name])
                print(name + ':\n' + sc_str + '\n')

        # print certain module

        elif len(args) == 1:
            scannable = args[0]
            scannable.pos()

        # Move something
        elif len(args) > 1:
            simultaneous = False

            # check for simultaneous movement
            if len(args) > 3:
                keys = []
                values = []

                for i in range(len(args) // 2):
                    j = i * 2
                    keys.append(self.varifykey(args[j]))
                    values.append(args[j + 1])

                if all(key in self.position.asdict.keys() for key in keys):
                    simultaneous = True
                    pos = self.position.asdict
                    for i in range(len(keys)):
                        pos[keys[i]] = values[i]
                    self.moveto(pos.values())

                elif all(key in self.k_angles.keys() for key in keys):
                    simultaneous = True
                    pos = self.position.asdict
                    for i in range(len(keys)):
                        self.k_angles[keys[i]] = values[i]
                        pos[keys[i]] = values[i]
                    self.moveto([*self.position.astuple[:3], *etok.KtoE(list(self.k_angles.values()))])

            if simultaneous:
                print("Moved to:")
                for i in range(len(keys)):
                    print(keys[i] + ': ', values[i])

            else:  # otherwise move separately
                for i in range(len(args) // 2):
                    j = i * 2
                    scannable = args[j]
                    val = args[j + 1]
                    scannable.pos(val)

        print()  # some white space

    def inc(self, key, val):
        """Increments a scannable's value.
        
        
        Example::
            
            inc(eta, 1) # eta moves to eta +1
        
        Parameters
        ----------
        key : Scannable
            the scannable you want to increment.
        val : float or list of floats
            The value by which to increment

        """
        val_old = key()

        if isinstance(val_old, dict):
            val_old = list(val_old.values())
            val_new = [val_old[i] + val[i] for i in range(len(val))]

        elif isinstance(val_old, (list, tuple)):
            val_new = [val_old[i] + val[i] for i in range(len(val))]

        elif isinstance(val_old, (int, float)):
            val_new = val_old + val

        self.pos(key, val_new)

    def sim(self, scannable, value):
        """Simulates a move to a certain sixc or hkl position and
        prints all the position values of that position. 
        Checks for collisions and errors before moving to a position.
        
        Example::
            
            sim(hkl,[1,1,1]) #predicts what would happen if moving to hkl = [1,1,1]

        Parameters
        ----------
        scannable : Scannable or str
            hkl or sixc (or their keys).
        value : list of floats
            corresponding position to simulate.
            
        """

        key = self.varifykey(scannable)
        val = value

        # save current state
        org_angles = self.position.astuple
        org_verbose = self.verbose

        if (self.ubcalc.UB is None):
            print('UB matrix not set')

        else:

            if (key == 'sixc'):
                pos = Position(*self.sixc_to_pos(val))
                hkl = self.hklcalc.get_hkl(pos, self.wl)

            elif (key == 'hkl'):
                hkl = val

            pos, virtual_angles = self.pos_from_hkl(hkl)
            self.verbose = False
            self.moveto(pos.astuple)
            print("Would move to:")
            print("(hkl) = ", hkl)
            self.fdict_print(pos.asdict)
            self.fdict_print(virtual_angles)
            self.intersect()

        self.moveto(org_angles)
        self.verbose = org_verbose
        print()

    def con(self, *args):
        """Diffcalc con function. 
        
        | If no arguments given, print all constraints in a table
        | elif the the only argument is a scannable, print its constraint.
        | elif there are two arguments, a scannable and a value, set the scannable constraint to that value.
        | elif there are multiple scannable and value pairs, set each scannable's constraint to the corresponding value.
        
        Examples::
            
            con() # show constraint table
            con(psi) # show value of psi constraint
            con(bisect, True) # enable bisect constraint
            
        
        Parameters
        ----------
        *args : [scannable1, value1, scannable2, value2, scannable3, value3], optional
            scanables and their values

        """
        if len(args) == 0:
            print(self.cons)

        elif len(args) == 1:
            key = self.varifykey(args[0])
            print(key, ' = ', getattr(self.cons, key))

        else:
            if (len(args) > 4):
                self.cons.clear()
            for i in range(len(args) // 2):
                j = i * 2
                key = self.varifykey(args[j])
                val = args[j + 1]
                if (val is None or val == 'None'):
                    val = True
                setattr(self.cons, key, val)
            print(self.cons.asdict)
        print()

    def scan(self, *args):
        """Scan 'scannable' from 'start' to 'stop' in increments of 'step'.
        
        Examples::
            
            scan(eta,0,5,1) # moves to eta = 0, 1, 2, 3, 4, and 5 in turn.
            scan(l, 0.1, 2, 0.1, animate, wait, 0.1) # animates the l scan. Moves every 0.1 seconds.
            con(mu,0,gam,0,psi,0)
            scan(psi,0,10,1, collision) # tests for collisions at every value of psi.

        Parameters
        ----------
        scannable : Scannable
            scannable to scan
        start : float or list of floats 
            starting value of scannable
        stop : float or list of floats
            upper limit of scannable
        step : float or list of floats
            size of step
        *args : any, optional
            Implemented options are: 'animate' makes the scan do an animation, 'wait, seconds:float'
            makes the animation wait for the set number of seconds between movements, 'collision' tests for collisions at every step. 
        
            


        """
        key, start, stop, step = args[:4]

        print("Scan start", key.key, start, 'to', stop, 'every', step)

        if (key.key in dc.cons.asdict.keys()):
            hkl = self.scannables['hkl']()
            con_initial = self.cons.asdict[key.key]
            steps = list(np.arange(start, stop + step / 10., step))

            def scan_once(val, key=key, hkl=hkl):
                self.con(key, val)
                self.pos(self.scannables['hkl'], hkl)

            def scan_cleanup(con_initial=con_initial):
                self.con(key, con_initial)

        else:
            if (key.key == 'hkl'):
                start = np.array(start)
                stop = np.array(stop)
                step = np.array(step)
                # print(start,stop,step)

                steps = []
                i = 0
                notfull = True
                while notfull:
                    steps.append(list(start + step * i))
                    i += 1
                    for j in range(len(start)):
                        if (start + step * i)[j] > (stop[j] + step[j] / 10):
                            notfull = False
                # print(steps)

            else:
                # print(start,stop+step/10,step)
                steps = list(np.arange(start, stop + step / 10., step))
                # print(steps)

            def scan_once(val, key=key):
                print(val)
                self.pos(key, val)

            def scan_cleanup():
                pass

        clean_args = [self.varifykey(arg) for arg in args[4:]]
        if 'animate' in clean_args:
            if 'wait' in clean_args:
                i = clean_args.index('wait')
                wait_time = clean_args[i + 1]
            else:
                wait_time = 0.1
            print('Animating with wait time', wait_time)
            bpy.types.Scene.animate_wait = wait_time
            bpy.types.Scene.animate_instructions = [scan_once, steps, scan_cleanup]
            bpy.ops.wm.modal_timer_operator()
            return (None)

        else:
            col_test = False
            if 'collision' in clean_args:
                col_test = True

            for val in steps:
                scan_once(val)
                if col_test: self.intersect()

            scan_cleanup()

        print("Scan finished")
        print()

    def scancn(self, *args):
        """Centered scan on current position.
        
        Scan 'scannable' around the starting position by going to 'numer_of_steps' number of positions
        that are separated by value 'step'
        Then return to starting positoin.
        
        Example::
            
            pos(eta,0) #go to central position
            scancn(eta,1,5) # moves to positions eta = -2, -1, 0, 1, and 2

        Parameters
        ----------
        scannable : Scannable
            scannable to scan
        step : float or list of floats
            size of step
        number_of_steps : int
            total number of steps
        *args : any, optional
            passed on to the 'scan' command. Implemented options are: 'animate' makes the scan do 
            an animation, 'wait, seconds:float' makes the animation wait for the set number of seconds 
            between movements, 'collision' tests for collisions at every step.

        """
        key, step, numsteps = args[:3]
        initial_pos = self.pos_to_sixc(list(self.position.astuple))

        if (key.key == 'hkl'):
            initial = np.array(key())

            step = np.array(step)
            start = list(initial - step * (numsteps // 2))
            stop = list(start + step * (numsteps - 1))
            step = list(step)
        else:
            if (key.key in dc.cons.asdict.keys()):
                hkl = self.scannables['hkl']
                self.pos(hkl, hkl())
            initial = key()
            start = initial - step * (numsteps // 2)
            stop = start + step * (numsteps - 1)
        self.scan(key, start, stop, step, *args[3:])

        self.pos(self.scannables['sixc'], initial_pos)

    def setlm(self, name, vals):
        """Set the limits of a scannable or composite limit.
        
        Example::
            
            setlm(eta,[None,90]) #the safety limits for eta are now 'eta < 90'

        Parameters
        ----------
        name : Scannable or str
            an id for a scannable or composite limit
        vals : float or list of floats
            new limit values.

        """
        name = self.varifykey(name)
        if (name in self.scannables):
            sc = self.scannables[name]
            if len(vals) >= 2:
                sc.min = vals[0]
                sc.max = vals[1]
                if len(vals) == 3:
                    sc.cut = vals[1]
            else:
                raise Exception("Wrong number of values to specify limits. Need [min, max, cut]")
        elif (name in self.composite_limits):
            self.composite_limits[name].args = vals
        else:
            raise Exception("'" + str(name) + "' object not found")

        self.showlm(name)

    def showlm(self, *args):
        """Prints limits.
        
        | If no parameters given, prints all safety limits.
        | If any are given, prints the limits of every parameter.
        
        Example::
            
            showlm(eta) # shows the limits and cut of eta.
        

        Parameters
        ----------
        *args : [id1, id2, id3, ..], optional
            scannables, composite limits, or their ids.

        """
        lims = self.limitsets
        print("limits: [min, max, cut]")
        if len(args) == 0:
            args = self.limitsets.keys()

        for key in args:
            name = self.varifykey(key)
            if (name in self.scannables):
                sc = self.scannables[name]
                lims = [sc.min, sc.max, sc.cut]
                print('%-7s' % (name + ':'), lims)
            elif (name in self.composite_limits):
                print('%-7s' % (name + ':'), self.composite_limits[name].args)
            elif name in self.limitsets:
                print('%-7s' % (name + ':'), self.limitsets[name])
            else:
                raise Exception("'" + str(name) + "' object limits not found")
        print()

    def enable_lm(self, if_use=True):
        """Enable or disable safety limits
        
        Example::
            
            enable_lm(False) #safety limits are disabled for the simulation
        
        Parameters
        ----------
        if_use : bollean, optional
            if enable. The default is True.

        """
        self.limits = if_use
        print("limits = ", self.limits)

    def enable_verbose(self, if_use=True):
        """Enable or disable printing the full position string every time the diffractometer moves
        
        Example::
            
            enable_verbose(True) #will print every movement
            
        Parameters
        ----------
        if_use : boolean, optional
            if enable. The default is True.

        """
        self.verbose = if_use
        print("verbose = ", self.verbose)

    def enable_collision_test(self, if_use=True):
        """Enable or disable checking for collisions after every movement. 
        
        Slow on most computers.
        
        Example::
            
            enable_collision_test(True) #will test for collisions all the time
            
        Parameters
        ----------
        if_use : boolean, optional
            if enable. The default is True.

        """
        self.collision_test = if_use
        print("collision_test = ", self.collision_test)

    def loadub(self, file):
        """Load a diffractomter state from a file.
        Can read .i16sim.txt or .nxs files.
        Loads UB, U, position, constraints, energy, crystal lattice, 
        and azimuthal references if they are given.
        
        If using .nxs files, only structures from i16 in 09/2021 are correctly interpreted.
        The file formats are regularly updated and data adresses can change.
        
        Example::
            
            loadub(0) #load first state file it can find
        
        Parameters
        ----------
        file:str or index:int
            path or index to file.

        """
        ub = None
        pos = None
        cons_list = None
        latt = None
        azi_ref = None
        azi_hkl = None

        if isinstance(file, int):
            file = self.listub(ret=True)[file]

        if str(file).endswith('.txt'):
            with open(file, 'r') as f:
                print("reading .txt file\n", file)

                lines = f.read().split('\n')
                # print(lines)

                # go through the file looking for markers
                for i, line in enumerate(lines):
                    # line=line.strip().split()
                    # print(line,line[0])
                    # read the ub matrix rows
                    if (line == 'ub'):
                        ub = np.zeros((3, 3))
                        # print("ub marker")
                        for j in range(3):
                            ubrow = lines[i + j + 1].strip().split()
                            ubrow = [float(x) for x in ubrow]
                            ub[j, :] = np.array(ubrow)

                    # read position
                    elif (line == 'sixc'):
                        # print("pos marker")
                        pos = lines[i + 1].strip().split()
                        pos = [float(x) for x in pos]  # uses position order

                    # read contraints
                    elif (line == 'con'):
                        cons = {}
                        cons_list = []
                        # print("con marker")
                        for j in range(3):
                            if (i + j + 1) < len(lines):
                                conline = lines[i + j + 1].strip().split()
                                if len(conline) == 1:
                                    cons[conline[0]] = True
                                elif len(conline) == 2:
                                    if (conline[1] == 'None' or conline[1] is None):
                                        cons[conline[0]] = True
                                    else:
                                        cons[conline[0]] = float(conline[1])

                        for key in cons:
                            key_varified = self.varifykey(key)
                            cons_list.append(key_varified)
                            cons_list.append(cons[key])

                    elif (line == 'en'):
                        en = float(lines[i + 1].strip())

                    elif (line == 'lattice'):
                        latt_name = lines[i + 1].strip()
                        latt = [float(x) for x in lines[i + 2].strip().split()]

                    elif (line == 'azi_ref'):
                        azi_ref = lines[i + 1].strip().split()
                        azi_ref = [float(x) for x in azi_ref]  # uses position order

                    elif (line == 'azi_hkl'):
                        azi_hkl = lines[i + 1].strip().split()
                        azi_hkl = [float(x) for x in azi_hkl]

                # print(cons_list,cons)

                print("Setting:\n")
                if not (ub is None):
                    print("ub")
                    self.ubcalc.set_ub(ub)
                    self.hklcalc.ubcalc.UB = ub
                    print(self.ubcalc.UB)
                    print()
                if not (pos is None):
                    print("sixc")
                    self.pos(self.scannables['sixc'], self.pos_to_sixc(pos))
                if not (cons_list is None):
                    print("con")
                    self.con(*cons_list)
                if not (en is None):
                    print('en')
                    self.pos(self.scannables['en'], en)
                if not (latt is None):
                    self.setlat(latt_name, *latt)
                    print("lattice")
                    print(latt_name, latt)
                    print()

                    try:
                        if self.ubcalc.crystal is not None:
                            self.ubcalc.U = self.ubcalc.UB @ np.linalg.inv(self.ubcalc.crystal.B)
                    except Exception as e:
                        traceback.print_exc()
                        print(e)
                        print('Failed to set U matrix')

                elif not (self.ubcalc.UB is None):
                    pass
                    # get real vectors from UB

                if not (azi_ref is None):
                    self.setnphi(azi_ref)
                    print('nphi')
                    print(azi_ref)
                    print()
                if not (azi_hkl is None):
                    self.setnhkl(azi_hkl)
                    print('nhkl')
                    print(azi_hkl)
                    print()

                self.hklcalc = HklCalculation(self.ubcalc, self.cons)
                self.update_pos()
                self.set_reciprocal_vectors()
                vectors.set_vector('reference azimuthal', self.setnphi())

        # if it is a nexus file, create a suitable .txt and read that
        elif str(file).endswith('.nxs'):
            from i16sim.util.hdf5_to_i16sim import interpret
            interpret(file)
            self.loadub(str(file) + '.i16sim.txt')

        else:
            raise Exception('File not recognised')

    # reinstall as user module
    # def export_state(self,filename):

    def listub(self, ret=False):
        """Print or return a list of diffractomter state files in the current directory.
        
        Example::
            
            listub() #print list of state files in the current directory and subdirectories

        Parameters
        ----------
        ret : bool, optional
            if return the list of files. The default is False.

        Returns
        -------
        state_files : list
            list of state files.

        """
        curpath = os.path.abspath(os.curdir)
        ubfiles = []
        folders = next(os.walk(curpath))[1]
        folders.append('.')
        for folder in folders:
            files = os.listdir(folder)
            for file in files:
                if file.endswith('i16sim.txt'):
                    ubfiles.append(folder + '/' + file)

        if ret:
            return ([os.path.abspath(file) for file in ubfiles])
        else:
            print("ub state files in '" + curpath + "':")
            if ubfiles == []:
                print('No ub state files found')
            else:
                for i, file in enumerate(ubfiles):
                    print(str(i) + ')', file)
            print()

    def lastub(self):
        """Load first diffractomter state file it can find.
        
        Example::
            
            lastub()
            
        """
        files = self.listub(ret=True)
        if len(files) == 0:
            print('No ub state files found')
        else:
            self.loadub(files[0])

    def update_pos(self, command=None):
        """Updates position and state to synchronise UI and emulator.
        
        Example::
            
            update_pos() #synchronises
            update_pos(0) # go to [0,0,0,0,0,0] position.
            update_pos(90) # go to chi 90. [0,90,0,0,0,0] position.

        Parameters
        ----------
        command : int, optional
            The default is None.

        """
        if command == 0:
            self.moveto([0, 0, 0, 0, 0, 0])
        elif command == 90:
            self.moveto([0, 0, 0, 0, 90, 0])
        else:
            mu, gamma, delta, ktheta, kappa, kphi = etok.BtoK(motors.read_motor_angles().values())
            e_angles = etok.KtoE([ktheta, kappa, kphi])
            self.moveto([mu, gamma, delta, *e_angles], use_limits=False)

    def allhkl(self, hkl, *args):
        """Prints all potential positions for a certain hkl regardless of limits.
        
        Example::
            
            allhkl([1,1,1]) #prints all theoretically possible eulerian positions.
            
        Parameters
        ----------
        hkl : [float,float,float]
            Miller indices.

        """
        print('all positions for hkl =', hkl)
        for pos, virtual_angles in self.hklcalc.get_position(*hkl, self.wl):
            pos = pos.asdict
            for key in pos:
                print(key + ': %-10.4f' % pos[key], end='')
            print(' | ', end='')
            for key in virtual_angles:
                print(key + ': %-10.4f' % virtual_angles[key], end='')
            print()
        print()

    def c2th(self, hkl):
        """Calculate two-theta scattering angle for a reflection
            
        Example::
            
            two_theta_val = c2th()
        
        
        Parameters
        ----------
        hkl : [float,float,float]
            Miller indices.

        Returns
        -------
        tth : float
            2*theta. Scattering angle

        """
        tth = degrees(self.ubcalc.get_ttheta_from_hkl(hkl, self.scannables['en']()))
        print(tth)
        print()
        return tth

    def latt(self):
        """Get current crystal lattice
        
        Example::
            
            lattice = latt() #returns current latice

        Returns
        -------
        lattice : [str:name, float:a, float:b, float:c ,float:alpha ,float:beta ,float:gamma]
            Current lattice.

        """
        lattice = self.ubcalc.crystal.get_lattice()
        return lattice

    # ub calculation emulator
    def newub(self, name):
        """Starts a new UB calculation
        
        Example::
            
            newub('example1')

        Parameters
        ----------
        name : str

        """
        self.ubcalc = UBCalculation(name)

    def calcub(self, *args):
        """Calculate UB matrix. Enables hkl calculations.

        Calculate UB matrix using two reference reflections and/or
        reference orientations.

        By default use the first two reference reflections when provided.
        If one or both reflections are not available use one or two reference
        orientations to complement missing reflection data.
        
        Example::
            
            calcub(1,2) #uses reflections 1 and 2 to calculate UB

        Parameters
        ----------
        idx1: int or str, optional
            The index or the tag of the first reflection or orientation.
        idx2: int or str, optional
            The index or the tag of the second reflection or orientation.
        """
        print("Calculating UB matrix")
        self.ubcalc.calc_ub(*args)
        self.hklcalc = HklCalculation(self.ubcalc, self.cons)
        print()

        self.set_reciprocal_vectors()
        vectors.set_vector('reference azimuthal', self.setnphi())

    def checkub(self, *args):
        """
        Print the hkl of added reflections next to the calculated hkl for corresponding positions.
        
        Example::
            
            checkub()
            
            # id, hkl,    hkl_calculated
            # 1, (1,1,1), (1,1,1)
            # 2, (0,0,1), (0,0,0.98) #means the lattice parameters are not exactly right
            
            
        """
        if (self.ubcalc.UB is None):
            print('UB matrix not set')
        else:
            if self.ubcalc.get_number_reflections() > 0:
                print("reflections")
                print("%s,  %s,  %s,  %s,  %s " % ("id", 'hkl_set', 'hkl_computed', 'energy', "tag"))
                for i in range(1, len(self.ubcalc.reflist) + 1):
                    ref = self.ubcalc.reflist.get_reflection(i)
                    hkl = self.hklcalc.get_hkl(ref.pos, self.wl)
                    ref = list(ref.astuple)
                    ref[1] = hkl  # swap position for calculated hkl
                    print(str(i) + ',', ref)
                print()
            if self.ubcalc.get_number_orientations() > 0:
                print("orientations")
                print("%s,  %s,  %s,  %s,  %s " % ("id", 'hkl_set', 'hkl_computed', 'xyz', "tag"))
                for i in range(1, len(self.ubcalc.orientlist) + 1):
                    ref = self.ubcalc.orientlist.get_orientation(i)
                    hkl = self.hklcalc.get_hkl(ref.pos, self.wl)
                    ref = list(ref.astuple)
                    ref[2] = ref[1]  # change order
                    ref[1] = hkl
                    print(str(i) + ',', ref)
                print()

    def get_sixc(self):
        """Get Eulerian angles in the same order as in GDA at i16
        
        Example::
            
            get_sixc()
            
        Returns
        -------
        angles : list [phi:float, chi:float, eta:float, mu:float, delta:float, gamma:float]
            eulerian angles in intuitive i16 order.

        """
        ret = list(self.position.astuple)
        ret = [*ret[3:][::-1], *ret[:3]]
        return ret

    def addref(self, hkl, name='', position=None):
        """Add a reference reflection.

        Adds a reflection position in degrees and in the systems internal
        representation. Calculates UB when a second reflection is added.
        
        Example::
            
            addref([1,1,1], "111_example") #adds a reflection at current position

        Parameters
        ----------
        hkl : list [float, float, float]
            hkl index of the reflection
        name : str, optional, default = None
            identifying tag for the reflection
        position: Position, optional, default is current position
            position of reflection as diffcalc position object
        """

        if position is None:
            position = self.position
        self.ubcalc.add_reflection(
            hkl,
            position,
            self.scannables['en'](),
            name,
        )
        print("reflection added at", self.get_position(asdict=True))
        print()
        if self.ubcalc.get_number_reflections() == 2:
            self.calcub(1, 2)

    def showref(self):
        """Shows added reflections
        
        Example::
            
            showref() #prints a table of reflections

        """

        if self.ubcalc.get_number_reflections() > 0:
            print(self.ubcalc.reflist)
        else:
            print("No reflections")
        print()

    def addorient(self, hkl, xyz, name='', position=None):
        """
        Adds a reference orientation in the diffractometer
        coordinate system.
        
        Example::
            
            #if at current position c* is in the same direction as +z in the sample coordinate system
            addorient([0,0,1], [0,0,1], '+z||c*') 
            

        Parameters
        ----------
        hkl : Tuple[float, float, float]
            hkl index of the reference orientation
        xyz : Tuple[float, float, float]
            xyz coordinate of the reference orientation in the diffcalc sample coordinate frame
            alternatively, a [x,y,z] vector parallel to the (h * a* + k * b* + l * c*) vector
        name : str
            identifying tag for the reflection
        position: Position, optional, default is current position
            position of reflection as diffcalc position object
        """
        if position is None:
            position = self.position
        self.ubcalc.add_orientation(
            hkl,
            xyz,
            position,
            name,
        )
        print("orientation added at", self.get_position(asdict=True))
        print()
        if self.ubcalc.get_number_orientations() == 2:
            self.calcub(1, 2)

    def showorient(self):
        """Shows added orientations
        
        Example::
            
            Showorient() #prints a table of orientations

        """
        if self.ubcalc.get_number_orientations() > 0:
            print(self.ubcalc.orientlist)
        else:
            print("No orientations")
        print()

    def setlat(self, *args):
        """Set crystal lattice parameters using shortform notation.

        Following combinations of system and lattice parameters are supported:

        | ('Cubic', a) -- sets Cubic system
        | ('Tetragonal', a, c) -- sets Tetragonal system
        | ('Hexagonal', a, c) -- sets Hexagonal system
        | ('Orthorhombic', a, b, c) -- sets Orthorombic system
        | ('Rhombohedral', a, alpha) -- sets Rhombohedral system
        | ('Monoclinic', a, b, c, beta) -- sets Monoclinic system
        | ('Triclinic', a, b, c, alpha, beta, gamma) -- sets Triclinic system

        Crystal system can be inferred from the lattice parameters for the
        following cases:

        | (a,) -- assumes Cubic system
        | (a, c) -- assumes Tetragonal system
        | (a, b, c) -- assumes Orthorombic system
        | (a, b, c, angle) -- assumes Monoclinic system with beta not equal to 90 or Hexagonal system if a = b and gamma = 120
        | (a, b, c, alpha, beta, gamma) -- sets Triclinic system
        
        Example::
            
            #5 Angstrom base and all lattice vectors are at right angles.
            setlat('orthorombic 5x5x10 A', 5, 5, 10, 90, 90, 90) 

        Parameters
        ----------
        name: str
            Crystal name
        system: Optional[float], default = None
            Crystal lattice type.
        a: Optional[float], default = None
            Crystal lattice parameter.
        b: Optional[float], default = None
            Crystal lattice parameter.
        c: Optional[float], default = None
            Crystal lattice parameter.
        alpha: Optional[float], default = None
            Crystal lattice angle.
        beta: Optional[float], default = None
            Crystal lattice angle.
        gamma: Optional[float], default = None
            Crystal lattice angle.
            
        """
        self.ubcalc.set_lattice(*args)

    def new_hklcalc(self):
        """
        Creates a new hkl calculation object
        
        """
        self.hklcalc = HklCalculation(self.ubcalc, self.cons)
        print(self.scannables['hkl'])

    def ub(self):
        """Prints the state of the current UB calculation
        
        Example::
            
            ub() #prints the ub table

        Returns
        -------
        numpy matrix (3,3)
            The UB matrix.

        """
        try:
            print(self.ubcalc)
        except:
            print(self.ubcalc.UB)
        print()
        return self.ubcalc.UB

    def trialub(self, id=1):
        """Estimate UB from one reflection
        
            Example::
                
                trialub() # will approximate the UB matrix if one reflection was added
                
        """
        print('Estimating UB from one reflection')
        self.calcub(id)
        # self.ubcalc._calc_ub_from_primary_only(id)

    def setnhkl(self, vector=None):
        """Return reference vector property represented using miller indices.
        If a parameter is given, set the vector to the given value.
        
        Example::
            
            setnhkl([0,0,1]) # the reference vector is now the c* reciprocal vector
        
        
        Parameters
        ----------
        vector : [float,float,float], optional
            The value to be set. The default is None and the function returns current value.

        Returns
        -------
        np.ndarray:
            Reference vector represented as (3,1) NumPy array.
        """
        if vector is None:
            return (self.ubcalc.n_hkl)
        else:
            self.ubcalc.n_hkl = vector
            vectors.set_vector('reference azimuthal', self.setnphi())

    def setnphi(self, vector=None):
        """Return reference vector property represented using sample frame coordinates.
        If a parameter is given, set the vector to the given value.
        
        
        Example::
            
            setnhkl([0,0,1]) # the reference vector is now along sample +z direction
        
        Parameters
        ----------
        vector : [float,float,float], optional
            The value to be set. The default is None and the function returns current value.

        Returns
        -------
        np.ndarray:
            Reference vector represented as (3,1) NumPy array.
        """
        if vector is None:
            return (self.ubcalc.n_phi)
        else:
            self.ubcalc.n_phi = vector
            vectors.set_vector('reference azimuthal', self.setnphi())

    def surfnhkl(self, vector=None):
        """Return surface vector property represented using miller indices.
        If a parameter is given, set the vector to the given value.
        
        Parameters
        ----------
        vector : [float,float,float], optional
            The value to be set. The default is None.

        Returns
        -------
        np.ndarray:
            Reference vector represented as (3,1) NumPy array.
        """
        if vector is None:
            return (self.ubcalc.surf_nhkl)
        else:
            self.ubcalc.surf_nhkl = vector

    def surfnphi(self, vector=None):
        """Return surface vector property represented using sample frame coordinates.
        If a parameter is given, set the vector to the given value.
        
        Parameters
        ----------
        vector : [float,float,float], optional
            The value to be set. The default is None.

        Returns
        -------
        np.ndarray:
            Reference vector represented as (3,1) NumPy array.
        """
        if vector is None:
            return (self.ubcalc.surf_nphi)
        else:
            self.ubcalc.surf_nphi = vector

    def ik(self, **args):
        """
        Enable inverse kinematics
        """
        ikfk.set_IK(**args)

    def fk(self, **args):
        """
        Disable inverse kinematics
        """
        ikfk.remove_IK(**args)
        self.update_pos()

    # position format conversions and getters
    def init_position_ob(self, e_angles):
        """Create a position object.
        
        Example::
            
            pos_ob = init_position_ob([0,90,0,0,0,0]) # object representing chi = 90 rest position.
        
        Parameters
        ----------
        e_angles : [mu:float, delta:float, gamma:float, eta:float, chi:float, phi:float]
            position tuple.

        Returns
        -------
        pos : Position
            position object.

        """
        pos = Position(*e_angles)
        return (pos)

    def pos_to_sixc(self, e_angles):
        """Change position tuple order from diffcalc ordering to i16 intuitive ordering.
        
        Example::
            
            diffcalc_ordering = [4,5,6,3,2,1]
            i16_ordering = pos_to_sixc(diffcalc_ordering) # [1,2,3,4,5,6]

        Parameters
        ----------
        e_angles : [mu:float, delta:float, gamma:float, eta:float, chi:float, phi:float]
            diffcalc order

        Returns
        -------
        [phi:float, chi:float, eta:float, mu:float, delta:float, gamma:float]
            i16 sixc order.

        """
        return ([*e_angles[3:][::-1], *e_angles[:3]])

    def sixc_to_pos(self, sixc_e_angles):
        """Change position tuple order from i16 intuitive ordering to diffcalc ordering.
        
        Example::
            
            i16_ordering = [1,2,3,4,5,6]
            diffcalc_ordering = sixc_to_pos(i16_ordering) # [4,5,6,3,2,1]
        
        Parameters
        ----------
        sixc_e_angles : [phi:float, chi:float, eta:float, mu:float, delta:float, gamma:float]
            i16 sixc order..

        Returns
        -------
        [mu:float, delta:float, gamma:float, eta:float, chi:float, phi:float]
            diffcalc order

        """
        return ([*sixc_e_angles[3:], *sixc_e_angles[:3][::-1]])

    def get_position(self, asdict=False):
        """Get current position eulerian angles as a tuple or a dictionary in i16 sixc ordering.
        
        Example::
            
            get_postion(asdict=True) #returns a dictionary of eulerian angles

        Parameters
        ----------
        asdict : bool, optional
            if return as a dictionary. The default is False.

        Returns
        -------
        position : [phi:float, chi:float, eta:float, mu:float, delta:float, gam:float] or dict {str:float}
            i16 sixc order of eulerian angles
        """
        val = self.position.astuple
        val = self.pos_to_sixc(val)
        if asdict:
            keys = list(self.position.asdict.keys())
            keys = self.pos_to_sixc(keys)
            keys[-1] = 'gam'
            return (dict(zip(keys, val)))
        else:
            return (val)

    def get_position_ob(self):
        """Get current position as diffcalc object.
    
        Returns
        -------
        position : Position
            current diffcalc position object.

        """
        return (self.position)

    def get_ubcalc(self):
        """get current diffcalc-core ub calculation object
        
        Returns
        -------
        ubcalc : UBCalculation

        """
        return (self.ubcalc)

    def get_hklcalc(self):
        """get current diffcalc-core hkl calculation object

        Returns
        -------
        hklcalc : HklCalculation

        """
        return (self.hklcalc)

    def get_constraints(self):
        """get current diffcalc-core constraints object
        
        Returns
        -------
        cons_ob : Constraints
        """
        return (self.cons)

    def get_scannables(self):
        """Get dicionary of all scannables
        

        Returns
        -------
        dict : {str:Scannable}

        """
        return (self.scannables)

    def fdict_print(self, d):
        """Print a dictionary of floats nicely

        Parameters
        ----------
        d : dict {str:float}

        """
        for key in d:
            print("%-8s : %10.5f" % (key, d[key]))
        print()

    def get_base_namespace(self, other_diffcalc_emulator=None):
        """
        Returns a dictionary with the base namespace. 
        
        Example::
            
            dc=DiffcalcEmulator()
            globals().update(dc.get_namespace()) #to enable shorthand sytax and scannables
            
        Returns
        -------
        dict: {str:Scannable, str:method}
        """

        if other_diffcalc_emulator is None:
            object = self
        else:
            object = other_diffcalc_emulator

        # generate functions
        method_names = [method_name for method_name in dir(object) if
                        callable(getattr(object, method_name)) and '__' not in method_name]
        namespace = {method: getattr(object, method) for method in method_names}

        # add scannables
        for key in self.scannables:
            namespace[key] = self.scannables[key]

        return namespace

    def get_namespace(self):
        """
        Returns a dictionary with the full namespace (base and user defined). 
        
        Example::
            
            dc=DiffcalcEmulator()
            globals().update(dc.get_namespace()) #to enable shorthand sytax and scannables
            
        Returns
        -------
        dict: {str:Scannable, str:method}
        """
        namespace = self.get_base_namespace()

        try:
            user_functions = additional_functions.get_additional_functions(self)
            namespace.update(user_functions)
        except:
            traceback.print_exc()
            print("Could not load user defined functions")

        return namespace


# set up global variables for UI
dc = DiffcalcEmulator()

if __name__ == "__main__":
    # dc=bpy.types.Scene.diffractometer
    # dc=DiffcalcEmulator()
    # clear()
    globals().update(dc.get_namespace())
    update_pos()
    print('start')

    lastub()
    pos(hkl, [0, 0, 0.1])
    scan(l, 0.1, 2, 0.1, animate, wait, 0.1)
