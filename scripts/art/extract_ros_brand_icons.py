"""Reproduce normalized ROS-family assets from the pinned local originals.

Source URLs, licenses and file hashes are recorded in docs/brand-sources.json.
"""
from pathlib import Path
import xml.etree.ElementTree as ET,plistlib,re,base64,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
ORIG=ROOT/'assets/brands/originals';OUT=ROOT/'assets/brands/icons'
SHA='4024191d62211c4d4fa024e9974dd372d92aa23a'
BASE=f'https://raw.githubusercontent.com/openrobotics/artwork/{SHA}/'
root=ET.fromstring((ORIG/'ros-nine-dots-original.svg').read_bytes());ns='{http://www.w3.org/2000/svg}'
shapes=[]
for e in root:
 assert e.tag==ns+'circle'
 shapes.append(f'<circle cx="{e.attrib["cx"]}" cy="{e.attrib["cy"]}" r="{e.attrib["r"]}" fill="#ffffff"/>')
assert len(shapes)==9
(OUT/'ros2.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">\n<title>ROS nine-dot mark — ROS 2</title>\n'+f'<!-- Source: {BASE}orgunits/ros.svg ; Open Robotics. CC BY-NC 4.0; trademark guidance also applies. Original geometry, official white color alternative. -->\n'+'\n'.join(shapes)+'\n</svg>\n')
p=plistlib.loads((ORIG/'ros-organizations-original.graffle').read_bytes());layer=next(i for i,x in enumerate(p['Layers']) if x['Name']=='perception');rects=[]
for g in p['GraphicsList']:
 if g.get('Layer')!=layer:continue
 assert g['Class']=='ShapedGraphic' and g['Shape']=='Rectangle' and g['Style']['stroke']['Draws']=='NO' and 'Rotation' not in g
 rects.append(tuple(map(float,re.findall(r'-?\d+(?:\.\d+)?',g['Bounds']))))
assert len(rects)==234
x1=min(v[0] for v in rects);y1=min(v[1] for v in rects);x2=max(v[0]+v[2] for v in rects);y2=max(v[1]+v[3] for v in rects);f=lambda v:format(v,'.9f').rstrip('0').rstrip('.')
(OUT/'ros-perception.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{f(x1)} {f(y1)} {f(x2-x1)} {f(y2-y1)}">\n<title>ROS Perception official organization mark</title>\n'+f'<!-- Source: {BASE}orgunits/ros_logos.graffle ; layer perception. Open Robotics. CC BY-NC 4.0; trademark guidance also applies. Original rectangle geometry; viewport trimmed and official white color alternative. -->\n'+'<path fill="#ffffff" d="'+''.join(f'M{f(x)} {f(y)}h{f(w)}v{f(h)}h-{f(w)}z' for x,y,w,h in rects)+'"/>'+'\n</svg>\n')
print('Reproduced official ROS and ROS Perception geometry.')
