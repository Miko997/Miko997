"""Typeset the Cycles scene for GitHub in Inter; deterministic, no network.
python3 scripts/art/compose_header.py --scene work/header/simulation.png
"""
from pathlib import Path
import argparse
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[2]
FONT=ROOT/'assets/source/fonts/InterVariable.ttf'
BACKGROUND=(9,11,18)
NAME_STYLES={False:(75,194,85),True:(52,51,72)}
def font(size,weight=400):
 f=ImageFont.truetype(str(FONT),size);f.set_variation_by_axes([32 if size>35 else 14,weight]);return f

def name_layout(mobile=False):
 return NAME_STYLES[mobile]

def name_bounds(mobile=False):
 x,y,size=name_layout(mobile)
 bounds=font(size,610).getbbox('Miko Parkkinen')
 return (x+bounds[0],y+bounds[1],x+bounds[2],y+bounds[3])

@lru_cache(maxsize=4)
def fixture_layer(mobile=False,active=False):
 """Physical rendered housings with restrained composited light spill."""
 width,height=(750,830) if mobile else (1600,600)
 layer=Image.new('RGBA',(width,height),(0,0,0,0))
 placements=[(65,169,280),(399,191,250)] if mobile else [(940,-70,300),(1250,-30,240)]
 quiet=Image.open(ROOT/'assets/source/lab-light-off.webp').convert('RGBA')
 lit=Image.open(ROOT/'assets/source/lab-light-on.webp').convert('RGBA')
 for x,y,w in placements:
  h=round(w*quiet.height/quiet.width)
  art=(lit if active else quiet).resize((w,h),Image.Resampling.LANCZOS)
  if active:
   # Soft violet-blue spill remains above/around the workcell, away from text.
   cone=Image.new('L',(width,height),0);d=ImageDraw.Draw(cone)
   left=(x+w*.23,y+h*.85);right=(x+w*.81,y+h*.75)
   reach=100 if mobile else 150
   d.polygon([left,right,(right[0]+38,right[1]+reach),(left[0]-32,left[1]+reach)],fill=22)
   cone=cone.filter(ImageFilter.GaussianBlur(20 if mobile else 25))
   glow=Image.new('RGBA',(width,height),(59,72,183,0));glow.putalpha(cone)
   layer=Image.alpha_composite(layer,glow)
   on=np.array(lit.resize((w,h),Image.Resampling.LANCZOS),dtype=float)
   off=np.array(quiet.resize((w,h),Image.Resampling.LANCZOS),dtype=float)
   emission=np.clip((on[:,:,:3].max(axis=2)-off[:,:,:3].max(axis=2)-15)/200,0,1)*on[:,:,3]
   mask=Image.new('L',(width,height),0);mask.paste(Image.fromarray(emission.astype('uint8')),(x,y));mask=mask.filter(ImageFilter.GaussianBlur(7 if mobile else 8))
   halo=Image.new('RGBA',(width,height),(111,140,255,0));halo.putalpha(mask.point(lambda v:round(v*.65)))
   layer=Image.alpha_composite(layer,halo)
  layer.alpha_composite(art,(x,y))
 if mobile:
  # A quiet ceiling rail joins the cropped suspensions below the descriptor.
  layer.paste((0,0,0,0),(0,0,width,252))
  d=ImageDraw.Draw(layer);d.line((100,252,651,252),fill=(37,49,70,255),width=2)
  for x,y,w in placements:
   for fraction in [.24,.755]:
    cx=round(x+w*fraction)
    d.rounded_rectangle((cx-6,249,cx+6,256),radius=2,fill=(54,62,78,255))
 return layer

def lab_lights(im,activation=0.0,mobile=False):
 q=max(0,min(1,float(activation)))
 layer=fixture_layer(mobile,False) if q==0 else fixture_layer(mobile,True) if q==1 else Image.blend(fixture_layer(mobile,False),fixture_layer(mobile,True),q)
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def compose(scene,width=1600,height=600,mobile=False,with_lights=True):
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
  d.text((52,51),'Miko Parkkinen',font=font(NAME_STYLES[True][2],610),fill='#f1f3ff')
  d.text((54,151),'Simulation systems · Robotics',font=font(34),fill='#aab6ce')
  d.text((54,197),'Research software',font=font(34),fill='#aab6ce')
 else:
  d.text((75,194),'Miko Parkkinen',font=font(NAME_STYLES[False][2],610),fill='#f1f3ff')
  d.text((78,306),'Simulation systems · Robotics',font=font(29),fill='#aab6ce')
  d.text((78,351),'Research software',font=font(29),fill='#aab6ce')
 return lab_lights(im,0,mobile) if with_lights else im

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,default=ROOT/'assets/source/switch-scene-quiet.webp');p.add_argument('--out',type=Path,default=ROOT/'assets/signature-header.webp');p.add_argument('--mobile-out',type=Path,default=ROOT/'assets/signature-header-mobile.webp');p.add_argument('--concept-sheet',action='store_true');p.add_argument('--save-source',action='store_true');p.add_argument('--package-lights',action='store_true');a=p.parse_args()
 if a.package_lights:
  for state in ['off','on']:
   Image.open(ROOT/f'work/header-v3/lab-light-{state}.png').save(ROOT/f'assets/source/lab-light-{state}.webp',quality=98,method=6)
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
