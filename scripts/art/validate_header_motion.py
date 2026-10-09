"""Validate the published motion files and optional physical render manifest.

python3 scripts/art/validate_header_motion.py --manifest work/header-v2/motion-manifest.json
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from compose_header import name_bounds,fixture_layer,compose,lab_lights,protect_typography,typography_mask,typography_shadow,bulb_layout
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path);a=p.parse_args()
results=[]
for mobile,name in [(False,'signature-header-animated.webp'),(True,'signature-header-mobile-animated.webp')]:
 path=ROOT/'assets'/name;im=Image.open(path)
 assert im.info.get('loop')==0, 'Animation must repeat'
 elapsed=0;first=None;active=None;before_press=None;last=None;durations=[]
 opening_hold=0;closing_hold=0;opening=True;previous=None
 for index in range(im.n_frames):
  im.seek(index);im.load();pixels=np.asarray(im.convert('RGB')).copy()
  duration=im.info['duration'];durations.append(duration)
  if first is None:first=pixels
  if opening and np.array_equal(pixels,first):opening_hold+=duration
  else:opening=False
  closing_hold=closing_hold+duration if previous is not None and np.array_equal(pixels,previous) else duration
  previous=pixels
  if elapsed<=12000<elapsed+duration:active=pixels
  if elapsed<=6600<elapsed+duration:before_press=pixels
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
 assert active is not None
 basew=750 if mobile else 1600;scale=im.width/basew
 roi=name_bounds(mobile)
 x1,y1,x2,y2=[round(n*scale) for n in roi]
 quiet=first[y1:y2,x1:x2];energized=active[y1:y2,x1:x2]
 interior=(quiet[:,:,0]>228)&(quiet[:,:,1]>228)&(quiet[:,:,2]>238)
 assert interior.sum()>400
 color_delta=float(np.mean(np.abs(quiet[interior].astype(float)-energized[interior].astype(float))))
 assert color_delta>25, f'{name}: activation not visible'
 # Measure against the actual protected wall beneath each glyph. A fixed
 # #090b12 denominator would overstate readability where a lit bulb crosses it.
 fullsize=(750,830) if mobile else (1600,600)
 base=compose(ROOT/'assets/source/switch-scene-active.webp',*fullsize,mobile,with_lights=False,with_text=False)
 background=protect_typography(lab_lights(base,1,mobile,12),mobile).resize(im.size,Image.Resampling.LANCZOS)
 def luminance(pixels):
  c=np.asarray(pixels,dtype=float)/255
  return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722])
 actual_contrast=(luminance(active)+.05)/(luminance(background)+.05)
 contrast=actual_contrast[y1:y2,x1:x2][interior]
 assert float(np.percentile(contrast,5))>=4.5, f'{name}: active name contrast too low against the wall'
 descriptor=np.array(typography_mask(mobile).resize(im.size,Image.Resampling.LANCZOS))>245
 descriptor[y1:y2,x1:x2]=False
 descriptor_contrast=actual_contrast[descriptor]
 assert float(np.percentile(descriptor_contrast,5))>=4.5, f'{name}: descriptor contrast too low against the wall'
 strands,bulbs=bulb_layout(mobile)
 assert len(strands)==3 and len(bulbs)==27, 'The wall requires three strands and 27 individual glass bulbs'
 quiet_fixture=np.array(fixture_layer(mobile,False),dtype=float)
 active_fixture=np.array(fixture_layer(mobile,True),dtype=float)
 lens=((active_fixture[:,:,:3]-quiet_fixture[:,:,:3]).max(axis=2)>70)&(quiet_fixture[:,:,3]>240)&(np.array(typography_shadow(mobile))<5)
 lens=np.array(Image.fromarray((lens*255).astype('uint8')).resize(im.size,Image.Resampling.NEAREST))>240
 assert lens.sum()>200, f'{name}: individual bulb bodies missing'
 light_delta=float(np.mean(active[lens].astype(float)-first[lens].astype(float)))
 early_delta=float(np.mean(np.abs(before_press[lens].astype(float)-first[lens].astype(float))))
 reset_delta=float(np.mean(np.abs(last[lens].astype(float)-first[lens].astype(float))))
 assert light_delta>40, f'{name}: bulbs do not visibly activate'
 assert early_delta<3 and reset_delta<3, f'{name}: bulbs violate switch timing or reset'
 results.append({'file':name,'size':list(im.size),'bytes':path.stat().st_size,'frames':im.n_frames,'duration_ms':elapsed,'opening_hold_ms':opening_hold,'closing_hold_ms':closing_hold,'first_frame_ms':durations[0],'max_frame_ms':max(durations),'loop_mean_pixel_error':round(seam,4),'static_fallback_mean_pixel_error':round(fallback_error,4),'active_text_p05_contrast':round(float(np.percentile(contrast,5)),2),'active_descriptor_p05_contrast':round(float(np.percentile(descriptor_contrast,5)),2),'bulb_count':len(bulbs),'strand_count':len(strands),'bulb_activation_delta':round(light_delta,2),'bulb_pre_press_delta':round(early_delta,2),'bulb_reset_delta':round(reset_delta,2)})
assert sum(r['bytes'] for r in results)<4*1024*1024,'Header animation exceeds4MiB combined budget'
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
