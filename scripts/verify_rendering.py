"""Browser-level guarantees for final SVGs; separate from source unit tests."""
from pathlib import Path
import sys,argparse,json,threading,functools,http.server,xml.etree.ElementTree as ET,copy
from PIL import Image,ImageChops
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
import render_profile
p=argparse.ArgumentParser();p.add_argument('--label',default='final-verification');p.add_argument('--browser',default='/usr/bin/google-chrome');a=p.parse_args();out=R/'work/review'/a.label;out.mkdir(parents=True,exist_ok=True)
snapshot=json.loads((R/'data/public-activity.json').read_text())
files=['contribution-core.svg','contribution-core-mobile.svg','contribution-core-static.svg','contribution-core-mobile-static.svg']
for file in files:
 (out/(file+'.html')).write_text(f'<style>html,body{{margin:0}}img{{display:block}}</style><img src="/assets/generated/{file}">')
for n in [0,1,10,100,365]:
 test=copy.deepcopy(snapshot);test['stats']['streak']['current']=n
 for mobile in [False,True]:
  name=f'synthetic-streak-{n}'+('-mobile' if mobile else '')
  (out/(name+'.svg')).write_text(render_profile.dashboard(test,False,mobile))
  (out/(name+'.html')).write_text(f'<style>html,body{{margin:0}}img{{display:block;width:100%}}</style><img src="{name}.svg">')
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
   mobile='mobile' in file;metrics=diff.crop((20,25,285 if mobile else 750,190)).getbbox() is not None
   number=diff.crop((460 if mobile else 980,35,625 if mobile else 1165,137)).getbbox() is not None
   row={'file':file,'browser_reduced_motion':reduced,'changed_pixels':changed,'inactive_days_changed':inactive_changed,'active_days_changed':active_changed,'contribution_text_changed':metrics,'streak_text_changed':number}
   expected_static=reduced or 'static' in file
   row['pass']=((changed==0) if expected_static else changed>0) and inactive_changed==0 and not metrics and not number
   results.append(row);pg.close()
  if not reduced:
   for n in [0,1,10,100,365]:
    for mobile in [False,True]:
     name=f'synthetic-streak-{n}'+('-mobile' if mobile else '');pg=b.new_page(viewport={'width':309 if mobile else 846,'height':500});pg.goto(f'http://127.0.0.1:{s.server_port}/work/review/{a.label}/{name}.html');pg.locator('img').screenshot(path=str(out/(name+'.png')));pg.close()
  b.close()
s.shutdown();(out/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));sys.exit(0 if all(x['pass'] for x in results) else 1)
