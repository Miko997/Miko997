"""Typeset the Cycles scene for GitHub in Inter; deterministic, no network.
python3 scripts/art/compose_header.py --scene work/header/simulation.png
"""
from pathlib import Path
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[2]
FONT=ROOT/'assets/source/fonts/InterVariable.ttf'
BACKGROUND=(9,11,18)
def font(size,weight=400):
 f=ImageFont.truetype(str(FONT),size);f.set_variation_by_axes([32 if size>35 else 14,weight]);return f

def compose(scene,width=1600,height=600,mobile=False):
 im=Image.new('RGB',(width,height),BACKGROUND)
 art=Image.open(scene).convert('RGBA')
 size=670 if not mobile else 620
 art=art.resize((size,size),Image.Resampling.LANCZOS)
 # Keep the physically rendered shadows; soften only the square studio boundary.
 yy,xx=np.mgrid[:size,:size]/size
 edge=np.minimum.reduce([xx,1-xx,yy,1-yy])
 mask=np.clip(edge/.16,0,1); mask=mask*mask*(3-2*mask)
 x,y=(855,-45) if not mobile else (65,204)
 alpha=np.asarray(art)[:,:,3]/255.0
 im.paste(art,(x,y),Image.fromarray((mask*alpha*255).astype('uint8')))
 d=ImageDraw.Draw(im)
 if mobile:
  d.text((52,51),'Miko Parkkinen',font=font(65,610),fill='#f1f3ff')
  d.text((54,141),'Simulation systems · Robotics',font=font(34),fill='#aab6ce')
  d.text((54,187),'Research software',font=font(34),fill='#aab6ce')
 else:
  d.text((75,194),'Miko Parkkinen',font=font(77,610),fill='#f1f3ff')
  d.text((78,306),'Simulation systems · Robotics',font=font(29),fill='#aab6ce')
  d.text((78,351),'Research software',font=font(29),fill='#aab6ce')
 return im

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,default=ROOT/'assets/source/switch-scene-quiet.webp');p.add_argument('--out',type=Path,default=ROOT/'assets/signature-header.webp');p.add_argument('--mobile-out',type=Path,default=ROOT/'assets/signature-header-mobile.webp');p.add_argument('--concept-sheet',action='store_true');p.add_argument('--save-source',action='store_true');a=p.parse_args()
 a.out.parent.mkdir(exist_ok=True,parents=True)
 if a.save_source:
  source=ROOT/'assets/source/simulation-scene.webp'
  source.parent.mkdir(exist_ok=True,parents=True)
  Image.open(a.scene).save(source,quality=98,method=6)
  a.scene=source
 compose(a.scene).save(a.out,quality=95,method=6)
 compose(a.scene,750,830,True).save(a.mobile_out,quality=95,method=6)
 if a.concept_sheet:
  sheet=Image.new('RGB',(1600,3*670),BACKGROUND)
  for i,(key,label) in enumerate([('laboratory','A · Hexcore laboratory'),('simulation','B · Simulation field'),('electromechanical','C · Electromechanical optics')]):
   panel=Image.new('RGB',(1600,600),BACKGROUND)
   source=Image.open(ROOT/f'work/header/{key}.png').convert('RGB')
   if key=='simulation':panel=compose(ROOT/f'work/header/{key}.png')
   else:
    size=650 if key=='laboratory' else 850
    source=source.resize((size,size),Image.Resampling.LANCZOS)
    yy,xx=np.mgrid[:size,:size]/size
    mask=np.clip(np.minimum.reduce([xx,1-xx,yy,1-yy])/.16,0,1)
    mask=mask*mask*(3-2*mask)
    panel.paste(source,(475,-30) if key=='laboratory' else (-10,-170),Image.fromarray((mask*255).astype('uint8')))
    d=ImageDraw.Draw(panel)
    if key=='laboratory':
     d.text((65,104),'Miko',font=font(74,420),fill='#f1f3ff')
     d.text((65,184),'Parkkinen',font=font(74,420),fill='#f1f3ff')
     for j,line in enumerate(['Simulation systems','Robotics','Research software']):d.text((1205,386+j*43),line,font=font(28),fill='#aab6ce')
    else:
     d.text((875,189),'Miko',font=font(82,530),fill='#f1f3ff')
     d.text((875,275),'Parkkinen',font=font(82,530),fill='#f1f3ff')
     d.text((880,411),'Simulation · Robotics',font=font(27),fill='#aab6ce')
     d.text((880,452),'Research software',font=font(27),fill='#aab6ce')
   sheet.paste(panel,(0,i*670))
   ImageDraw.Draw(sheet).text((75,i*670+611),label,font=font(26,500),fill='#aa91ff')
  sheet.save(ROOT/'work/header/concepts-layout-exploration.jpg',quality=95)
if __name__=='__main__':main()
