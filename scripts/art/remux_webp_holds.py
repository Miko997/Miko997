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

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('destination',type=Path);p.add_argument('--max-duration',type=int,default=40);a=p.parse_args()
 a.destination.write_bytes(split_holds(a.source.read_bytes(),a.max_duration))
 print(a.destination,a.destination.stat().st_size)
