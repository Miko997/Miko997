"""Original procedural artwork. Blender 5.0.1, Cycles; no downloaded models.
blender -b --python scripts/art/render_header_scene.py -- --concept laboratory --output work/header/laboratory.png --size 1200 --samples 128
"""
from __future__ import annotations
import argparse, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector
args = argparse.ArgumentParser()
args.add_argument('--concept', choices=['laboratory','simulation','electromechanical','none'],default='laboratory')
args.add_argument('--output',default='work/header/laboratory.png')
args.add_argument('--size',type=int,default=1000)
args.add_argument('--samples',type=int,default=96)
args.add_argument('--save-scene',default='')
args.add_argument('--no-render',action='store_true')
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
random.seed(997)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, color, metal=0, rough=.3, emission=0, transmission=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
 p.inputs['Transmission Weight'].default_value=transmission; p.inputs['IOR'].default_value=1.46
 return m
metal=mat('Blue black anodized aluminum',(.035,.047,.073),.82,.26)
steel=mat('Machined titanium',(.19,.23,.31),.8,.36)
dark=mat('Recesses',(.012,.018,.034),.7,.31)
violet=mat('Violet ceramic',(.19,.067,.38),.58,.25)
blue=mat('Blue optical channels',(.055,.30,1),.32,.18,3.5)
purple=mat('Violet optical channels',(.31,.10,1),.2,.22,2.4)
white=mat('Fiber optic emission',(.48,.66,1),.2,.14,4.5)
glass=mat('Optical quartz',(.12,.07,.5),.12,.11,.15,.78)
floor=mat('Near black floor',(.013,.016,.026),.35,.4)

def assign(o,m):
 o.data.materials.append(m); return o

def bevel(o,width=.05,segments=3):
 mod=o.modifiers.new('Machined edge chamfer','BEVEL'); mod.width=width; mod.segments=segments
 mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def box(name,loc,scale,m=metal,bev=.05,rot=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.scale=scale
 if rot: o.rotation_euler=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,m)
 if bev: bevel(o,bev)
 return o

def cylinder(name,a,b,r,m=steel,verts=64):
 a,b=Vector(a),Vector(b); d=b-a; bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d.length,location=(a+b)/2)
 o=bpy.context.object; o.name=name; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); assign(o,m); bevel(o,.015,2)
 return o

def beam(name,a,b,width=.14,depth=.14,m=metal):
 a,b=Vector(a),Vector(b); d=b-a; o=box(name,(a+b)/2,(width,depth,d.length),m,min(.03,width/5)); o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return o

def path(name,coords,r,m=blue):
 c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=16; c.bevel_depth=r; c.bevel_resolution=3
 s=c.splines.new('POLY'); s.points.add(len(coords)-1)
 for p,co in zip(s.points,coords):p.co=(*co,1)
 o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); assign(o,m); return o

def bolt(pos,axis='Z'):
 a=Vector(pos); b=a+Vector({'Z':(0,0,.06),'X':(.06,0,0),'Y':(0,.06,0)}[axis]); cylinder('Socket fastener',a,b,.057,steel,6)

def ico(name,loc,r,m,sub=1,scale=(1,1,1)):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=r,location=loc); o=bpy.context.object;o.name=name;o.scale=scale;assign(o,m);return o

def torus(name,loc,major,minor,m=steel,rot=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=12,location=loc,major_radius=major,minor_radius=minor,rotation=rot);o=bpy.context.object;o.name=name;assign(o,m);return o

def plate(z,r,depth,m,vertices=8):
 return cylinder('Octagonal precision stage',(0,0,z-depth/2),(0,0,z+depth/2),r,m,vertices)

def laboratory():
 plate(.14,1.77,.25,metal); plate(.30,1.63,.08,steel); plate(.365,1.6,.075,dark)
 # Broad-footed four-corner gantry, visible through the split upper bridge.
 for x in [-1.05,1.05]:
  for y in [-1.05,1.05]:
   box('Gantry socket',(x,y,.50),(.46,.46,.26),steel)
   box('Anodized gantry column',(x,y,1.79),(.20,.20,2.6),metal)
   box('Titanium edge',(x-.075,y-.075,1.79),(.035,.035,2.46),steel,.008)
   box('Blue fiber in channel',(x+.103,y-.04,1.8),(.014,.037,2.05),blue,.004)
   for dx in [-.13,.13]: bolt((x+dx,y-.10,.65))
 # Open roof makes the central optical core readable.
 for y in [-1.05,1.05]:
  box('Bridge beam',(0,y,3.05),(2.65,.32,.23),metal)
  box('Bridge inset',(0,y-.165,3.06),(1.96,.018,.035),steel,.005)
 for x in [-1.05,1.05]:box('Return beam',(x,0,3.05),(.30,2.1,.23),metal)
 for x,y in [(-1.05,-1.05),(1.05,-1.05),(-1.05,1.05),(1.05,1.05)]:
  bolt((x,y,3.19)); cylinder('Core clamp',(x,y,1.6),(x*.62,y*.62,1.6),.095,steel)
 plate(.49,.81,.15,metal,12); plate(.57,.60,.035,purple,12)
 ico('Faceted optical compute core',(0,0,1.68),1,glass,2,(.79,.79,1.02))
 core=ico('Internal field geometry',(0,0,1.68),.75,purple,1,(.84,.84,1.15))
 wire=core.modifiers.new('Optical lattice struts','WIREFRAME');wire.thickness=.021;wire.use_replace=True
 ico('Contained emitter',(0,0,1.65),.20,white,2,(1,1,2.5))
 for j in range(4):
  coords=[]
  for i in range(90):
   t=i/89; a=t*math.pi*3.4+j*math.pi/2; r=.34+.18*math.sin(t*math.pi)
   coords.append((math.cos(a)*r,math.sin(a)*r,.9+1.52*t))
  path('Curved internal optical fiber',coords,.013,white if j==1 else purple)
 for x in [-1,1]:
  for j in range(7):box('Cooling fin',(x*.58,.96,.72+j*.12),(.47,.51,.035),metal,.01)
 # Pair of non-ornamental cable glands; actual curved service routing.
 for x in [-.58,.58]:
  path('Service cable',[(x,-.24,.53),(x,-.65,.49),(x,-1.0,.5),(x,-1.38,.34),(x,-1.45,.19)],.045,dark)
  cylinder('Cable gland',(x,-1.25,.32),(x,-1.43,.32),.075,steel)

def simulation():
 box('Simulation stage',(0,0,.12),(3.4,3.1,.23),metal,.13)
 for x in [-1.35,1.35]:
  for y in [-1.2,1.2]:bolt((x,y,.255))
 cylinder('Robot mounting pedestal',(-.55,.15,.22),(-.55,.15,.59),.60,dark)
 cylinder('First axis',(-.55,.15,.55),(-.55,.15,.83),.43,steel)
 torus('Encoder band',(-.55,.15,.80),.385,.020,blue)
 points=[(-.55,.15,.88),(-.62,.18,1.25),(-.9,.2,2.36),(.27,.05,2.98),(.88,-.15,2.60)]
 for i,(a,b) in enumerate(zip(points,points[1:])):
  a,b=Vector(a),Vector(b);d=b-a
  # A wide cast housing with recessed side panel, instead of a generic rod.
  housing=beam('Cast actuator housing',a,b,.38 if i<3 else .26,.33 if i<3 else .25,metal)
  if i in (1,2):
   panel=beam('Inset machined side panel',a+d*.16+Vector((0,-.181,0)),b-d*.16+Vector((0,-.181,0)),.24,.025,steel)
   for t in [.23,.77]:
    pos=a+d*t+Vector((0,-.20,0))
    cylinder('Recessed panel screw',pos,pos+Vector((0,-.014,0)),.024,dark,6)
  side=d.cross(Vector((0,1,0))).normalized()*.175
  beam('Housing reinforcement edge',a+side+d*.12,b+side-d*.12,.035,.30,dark)
 for p in points[1:-1]:
  cylinder('Joint housing',Vector(p)+Vector((0,-.22,0)),Vector(p)+Vector((0,.22,0)),.27,steel)
  cylinder('Recessed joint bearing',Vector(p)+Vector((0,-.239,0)),Vector(p)+Vector((0,-.273,0)),.228,dark)
  cylinder('Joint cap',Vector(p)+Vector((0,-.268,0)),Vector(p)+Vector((0,-.281,0)),.18,metal)
  torus('Encoder edge',Vector(p)+Vector((0,-.278,0)),.201,.007,purple,(math.pi/2,0,0))
  for j in range(6):
   a=j*math.pi/3; v=Vector(p)+Vector((math.cos(a)*.14,-.286,math.sin(a)*.14))
   cylinder('Joint cover fastener',v,v+Vector((0,-.015,0)),.021,steel,6)
  cylinder('Axle recess',Vector(p)+Vector((0,-.284,0)),Vector(p)+Vector((0,-.288,0)),.050,dark,32)
 cylinder('Wrist tool flange',(.87,-.15,2.58),(.87,-.15,2.43),.17,steel)
 box('Pneumatic gripper body',(.88,-.15,2.40),(.26,.39,.17),metal,.025)
 for y in [-.32,.02]:
  beam('Parallel gripper finger',(.88,y,2.4),(.95,y,2.14),.06,.06,steel)
  box('Gripper contact pad',(.947,y,2.16),(.075,.069,.1),dark,.006)
 for x in [.80,.95]:
  cylinder('Tool socket', (x,-.354,2.40),(x,-.36,2.40),.020,steel,6)
 # Physical workpiece plus exact ghost geometry above a jig.
 box('Workpiece fixture',(.8,-.28,.35),(1.0,.95,.17),steel)
 work=box('Physical workpiece',(.8,-.28,.84),(.64,.64,.74),glass,.07,rot=(0,0,.25))
 frame=box('Digital twin wire surface',(.8,-.28,.84),(.68,.68,.78),purple,.0,rot=(0,0,.25))
 wire=frame.modifiers.new('Wireframe digital twin','WIREFRAME');wire.thickness=.010
 # Illustrative sampled approach ends between the gripper jaws; not solver output.
 def approach(t):
  return (.80+.50*math.sin(math.pi*t)+.15*t,-.28+.13*t,1.3+.84*t)
 for i in range(42):
  t=i/41
  ico('Sampled approach path',approach(t),.009,blue,1)
 # Sparse, low-power samples mark the measured support plane.
 sample=mat('Measured point cloud',(.06,.19,.40),.15,.5,.75)
 for x in range(-6,7):
  for y in range(-5,6):
   if (x+2)**2+(y-1)**2>7 and random.random()>.32:
    ico('Measured scene sample',(x*.21,y*.21,.258),.006,sample,1)
 path('Signal cable',[(-.64,.36,.69),(-.89,.46,1.2),(-1.1,.4,2.25),(-.72,.4,2.51),(.21,.25,3.08),(.81,.05,2.63)],.035,dark)

def electromechanical():
 box('Floating instrument foundation',(0,0,.28),(2.45,1.8,.35),metal,.16)
 box('Precision plinth',(0,0,.095),(2.7,2.03,.08),steel,.035)
 for y in [-.69,.69]:
  box('Instrument rail',(.0,y,1.82),(.19,.24,3.1),metal,.06,rot=(0,-.27,0))
  box('Optical rail channel',(-.01,y-.123,1.82),(.06,.016,2.5),blue,.009,rot=(0,-.27,0))
 for z in [.69,2.78]:
  box('Crystal terminal',(0,0,z),(1.38,1.45,.24),metal,.07,rot=(0,-.27,0))
  for y in [-.47,.47]:bolt((.46,y,z+.13))
 for j in range(8):
  box('Heat exchange blade',(-.37+j*.11,.57,1.30),(.045,.76,.92),steel,.014,rot=(0,.38,0))
 # A tall anisotropic optical field, held by physical clamps.
 o=ico('Main optical crystal',(.14,-.2,1.78),1,glass,1,(.52,.57,1.21));o.rotation_euler=(.07,-.27,.13)
 for j in range(6):
  a=math.pi*2*j/6
  path('Optical filament',[(.1+math.cos(a)*.28,-.2+math.sin(a)*.3,.81),(.1+math.cos(a+.25)*.26,-.2+math.sin(a+.25)*.28,1.48),(-.1+math.cos(a)*.18,-.2+math.sin(a)*.21,2.63)],.015,purple if j%2 else white)
 for j in range(4):
  o=ico('Suspended field shard',(.51+j*.1,-.18,1.1+j*.32),.2,glass,1,(.4,.8,2.0));o.rotation_euler=(0,-.3,j*.7)
 for x in [-.9,.9]:
  for y in [-.60,.60]:bolt((x,y,.47))
 path('Service umbilical',[(-.67,.5,.4),(-1.0,.7,.44),(-1.18,.52,.7),(-1.12,.16,1.17),(-.54,.18,1.31)],.043,dark)

{'laboratory':laboratory,'simulation':simulation,'electromechanical':electromechanical,'none':lambda:None}[opt.concept]()
# Grounded shadow and near-black horizon; no environment textures.
ground=box('Studio shadow catcher',(0,0,-.105),(200,200,.10),floor,0)
ground.is_shadow_catcher=True
scene=bpy.context.scene
scene.world.color=(.015,.02,.045)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.025,.032,.07,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25

def area(name,loc,power,color,size,target=(0,0,1.5),shape='DISK',size_y=None):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape=shape;d.size=size
 if size_y:d.size_y=size_y
 o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Large soft titanium key',(1,-4,7),800,(.72,.79,1),5)
area('Violet rim',(-3,2,4.8),750,(.30,.09,1),3)
area('Narrow blue rim',(3.4,1.0,3.2),700,(.07,.36,1),2,shape='RECTANGLE',size_y=4)
area('Front strip',(-3,-4,1.3),200,(.58,.65,1),3,shape='RECTANGLE',size_y=.65)
# Internal light illuminates structure without burying it in bloom.
d=bpy.data.lights.new('Contained core light','POINT');d.energy=24;d.color=(.23,.12,1);d.shadow_soft_size=.5;o=bpy.data.objects.new('Contained core light',d);bpy.context.collection.objects.link(o);o.location=(0,0,1.65)
bpy.ops.object.camera_add(location=(6.6,-9.4,5.9));camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,1.5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=5.2;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=opt.samples;scene.cycles.use_denoising=True
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 if any(d.use for d in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('GPU setup fallback:',e)
scene.render.resolution_x=opt.size;scene.render.resolution_y=opt.size;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.4
# Actual Cycles output remains uncluttered; glow is restrained in final composite.
scene.render.filepath=str(Path(opt.output).resolve());Path(opt.output).parent.mkdir(parents=True,exist_ok=True)
if opt.save_scene:bpy.ops.wm.save_as_mainfile(filepath=str(Path(opt.save_scene).resolve()))
if not opt.no_render:bpy.ops.render.render(write_still=True)
