"""Split long holds into original frames plus transparent, lossless no-op frames.

This edits only the WebP RIFF timeline, without re-encoding existing image data.
ANMF format: https://developers.google.com/speed/webp/docs/riff_container
The input must use no disposal for held frames. Candidate files should be checked
in target browsers before adoption; shorter chunks alone do not imply a fix.
"""
from __future__ import annotations
import argparse,io,struct
from pathlib import Path
from PIL import Image

def chunk(kind:bytes,payload:bytes)->bytes:
 return kind+struct.pack('<I',len(payload))+payload+(b'\0' if len(payload)%2 else b'')

def chunks(blob:bytes):
 if blob[:4]!=b'RIFF' or blob[8:12]!=b'WEBP' or int.from_bytes(blob[4:8],'little')!=len(blob)-8:
  raise ValueError('Invalid WebP RIFF header')
 pos=12
 while pos<len(blob):
  if pos+8>len(blob):raise ValueError('Truncated chunk header')
  size=int.from_bytes(blob[pos+4:pos+8],'little');end=pos+8+size
  if end+(size%2)>len(blob):raise ValueError('Truncated chunk payload')
  yield blob[pos:pos+4],blob[pos+8:end]
  pos=end+(size%2)

def close_quiet_loop(blob:bytes,quiet_start_ms:int=17840)->bytes:
 """Reuse the first full-canvas image at an authored identical quiet ending.

 Lossy encoding can independently approximate two identical input frames. The
 header explicitly returns to the initial composition at 17.84s. Replacing just
 that ANMF image payload with the first one makes the decoded loop exact; frame
 durations, disposal, earlier frames and transparent continuation holds stay
 intact. This accepts either the encoded timeline or its remuxed equivalent.
 """
 entries=list(chunks(blob));first=next(p for k,p in entries if k==b'ANMF')
 canvas=next(p for k,p in entries if k==b'VP8X')
 width=int.from_bytes(canvas[4:7],'little')+1;height=int.from_bytes(canvas[7:10],'little')+1
 if first[:6]!=bytes(6) or int.from_bytes(first[6:9],'little')+1!=width or int.from_bytes(first[9:12],'little')+1!=height or first[15]!=2:
  raise ValueError('Exact loop closure requires a full-canvas, no-blend first frame')
 with Image.open(io.BytesIO(blob)) as image:
  if image.convert('RGBA').getextrema()[3]!=(255,255):raise ValueError('The replacement frame must be fully opaque')
 elapsed=0;replaced=False;output=[]
 for kind,payload in entries:
  if kind==b'ANMF':
   duration=int.from_bytes(payload[12:15],'little')
   if elapsed==quiet_start_ms:
    if payload[15]&1:raise ValueError('The quiet hold must not dispose the canvas')
    payload=first[:12]+payload[12:15]+first[15:];replaced=True
   elapsed+=duration
  output.append(chunk(kind,payload))
 if not replaced:raise ValueError('No frame begins at the authored quiet boundary')
 body=b'WEBP'+b''.join(output)
 return b'RIFF'+struct.pack('<I',len(body))+body

def split_holds(blob:bytes,max_duration:int=40,first_duration:int=40)->bytes:
 if not 1<=max_duration<=1000:raise ValueError('Hold interval must be 1–1000ms')
 if not 1<=first_duration<=max_duration:raise ValueError('First duration must fit the hold interval')
 buf=io.BytesIO();Image.new('RGBA',(1,1),(0,0,0,0)).save(buf,format='WEBP',lossless=True,exact=True)
 subchunks=b''.join(chunk(k,p) for k,p in chunks(buf.getvalue()) if k in (b'VP8L',b'VP8 ',b'ALPH'))
 output=[]
 frame_index=0
 for kind,payload in chunks(blob):
  if kind==b'VP8X':
   payload=bytes([payload[0]|0x10])+payload[1:]
  if kind!=b'ANMF':output.append(chunk(kind,payload));continue
  if len(payload)<16:raise ValueError('Truncated ANMF')
  duration=int.from_bytes(payload[12:15],'little')
  current_index=frame_index;frame_index+=1
  # Preserve real motion timing, including ordinary 50/80ms frames.
  # Only long authored holds get transparent continuation frames.
  if duration<=1000:output.append(chunk(kind,payload));continue
  if payload[15]&1:raise ValueError('Cannot extend a disposing frame with a no-op')
  first_step=min(max_duration,first_duration) if current_index==0 else max_duration
  output.append(chunk(kind,payload[:12]+first_step.to_bytes(3,'little')+payload[15:]))
  remaining=duration-first_step
  while remaining:
   step=min(remaining,max_duration)
   noop=bytes(12)+step.to_bytes(3,'little')+b'\0'+subchunks
   output.append(chunk(b'ANMF',noop));remaining-=step
 body=b'WEBP'+b''.join(output)
 return b'RIFF'+struct.pack('<I',len(body))+body

def trim_quiet_opening(blob:bytes,trim_ms:int=5000,init_duration_ms:int=40)->bytes:
 """Remove a quiet prefix while retaining the original opaque initialization.

 The original first motion frame is a delta that needs the quiet canvas beneath
 it. Keep that canvas for 40ms, subtract those 40ms from the first retained frame,
 and preserve every later timestamp shifted by exactly trim_ms. No image payload
 is re-encoded. The source must have an exact frame boundary at trim_ms, and every
 earlier decoded frame must be identical to its full-canvas opaque first frame.
 """
 if trim_ms<=0 or init_duration_ms<=0:raise ValueError('Trim and initialization must be positive')
 entries=list(chunks(blob));frames=[p for k,p in entries if k==b'ANMF']
 if not frames:raise ValueError('Animation has no frames')
 first=frames[0];canvas=next(p for k,p in entries if k==b'VP8X')
 width=int.from_bytes(canvas[4:7],'little')+1;height=int.from_bytes(canvas[7:10],'little')+1
 if first[:6]!=bytes(6) or int.from_bytes(first[6:9],'little')+1!=width or int.from_bytes(first[9:12],'little')+1!=height or first[15]!=2:
  raise ValueError('Quiet initialization must replace the full canvas without disposal')
 elapsed=0;boundary=None
 with Image.open(io.BytesIO(blob)) as image:
  image.load();initial=image.convert('RGBA')
  if initial.getextrema()[3]!=(255,255):raise ValueError('Quiet initialization must be opaque')
  initial_bytes=initial.tobytes()
  for index,frame in enumerate(frames):
   if elapsed==trim_ms:boundary=index;break
   if elapsed>trim_ms:break
   image.seek(index);image.load()
   if image.convert('RGBA').tobytes()!=initial_bytes:
    raise ValueError('The removed prefix contains visible changes')
   elapsed+=int.from_bytes(frame[12:15],'little')
 if boundary is None:raise ValueError('No exact frame boundary at the requested trim time')
 retained_duration=int.from_bytes(frames[boundary][12:15],'little')
 if retained_duration<=init_duration_ms:raise ValueError('First retained frame is too short to absorb initialization')
 output=[];frame_index=0
 for kind,payload in entries:
  if kind!=b'ANMF':output.append(chunk(kind,payload));continue
  if frame_index==0:output.append(chunk(kind,first[:12]+init_duration_ms.to_bytes(3,'little')+first[15:]))
  if frame_index>=boundary:
   if frame_index==boundary:payload=payload[:12]+(retained_duration-init_duration_ms).to_bytes(3,'little')+payload[15:]
   output.append(chunk(kind,payload))
  frame_index+=1
 body=b'WEBP'+b''.join(output)
 return b'RIFF'+struct.pack('<I',len(body))+body

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);p.add_argument('--max-duration',type=int,default=40);p.add_argument('--trim-opening-ms',type=int,default=0);a=p.parse_args()
 result=split_holds(a.source.read_bytes(),a.max_duration)
 if a.trim_opening_ms:result=trim_quiet_opening(result,a.trim_opening_ms)
 a.destination.write_bytes(result)
 print(a.destination,a.destination.stat().st_size)
