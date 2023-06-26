# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 18:40:23 2021

@author: axw86756
"""

import matplotlib.pyplot as plt
import numpy as np

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


kappa=[]
ktheta=[]
col=[]

with open('collision map.txt','r') as f:
    for line in f:
        if line.startswith('#'):
            continue
        
        line=line.strip().split()
        kappa.append(setrange(float(line[1])))
        ktheta.append(setrange(float(line[2])))
        col.append(line[3]=='True')
        
col=np.array(col)
ktheta=np.array(ktheta)
kappa=np.array(kappa)

plt.figure(figsize=(5,5))
plt.scatter(ktheta[col==False],kappa[col==False],label='Good')
plt.scatter(ktheta[col==True],kappa[col==True],label='Collision')
plt.xlabel('ktheta, deg')
plt.ylabel('kappa, deg')
plt.title('2D Collision map for kphi=mu=delta=gamma=0.\n With cryostat and dome, no pipes.')
plt.legend()
plt.savefig('Map graph.png', dpi=300)
plt.show()