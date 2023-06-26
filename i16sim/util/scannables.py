# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 10:37:22 2021
@author: Aurys Silinga

Functions and factories for creating scannable objects and composite limits

base_scannables(dc):
    get dict of base scannables
    
additional_scannables(dc):
    get dict of additional scannables
    
create_composite_limits(dc):
    get dict of composite limits
    
in_composite_limits(composite_limits, position=None, raise_error=False):
    If outside any of the composite limits
    
"""

import i16sim.util.eulerian_conversion as etok
import i16sim.parameters as params

#utility
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
    
    
#default scannable methods
def _get(self):
    """
    Default scannable method
    Get value
    """
    return(self.key)

def _get_str(self):
    """
    Default scannable method
    Get formatted string of value
    """
    return(str(self.get()))

def _call(self):
    """
    Default scannable method
    Get value
    """
    return (self.get())

def _set(self,value):
    """
    Default scannable method
    Set value
    """
    raise Exception(str(self.key)+" cannot be changed by 'pos' command")

def _pos(self,value=None,silent=False):
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
            
def _move_print(self):
    """
    Default scannable method
    Print string representing movement
    """
    print('Moving to '+str(self.key)+':',self.get_str())


def _tostring(self):
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

def _inlimits(self,value=None,raise_error=False):
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
    

class Scannable:
    """Class for defining scannable objects in a factory. 
    Each instance has its methods defined on creation and the methods can be modified.

    Attributes
    ----------
    key : str
        scannable id
    min : float, None
        minimum value for this scannable
    max : float, None
        maximum value for this scannable
    cut : float, None
        cut value for angles represented in degrees
    _get : function(self)
        Get value
    _set: function(self, *args, **kwargs)
        Set value
    _call: function(self)
        Get value
    _pos: function(self, value=None, **kwargs)
        Handle pos command
    _move_print: function(self)
        Print string representing movement
    _get_str: function(self)
        Get formatted string of value
    _tostring: function(self)
        Get string representation of scannable
    _inlimits: function(value=None, raise_error=False)
        If scannable value is inside its limits

        
    Methods
    -------
    get()
        calls self._get(self)
    get_str()
        calls self._get_str(self)
    __call__()
        calls self._call(self)
    set(*args,**kwargs)
        calls self._set(self, *args, **kwargs)
    pos(*args,**kwargs)
        calls self._pos(self, *args, **kwargs)
    move_print()
        calls self._move_print(self)
    __repr__() 
        calls self._tostring(self)
    inlimits(value=None, raise_error=False)
        calls self._inlimits(self, value, raise_error)
        
    """
    def __init__(self, key, getter=None, setter=None, call=None, pos=None,
                 move_print=None, get_str=None, tostring=None,
                 limits=None, inlimits=None):
        """
        Parameters
        ----------
        key : str
            scannable id
        getter : function, optional
            Get value
            The default is _get
        setter: function, optional
            Set value
            The default is _set
        call: function, optional
            Get value
            The default is _call
        pos: function, optional
            Handle pos command
            The default is _pos
        move_print: function, optional
            Print string representing movement
            The default is _move_print
        get_str: function, optional
            Get formatted string of value
            The default is _get_str
        tostring: function, optional
            Get string representation of scannable
            The default is tostring
        limits: [min:float ,max:float ,cut:float], optional
            limits for a single value scannable
            The default is [None,None,None]
        inlimits: function, optional
            If scannable value is inside its limits
            The default is _inlimits

        Returns
        -------
        None.

        """
        
        self.key=key
        
        #set limits if there are any
        if limits is not None:
            self.min=limits[0]
            self.max=limits[1]
            if len(limits)==3:
                self.cut=limits[2]
        
        #define methods
        if getter is None:
            self._get=_get
        else:
            self._get=getter
            
        if setter is None:
            self._set=_set
        else:
            self._set=setter
            
        if call is None:
            self._call=_call
        else:
            self._call=call
            
        if pos is None:
            self._pos=_pos
        else:
            self._pos=pos
            
        if move_print is None:
            self._move_print=_move_print
        else:
            self._move_print=move_print
            
        if get_str is None:
            self._get_str=_get_str
        else:
            self._get_str=get_str
            
        if tostring is None:
            self._tostring=_tostring
        else:
            self._tostring=tostring
            
        if inlimits is None:
            self._inlimits=_inlimits
        else:
            self._inlimits=inlimits

    #default values
    key=None
    min=None
    max=None
    cut=None
    
    def get(self):
        """Get value of scannable
        

        Returns
        -------
        any
            scannable value

        """
        return(self._get(self))
    
    def get_str(self):
        """Get formatted string of value
        

        Returns
        -------
        string 
            representation of scannable

        """
        return(self._get_str(self))
    
    def __call__(self):
        """Get value of scannable
        

        Returns
        -------
        any
            scannable value

        """
        return (self._call(self))
    
    def set(self,*args,**kwargs):
        """Set value and move diffractometer
        

        Parameters
        ----------
        *args : any
        **kwargs : any

        Returns
        -------
        None.

        """
        return(self._set(self,*args,**kwargs))

    def pos(self,*args,**kwargs):
        """diffcalc 'pos' command for this scannable.
        if no arguments given, print current value.
        if arguments given, set value to given value 
        

        Parameters
        ----------
        *args : any
        **kwargs : any

        Returns
        -------
        None.

        """
        return(self._pos(self,*args,**kwargs))
                
    def move_print(self):
        """Print string representing movement
        

        Returns
        -------
        None.

        """
        return(self._move_print(self))

    def __repr__(self):
        """repr(self) output
        

        Returns
        -------
        ret : string
            string representation of this scannable

        """
        try:
            ret=self._tostring(self)
        except:
            ret=(self.key+' could not get value')
        return (ret)
    
    def inlimits(self,value=None,raise_error=False):
        """If scannable value is within its limits
        

        Parameters
        ----------
        value : any, optional
            if value is None, check current value against limits.
            if value given, check that value.
            The default is None.
        raise_error : bool, optional
            True if the funciton should raise an error if value is outside its limits.
            False if function should just return 'False' if value is outside its limits.
            The default is False.

        Returns
        -------
        bool
            if scannable value is within its limits

        """
        return(self._inlimits(self,value,raise_error))
    
        
 #extened by cons.all.keys()
#Create a list of scannables:
def base_scannables(dc):
    """Create scannable objects with appropriate limits, getters, setters and return them in a dictionary.
    This is a factory for scannables.
    

    Parameters
    ----------
    dc : DiffcalcEmulator
        the current emulator instance


    Returns
    -------
    scannables : dict {str : Scannable}
        a dictionary of scannables indexed by their key and alternate keys. 
        Includes position, k_angle, constraint, pseudo_angle, and simple scan command scannables.

    """
    
    scannables={}
    simple_scannables=list(dc.cons.all.keys())
    simple_scannables.extend(params.simple_scannables)
    
    #simple scannables methods
    def tostring_simple(self):
        return(str(self.key))
    
    for key in simple_scannables:
        scannables[key]=Scannable(key,tostring=tostring_simple)
    
    #position scannables methods
    def get_pos(self):
        return(getattr(dc.position,self.key))
    def get_str_pos(self):
        return('%.5f'%(self.get()))
    def setter_pos(self,value):
        pos=dc.position.asdict
        pos[self.key]=value
        dc.moveto(list(pos.values()))
        
    for key in dc.position.asdict.keys():
        scannables[key]=Scannable(key,
                                  getter=get_pos,
                                  get_str=get_str_pos,
                                  setter=setter_pos,
                                  limits=params.limitsets[key])
        
    #real motor angles methods
    def get_k(self):
        return(dc.k_angles[self.key])
    def setter_k(self,value):
        dc.k_angles[self.key]=value
        dc.moveto([*dc.position.astuple[:3],*etok.KtoE(list(dc.k_angles.values()))])

    for key in dc.k_angles.keys():
        scannables[key]=Scannable(key,
                                  getter=get_k,
                                  get_str=get_str_pos,
                                  setter=setter_k,
                                  limits=params.limitsets[key])
        
    #virtual angles methods
    def get_virtual(self):
        if dc.ubcalc.UB is None:
            raise Exception ('UB matrix not set')
        else:
            return(dc.hklcalc.get_virtual_angles(dc.position)[self.key])
    def set_virtual(self,value):
        raise Exception(str(self.key)+
" cannot be changed directly. Use 'con' to change constraints and then call 'pos(hkl,[h,k,l])'")
    for key in params.virtual_angle_keys:
        scannables[key]=Scannable(key,
                                  getter=get_virtual,
                                  get_str=get_str_pos,
                                  setter=set_virtual
                                  )
        

    #other scannables ['sixc','hkl','h','k','l','kang','wl','en'] 
    #sixc methods
    key='sixc'
    def get_sixc(self):
        return(dc.get_position())
    def get_str_sixc(self):
        sixc=dc.get_position(asdict=True)
        ret=[' ']
        for key in sixc:
            ret.append(key+': %.5f'%sixc[key])
        ret='\n'.join(ret)
        return(ret)
    def set_sixc(self,val):
        val=dc.sixc_to_pos(val)
        dc.moveto(val)
    def move_print_sixc(self):
         sixc=dc.get_position(asdict=True)
         ret=[]
         for key in sixc:
             ret.append(key+': %.5f'%sixc[key])
         ret=', '.join(ret)
         ret='Moving to: '+ret
         print(ret)
    def inlimits_raw(self,value=None,raise_error=False):
        if value is None:
            position = dc.position
        else:
            position = dc.init_position_ob(value)
            
        #create dicts
        new_k_angles = etok.EtoK([position.eta, position.chi, position.phi])
        if new_k_angles[0]==None:
            if (raise_error):
                raise Exception('Eulerian to K conversion not possible in this mode')
            return False
        new_k_angles=dict(zip(dc.k_angles.keys(), new_k_angles))
        #print("here",new_k_angles, position.asdict)
        pos=position.asdict
        
        #check if any angles are beyond their limits
        ret=True
        for key,value in {**pos,**new_k_angles}.items():
            sc=scannables[key]
            if not sc.inlimits(value):
                ret=False
                output=(key+': '+str(value)+" must be between "+str(sc.min)+' and '+str(sc.max))
                if (raise_error):
                    raise Exception(output)
        return ret
    
    scannables[key]=Scannable(key,
                                getter=get_sixc,
                                get_str=get_str_sixc,
                                setter=set_sixc,
                                move_print=move_print_sixc,
                                inlimits=inlimits_raw
                                )
    
    
    #real motor angles methods
    key='kang'
    def get_kang(self):
        return(list(dc.k_angles.values())[::-1])
    def get_str_kang(self):
        kang=dc.k_angles
        ret=[]
        for key in kang:
            ret.append(key+': %.5f'%kang[key])
        ret.append('')
        ret='\n'.join(ret[::-1])
        return(ret)
    def setter_kang(self,value):
        dc.moveto([*dc.position.astuple[:3],*etok.KtoE(list(value[::-1]))])
    def inlimits_kang(self,value=None,raise_error=False):
        if value is not None:
            value=[*dc.position.astuple[:3],*etok.KtoE(list(value[::-1]))]
        return(inlimits_raw(self,value,raise_error=raise_error))
        
    scannables[key]=Scannable(key,
                            getter=get_kang,
                            get_str=get_str_kang,
                            setter=setter_kang,
                            move_print=move_print_sixc,
                            inlimits=inlimits_kang
                            )
    
    #hkl methods
    key='hkl'
    def get_hkl(self):
        return(dc.hklcalc.get_hkl(dc.position, dc.wl))
    def get_str_hkl(self):
        ret=["%.5f"%x for x in (dc.hklcalc.get_hkl(dc.position, dc.wl))]
        ret='['+', '.join(ret)+']'
        return (ret)
    def set_hkl(self,val):
        pos, virtual_angles = dc.pos_from_hkl(val)
        dc.moveto(pos.astuple)
    def pos_hkl(self,*args,**kwargs):
        if (dc.ubcalc.UB is None):
            raise Exception ('UB matrix not set')
        else:
            _pos(self,*args,**kwargs)
    def inlimits_hkl(self,value=None,raise_error=False):
        if value is not None:
            value, virtual_angles = dc.pos_from_hkl(value)
        return(inlimits_raw(self,value,raise_error=raise_error))  
            
    scannables[key]=Scannable(key,
                            getter=get_hkl,
                            get_str=get_str_hkl,
                            setter=set_hkl,
                            pos=pos_hkl,
                            move_print=move_print_sixc,
                            inlimits=inlimits_hkl
                                )
    #h, k, and l methods
    for i in range(len('hkl')):
        key='hkl'[i]
        def get_hkl_i(self):
            return(dc.hklcalc.get_hkl(dc.position, dc.wl)[i])
        def get_str_hkl_i(self):
            ret="%.5f"%self.get()
            return (ret)
        def set_hkl_i(self,val):
            hkl=list(dc.hklcalc.get_hkl(dc.position, dc.wl))
            hkl[i]=val
            pos, virtual_angles = dc.pos_from_hkl(hkl)
            dc.moveto(pos.astuple) 
            
        scannables[key]=Scannable(key,
                                getter=get_hkl_i,
                                get_str=get_str_hkl_i,
                                setter=set_hkl_i,
                                pos=pos_hkl,
                                move_print=move_print_sixc
                                    )
    #wavelength methods
    key='wl'
    def get_wl(self):
        return(dc.wl)
    def get_str_wl(self):
        return ("%.5f A"%self.get())
    def set_wl(self,val):
        dc.wl=val
        dc.update_pos()
    def move_print_wl(self):
        print(self.key,'set to:',self.get_str())
        
    scannables[key]=Scannable(key,
                        getter=get_wl,
                        get_str=get_str_wl,
                        setter=set_wl,
                        move_print=move_print_wl
                        )
    
    #energy methods
    key='en'
    AxkeV=12.398419745831506
    def get_en(self):
        return(AxkeV/dc.wl)
    def get_str_en(self):
        return ("%.5f keV"%self.get())
    def set_en(self,val):
        dc.wl=AxkeV/val
        dc.update_pos()
    def move_print_wl(self):
        print(self.key,'set to:',self.get_str())
        
    scannables[key]=Scannable(key,
                        getter=get_en,
                        get_str=get_str_en,
                        setter=set_en,
                        move_print=move_print_wl
                        )
    
    #adding extra pointers for additional names
    for key in params.renamed:
        scannables[key]=scannables[params.renamed[key]]
    
    return scannables



class CompositeLimit():
    """A limit that can depend on multiple angles"""
    
    
    def __init__(self,key,inlimits,dc,error_str=None,args=None):
        """
        

        Parameters
        ----------
        key : str
            id for limit
        inlimits(self, angles, args): : function
            if diffractometer is in the limits defined by this object
            angles - dictionary of eulerian and real rotations normalised between -180 to 180 deg
            args - any arguments you need
        dc : DiffcalcEmulator
            the current emulator instance
        error_str : str, optional
            Exception description if exception for this limit is thrown. 
            The default is None.
        args : any, optional
            parameters for this limit. 
            The default is None.

        Returns
        -------
        None.

        """
        self.key=key
        self._inlimits=inlimits
        self.error_str=error_str
        self.args=args
        self.dc=dc
    
    def normalise_angles(self,position):
        """
        Parameters
        ----------
        dc : DiffcalcEmulator object
        position : tuple of floats
            Eulerian angles

        Returns
        -------
        angles : dictionary {str : float}
            eulerian and k_angles normalised between -180 and 180 deg
        """
        dc=self.dc
        position = dc.init_position_ob(position)
            
        #create dicts
        new_k_angles = etok.EtoK([position.eta, position.chi, position.phi])
        new_k_angles=dict(zip(dc.k_angles.keys(), new_k_angles))
        
        if None in new_k_angles.values():
            return None
        
        position=position.asdict
        angles={**new_k_angles,**position}
        for key in angles:
            angles[key]=setrange(angles[key])
        return angles
        
    def inlimits(self,position=None,raise_error=False):
        """if diffractometer is in the limits defined by this object. 
        Calls the custom function defined on creation.
        

        Parameters
        ----------
        position : tuple of floats, optional
            Eulerian angles representing a position. 
            The default is the current position.
        raise_error : bool, optional
            If function should raise error if diffractometer is outside the limits 
            defined by this object. 
            The default is False.

        Raises
        ------
        Exception
            raises Exception (self.error_str) if raise_error is True and self._inlimits returns False

        Returns
        -------
        bool
            self._inlimits.(self, normalised_angles, self.args)

        """
        dc=self.dc
        if position is None:
            position=dc.position.astuple
        angles=self.normalise_angles(position)
        
        #check for problems
        if angles is None:
            if (raise_error):
                raise Exception('Eulerian to K conversion not possible in this mode')
            return False
        
        ret=self._inlimits(self,angles,self.args)
        
        if (raise_error and ret==False):
            raise Exception(str(self.error_str))
        
        return (ret)
    

def in_composite_limits(composite_limits,position=None,raise_error=False):
    """If outside any of the composite limits
    

    Parameters
    ----------
    composite_limits : dict {str : CompositeLimit}
        a dictionary of composite limits indexed by their keys.
    position : tuple of floats, optional
        Eulerian angles representing a position. 
        The default is the current position.
    raise_error : bool, optional
        If function should raise error if diffractometer is outside its limits 
        The default is False.

    Returns
    -------
    bool
        If given position is outside any of the composite limits

    """
    for limit in composite_limits.values():
        if not limit.inlimits(position,raise_error):
            return False
    return True


    
def create_composite_limits(dc):
    """Create user defined limits and return them in a dictionary.
    This is a factory for composite limits.

    Parameters
    ----------
    dc : DiffcalcEmulator object

    Returns
    -------
    composite_limits : dict {str : CompositeLimit}
        a dictionary of composite limits indexed by their keys. 
        
    Factory layout:
        #define your parameters and methods
        your_key = 'limit name' # must be a unique name
        
        def your_inlimits(self, angles, args): 
            # if diffractometer is in the limits defined by this object
            #
            # angles - dictionary of eulerian and real rotations normalised between -180 to 180 deg
            # args - any arguments you need
            #
            # must return True of False
            return (True)
            
        #create limit object
        your_limit = CompositeLimit(your_key,
                                    inlimits= your_inlimits,
                                    dc=dc,
                                    args= your_args,
                                    error_str= your_error_str
                                    )
        
        #add your limit to the dictionary
        composite_limits[ your_limit.key ] = your_limit

    """
    composite_limits={}
    
    #(ktheta - delta) limit
    def ktheta_delta (self,angles,args):
        ktheta=angles['ktheta']
        delta=angles['delta']
        #args = 77.5
        
        if ktheta < 0:
            ktheta=ktheta+360
            
        return ((ktheta - delta) <= args)
    
    #add the limit to the dict
    key='ktheta-delta'
    args=params.limitsets[key]
    composite_limits[key]=  CompositeLimit(key,
                                           inlimits=ktheta_delta,
                                           dc=dc,
                                           args=args,
                                           error_str='(ktheta - delta) must be <= '+str(args)) 
    #(gamma - mu) limit
    def gamma_mu(self,angles,args):
        gamma=angles['nu']
        mu=angles['mu']
        #args = -1
        
        return((gamma-mu)>=args)
    
    #add the limit to the dict
    key='gamma-mu'
    args=args=params.limitsets[key]
    composite_limits[key]=  CompositeLimit(key,
                                           inlimits=gamma_mu,
                                           dc=dc,
                                           args=args,
                                           error_str='(gamma - mu) must be >= '+str(args)) 


    #-------------------------
    #Add New Limits Here
    #-------------------------







    #------------------------
    #Finish adding here
    #------------------------
    
    return (composite_limits)  
    

            
            
            
            