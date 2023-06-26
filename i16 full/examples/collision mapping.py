from i16sim.commands import *
enable_lm(False)
clear()

class Collision():
    def __init__(self,k_vals,intersections,sixc_val=None):
        self.k_vals=k_vals
        self.sixc_val=sixc_val
        self.intersections=intersections
        
    def tostring(self):
        string=[]
        intersect = (self.intersections!=[]) #True if intersects
        for val in self.k_vals:
            string.append('%.1f'%val)
        string.append(str(intersect))
        string=' '.join(string)
        return (string)

        

pos(sixc, [0,0,0,0,0,0])
collisions=[]

#scanning ktheta,kappa space at delta=mu=gamma=phi=0
phi_val=0
for kth_val in range(-179,180,20):
    for kap_val in range(-179,180,20):
        pos(kang, [phi_val,kap_val,kth_val])
        collisions.append(Collision(kang(),intersect(),sixc()))
     
with open('collision map.txt','w') as f:   
    f.write("# kphi, kappa, ktheta, if_was_collision. mu=delta=gamma=0. Using cryostat with dome and no pipes\n")
    for col in collisions:
        f.write(col.tostring()+'\n')
        

