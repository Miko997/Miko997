"""Build and render the original articulated Hextech-inspired switch scene.

blender -b --python scripts/art/render_header_motion.py -- --preview --size 900
blender -b --python scripts/art/render_header_motion.py -- --size 1000 --samples 96

The 2-link arm uses exact planar IK: both link lengths remain constant and the
vertical tool contacts the moving switch cap without scaling or sliding.
Pose timestamps deliberately retain the original 20-second authoring clock for
cache compatibility. compose_header_motion.py removes its opening five-second
hold at export: authored 6.8s activation is published at 1.8s in a 15-second loop.
"""
import argparse, json, math, runpy, sys
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--size',type=int,default=1000);p.add_argument('--samples',type=int,default=96);p.add_argument('--start',type=int,default=0);p.add_argument('--end',type=int,default=999);p.add_argument('--save-scene',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
sys.argv=['render_header_scene.py','--','--concept','none','--no-render','--size',str(a.size),'--samples',str(a.samples)]
lib=runpy.run_path(str(ROOT/'scripts/art/render_header_scene.py'))
for key in ['mat','box','cylinder','beam','path','ico','torus','bolt','area','metal','steel','dark','blue','purple','white','glass']:
 globals()[key]=lib[key]
scene=bpy.context.scene
scene.render.use_persistent_data=True
scene.cycles.seed=997
scene.cycles.use_animated_seed=False
brass=mat('Warm machined bronze',(.33,.205,.087),.84,.27)
sapphire=mat('Sapphire optical housing',(.035,.095,.29),.36,.17,.0,.45)
channel=mat('Actuator optical transmission',(.13,.32,1.0),.25,.19,.35)
button_mat=mat('Polished sapphire switch',(.047,.072,.12),.67,.2)
power_mat=mat('Power glyph',(.50,.62,.82),.30,.19,.6)
# A technical plinth with interrupted bronze edges, real screws and one service run.
box('Bench foundation',(0,0,.11),(3.65,2.75,.20),metal,.12)
box('Lower machined edge',(0,0,.027),(3.53,2.63,.035),brass,.08)
box('Upper inset',(0,0,.22),(3.48,2.58,.042),dark,.09)
for x in [-1.50,1.50]:
 for y in [-1.03,1.03]:bolt((x,y,.247))
base=Vector((-.82,.12,.0))
cylinder('Hexagonal robot mount',base+Vector((0,0,.24)),base+Vector((0,0,.47)),.54,metal,6)
cylinder('Bronze mount shoulder',base+Vector((0,0,.455)),base+Vector((0,0,.49)),.46,brass,6)
cylinder('Turntable',base+Vector((0,0,.49)),base+Vector((0,0,.77)),.36,steel)
torus('Turntable seal',base+Vector((0,0,.72)),.36,.018,dark)
cylinder('Shoulder pedestal',base+Vector((0,0,.73)),base+Vector((0,0,.96)),.235,metal,32)
BUTTON=Vector((1.02,.12,0))
cylinder('Hexagonal switch fixture',BUTTON+Vector((0,0,.24)),BUTTON+Vector((0,0,.31)),.58,dark,6)
cylinder('Switch fixture bronze flange',BUTTON+Vector((0,0,.31)),BUTTON+Vector((0,0,.345)),.55,brass,6)
cylinder('Switch optical housing',BUTTON+Vector((0,0,.345)),BUTTON+Vector((0,0,.58)),.46,sapphire,6)
cylinder('Switch top bezel',BUTTON+Vector((0,0,.57)),BUTTON+Vector((0,0,.66)),.435,brass,6)
cylinder('Switch recessed pocket',BUTTON+Vector((0,0,.64)),BUTTON+Vector((0,0,.68)),.354,dark,64)
for j in range(6):
 ang=j*math.pi/3+math.pi/6
 v=BUTTON+Vector((math.cos(ang)*.38,math.sin(ang)*.38,.665))
 cylinder('Bezel socket fastener',v,v+Vector((0,0,.017)),.022,steel,6)
# A single physical optical signal route, terminated at each device.
path('Signal conduit',[(-.78,-.29,.253),(-.78,-.54,.253),(.70,-.54,.253),(1.02,-.24,.253)],.027,brass)
path('Sapphire fiber',[(-.78,-.29,.276),(-.78,-.54,.276),(.70,-.54,.276),(1.02,-.24,.276)],.008,channel)
for x in [-1.2,-.5,.2,.9]:
 cylinder('Cable clamp screw',(x,-.59,.25),(x,-.59,.271),.018,steel,6)
# An optical crystal insert is part of the real button housing, not a separate trophy.
for j in range(6):
 ang=j*math.pi/3
 o=ico('Sapphire crystal facet',BUTTON+Vector((math.cos(ang)*.395,math.sin(ang)*.395,.47)),.10,sapphire,1,(.45,.45,1.0))
 o.rotation_euler=(0,0,ang)

scene.camera.location=(6.6,-10.2,7.2)
scene.camera.rotation_euler=(Vector((0,0,1.43))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=5.15
bpy.data.lights['Front strip'].color=(.85,.70,.49);bpy.data.lights['Front strip'].energy=220
bpy.data.lights['Violet rim'].energy=680
bpy.data.lights['Contained core light'].energy=5
bpy.data.objects['Contained core light'].location=BUTTON+Vector((0,0,.80))
# A controlled top reflection makes the switch surface visibly polished.
area('Switch highlight',(2.2,-1.7,3.4),85,(.58,.68,1),1.1,target=BUTTON+Vector((0,0,.6)))
SHOULDER=Vector((-.82,.12,1.02));L1=1.29;L2=1.19
HOME=Vector((.65,.12,2.57));TOOL=.43
CAP_TOP=.744;TRAVEL=.074
DYNAMIC=[]

def ease(t):
 t=max(0,min(1,t));return t*t*t*(t*(t*6-15)+10)

def pose(t):
 """Return world wrist, physical cap displacement and electrical activation."""
 press=0.;wrist=HOME.copy()
 contact=BUTTON+Vector((0,0,CAP_TOP+TOOL))
 above=contact+Vector((0,0,.25))
 if 5<t<6.35:wrist=HOME.lerp(above,ease((t-5)/1.35))
 elif 6.35<=t<6.65:wrist=above.lerp(contact,ease((t-6.35)/.30))
 elif 6.65<=t<6.85:
  press=TRAVEL*ease((t-6.65)/.20);wrist=contact-Vector((0,0,press))
 elif 6.85<=t<7.05:press=TRAVEL;wrist=contact-Vector((0,0,press))
 elif 7.05<=t<7.30:
  press=TRAVEL*(1-ease((t-7.05)/.25));wrist=contact-Vector((0,0,press))
 elif 7.30<=t<7.65:wrist=contact.lerp(above,ease((t-7.30)/.35))
 elif 7.65<=t<8.8:wrist=above.lerp(HOME,ease((t-7.65)/1.15))
 active=ease((t-6.8)/.40) if t<16.8 else 1-ease((t-16.8)/1.0)
 return wrist,press,active

def set_pose(t):
 global DYNAMIC
 for o in DYNAMIC:bpy.data.objects.remove(o,do_unlink=True)
 names=set(bpy.data.objects.keys())
 wrist,press,active=pose(t)
 # Exact analytic IK in the x/z plane. Elbow-up branch stays consistent.
 dx,dz=wrist.x-SHOULDER.x,wrist.z-SHOULDER.z
 distance=math.hypot(dx,dz)
 angle=math.atan2(dz,dx)+math.acos(max(-1,min(1,(L1*L1+distance*distance-L2*L2)/(2*L1*distance))))
 elbow=SHOULDER+Vector((L1*math.cos(angle),0,L1*math.sin(angle)))
 for index,(v1,v2) in enumerate([(SHOULDER,elbow),(elbow,wrist)]):
  d=v2-v1;n=d.normalized();side=Vector((-n.z,0,n.x))
  beam('Cast actuator housing',v1+n*.05,v2-n*.04,.30,.31,metal)
  beam('Recessed actuator face',v1+n*.22+Vector((0,-.170,0)),v2-n*.22+Vector((0,-.170,0)),.19,.025,steel)
  # Two restrained bronze cut edges provide material warmth.
  for s in [-1,1]:
   beam('Bronze inlay',v1+n*.23+side*(s*.135)+Vector((0,-.155,0)),v2-n*.23+side*(s*.135)+Vector((0,-.155,0)),.014,.015,brass)
  beam('Actuator optical slot',v1+n*.30+Vector((0,-.190,0)),v2-n*.30+Vector((0,-.190,0)),.027,.012,channel)
  for frac in [.20,.80]:
   v=v1+d*frac+Vector((0,-.197,0));cylinder('Panel screws',v,v+Vector((0,-.015,0)),.022,dark,6)
 for v,r in [(SHOULDER,.265),(elbow,.252),(wrist,.190)]:
  cylinder('Joint cast bearing',v+Vector((0,-.23,0)),v+Vector((0,.22,0)),r,metal)
  cylinder('Hexagonal bronze bearing collar',v+Vector((0,-.232,0)),v+Vector((0,-.255,0)),r*.98,brass,6)
  cylinder('Recessed joint cap',v+Vector((0,-.256,0)),v+Vector((0,-.271,0)),r*.81,dark)
  torus('Optical encoder',v+Vector((0,-.273,0)),r*.80,.006,channel,(math.pi/2,0,0))
  for j in range(6):
   ang=j*math.pi/3;v0=v+Vector((math.cos(ang)*r*.59,-.276,math.sin(ang)*r*.59))
   cylinder('Joint socket fastener',v0,v0+Vector((0,-.014,0)),.018,steel,6)
  cylinder('Joint axle',v+Vector((0,-.276,0)),v+Vector((0,-.284,0)),r*.22,steel,32)
 # Tool is constrained to remain vertical during both contact and retreat.
 cylinder('Tool flange',wrist+Vector((0,0,-.03)),wrist+Vector((0,0,-.11)),.16,brass)
 box('Parallel gripper',wrist+Vector((0,0,-.17)),(.25,.35,.17),metal,.025)
 for sy in [-.125,.125]:
  beam('Gripper fingers',wrist+Vector((0,sy,-.22)),wrist+Vector((0,sy,-.385)),.062,.062,steel)
  box('Non-slip contact pad',wrist+Vector((0,sy,-.403)),(.078,.082,.054),dark,.008)
 # The cap follows the contact point, retaining exact 74mm travel.
 capz=CAP_TOP-press
 cylinder('Moving button cap',BUTTON+Vector((0,0,capz-.065)),BUTTON+Vector((0,0,capz)),.302,button_mat,64)
 torus('Moving cap bronze edge',BUTTON+Vector((0,0,capz-.01)),.294,.010,brass)
 torus('Button activation ring',BUTTON+Vector((0,0,capz+.003)),.266,.006,channel)
 coords=[]
 for i in range(49):
  ang=2.142+.60+i/48*(math.pi*2-1.20);coords.append(tuple(BUTTON+Vector((math.cos(ang)*.106,math.sin(ang)*.106,capz+.008))))
 path('Power glyph circle',coords,.013,power_mat)
 path('Power glyph stem',[tuple(BUTTON+Vector((-.54*.025,.84*.025,capz+.008))),tuple(BUTTON+Vector((-.54*.145,.84*.145,capz+.008)))],.013,power_mat)
 # Flexible service hose follows the articulated links with relaxed joint loops.
 path('Service hose',[tuple(SHOULDER+Vector((-.13,.23,-.18))),tuple(SHOULDER+Vector((-.19,.27,.22))),tuple(elbow+Vector((-.14,.27,.16))),tuple(elbow+Vector((.10,.27,.19))),tuple(wrist+Vector((.02,.24,.11))),tuple(wrist+Vector((.02,.12,-.15)))],.025,dark)
 DYNAMIC=[o for name,o in bpy.data.objects.items() if name not in names]
 channel.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.012+.078*active,.03+.17*active,.07+.53*active,1)
 channel.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value=(.13,.32,1,1)
 channel.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.045+active*3.1
 power_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=.30+active*2.0
 button_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.028+.025*active,.050+.060*active,.09+.19*active,1)
 bpy.data.lights['Contained core light'].energy=2+active*20
 bpy.data.lights['Violet rim'].energy=680+active*170
 return {'time':t,'wrist':list(wrist),'elbow':list(elbow),'cap_top':capz,'tool_contact_z':wrist.z-TOOL,'activation':active,'upper_length':(elbow-SHOULDER).length,'forearm_length':(wrist-elbow).length}

out=ROOT/'work/header-v2/frames';out.mkdir(parents=True,exist_ok=True)
# Quiet and fully lit resting views are reused during holds; only articulated
# movement needs physical rendering. Film compositing supplies slow name motion.
times=[0.0]+[round(5+i/20,4) for i in range(1,77)]+[9.0]
if a.preview:times=[0,5.7,6.35,6.65,6.85,7.05,7.65,8.8,12.0]
metadata=[]
for index,t in enumerate(times):
 filename=f'pose-{index:03d}.png' if not a.preview else f'preview-{t:05.2f}.png'
 state=set_pose(t);state.update({'index':index,'file':filename});metadata.append(state)
 if index<a.start or index>a.end:continue
 dest=out/filename
 if dest.exists() and not a.preview:print('Reusing',dest,flush=True);continue
 scene.render.filepath=str(dest)
 if a.save_scene and index==0:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'work/header-v2/robot-switch.blend'))
 bpy.ops.render.render(write_still=True)
 print('MOTION_FRAME',index,len(times),t,flush=True)
manifest=ROOT/'work/header-v2'/('preview-manifest.json' if a.preview else 'motion-manifest.json')
manifest.write_text(json.dumps({'duration':20,'fps_motion':20,'times':metadata},indent=2)+'\n')
print('MANIFEST',manifest)
