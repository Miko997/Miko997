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

@lru_cache(maxsize=2)
def typography_mask(mobile=False):
 width,height=(750,830) if mobile else (1600,600)
 mask=Image.new('L',(width,height),0);d=ImageDraw.Draw(mask)
 x,y,size=name_layout(mobile);d.text((x,y),'Miko Parkkinen',font=font(size,610),fill=255)
 if mobile:
  for yy,line in [(151,'Simulation systems · Robotics'),(197,'Research software')]:d.text((54,yy),line,font=font(34),fill=255)
 else:
  for yy,line in [(306,'Simulation systems · Robotics'),(351,'Research software')]:d.text((78,yy),line,font=font(29),fill=255)
 return mask

@lru_cache(maxsize=2)
def typography_shadow(mobile=False):
 # Expand each individual glyph, then feather it. This protects the nearby wall
 # as well as the stroke itself, without introducing a rectangular backdrop.
 return typography_mask(mobile).filter(ImageFilter.MaxFilter(13 if mobile else 15)).filter(ImageFilter.GaussianBlur(4)).point(lambda v:round(v*.90))

def protect_typography(im,mobile=False):
 im=im.convert('RGB').copy()
 im.paste(Image.new('RGB',im.size,BACKGROUND),(0,0),typography_shadow(mobile))
 return im

def draw_typography(im,mobile=False):
 im=protect_typography(im,mobile)
 d=ImageDraw.Draw(im);x,y,size=name_layout(mobile)
 d.text((x,y),'Miko Parkkinen',font=font(size,610),fill='#f1f3ff')
 if mobile:
  for yy,line in [(151,'Simulation systems · Robotics'),(197,'Research software')]:d.text((54,yy),line,font=font(34),fill='#aab6ce')
 else:
  for yy,line in [(306,'Simulation systems · Robotics'),(351,'Research software')]:d.text((78,yy),line,font=font(29),fill='#aab6ce')
 return im

@lru_cache(maxsize=2)
def bulb_layout(mobile=False):
 """Three cable spans: 11 bulbs each on desktop, 9 on the narrower mobile wall."""
 # Each tuple is left/right height, sag, and an individual strand phase. Unequal
 # endpoints and irregular spacing deliberately avoid a regular LED matrix.
 strands=[(4,31,29,.25),(111,125,32,1.2),(224,218,38,2.1)] if mobile else [(55,96,66,.25),(184,201,49,1.2),(325,318,92,2.1)]
 left,right=(-17,763) if mobile else (22,975)
 offsets=[.020,.136,.242,.349,.457,.570,.679,.793,.910]
 if not mobile:
  # Preserve the original horizontal spacing and add two lamps per strand.
  offsets=[u*773/953 for u in offsets+[1.023,1.136]]
 result=[];paths=[]
 for row,(ya,yb,sag,phase) in enumerate(strands):
  def point(u):return (left+(right-left)*u,ya+(yb-ya)*u+4*sag*u*(1-u)+4*np.sin(u*7+phase))
  paths.append([point(u) for u in np.linspace(0,1,180)])
  for j,u in enumerate(offsets):
   u+=(.010 if mobile else .010*773/953)*np.sin(j*3.1+row*1.5);x,y=point(u)
   # The suspension is short, irregular and gravity-aligned, with a mild glass
   # tilt. Every bulb has its own visible graphite collar and ribbed socket.
   size=(33 if mobile else 31)+(j+row)%3*2
   angle=round(9*np.sin(j*1.9+row*2.3),1)
   result.append({'x':round(x),'y':round(y),'w':size,'angle':angle,'key':['sapphire','violet','lavender'][(j+row*2)%3],'index':row*len(offsets)+j,'row':row})
 return paths,result

@lru_cache(maxsize=2)
def wall_and_cables(mobile=False):
 width,height=(750,830) if mobile else (1600,600)
 yy,xx=np.mgrid[:height,:width].astype(np.float32)
 # A faint graphite surface fades continuously into the existing near-black
 # canvas, rather than introducing a rectangular plaque behind the name.
 cx,cy,rx,ry=(360,150,400,195) if mobile else (468,250,530,295)
 field=np.exp(-(((xx-cx)/rx)**4+((yy-cy)/ry)**4)*1.6)
 rng=np.random.default_rng(997)
 fine=rng.normal(0,.5,(height,width))
 grain=(np.sin(xx*.79+yy*.36)+np.sin(yy*1.23-xx*.2))*.20+fine
 rgb=np.zeros((height,width,4),dtype=np.uint8)
 for c,v in enumerate([19,23,35]):rgb[:,:,c]=np.clip(v+grain,0,255)
 rgb[:,:,3]=(field*170).astype('uint8')
 layer=Image.fromarray(rgb,'RGBA');draw=ImageDraw.Draw(layer)
 paths,bulbs=bulb_layout(mobile)
 for points in paths:
  draw.line([(x+1,y+2) for x,y in points],fill=(0,0,0,160),width=5)
  draw.line(points,fill=(55,58,68,255),width=3)
  draw.line([(x,y-.8) for x,y in points],fill=(76,78,91,170),width=1)
  for x,y in [points[0],points[-1]]:
   draw.ellipse((x-4,y-4,x+4,y+4),fill=(60,55,51,255),outline=(105,96,80,255),width=1)
 return layer

@lru_cache(maxsize=128)
def bulb_patch(mobile,index,active=False):
 _,placements=bulb_layout(mobile);b=placements[index]
 source=Image.open(ROOT/f'assets/source/bulb-{b["key"]}-{"on" if active else "off"}.webp').convert('RGBA')
 w=b['w'];h=round(w*source.height/source.width)
 art=source.resize((w,h),Image.Resampling.LANCZOS).rotate(b['angle'],Image.Resampling.BICUBIC,expand=True)
 # Sprites include the lead. Their first opaque pixel joins the sagging cable.
 bbox=art.getbbox();art=art.crop((bbox[0],bbox[1],bbox[2],bbox[3]))
 pad=70 if mobile else 76
 patch=Image.new('RGBA',(art.width+pad*2,art.height+pad*2),(0,0,0,0))
 if active:
  yy,xx=np.mgrid[:patch.height,:patch.width]
  cx,cy=patch.width/2,pad+art.height*.69
  radius=39 if mobile else 46
  field=np.exp(-((xx-cx)**2+(yy-cy)**2)/(radius*radius))
  core=np.exp(-((xx-cx)**2+(yy-cy)**2)/(10*10))
  color={'sapphire':(63,126,255),'violet':(135,73,255),'lavender':(153,137,255)}[b['key']]
  glow=Image.new('RGBA',patch.size,(*color,0));glow.putalpha(Image.fromarray(np.clip(field*44+core*45,0,255).astype('uint8')))
  patch=Image.alpha_composite(patch,glow)
 patch.alpha_composite(art,(pad,pad))
 return patch,(b['x']-art.width//2-pad,b['y']-pad+1)

@lru_cache(maxsize=64)
def blink_schedule(index,mobile=False):
 """Original deterministic lamp events, with distinct on and fully off dwells.

 Adjacent sockets have independent seeded timings. These are local bulb blinks,
 not a synchronized wall strobe. Slow name energy stays completely independent.
 """
 count=27 if mobile else 33
 rng=np.random.default_rng(997+index*7919)
 start=6.8+(count-1-index)/(count-1)*.55
 events=[]
 while start<17:
  length=float(rng.uniform(.50,1.18))
  events.append((start,start+length,float(rng.uniform(.08,.12)),float(rng.uniform(.10,.16))))
  start+=length+float(rng.uniform(.35,.90))
 return tuple(events)

def bulb_brightness(index,time,mobile=False):
 # Freeze the local state when the power interval ends; the shared activation
 # envelope then fades every remaining illuminated lamp back to its quiet glass.
 time=min(float(time),16.8)
 for start,end,attack,release in blink_schedule(index,mobile):
  if start<=time<end:
   x=max(0,min(1,(time-start)/attack));y=max(0,min(1,(end-time)/release))
   return x*x*(3-2*x)*y*y*(3-2*y)
 return 0.0

def fixture_layer(mobile=False,active=False,time=12.0):
 """Independently blinking glass lamps and their local light pools, behind type."""
 layer=wall_and_cables(mobile).copy()
 for index in range(len(bulb_layout(mobile)[1])):
  off,pos=bulb_patch(mobile,index,False)
  amplitude=bulb_brightness(index,time,mobile) if active else 0
  if amplitude:
   on,_=bulb_patch(mobile,index,True)
   layer.alpha_composite(Image.blend(off,on,amplitude),pos)
  else:layer.alpha_composite(off,pos)
 return layer

def lab_lights(im,activation=0.0,mobile=False,time=12.0):
 q=max(0,min(1,float(activation)))
 quiet=fixture_layer(mobile,False)
 layer=quiet if q==0 else Image.blend(quiet,fixture_layer(mobile,True,time),q)
 return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')

def compose(scene,width=1600,height=600,mobile=False,with_lights=True,with_text=True):
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
 if with_lights:im=lab_lights(im,0,mobile)
 return draw_typography(im,mobile) if with_text else im

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,default=ROOT/'assets/source/switch-scene-quiet.webp');p.add_argument('--out',type=Path,default=ROOT/'assets/signature-header.webp');p.add_argument('--mobile-out',type=Path,default=ROOT/'assets/signature-header-mobile.webp');p.add_argument('--concept-sheet',action='store_true');p.add_argument('--save-source',action='store_true');p.add_argument('--package-lights',action='store_true');a=p.parse_args()
 if a.package_lights:
  for key in ['sapphire','violet','lavender']:
   for state in ['off','on']:
    Image.open(ROOT/f'work/header-v4/bulb-{key}-{state}.png').save(ROOT/f'assets/source/bulb-{key}-{state}.webp',quality=98,method=6)
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
