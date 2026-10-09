"""Decode both published headers; verify timing, contact, readability and blinking.

python3 scripts/art/validate_header_motion.py --manifest work/header-v2/motion-manifest.json
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from compose_header import (name_bounds,compose,lab_lights,protect_typography,
                            typography_mask,typography_shadow,bulb_layout,bulb_patch)
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path);a=p.parse_args()

def luminance(pixels):
 c=np.asarray(pixels,dtype=float)/255
 return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722])

def bulb_masks(mobile,size):
 """Select visible glass interiors, away from foreground text and neighboring pools."""
 fullsize=(750,830) if mobile else (1600,600)
 indices=[7,8,20,24] if mobile else [1,4,9,24,30]
 masks=[]
 for index in indices:
  off,pos=bulb_patch(mobile,index,False);on,_=bulb_patch(mobile,index,True)
  q=np.array(off,dtype=float);v=np.array(on,dtype=float)
  local=((v[:,:,:3]-q[:,:,:3]).mean(axis=2)>40)&(q[:,:,3]>240)
  mask=Image.new('L',fullsize,0);mask.paste(Image.fromarray((local*255).astype('uint8')),pos)
  clear=(np.array(mask)>240)&(np.array(typography_shadow(mobile))<5)
  clear=np.array(Image.fromarray((clear*255).astype('uint8')).resize(size,Image.Resampling.NEAREST))>240
  assert clear.sum()>15, f'Lamp {index} has no clear glass interior for temporal validation'
  masks.append(clear)
 return indices,masks

def dwell_lengths(samples,predicate):
 runs=[];current=0
 for _,duration,level in samples:
  if predicate(level):current+=duration
  elif current:runs.append(current);current=0
 if current:runs.append(current)
 return runs

results=[]
for mobile,name in [(False,'signature-header-animated.webp'),(True,'signature-header-mobile-animated.webp')]:
 path=ROOT/'assets'/name;im=Image.open(path)
 assert im.info.get('loop')==0, 'Animation must repeat'
 indices,masks=bulb_masks(mobile,im.size)
 targets=[9000,10400,12000,13600,15200,16400]
 active_samples={};history=[];elapsed=0;first=None;before_press=None;last=None;durations=[]
 opening_hold=0;closing_hold=0;opening=True;previous=None
 for index in range(im.n_frames):
  im.seek(index);im.load();pixels=np.asarray(im.convert('RGB')).copy()
  duration=im.info['duration'];durations.append(duration)
  if first is None:first=pixels
  if opening and np.array_equal(pixels,first):opening_hold+=duration
  else:opening=False
  closing_hold=closing_hold+duration if previous is not None and np.array_equal(pixels,previous) else duration
  previous=pixels
  for target in targets:
   if elapsed<=target<elapsed+duration:
    # The frame's real timestamp matters at blink boundaries; do not reconstruct
    # a background for the requested sample time if its frame started earlier.
    active_samples[target]=(elapsed/1000,pixels)
  if elapsed<=6600<elapsed+duration:before_press=pixels
  history.append((elapsed,duration,[float(pixels[mask].mean()) for mask in masks]))
  last=pixels;elapsed+=duration
 assert elapsed==20000, f'{name}: timeline drift: {elapsed}'
 assert opening_hold>=5000, f'{name}: quiet hold too short'
 assert closing_hold>=2000, f'{name}: settling hold too short'
 assert durations[0]<=40 and max(durations)<=500, f'{name}: incompatible long frame hold'
 seam=float(np.mean(np.abs(first.astype(float)-last.astype(float))))
 assert seam<2, f'{name}: visible loop discontinuity: {seam}'
 fallback_path=ROOT/'assets'/('signature-header-mobile.webp' if mobile else 'signature-header.webp')
 fallback=np.array(Image.open(fallback_path).convert('RGB').resize(im.size,Image.Resampling.LANCZOS),dtype=float)
 fallback_error=float(np.mean(np.abs(fallback-first.astype(float))))
 assert fallback_error<2.5, f'{name}: static fallback does not match the quiet frame'
 assert len(active_samples)==len(targets)
 fullsize=(750,830) if mobile else (1600,600);scale=im.width/fullsize[0]
 x1,y1,x2,y2=[round(n*scale) for n in name_bounds(mobile)]
 quiet=first[y1:y2,x1:x2]
 interior=(quiet[:,:,0]>228)&(quiet[:,:,1]>228)&(quiet[:,:,2]>238)
 assert interior.sum()>400
 descriptor=np.array(typography_mask(mobile).resize(im.size,Image.Resampling.LANCZOS))>245
 descriptor[y1:y2,x1:x2]=False
 base=compose(ROOT/'assets/source/switch-scene-active.webp',*fullsize,mobile,with_lights=False,with_text=False)
 name_contrasts=[];descriptor_contrasts=[]
 for instant,pixels in active_samples.values():
  background=protect_typography(lab_lights(base,1,mobile,instant),mobile).resize(im.size,Image.Resampling.LANCZOS)
  local_contrast=(luminance(pixels)+.05)/(luminance(background)+.05)
  name_contrasts.append(float(np.percentile(local_contrast[y1:y2,x1:x2][interior],5)))
  descriptor_contrasts.append(float(np.percentile(local_contrast[descriptor],5)))
  color_delta=float(np.mean(np.abs(quiet[interior].astype(float)-pixels[y1:y2,x1:x2][interior].astype(float))))
  assert color_delta>25, f'{name}: steady name energy missing at {instant}'
 assert min(name_contrasts)>=4.5, f'{name}: active name contrast too low against the blinking wall'
 assert min(descriptor_contrasts)>=4.5, f'{name}: descriptor contrast too low against the blinking wall'
 strands,bulbs=bulb_layout(mobile);expected=27 if mobile else 33
 assert len(strands)==3 and len(bulbs)==expected, 'Three strands must retain the responsive lamp counts'
 temporal=[]
 for slot,index in enumerate(indices):
  quiet_level=history[0][2][slot]
  active_history=[(t,d,values[slot]) for t,d,values in history if 8000<=t and t+d<=16800]
  peak=max(level for _,_,level in active_history)-quiet_level
  assert peak>50, f'{name}: lamp {index} never becomes visibly illuminated'
  normalized=[(t,d,(level-quiet_level)/peak) for t,d,level in active_history]
  off_dwells=[d for d in dwell_lengths(normalized,lambda v:v<=.15) if d>=160]
  on_dwells=[d for d in dwell_lengths(normalized,lambda v:v>=.80) if d>=160]
  state=None;relights=0
  for _,_,level in normalized:
   new='off' if level<=.15 else 'on' if level>=.80 else None
   if new is not None:
    if state=='off' and new=='on':relights+=1
    state=new
  assert len(off_dwells)>=3 and len(on_dwells)>=3 and relights>=3, f'{name}: lamp {index} does not repeatedly turn fully off and relight'
  temporal.append({'index':index,'peak_above_quiet_rgb':round(peak,2),'minimum_normalized':round(min(v for _,_,v in normalized),3),'off_dwells_ms':off_dwells,'on_dwells_ms':on_dwells,'relights':relights})
 lens=np.logical_or.reduce(masks)
 early_delta=float(np.mean(np.abs(before_press[lens].astype(float)-first[lens].astype(float))))
 reset_delta=float(np.mean(np.abs(last[lens].astype(float)-first[lens].astype(float))))
 assert early_delta<3 and reset_delta<3, f'{name}: bulbs violate switch timing or reset'
 results.append({'file':name,'size':list(im.size),'bytes':path.stat().st_size,'frames':im.n_frames,'duration_ms':elapsed,'opening_hold_ms':opening_hold,'closing_hold_ms':closing_hold,'first_frame_ms':durations[0],'max_frame_ms':max(durations),'loop_mean_pixel_error':round(seam,4),'static_fallback_mean_pixel_error':round(fallback_error,4),'active_text_worst_p05_contrast':round(min(name_contrasts),2),'active_descriptor_worst_p05_contrast':round(min(descriptor_contrasts),2),'contrast_sample_frame_times':[t for t,_ in active_samples.values()],'bulb_count':len(bulbs),'strand_count':len(strands),'bulb_pre_press_delta':round(early_delta,2),'bulb_reset_delta':round(reset_delta,2),'decoded_bulb_blinks':temporal})
assert sum(r['bytes'] for r in results)<4*1024*1024,'Header animation exceeds 4MiB combined budget'
if a.manifest:
 rows=json.loads(a.manifest.read_text())['times']
 for r in rows:
  assert abs(r['upper_length']-1.29)<1e-6
  assert abs(r['forearm_length']-1.19)<1e-6
  if 6.65<=r['time']<=7.30:
   assert abs(r['tool_contact_z']-r['cap_top'])<1e-6
   assert abs(r['wrist'][0]-1.02)<1e-6 and abs(r['wrist'][1]-.12)<1e-6
 print('Physical contact and rigid link validation: PASS')
print(json.dumps(results,indent=2))
