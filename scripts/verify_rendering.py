"""Browser-level guarantees for final SVGs; separate from source unit tests."""
from pathlib import Path
import sys,argparse,json,threading,functools,http.server,xml.etree.ElementTree as ET,copy,re
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import render_profile
p=argparse.ArgumentParser();p.add_argument('--label',default='final-verification');p.add_argument('--browser',default='/usr/bin/google-chrome');p.add_argument('--mobile-only',action='store_true');a=p.parse_args();out=R/'work/review'/a.label;out.mkdir(parents=True,exist_ok=True)
snapshot=json.loads((R/'data/public-activity.json').read_text())
files=['contribution-core.svg','contribution-core-mobile.svg','contribution-core-static.svg','contribution-core-mobile-static.svg']
if a.mobile_only:files=[f for f in files if 'mobile' in f]
sizes=[True] if a.mobile_only else [False,True]
for file in files:
 (out/(file+'.html')).write_text(f'<style>html,body{{margin:0}}img{{display:block}}</style><img src="/assets/generated/{file}">')
for n in [0,1,10,100,365]:
 test=copy.deepcopy(snapshot);test['stats']['streak']['current']=n
 for mobile in sizes:
  name=f'synthetic-streak-{n}'+('-mobile' if mobile else '')
  (out/(name+'.svg')).write_text(render_profile.dashboard(test,False,mobile))
  (out/(name+'.html')).write_text(f'<style>html,body{{margin:0}}img{{display:block;width:100%}}</style><img src="{name}.svg">')
  if n==0:
   (out/(name+'-animated.svg')).write_text(render_profile.dashboard(test,True,mobile))
   (out/(name+'-animated.html')).write_text(f'<style>html,body{{margin:0}}img{{display:block}}</style><img src="{name}-animated.svg">')
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start();results=[]
with sync_playwright() as pw:
 for reduced in [False,True]:
  b=pw.chromium.launch(executable_path=a.browser,headless=True,args=['--no-sandbox']+(['--force-prefers-reduced-motion'] if reduced else []))
  for file in files:
   tree=ET.parse(R/'assets/generated'/file).getroot();width=int(tree.attrib['width']);height=int(tree.attrib['height']);pg=b.new_page(viewport={'width':width,'height':height})
   pg.goto(f'http://127.0.0.1:{s.server_port}/work/review/{a.label}/{file}.html');pg.wait_for_timeout(150)
   stem=file+('-browser-reduced' if reduced else '')
   first=out/(stem+'-0.png');last=out/(stem+'-1.png');pg.locator('img').screenshot(path=str(first));pg.wait_for_timeout(1100);pg.locator('img').screenshot(path=str(last))
   diff=ImageChops.difference(Image.open(first).convert('RGB'),Image.open(last).convert('RGB'))
   changed=sum(any(x) for x in diff.getdata());inactive_changed=0;active_changed=0;ns={'s':'http://www.w3.org/2000/svg'}
   for day in tree.findall('.//s:g[@class="day"]',ns):
    rect=day.find('s:rect',ns);x,y,cw,ch=(float(rect.attrib[k]) for k in ['x','y','width','height']);patch=diff.crop((round(x+3),round(y+3),round(x+cw-3),round(y+ch-3)))
    has_change=patch.getbbox() is not None
    if day.attrib['data-count']=='0':inactive_changed+=has_change
    else:active_changed+=has_change
   mobile='mobile' in file
   # Inspect semantic text regions, excluding the independently animated rail.
   # Number coordinates are read from the SVG so layout changes remain covered.
   def text_changes(element):
    x=float(element.attrib['x']);y=float(element.attrib['y']);size=float(element.attrib['font-size'])
    extent=len(''.join(element.itertext()))*size*.8
    return diff.crop((int(x-2),int(y-size-2),int(min(width,x+extent+2)),int(y+size*.13+2))).getbbox() is not None
   contribution=tree.find('.//s:text[@id="contribution-number"]',ns)
   streak=tree.find('.//s:text[@id="streak-number"]',ns)
   assert contribution is not None and streak is not None, 'Stable number regions must have semantic IDs'
   metrics=text_changes(contribution)
   number=text_changes(streak)
   rail_path=tree.find('.//s:g[@id="energy-separator"]/s:path',ns)
   rail_y=float(re.match(r'M[-\d.]+ ([-\d.]+)H',rail_path.attrib['d']).group(1))
   rail_diff=diff.crop((16,int(rail_y-14),width-16,int(rail_y+16)))
   rail_pixels=sum(any(pixel) for pixel in rail_diff.getdata())
   flame_region=(292,16,426,157) if mobile else (796,16,944,178)
   flame_pixels=sum(any(pixel) for pixel in diff.crop(flame_region).getdata())
   row={'separator_changed_pixels':rail_pixels,'flame_changed_pixels':flame_pixels,'file':file,'browser_reduced_motion':reduced,'changed_pixels':changed,'inactive_days_changed':inactive_changed,'active_days_changed':active_changed,'contribution_text_changed':metrics,'streak_text_changed':number}
   expected_static=reduced or 'static' in file
   row['pass']=((changed==0) if expected_static else changed>0 and rail_pixels>0 and (flame_pixels>0 if int(''.join(streak.itertext())) else flame_pixels==0)) and inactive_changed==0 and not metrics and not number
   results.append(row);pg.close()
  if not reduced:
   for n in [0,1,10,100,365]:
    for mobile in sizes:
     name=f'synthetic-streak-{n}'+('-mobile' if mobile else '');pg=b.new_page(viewport={'width':309 if mobile else 846,'height':500});pg.goto(f'http://127.0.0.1:{s.server_port}/work/review/{a.label}/{name}.html');pg.locator('img').screenshot(path=str(out/(name+'.png')));pg.close()
   for mobile in sizes:
    name='synthetic-streak-0'+('-mobile' if mobile else '')+'-animated'
    width,height=(640,684) if mobile else (1200,440)
    pg=b.new_page(viewport={'width':width,'height':height});pg.goto(f'http://127.0.0.1:{s.server_port}/work/review/{a.label}/{name}.html');pg.wait_for_timeout(150)
    first=out/(name+'-0.png');last=out/(name+'-1.png')
    pg.locator('img').screenshot(path=str(first));pg.wait_for_timeout(1100);pg.locator('img').screenshot(path=str(last))
    diff=ImageChops.difference(Image.open(first).convert('RGB'),Image.open(last).convert('RGB'))
    flame_region=(292,16,426,157) if mobile else (796,16,944,178)
    flame_pixels=sum(any(pixel) for pixel in diff.crop(flame_region).getdata())
    tree=ET.parse(out/(name+'.svg')).getroot();rail_path=tree.find('.//s:g[@id="energy-separator"]/s:path',ns)
    rail_y=float(re.match(r'M[-\d.]+ ([-\d.]+)H',rail_path.attrib['d']).group(1))
    rail_pixels=sum(any(pixel) for pixel in diff.crop((16,int(rail_y-14),width-16,int(rail_y+16))).getdata())
    results.append({'file':name+'.svg','synthetic':True,'streak':0,'flame_changed_pixels':flame_pixels,'separator_changed_pixels':rail_pixels,'pass':flame_pixels==0 and rail_pixels>0})
    pg.close()
  b.close()
s.shutdown();(out/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));sys.exit(0 if all(x['pass'] for x in results) else 1)
