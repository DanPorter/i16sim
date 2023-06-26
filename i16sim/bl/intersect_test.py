"""
function for checking if meshes in the simulation are intersecting
"""

import bpy
import bmesh 
import mathutils
BVHTree = mathutils.bvhtree.BVHTree # shorthand

import i16sim.parameters as params

#Constants
Arm_name = params.arm_name #"Armature"
mesh_names = params.mesh_names

def ShowMessageBox(message = "", title = "Collision Detected", icon = 'ERROR'):
    """Draw a popup window with message in Blender
    

    Parameters
    ----------
    message : str, optional
        Message to show. The default is "".
    title : str, optional
        Title of popup window. The default is "Collision Detected".
    icon : str, optional
        Icon id. The default is 'ERROR'.

    Returns
    -------
    None.
    
    example: 
        ShowMessageBox("This is a message") 
    """

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


#Print objects that are intersecting
def is_intersect(Arm_name = None, mesh_names=mesh_names, check_all_meshes=True, verbose=False, popups=False, exceptions=None):
    """Check if meshes in the simulation are intersecting
    

    Parameters
    ----------
    Arm_name : str, optional
        armature name. The default is params.arm_name.
    mesh_names : [str], optional
        mesh ids. The default is mesh_names.
    check_all_meshes : bool, optional
        if a list of meshes should be generated so all possible are checked.
        Checks are meshes that have the same name as their parent object to avoid misslabling.
        Only checks meshes that are visible in Blender's 3D view, 
        so disabling them is easy in the outliner.
        The default is True.
    verbose : bool, optional
        print every check. The default is False.
    popups : bool, optional
        Draw popup window if collision is detected. The default is False.
    exceptions : TYPE, optional
        sets of meshes that should touch. The default is None.


    Returns
    -------
    intersections : list [[mesh1,mesh2],...,[mesh69,mesh420]]
        list of intersecting mesh name pairs.

    """
    
    intersections=[] # returns list of intersecting mesh names.
    
    try:
        #set up context, view, and selection
        bpy.context.view_layer.objects.active=bpy.data.objects[0]
        if (bpy.data.objects[0].hide_viewport==False):
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")

        #shorthands 
        objects = bpy.context.scene.objects #object dictionary
        
        # get the current valid mesh names
        if (check_all_meshes):
            mesh_names=[]
            for object in objects:
                if (object.type=='MESH'):
                    if (object.name==object.data.name):
                        mesh_names.append(object.data.name)
        
        #[print(mesh.name) for mesh in bpy.data.meshes]
        #[print(mesh) for mesh in mesh_names]
        
        #shorthands 
        objects = bpy.context.scene.objects #object dictionary
        
        #create clones with armature deform transforms 
        #(cheesy hack to preserve parenting and pose)
        clone_names=[]
        for name in mesh_names:
            #for each object make it active and selected
            objects[name].select_set(True)
            bpy.context.view_layer.objects.active = objects[name]
            bpy.context.view_layer.update()
            
            #print(name)
            
            #if object is hidden, do not check it
            if (bpy.context.view_layer.objects.active.visible_get() == False or
             bpy.context.view_layer.objects.active.hide_select == True):
                continue
            
            try:
                #create clone and rename it so we can trace back the original
                bpy.ops.object.convert(target='MESH', keep_original=True) #creates clone and selects the clone
                new_name=name+".clone"
                bpy.context.selected_objects[0].name=new_name
                bpy.context.selected_objects[0].data.name=new_name #rename child mesh
                
                #save name and 
                clone_names.append(new_name)
            except:
                raise Exception("Could not copy visual mesh of "+name)
                
                
            #clean up before next clone    
            bpy.ops.object.select_all(action="DESELECT")
            
            #refresh object dictionary
            objects = bpy.context.scene.objects
            
        #print(clone_names) 
        
        if (verbose):
            print("Checked meshes: ",[name[:-6] for name in clone_names])
        
        #check every object for intersection with every other object
        #print("Starts Here")
        for i in range(len(clone_names)):
            for j in range(i,len(clone_names)):
                if i == j:
                    continue
                name1=clone_names[i]
                name2=clone_names[j]
                #print(name1,name2)
                
                #check is the meshes should be touching
                to_skip=False
                for exception in exceptions:
                    if ((name1[:-6] in exception) and (name2[:-6] in exception)):
                        to_skip=True
                        break
                if (to_skip):
                    continue


            #create bmesh objects
                bm1 = bmesh.new()
                bm2 = bmesh.new()
                

            #fill bmesh data from objects
                bm1.from_mesh(objects[name1].data)   
                bm2.from_mesh(objects[name2].data)  
                
                #get matrix of transform
                m_world1=objects[name1].matrix_world
                m_world2=objects[name2].matrix_world

            #fixed it here: Transform the objects based transform
                bm1.transform(m_world1)   
                bm2.transform(m_world2)  

            #make BVH tree from BMesh of objects
                obj_now_BVHtree = BVHTree.FromBMesh(bm1)
                obj_next_BVHtree = BVHTree.FromBMesh(bm2)   

            #get intersecting pairs
                inter = obj_now_BVHtree.overlap(obj_next_BVHtree)

            #if list of vertexes and lines is empty, no objects are touching
                #print(inter)

                
                
                if inter != []:
                    intersections.append([name1[:-6],name2[:-6]])
                    print(name1[:-6] + " and " + name2[:-6] + " are touching!")  
     
        if (intersections==[]):
            print("No intersections") 
        else:
            if(popups):
                ShowMessageBox("Intersections between: "+str(intersections))
            for pair in intersections:
                for ob_name in pair:
                    bpy.data.objects[ob_name].select_set(True)
        
        
    finally:
        #delete clones
        for name in clone_names:
            bpy.data.objects.remove(objects[name], do_unlink=True)
            bpy.data.meshes.remove(bpy.data.meshes[name])
        print()
    
    return (intersections)

#testing
"""
#Arm_name = "Armature"
#mesh_names = ["base","detector arm","mu","delta","gamma","theta","kappa","phi","detector arm back","detector carriage"] # a minimal list of meshes in case automatic detection does not work
#exceptions=[["delta","detector arm"],['high pressure','high pressure holder','phi']] #meshes that should touch
#print(is_intersect(Arm_name = Arm_name, mesh_names=mesh_names, check_all_meshes=True, verbose=False, popups=False, exceptions=exceptions))  #Call FN
"""
