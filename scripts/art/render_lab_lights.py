"""Render an original suspended laboratory LED fixture, quiet and energized.
blender -b --python-exit-code 1 --python scripts/art/render_lab_lights.py
No stock geometry, texture, or image inputs are used.
"""
import math,runpy,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.argv=['render_header_scene.py','--','--concept','none','--no-render','--size','900','--samples','96']
lib=runpy.run_path(str(ROOT/'scripts/art/render_header_scene.py'))
for k in ['mat','box','cylinder','path','area','metal','steel','dark']:globals()[k]=lib[k]
# Only the fixture is rendered; the shared art setup provides physical materials.
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
brass=mat('Brushed brass fixture ends',(.29,.19,.09),.85,.30)
left=mat('Violet diffusing glass',(.12,.12,.25),.15,.35,.0)
right=mat('Blue diffusing glass',(.08,.16,.24),.15,.35,.0)
box('Extruded anodized housing',(0,0,0),(2.6,.36,.16),metal,.045)
box('Recessed diffuser pocket',(0,0,-.088),(2.44,.29,.040),dark,.020)
for x,m in [(-.61,left),(.61,right)]:box('Continuous optical diffuser',(x,0,-.116),(1.18,.23,.018),m,.014)
for x in [-1.28,1.28]:
 box('Machined bronze end cap',(x,0,0),(.060,.38,.165),brass,.018)
 for y in [-.12,.12]:
  cylinder('Recessed fixture screw',(x,y,-.081),(x,y,-.091),.024,steel,6)
# Cable studs and steel suspension hang from beyond the image's top edge.
for x in [-.95,.95]:
 cylinder('Suspension stud',(x,0,.075),(x,0,.15),.047,steel,16)
 cylinder('Cable termination',(x,0,.15),(x,0,.235),.026,brass,16)
 cylinder('Braided steel suspension',(x,0,.22),(x,0,2.4),.009,steel,12)
area('Fixture soft key',(1,-4,-2),200,(.72,.79,1),4,target=(0,0,0))
area('Fixture violet edge',(-3,1,1),180,(.28,.12,1),3,target=(0,0,0))
area('Fixture blue edge',(3,0,1),200,(.08,.32,1),2,target=(0,0,0))
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(3,-7,-2.1));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.4;scene.camera=cam
scene.render.resolution_x=1000;scene.render.resolution_y=620;scene.render.resolution_percentage=100
scene.render.film_transparent=True
out=ROOT/'work/header-v3';out.mkdir(exist_ok=True,parents=True)
for active in [False,True]:
 for material,color in [(left,(.30,.16,1)),(right,(.12,.55,1))]:
  shader=material.node_tree.nodes['Principled BSDF'];shader.inputs['Emission Color'].default_value=(*color,1);shader.inputs['Emission Strength'].default_value=4.2 if active else .025
  shader.inputs['Base Color'].default_value=(*((.15,.22,.36) if active else (.055,.08,.12)),1)
 scene.render.filepath=str(out/('lab-light-on.png' if active else 'lab-light-off.png'))
 bpy.ops.render.render(write_still=True)
