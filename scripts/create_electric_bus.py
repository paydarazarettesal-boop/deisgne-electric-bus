import bpy
import math
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, roughness=0.4):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    return m

white=mat("Body white",(0.82,0.88,0.91))
dark=mat("Window glass",(0.035,0.11,0.16),0.25)
black=mat("Rubber",(0.018,0.022,0.025))
silver=mat("Wheel hubs",(0.42,0.48,0.53),0.65)
blue=mat("Electric blue",(0.0,0.36,0.85))
red=mat("Tail lights",(0.9,0.035,0.02))

def cube(name,loc,scale,material,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new("Rounded edges","BEVEL")
        mod.width=bevel
        mod.segments=3
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

# Vehicle axes: X length, Y width, Z height; dimensions 12m x 2.55m x 3.25m
cube("Low floor chassis",(0,0,0.68),(11.8,2.5,0.85),white,0.17)
cube("Upper body",(0,0,2.04),(11.65,2.5,2.15),white,0.22)
cube("Roof battery enclosure",(0,0,3.24),(5.4,1.72,0.26),blue,0.09)
cube("Front windshield",(5.855,0,2.27),(0.045,2.17,1.43),dark,0.02)
cube("Rear window",(-5.855,0,2.32),(0.045,2.05,1.15),dark,0.02)
for side in [-1,1]:
    y=side*1.267
    # six side windows with dark mullions
    for i in range(6):
        x=-4.45+i*1.7
        cube("Side window %s %s"%(side,i),(x,y,2.34),(1.48,0.027,1.03),dark,0.04)
    # two passenger doors, simplified glazing
    for x in (1.8,4.25):
        cube("Passenger door glass %s %s"%(side,x),(x,y+side*0.009,1.67),(0.76,0.035,1.87),dark,0.03)
        cube("Door division %s %s"%(side,x),(x,y+side*0.032,1.65),(0.025,0.03,1.94),silver)
    cube("Blue beltline %s"%side,(0,side*1.278,1.16),(11.25,0.035,0.11),blue)
    for x in (-3.65,3.65):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=0.48,depth=0.18,location=(x,side*1.31,0.48),rotation=(math.pi/2,0,0))
        w=bpy.context.object
        w.name="Wheel %s %s"%(side,x)
        w.data.materials.append(black)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=0.24,depth=0.19,location=(x,side*1.41,0.48),rotation=(math.pi/2,0,0))
        bpy.context.object.name="Hub"
        bpy.context.object.data.materials.append(silver)
cube("Front destination panel",(5.9,0,3.0),(0.06,1.65,0.28),dark)
for y in (-0.97,0.97):
    cube("Front headlamp",(5.95,y,1.0),(0.04,0.27,0.13),silver)
    cube("Rear tail lamp",(-5.95,y,1.0),(0.04,0.23,0.2),red)
cube("Ground",(0,0,-0.045),(16,7,0.09),mat("Ground gray",(0.21,0.24,0.27)))

world=bpy.context.scene.world
world.color=(0.35,0.35,0.35)
def point_at(obj,point):
    direction=Vector(point)-obj.location
    obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

bpy.ops.object.camera_add(location=(17,-19,11))
camera=bpy.context.object
point_at(camera,(0,0,1.5))
bpy.context.scene.camera=camera
for pos,power,size in [((0,-7,12),2500,8),((5,5,10),1900,7)]:
    bpy.ops.object.light_add(type='AREA',location=pos)
    l=bpy.context.object
    l.data.energy=power
    l.data.shape='DISK'
    l.data.size=size
    point_at(l,(0,0,1))
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=24
scene.render.resolution_x=1280
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath='/tmp/electric_bus.png'
bpy.ops.wm.save_as_mainfile(filepath='/tmp/electric_bus.blend')
bpy.ops.render.render(write_still=True)
print("MODEL_COMPLETE: /tmp/electric_bus.blend and /tmp/electric_bus.png")
