"""Synchronize a physical 3D press with a readable spectral name treatment.

python3 scripts/art/compose_header_motion.py --preview
python3 scripts/art/compose_header_motion.py

WebP contains the entire timeline: it needs no scripting or external resources.
The first and final frames are the exact same quiet composition. Reduced-motion
users receive separate static files through README picture sources.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from compose_header import compose,font,ROOT,BACKGROUND,name_layout,lab_lights,draw_typography
from remux_webp_holds import split_holds,close_quiet_loop
p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--blink-preview',action='store_true');p.add_argument('--quality',type=int,default=86);p.add_argument('--desktop-width',type=int,default=1400);p.add_argument('--mobile-width',type=int,default=650);p.add_argument('--only',choices=['desktop','mobile','both'],default='both');a=p.parse_args()
WORK=ROOT/'work/header-v5';WORK.mkdir(exist_ok=True,parents=True)
POSE_WORK=ROOT/'work/header-v2'

def smooth(t):
 t=np.clip(t,0,1);return t*t*t*(t*(t*6-15)+10)

def activation(t):return float(smooth((t-6.8)/.4) if t<16.8 else 1-smooth((t-16.8)))

def name_effect(im,t,mobile=False):
 q=activation(t)
 if q<=0:return im
 x,y,size=name_layout(mobile)
 f=font(size,610);w=round(f.getlength('Miko Parkkinen'))+8;h=round(size*1.25)
 pad=22
 mask=Image.new('L',(w+pad*2,h+pad*2),0);ImageDraw.Draw(mask).text((pad,pad),'Miko Parkkinen',font=f,fill=255)
 yy,xx=np.mgrid[:h+pad*2,:w+pad*2].astype(np.float32);u=(xx-pad)/w
 # Color moves gently inside the original letterforms. All letter strokes stay
 # luminous and intact; there are no flickers, cutouts or decorative sparkles.
 mix=.5+.5*np.sin(u*4.5-(t-6.8)*.56+.15*np.sin(yy*.05))
 violet=np.array([167,142,255],dtype=float);blue=np.array([105,195,255],dtype=float)
 rgb=violet[None,None,:]*(1-mix[:,:,None])+blue[None,None,:]*mix[:,:,None]
 ridge=np.exp(-((yy-(h*.58+pad+9*np.sin(u*10-(t-6.8)*1.15)))/2.2)**2)
 rgb=rgb*(1-ridge[:,:,None]*.24)+np.array([212,236,255])*ridge[:,:,None]*.24
 # Activation propagates from the hardware toward the left of the name.
 charge=smooth((t-6.8)*2.9-(1-u)*.90)
 fade=1-smooth(t-16.8) if t>=16.8 else 1.0
 amp=charge*fade
 original=np.array([241,243,255]);rgb=original+(rgb-original)*amp[:,:,None]
 color=Image.fromarray(np.clip(rgb,0,255).astype('uint8'),'RGB')
 glow=mask.filter(ImageFilter.GaussianBlur(8))
 glow=np.asarray(glow,dtype=float)*q*.24
 glow_im=Image.new('RGB',mask.size,(87,105,216))
 im=im.copy();im.paste(glow_im,(x-pad,y-pad),Image.fromarray(glow.astype('uint8')))
 im.paste(color,(x-pad,y-pad),mask)
 return im

manifest_path=POSE_WORK/'motion-manifest.json'
if (a.preview or a.blink_preview) and not manifest_path.exists():manifest_path=POSE_WORK/'preview-manifest.json'
manifest=json.loads(manifest_path.read_text())
rows=manifest['times']
render_cache={}

def render_at(t,mobile=False):
 if t>=8.8:
  active=rows[-1]['file'];quiet=rows[0]['file']
  if t>=17.8:filename=quiet
  else:filename=active
 else:filename=min(rows,key=lambda r:abs(r['time']-t))['file']
 key=(filename,mobile)
 if key not in render_cache:
  render_cache[key]=compose(POSE_WORK/'frames'/filename,750,830,True,False,False) if mobile else compose(POSE_WORK/'frames'/filename,with_lights=False,with_text=False)
 im=render_cache[key]
 if 16.8<t<17.8:
  quietkey=(rows[0]['file'],mobile)
  if quietkey not in render_cache:render_cache[quietkey]=compose(POSE_WORK/'frames'/rows[0]['file'],750,830,True,False,False) if mobile else compose(POSE_WORK/'frames'/rows[0]['file'],with_lights=False,with_text=False)
  im=Image.blend(im,render_cache[quietkey],float(smooth(t-16.8)))
 return name_effect(draw_typography(lab_lights(im,activation(t),mobile,t),mobile),t,mobile)

# Still evidence is always emitted at meaningful physical and visual moments.
boardtimes=[0,6.35,6.85,7.3,12,17.8]
board=Image.new('RGB',(1600,3*650),BACKGROUND)
for i,t in enumerate(boardtimes):
 snapshot=render_at(t)
 snapshot.save(WORK/f'story-{t:05.2f}.png')
 small=snapshot.resize((800,300),Image.Resampling.LANCZOS)
 board.paste(small,((i%2)*800,(i//2)*650))
 # Mobile companion under each desktop view exposes real responsive layout.
 mob=render_at(t,True);mob.save(WORK/f'mobile-full-story-{t:05.2f}.png');mob.resize((250,277),Image.Resampling.LANCZOS).save(WORK/f'mobile-story-{t:05.2f}.png')
 board.paste(mob.resize((250,277),Image.Resampling.LANCZOS),((i%2)*800+275,(i//2)*650+320))
 ImageDraw.Draw(board).text(((i%2)*800+28,(i//2)*650+602),f'{t:.2f}s',font=font(23,500),fill='#aab6ce')
board.save(WORK/'motion-storyboard.jpg',quality=95)
if a.blink_preview:
 # Low-cost review media shows true on/off states before final WebP encoding.
 preview_times=[round(6.4+i*.10,3) for i in range(71)]
 for mobile,width,label in [(False,800,'desktop'),(True,293,'mobile')]:
  frames=[]
  for t in preview_times:
   im=render_at(t,mobile);im=im.resize((width,round(im.height*width/im.width)),Image.Resampling.LANCZOS)
   frames.append(im)
  frames[0].save(WORK/f'blink-preview-{label}.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
  sheet=Image.new('RGB',(width*2,frames[0].height*3+90),BACKGROUND)
  for j,idx in enumerate([8,16,24,32,40,48]):
   x=(j%2)*width;y=(j//2)*(frames[0].height+30)
   sheet.paste(frames[idx],(x,y));ImageDraw.Draw(sheet).text((x+15,y+frames[0].height+3),f'{preview_times[idx]:.2f}s',font=font(20),fill='#aab6ce')
  sheet.save(WORK/f'blink-contact-sheet-{label}.jpg',quality=94)
 print('Blink previews:',WORK)
if a.preview or a.blink_preview:
 print('Preview storyboard:',WORK/'motion-storyboard.jpg');raise SystemExit(0)

# One long quiet frame, 20fps during movement, 12.5fps during the delicate name
# treatment, then a long exact quiet frame. Holds do not encode duplicate images.
times=[0.0]+[round(5+i*.05,5) for i in range(76)]+[round(8.8+i*.08,5) for i in range(113)]+[17.84]
times=sorted(set(times));durations=[round((b-c)*1000) for c,b in zip(times,times[1:])]+[round((20-times[-1])*1000)]
assert sum(durations)==20000 and min(durations)>0
for mobile,width,filename in [(False,a.desktop_width,'signature-header-animated.webp'),(True,a.mobile_width,'signature-header-mobile-animated.webp')]:
 if a.only!='both' and (mobile != (a.only=='mobile')):continue
 frames=[]
 for i,t in enumerate(times):
  im=render_at(t,mobile)
  target=(width,round(im.height*width/im.width));im=im.resize(target,Image.Resampling.LANCZOS)
  frames.append(im)
 out=ROOT/'assets'/filename
 temporary=WORK/('encoding-'+filename)
 frames[0].save(temporary,save_all=True,append_images=frames[1:],duration=durations,loop=0,quality=a.quality,method=6,minimize_size=True,allow_mixed=True)
 temporary.write_bytes(split_holds(close_quiet_loop(temporary.read_bytes())))
 temporary.replace(out)
 with Image.open(out) as encoded:encoded_count=encoded.n_frames
 print(out,out.stat().st_size,frames[0].size,'authored_frames',len(frames),'encoded_frames',encoded_count,flush=True)
 # Static files use precisely the same composition and geometry as time zero.
 static=render_at(0,mobile);static.save(ROOT/'assets'/('signature-header-mobile.webp' if mobile else 'signature-header.webp'),quality=95,method=6)
 frames.clear();render_cache.clear()
# Keep compact reusable source stills; physical frame caches remain local.
for state,row in [('quiet',rows[0]),('active',rows[-1])]:
 Image.open(POSE_WORK/'frames'/row['file']).save(ROOT/'assets/source'/f'switch-scene-{state}.webp',quality=98,method=6)
metadata={'duration_ms':20000,'quiet_until':5,'press_starts':6.65,'activation_start':6.8,'return_complete':8.8,'activation_end':16.8,'fade_end':17.8,'frame_times':times,'durations_ms':durations,'motion_render_fps':20,'name_fps':12.5,'lighting_fps':12.5,'wall_strands':3,'wall_bulbs':{'desktop':33,'mobile':27},'bulb_colors':['sapphire','violet','lavender'],'bulb_activation_spread_seconds':.55,'bulb_on_dwell_seconds':[.50,1.18],'bulb_off_dwell_seconds':[.35,.90],'bulb_attack_seconds':[.08,.12],'bulb_release_seconds':[.10,.16]}
(WORK/'composition-timing.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('Timing:',WORK/'composition-timing.json')
