# -*- coding: utf-8 -*-
"""
Created on 14/07/2021

@author: Aurys Silinga
@python: 3.9.2
@version 1.2B

Functions for converting angles of rotation between Eulerian space, 
real motor space, and Blender simulation space. 
For the I16 six-axis Kappa diffractometer.

The script was shamelessly hacked together from bits of code 
by Alessandro Bombardi and Dan Porter
"""

import math
pi = math.pi
asin = math.asin
atan = math.atan
tan = math.tan
sin = math.sin
cos = math.cos
deg = math.degrees
radians= math.radians


#constants
kalpha=50.0*pi/180 # limits the range of possible chi in different modes. 
#Maybe the angle between kth and kappa arms when phi || z ? Or angle needed for chi=90? 
chi_magic = 65.595503 # some unexplained angle


def setRange(x,m=-180.,M=180.):
    """
    Simplify the numerical value of an angle 'x'
    in: x, m, M # in degrees
    out: x equivalent, such that m < x < M
    """
    if x  <  m:
        x=x+360.
        return setRange(x,m,M)
    elif x > M:
        x=x-360.
        return setRange(x,m,M)
    else:
        return x


def EtoK(e_angles, mode=1, kalpha=kalpha, chi_magic = chi_magic):
    """
    Convert from Eulerian space angles to real world motor angles
    in: e_angles = [eta_now, chi_now, phi_now] # in degrees
    out : k_angles = [ktheta, kappa, kphi] # in degrees
    
    This function takes some weird constant parameters, and a mode parameter.
    The code requires mu constraints (mu = 0 or mu = 180 degrees) to work in the specified modes.
    The modes allow to invert the movement of kappa (kappa -> (-1)*kappa) and adjust 
    the other angles accordingly. 
    The inverted modes could be useful when working with large equipment.
    
    # Coversion Modes:
    # Mode; Constraint; Effect
    # "  1; mu=0      ; Normal operation
    # "  2; mu=0      ; kappa -> (-1)*kappa
    # "  3; mu=180    ; Normal operation, with mu on the opposite side of the diffractometer. 
    phi rotates >180 degrees, be careful with pipes!
    # "  4; mu=180    ; kappa -> (-1)*kappa, with mu on the opposite side. 
    phi rotates >180 degrees, be careful with pipes!
        
    Potential upgrade: Include mu in the calculations so the code could work for any value of mu.
    
    Known Bugs:
        1. Rotation matrix algebra cannot be varified
        
    Fixed Bugs (since version 1.0):
        1. Weird behaviour at chi=100.
        2. Errors of accessing undefined k_angle variables
        3. Total ugliness
        4. Added setRange before checking abs(chi)
    """
    #to prevent accessing undefined variables
    [[theta_K1,K1,phi_K1],[theta_K2,K2,phi_K2],[theta_K3,K3,phi_K3],[theta_K4,K4,phi_K4]]=[[None]*3]*4
    
    theta_now = setRange(e_angles[0])
    chi_now = setRange(e_angles[1])
    phi_now = setRange(e_angles[2])
    
    #calculates modes 1 and 2 for -100 < chi < 100
    if abs(chi_now) < kalpha*180./pi*2:
        delta1=-asin(tan(pi/180.*chi_now/2.)/tan(kalpha))
        K1=-asin(cos(delta1)*sin(pi/180*chi_now)/sin(kalpha))*180/pi

        if abs(chi_now) > chi_magic and chi_now > 0.:
            K1=setRange(180-K1)
        elif abs(chi_now) > chi_magic and chi_now < 0.:
            K1=setRange(-180-K1)
            
        theta_K1=setRange(theta_now-delta1*180/pi,-90.,270.)
        phi_K1=setRange(phi_now-delta1*180/pi,-90.,270.)
        
        theta_K2=setRange(theta_now-(pi-delta1)*180/pi,-90.,270.)
        phi_K2=setRange(phi_now-(pi-delta1)*180/pi,-90.,270.)
        K2=setRange(-K1)
    
    #if chi is out of range
    elif abs(chi_now) >= kalpha*180./pi*2:
        K1=None
        K2=None
        phi_K1=None
        phi_K2=None
        theta_K1=None
        theta_K2=None
        
    else:
        raise Exception('chi is wrong')
        
    #calculates modes 3 and 4 for -180 < chi < -100 and 100 < chi < 180
    if abs(chi_now) > (180.-kalpha*180./pi*2):
        chi_r =  setRange(180-chi_now)
        delta3=-asin(tan(pi/180.*chi_r/2.)/tan(kalpha))
        K3=-asin(cos(delta3)*sin(pi/180*chi_r)/sin(kalpha))*180/pi
        
        if abs(chi_r) > chi_magic and chi_r > 0.:
            K3=setRange(180-K3)
        elif abs(chi_r) > chi_magic and chi_r < 0.:
            K3=setRange(-180-K3)
            
        theta_K3=setRange(theta_now-delta3*180/pi,-90.,270.)
        phi_K3=setRange(phi_now-delta3*180/pi+180,-90.,270.)
        theta_K4=setRange(theta_now-(pi-delta3)*180/pi,-90.,270.)
        phi_K4=setRange(phi_now-(pi-delta3)*180./pi+180.,-90.,270.)
        K4=setRange(-K3)
        
    #if chi is out of range
    elif abs(chi_now) <= (180.-kalpha*180./pi*2):
        K3=None
        K4=None
        phi_K3=None
        phi_K4=None
        theta_K3=None
        theta_K4=None
        
    else:
        raise Exception('chi is wrong')
        
    Kvalues = [[theta_K1,K1,phi_K1],[theta_K2,K2,phi_K2],[theta_K3,K3,phi_K3],[theta_K4,K4,phi_K4]]
    #print(Kvalues)

    k_angles=Kvalues[mode-1]
    return(k_angles)


def KtoE(k_angles, mode=1, kalpha=kalpha):
    """
    Convert k_angles of real motors to e_angles in Eulerian space
    in : k_angles = [ktheta, kappa, kphi] # in degrees
    out: e_angles = [eta_now, chi_now, phi_now] # in degrees
    mode: must be the same mode as in EtoK()
    """

    theta_K_now=setRange(k_angles[0],-90,270)
    K=setRange(k_angles[1])
    phi_K_now=setRange(k_angles[2],-90,270)
    
    if mode==1:
        gamma = -atan(cos(kalpha)*tan(K/2.*pi/180.))*180./pi
        chi   = -2*asin(sin(K*pi/180/2)*sin(kalpha))*180./pi
        theta =  theta_K_now-gamma
        phi   =  phi_K_now-gamma
        
    elif mode==2:
        gamma = -atan(cos(kalpha)*tan(K/2.*pi/180.))*180./pi+180.
        chi   = 2*asin(sin(K/2*pi/180)*sin(kalpha))*180./pi
        theta = theta_K_now-gamma
        phi   = phi_K_now-gamma
        
    elif mode==3:
        gamma = -atan(cos(kalpha)*tan(K/2.*pi/180.))*180./pi
        chi   = 2*asin(sin(K/2*pi/180)*sin(kalpha))*180./pi+180.
        theta = theta_K_now-gamma
        phi   = phi_K_now-gamma+180.
        
    elif mode==4:
        gamma = -atan(cos(kalpha)*tan(K/2.*pi/180.))*180./pi
        chi = -2*asin(sin(K/2*pi/180)*sin(kalpha))*180./pi+180.
        theta =theta_K_now-gamma+180.
        phi=phi_K_now-gamma
        theta=setRange(theta,-90.,270.)
        chi=setRange(chi)
        phi=setRange(phi,-90.,270.)
        
    else:
        raise Exception('mode not recognized')
        
    e_angles = [setRange(theta,-90., 270.), setRange(chi), setRange(phi,-90., 270.)]
    #e_angles = [theta,chi,phi]
    return e_angles


def KtoB(k_angles, degrees=False):
    """
    Convert k_angles of real motors to correspoding b_angles in Blender
    in: [kmu,kdelta,kgamma,ktheta,kappa,kphi] # in degrees
    out: [btheta,bkappa,bphi] #blender model equivalend angles
    degrees: if Blender angles should be in degrees
    """
    if (len(k_angles)==3):
        [ktheta, kappa, kphi] = k_angles
        b_angles = [-ktheta, -kappa, -kphi]
    elif (len(k_angles)==6):
        [kmu,kdelta,kgamma,ktheta,kappa,kphi] = k_angles
        b_angles = [kmu, -kdelta, kgamma, -ktheta, -kappa, -kphi]
    else:
        raise Exception('wrong number of angles given')
        
    if (degrees==False):
        b_angles = [radians(a) for a in b_angles]
               
    return (b_angles)


def BtoK(b_angles, degrees=False):
    """
    Convert b_angles in Blender to correspoding real motor k_angles  
    in: [bmu,bdelta,bgamma,btheta,bkappa,bphi] # blender model equivalend angles
    out: [ktheta,kappa,kphi] # in degrees
    degrees: if Blender angles are in degrees
    """
    if (len(b_angles)==3):
        [ktheta, kappa, kphi] = b_angles
        k_angles = [-ktheta, -kappa, -kphi]
    elif (len(b_angles)==6):
        [kmu,kdelta,kgamma,ktheta,kappa,kphi] = b_angles
        k_angles = [kmu, -kdelta, kgamma, -ktheta, -kappa, -kphi]
    else:
        raise Exception('wrong number of angles given')
        
    if (degrees==False):
        k_angles = [deg(a) for a in k_angles]

    return (k_angles)


#print(KtoB(EtoK([20,0,0]),degrees=True))
#print(KtoE(EtoK([-15,80,290],mode=3),mode=3))
#print(KtoB(EtoK([0,100,0],mode=1),degrees=True)," 1")
#print(KtoB(EtoK([0,90,0],mode=3),degrees=True)," 3")
#print(EtoK([0,100,0],mode=1))
#print(KtoE(BtoK(KtoB(EtoK([20,90,-190],mode=1) ) ),mode=1 ) )
#print(BtoK(KtoB([10,20,30,40,50,60])))