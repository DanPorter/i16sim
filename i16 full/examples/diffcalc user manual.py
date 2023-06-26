"""
Follows the diffcalc user guide examples: 'https://diffcalc.readthedocs.io/en/latest/youmanual.html' 
but the commands use the diffcalc emulator syntax. Also comments on differencences between diffcalc and emulator.
"""


from i16sim.commands import *
clear() #remove previous calculations
enable_lm(True) #enable realistic limits

print("GETTING HELP")
print(">>> help(dc) #all commands")
#print(help(dc))

print(">>> help(hkl) #scannable structure")
#help(hkl)
print("Command list is so long console cannot handle it. Instead use Blender's python console as it has autcompletion which includes documentation.")

print(">>> help(loadub) #specific command")
#help(loadub)

print("SCANNABLES and their multiple variable names")
print(">>> pos()")
pos()

print("START NEW UB CALCULATION")
print(">>> ub()")
ub()

print(">>> newub('example')")
print(">>> setlat('1Acube', 1, 1, 1, 90, 90, 90)")
newub('example')
setlat('1Acube',1,1,1,90,90,90)

print(">>> newub() #interactive definition not implemented")
try:
    newub()
except Exception as e:
    print('Exception:',e)
    
print(">>> ub()")
ub()

print("LOAD UB CALCULATION")
print(">>> lastub()")
lastub()

print(">>> listub()")
listub()

print(">>> loadub(0)")
loadub(0)

print("GENERATE U FROM TWO REFLECTIONS")

print(">>> newub('example')")
print(">>> setlat('1Acube', 1, 1, 1, 90, 90, 90)")
newub('example')
setlat('1Acube',1,1,1,90,90,90)

print(">>> pos(wl, 1)")
pos(wl, 1)
print(">>> c2th([0, 0, 1])")
c2th([0, 0, 1])

print(">>> pos(sixc, [0, 90, 30, 0, 60, 0]) #i16 beamline uses different number order to diffcalc")
pos(sixc, [0, 90, 30, 0, 60, 0])

print(">>> addref([0, 0, 1])")
addref([0, 0, 1])

print(">>> diffcalc_order = [0, 90, 0, 45, 45, 90] #[mu, delta, gamma, eta, chi, phi]")
print(">>> i16_order = pos_to_sixc(diffcalc_order) #[phi, chi, eta, mu, delta, gamma]")

print(">>> pos(sixc, i16_order)")
pos(sixc, pos_to_sixc([0, 90, 0, 45, 45, 90]))

print(">>> addref([0, 1, 1])")
addref([0, 1, 1])

print(">>> checkub()")
checkub()

print(">>> con(mu, 0, gam, 0, bisect, True) #always need constraints before moving in hkl space")
con(mu, 0, gam, 0, bisect, True)

print(">>> pos(hkl, [1,0,1])")
pos(hkl, [1,0,1])

print(">>> addref([1,0,1])")
addref([1,0,1])

print(">>> calcub(1,3)")
calcub(1,3)

print(">>> checkub()")
checkub()

print("GENERATE U FROM ONE REFLECTION")
print(">>> trialub() #tends to be wrong for more complex crystals")
trialub()

print(">>> ub()")
ub()

print("EDIT REFLECTION LIST")
print(">>> showref()")
showref()

print(">>> dc.ubcalc.swap_reflections(1,2) #No reason to do this in practice, but it is still possible with internal commands")
dc.ubcalc.swap_reflections(1,2)

print(">>> dc.ubcalc.del_reflection(1)")
dc.ubcalc.del_reflection(1)

print(">>> showref()")
showref()

print("GENERATE U FROM LATTICE DIRECTIONS")

print(">>> pos(sixc,[0,0,0,0,90,0])")
print(">>> addorient([0,0,1],[0,0,1],'c*=z direction')")
pos(sixc,[0,0,0,0,90,0])
addorient([0,0,1],[0,0,1],'c*=z direction')

print(">>> pos(sixc,[0,0,0,0,0,0])")
print(">>> addorient([1,0,0],[1,0,0],'a*=-x direction') #Notice -x in i16 sample coordinate system (shown in simulation) corresponds to +x in the diffcalc coordinate system (used to specify orientations)")
pos(sixc,[0,0,0,0,0,0])
addorient([1,0,0],[1,0,0],'a*=-x direction')

print(">>> calcub('a*=-x direction','c*=z direction')")
calcub('a*=-x direction','c*=z direction')

print(">>> ub() #Notice same ub as before")
ub()


print("UNIMPLEMENTED COMMANDS")
print("miscut, manual specification, fitting multiple reflections, and crystal refinement commands have not been implemented in the emulator. They are available internally in the diffcalc-core ub calculator object 'dc.ubcalc', but have not been fully tested.")

print("REFERENCE VECTORS")
print(">>> setnphi([1, 0, 0])")
setnphi([1, 0, 0])

print(">>> print(setnphi())")
print(setnphi())


print(">>> setnhkl([1, 0, 0])")
setnhkl([1, 0, 0])

print(">>> surfnphi([0, 0, 1])")
surfnphi([0, 0, 1])

print(">>> surfnhkl([0, 0, 1])")
surfnhkl([0, 0, 1])

print("CONSTRAINING SOLUTIONS FOR MOVING IN HKL SPACE")

print(">>> con()")
con()

print(">>> con(gam, 0, mu, 0, a_eq_b, True) #Need to specify True for boolean constraints")
print(">>> con(gam, 0, mu, 0, a_eq_b, True)")
con(gam, 0, mu, 0, a_eq_b, True)

print(">>> con(qaz,90,mu,0,a_eq_b,True)")
con(qaz,90,mu,0,a_eq_b,True)
print(">>> con(alpha,1)")
con(alpha,1)

print(">>> con(naz,90,mu,0,betain,1)")
con(naz,90,mu,0,betain,1)

print(">>> con(naz,0,eta,0,betain,1)")
con(naz,0,eta,0,betain,1)

print(">>> con(naz,0,phi,0,betain,1)")
con(naz,0,phi,0,betain,1)


print(">>> con(gam, 0, mu, 0, psi, 0)")
con(gam, 0, mu, 0, psi, 0)

print(">>> con(mu,10)")
con(mu,10)
print(">>> pos(psi,10) #constraints do not have proper scannables and are overwritten by (pseudo)angles")
try:
    pos(psi,10)
except Exception as e:
    print("Exception:",e)
print()
    
print("CONFIGURING LIMITS AND CUTS")
print(">>> showlm()")
showlm()

print("Configuring cuts is the quickest way to break something. Instead you can disable or enable all limits simultaneously for the sake of the simulation.")
print(">>> enable_lm(False)")
enable_lm(False)

print(">>> enable_lm(True)")
enable_lm(True)
print()

print(">>> setlm(chi,[-88,88])")
setlm(chi,[-88,88])
print(">>> showlm(chi)")
showlm(chi)
print(">>> setlm(chi,[-90,99]) #reset imediately")
setlm(chi,[-90,99])

print("MOVING IN HKL SPACE")
print(">>> setlmcon (gam,0,mu,0,a_eq_b,True)")
con (gam,0,mu,0,a_eq_b,True)

print(">>> setlmsim(hkl,[0,1,1])")
sim(hkl,[0,1,1])

print(">>> pos(hkl,[0,1,1])")
pos(hkl,[0,1,1])

print(">>> pos(sixc)")
pos(sixc)

print(">>> sim(sixc,[0,90,30,0,60,0])")
sim(sixc,[0,90,30,0,60,0])
    
print("SCANNING IN HKL SPACE")

print(">>> pos(hkl, [0,0,1])")
pos(hkl, [0,0,1])

print(">>> con(psi,0)")
con(psi,0)
print(">>> scan(psi,0,4,1)")
scan(psi,0,4,1)

print(">>> scancn(eta,0.1,5)")
scancn(eta,0.1,5)

print(">>> con(gam,0,mu,0,phi,0)")
con(gam,0,mu,0,phi,0)

print(">>> scan(hkl,[1,0,0],[1,0.2,0],[0,0.1,0])")
scan(hkl,[1,0,0],[1,0.2,0],[0,0.1,0])

print("End of manual")
print()
