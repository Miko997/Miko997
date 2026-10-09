"""Render original miniature glass bulbs for the three-strand laboratory wall.

blender -b --python-exit-code 1 --python scripts/art/render_bulb_wall.py
The six transparent sprites are real Cycles renders of one authored glass shell,
ribbed brass socket, insulating collar, lead wires and an internal light element.
The compositor positions, rotates and lights them on original sagging cables.
"""
import math,runpy,sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.argv=['render_header_scene.py','--','--concept','none','--no-render','--size','400','--samples','96']
lib=runpy.run_path(str(ROOT/'scripts/art/render_header_scene.py'))
for k in ['mat','cylinder','path','torus','area','dark','steel']:globals()[k]=lib[k]
for obj in list(bpy.data.objects):bpy.data.objects.remove(obj,do_unlink=True)
brass=mat('Aged machined brass socket',(.26,.17,.078),.82,.30)
rubber=mat('Graphite phenolic insulator',(.030,.032,.046),.08,.43)
glass=mat('Colored curved glass envelope',(.13,.17,.28),.06,.12,0,.35)
glass.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value=.35
element=mat('Fine internal light element',(.3,.4,.6),.15,.24)

# Closed lathed shell, pear-shaped rather than a flat disc or generic LED dot.
profile=[(-.51,0),(-.48,.065),(-.43,.115),(-.34,.169),(-.23,.202),(-.10,.216),(.02,.211),(.12,.184),(.22,.140),(.27,.112),(.29,.112),(.30,0)]
verts=[];faces=[];segments=96
for z,r in profile:
 for i in range(segments):
  a=i*2*math.pi/segments;verts.append((r*math.cos(a),r*math.sin(a),z))
for j in range(len(profile)-1):
 for i in range(segments):
  k=j*segments+i;n=j*segments+(i+1)%segments
  faces.append((k,n,n+segments,k+segments))
mesh=bpy.data.meshes.new('Lathed curved glass shell');mesh.from_pydata(verts,[],faces);mesh.update()
bulb=bpy.data.objects.new('Blown optical glass',mesh);bpy.context.collection.objects.link(bulb);bulb.data.materials.append(glass)
for poly in mesh.polygons:poly.use_smooth=True
solid=bulb.modifiers.new('Glass thickness','SOLIDIFY');solid.thickness=.012
cylinder('Brass threaded socket',(0,0,.26),(0,0,.47),.132,brass,64)
for z in [.29,.335,.38,.425]:torus('Socket machining ridge',(0,0,z),.133,.014,brass)
cylinder('Insulating cable collar',(0,0,.465),(0,0,.58),.099,rubber,64)
cylinder('Short dark lead',(0,0,.57),(0,0,.71),.027,dark,24)
for x in [-.058,.058]:
 path('Internal support wire',[(x,0,.27),(x,0,.12),(x*.75,0,-.27)],.008,steel)
path('Internal luminous hairpin',[(-.044,-.012,-.28),(-.055,-.012,-.07),(-.04,-.012,.045),(.04,-.012,.045),(.055,-.012,-.07),(.044,-.012,-.28)],.012,element)
area('Broad cool glass reflection',(-2,-3,2),65,(.68,.78,1),2.0,target=(0,0,.1))
area('Soft violet edge',(2,1,1),55,(.37,.25,1),1.3,target=(0,0,0))
area('Socket warm reflection',(-1,-1,3),35,(1,.72,.40),1.0,target=(0,0,.4))
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(.28,-4,.32));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.38;scene.camera=cam
scene.render.resolution_x=220;scene.render.resolution_y=400;scene.render.resolution_percentage=100;scene.render.film_transparent=True
out=ROOT/'work/header-v4';out.mkdir(exist_ok=True,parents=True)
for key,color in [('sapphire',(.055,.34,1)),('violet',(.30,.08,1)),('lavender',(.40,.31,1))]:
 for active in [False,True]:
  shader=glass.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(*(tuple(.12+c*.33 for c in color)),1)
  shader.inputs['Emission Color'].default_value=(*color,1);shader.inputs['Emission Strength'].default_value=.65 if active else 0
  shader.inputs['Transmission Weight'].default_value=.26 if active else .36
  p=element.node_tree.nodes['Principled BSDF'];p.inputs['Emission Color'].default_value=(*(tuple(.4+c*.6 for c in color)),1);p.inputs['Emission Strength'].default_value=10 if active else 0
  scene.render.filepath=str(out/f'bulb-{key}-{"on" if active else "off"}.png');bpy.ops.render.render(write_still=True)
