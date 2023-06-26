from i16sim.commands import *
enable_lm(True)

newub('example')
setlat('example_lat', 5.0, 5.0, 3.0, 90.0, 90.0, 120)
pos(en,8)

#if we know one reflection
ttheta_val=c2th([0,0,3])
pos(sixc, [-42.82543054214057, 90.86852921076816, ttheta_val/2, 0.0, ttheta_val, 0.0])  
addref([0,0,3],'003')

trialub()
con(mu,0,gam,0,bisect,True) #

sim(hkl,[1,1,1]) #always simulate before moving
pos(hkl,[1,1,1])

#trial ub is not exactly correct, so we scan for second peak
scancn(chi, 0.025, 41) #step of 0.025 deg 41 times

pos(chi, 40.057)
addref([1,1,1],'111')
checkub() #propper UB looks good
ub()