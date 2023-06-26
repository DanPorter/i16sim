"""
User defined or non-essential scannables that require Blender

"""


import i16sim.parameters as params
import math
import bpy

def setrange(a,cut=-180):
        """
        Simplify the numerical value of an angle 'x'
        in: x, m, M # in degrees
        out: x equivalent, such that cut < x < cut+360
        """
        if cut is None:
            return a
        
        if (a < cut):
            a=a+360.
        elif (a > cut+360):
            a=a-360.
        else:
            return a
        return setrange(a,cut)



def get_additional_scannables(dc, scannable_cls):
    """Create secondary and user defined scannable objects and return them in a dictionary
    This is a factory for user defined scannables.
    

    Parameters
    ----------
    dc : DiffcalcEmulator
        the current emulator instance
    scannable_cls: Class
        a class that will be used to create instances of scannables


    Returns
    -------
    scannables : dict {str : Scannable}
        a dictionary of scannables indexed by their keys. 
        Includes detector arm detector movement scannables

    """
    #create namespace and get class to use in the factory
    globals().update(dc.get_namespace())
    Scannable = scannable_cls
    scannables = {} #dictionary of scannables.  {key : Scannable}
    
    #default methods
    def default_get(self):
        """
        Default scannable method
        Get value
        """
        return(self.key)
    
    def default_get_str(self):
        """
        Default scannable method
        Get formatted string of value
        """
        return(str(self.get()))
    
    def default_call(self):
        """
        Default scannable method
        Get value
        """
        return (self.get())
    
    def default_set(self,value):
        """
        Default scannable method
        Set value
        """
        raise Exception(str(self.key)+" cannot be changed by 'pos' command")
    
    def default_pos(self,value=None,silent=False):
        """
        Default scannable method
        Handle pos command
        """
        if value is None:
            print(str(self.key)+':',self.get_str())
        else:
            self.set(value)
            if not silent:
                self.move_print()
                
    def default_move_print(self):
        """
        Default scannable method
        Print string representing movement
        """
        print('Moving to '+str(self.key)+':',self.get_str())
    
    
    def default_tostring(self):
        """
        Default scannable method
        Get string representation of scannable
        """
        ret=[str(self.key)+':',self.get_str()]
        if self.min is not None:
            ret.extend(['min:',self.min])
        if self.max is not None:
            ret.extend(['max:',self.max])
        if self.cut is not None:
            ret.extend(['cut:',self.cut])
            
        ret=' '.join([str(el) for el in ret])
        return (ret)
    
    def default_inlimits(self,value=None,raise_error=False):
        """
        Default scannable method
        If scannable value is inside its limits
        """
        x=value
        ret=True
        
        if x is None:
            x=self.get()
        if self.cut is not None:
            x = setrange(x,self.cut)
            
        if self.min is not None:
            min = setrange(self.min,self.cut)
            if x <  min:
                ret = False
                
        if self.max is not None:
            max = setrange(self.max,self.cut)
            if max < x:
                ret = False
                
        if (raise_error and ret==False):
            raise Exception(self.key+': '+str(x)+" must be between "+str(self.min)+' and '+str(self.max))
        return ret

    
    #detector arm rotations factory
    arm_name=params.arm_name
    detector_motors=params.detector_motors
    
    def det_set(self, val):
        """
        Parameters
        ----------
        val : Float
            rotation of the detector motor.
        """
        bpy.data.objects[arm_name].pose.bones[self.key].rotation_euler[1]= math.radians(val) #set rotation
        update_pos() #Force blender to syncronise with simulatin
    
    def det_get(self):
        """
            Get rotation of the detector motor in degrees
        """
        rot=bpy.data.objects[arm_name].pose.bones[self.key].rotation_euler[1]
        rot=setrange(math.degrees(rot))
        return(rot)
        
    def det_get_str(self):
        """
        Get formatted string of value
        """
        return("%.5f"%(self.get()))
        
    #make scannables [stokes,thp,tthp,mtthp]
    for key in detector_motors:
        sc=Scannable(key, 
                    getter=det_get, #custom
                    setter=det_set, #custom
                    call=default_call, 
                    pos=default_pos,
                    move_print=default_move_print, 
                    get_str=det_get_str, #custom
                    tostring=default_tostring,
                    limits=[None,None,None], #[min,max,cut]
                    inlimits=default_inlimits)
            
        scannables[sc.key]=sc #add to dictionary
            
    #-----------------------------------------------------------
    #Your Code Goes Here
    #Put your scannables into the dictionary
    #and they will be added into the simulation namespace.
    #Scannables need to have unique identifiers stored as sc.key
    #-----------------------------------------------------------


    #sx, sy, sz by Aurys 06/09/2021
    collection_name='Sample environments'
    
    def sz_get(self):
        some_object=bpy.data.collections[collection_name].all_objects.values()[0]
        return (some_object.location[0])
        
    def sz_set(self,value):
        objects=bpy.data.collections[collection_name].all_objects.values()
        for ob in objects:
            ob.location[0]=value/1000 #in mm
        update_pos()
        
    sz=Scannable(key='sz', 
            getter=sz_get, #custom
            setter=sz_set, #custom
            call=default_call, 
            pos=default_pos,
            move_print=default_move_print, 
            get_str=det_get_str, #custom
            tostring=default_tostring,
            limits=params.limitsets['sy'], #[min,max,cut]
            inlimits=default_inlimits)
    scannables[sz.key]=sz
    
    #sx
    def sx_get(self):
        some_object=bpy.data.collections[collection_name].all_objects.values()[0]
        return (-1*some_object.location[1])
        
    def sx_set(self,value):
        objects=bpy.data.collections[collection_name].all_objects.values()
        for ob in objects:
            ob.location[1]=-1*value/1000 #in mm
        update_pos()
        
    key='sx'
    scannables[key]=Scannable(key, 
        getter=sx_get, #custom
        setter=sx_set, #custom
        call=default_call, 
        pos=default_pos,
        move_print=default_move_print, 
        get_str=det_get_str, #custom
        tostring=default_tostring,
        limits=params.limitsets[key], #[min,max,cut]
        inlimits=default_inlimits)

    #sy
    def sy_get(self):
        some_object=bpy.data.collections[collection_name].all_objects.values()[0]
        return (some_object.location[2])
        
    def sy_set(self,value):
        objects=bpy.data.collections[collection_name].all_objects.values()
        for ob in objects:
            ob.location[2]=value/1000 #in mm
        update_pos()

    key='sy'
    scannables[key]=Scannable(key, 
        getter=sy_get, #custom
        setter=sy_set, #custom
        call=default_call, 
        pos=default_pos,
        move_print=default_move_print, 
        get_str=det_get_str, #custom
        tostring=default_tostring,
        limits=params.limitsets[key], #[min,max,cut]
        inlimits=default_inlimits)

















    #-----------------------------------------------------------
    #Your Code Ends Here
    #-----------------------------------------------------------

    return(scannables)

    