"""user defined functions"""
import os

def get_additional_functions(dc):
    """
    Get user defined funcitions in a dictionary so they could be added to the namespace
    Sets up base namespace so functions could be defined
    """
    globals().update(dc.get_base_namespace())    #set up namespace
    
    def simbl (hkl_ob=None,
               val=None, 
               debug=False, 
               filename=None):
        """
        in: (sixc, [phi, chi, eta, mu, delta, gam]) or (hkl, [h,k,l])
        return: True if 'sim (hkl_ob, val)' did not throw an error
        out: usual simulation outputs and the simulated diffractometer state is stored in a file.
        
        If called without parameters or a simulation is not possible, the current state is saved instead
        
        debug - if the function should print the saved diffractometer state
        filename - location to write diffractometer state
        
        
        
        An extension of the sim command. 
        Simulates the given move and 
        stores the simulated position in a file that the i16sim simulation can import.  
        
        Author: Aurys Silinga
        19/08/2021
        tested on 20/08/2021, cm28156-10, i16
        
        Examples:
        simbl(hkl, [1,1,1]) # simulates a move to [1,1,1] and saves the [1,1,1] position to a file
        simbl() # saves current position to file
        simbl(debug=True) # saves current position and print( ub, sixc, en, lattice, constraints)
        """
        move_possible=True
        
        #Run 'sim' command if parameters are given
        if not (hkl_ob is None or val is None):
            try:
                sim(hkl_ob,val)
            except Exception as e:
                print(e)
                print('Simulation not possible')
                hkl_ob=None #use current position
                move_possible=False
                
        #get pseudomotor rotations
        try:
            if (hkl_ob is None or val is None):
                #use current position
                [p,c,e,m,d,g]=sixc()#phi,chi,eta,mu,delta,gam
                pos_now=[m,d,g,e,c,p] #convert to [mu,del,gam,eta,chi,phi]
                print('Writing current position:')
                print(sixc)
                
            elif (hkl_ob==hkl):
                p,va=hklcalc.hklToAngles(val[0],val[1],val[2],wl())
                pos_now=p.totuple() #[mu,delta,gam,eta,chi,phi]
                
            elif (hkl_ob==sixc):
                [p,c,e,m,d,g]=val#phi,chi,eta,mu,delta,gam
                pos_now=[m,d,g,e,c,p] #convert to [mu,del,gam,eta,chi,phi]
        except:
            pos_now=None
            move_possible=False
            
        #copy UB elements 
        #copy UB elements 
        try:
            ub_now=list(dc.ubcalc.UB)
        except:
            ub_now=None
            
        #get energy
        try:
            en_now=en()
        except:
            en_now=None
        
        #get constraints
        try:
            con_now=dc.cons.asdict
            if con_now=={}:
                con_now=None
        except:
            con_now=None
        
        #get lattice
        try:
            latt_now=latt()
        except:
            latt_now=None
            
        #get reference vector
        try:
            nphi_now=setnphi()
        except:
            nphi_now=None
        
        #save state to file
        if filename is None:
            directory=os.path.realpath(os.curdir)
            filename=os.path.join(directory,'diffractometer state files','sim.i16sim.txt')
        
        with open (filename,'w') as f:
        
            if not ub_now is None:
                f.write('ub\n')
                for row in ub_now:
                    for el in row:
                        f.write(str(el)+' ')
                    f.write('\n')
                    
            if not pos_now is None:
                f.write('sixc\n')
                for el in pos_now:
                    f.write(str(el)+' ')
                f.write('\n')
            
            if not en_now is None:
                f.write('en\n')
                f.write(str(en_now)+'\n')
            
            if not latt_now is None:
                f.write('lattice\n')
                f.write(str(latt_now[0])+'\n')
                for el in latt_now[1:]:
                    f.write(str(el)+' ')
                f.write('\n')
            
            if not con_now is None:
                f.write('con\n')
                for key in con_now:
                    val=con_now[key]
                    if isinstance(val,bool):
                        val=None #handle booleans to match GDA
                    f.write(str(key)+' '+str(val)+'\n')
                    
            if not nphi_now is None:
                f.write('azi_ref\n')
                for el in nphi_now:
                    f.write(str(el[0])+' ')
                f.write('\n')
        
        print('')
        print("Finished writing to "+filename)
        print('')
        
        #debug printing
        if debug:
            print('debug:')
            state_names=['ub','pos:[mu,del,gam,eta,chi,phi]','en','lattice','con','azimuthal_reference']
            state_now=(ub_now, pos_now, en_now, latt_now, con_now, nphi_now)
            for i in range(len(state_now)):
                print(state_names[i],state_now[i])
            print('')
            
        return (move_possible)



    #-----------------------------------------------------------
    #Your Code Goes Here
    #-----------------------------------------------------------


























    #-----------------------------------------------------------
    #Your Code Ends Here
    #-----------------------------------------------------------
    
    functions={}
    names=tuple(locals().keys())
    for name in names:
        if callable(locals()[name]):
            functions[name]=locals()[name]
            
    return(functions)

