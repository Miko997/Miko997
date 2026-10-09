"""Decode the pinned legacy XCF losslessly; no tracing, matting or recoloring.
Format: https://developer.gimp.org/core/standards/xcf/
Only this asset's v0, 8-bit RGBA, RLE, unmasked normal layers are supported.
"""
from pathlib import Path
import struct,json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
b=(ROOT/'assets/brands/originals/rviz-isolated-original.xcf').read_bytes()
assert hashlib.sha256(b).hexdigest()=='5c6ddcae1e212df6b6778678c8fe7bec852933cae4bc4c5acd8bca178389e0c6'
(ROOT/'work/brand-icons').mkdir(parents=True,exist_ok=True)
def ui(p,n=1):return struct.unpack('>'+('I'*n),b[p:p+4*n])
def props(p):
 out={}
 while True:
  kind,size=ui(p,2);p+=8
  if not kind:return out,p
  out[kind]=b[p:p+size];p+=size
assert b[:14]==b'gimp xcf file\0'
w,h,mode=ui(14,3);pr,p=props(26)
assert pr[17]==b'\x01',pr # RLE compression
layer_offsets=[]
while True:
 off=ui(p)[0];p+=4
 if not off:break
 layer_offsets.append(off)
report=[]
for i,off in enumerate(layer_offsets):
 lw,lh,typ,length=ui(off,4);name=b[off+16:off+16+length].rstrip(b'\0').decode()
 lp,p=props(off+16+length);hier,mask=ui(p,2)
 assert typ==1 and mask==0
 hw,hh,bpp,level=ui(hier,4);assert (hw,hh,bpp)==(lw,lh,4)
 assert ui(level,2)==(lw,lh)
 tile_count=((lw+63)//64)*((lh+63)//64);tiles=ui(level+8,tile_count)
 assert ui(level+8+4*tile_count)[0]==0
 rgba=Image.new('RGBA',(lw,lh));tilei=0
 for ty in range(0,lh,64):
  for tx in range(0,lw,64):
   tw,th=min(64,lw-tx),min(64,lh-ty);n=tw*th;p=tiles[tilei];tilei+=1;planes=[]
   for channel in range(4):
    out=bytearray()
    while len(out)<n:
     op=b[p];p+=1
     if op<=126:
      count=op+1;out.extend([b[p]]*count);p+=1
     elif op==127:
      count=int.from_bytes(b[p:p+2],'big');p+=2;out.extend([b[p]]*count);p+=1
     elif op==128:
      count=int.from_bytes(b[p:p+2],'big');p+=2;out.extend(b[p:p+count]);p+=count
     else:
      count=256-op;out.extend(b[p:p+count]);p+=count
    assert len(out)==n
    planes.append(Image.frombytes('L',(tw,th),bytes(out)))
   rgba.paste(Image.merge('RGBA',planes),(tx,ty))
 png=ROOT/f'work/brand-icons/rviz-layer-{i}.png';rgba.save(png)
 ah=rgba.getchannel('A').histogram()
 report.append({'index':i,'name':name,'size':[lw,lh],'type':typ,'properties':{str(k):v.hex() for k,v in lp.items()},'alpha_range':rgba.getchannel('A').getextrema(),'transparent_pixels':ah[0],'opaque_pixels':ah[255],'bounds':rgba.getbbox(),'output':str(png.relative_to(ROOT))})
print(json.dumps(report,indent=2))
(ROOT/'work/brand-icons/rviz-xcf-layer-metadata.json').write_text(json.dumps(report,indent=2)+'\n')
