from i16sim.commands import *
enable_lm(False)
clear()

class Collision():
    def __init__(self,eta_val,chi_val,intersections):
        self.eta=eta_val
        self.chi=chi_val
        self.intersections=intersections
        
    def tostring(self):
        if self.intersections==[]:
            col_string='good'
        else:
            col_string='would be a collision between '+str(self.intersections)
        return('eta: %.3f, chi: %.3f '%(self.eta,self.chi) +col_string)

pos(sixc, [0,0,0,0,0,0])
collisions=[]

for eta_val in range(45,51,5):
    for chi_val in range(40,81,10):
        pos(eta,eta_val,chi,chi_val)
        intersections=intersect()
        collisions.append(Collision(eta_val,chi_val,intersections))

for col in collisions:
    print(col.tostring())