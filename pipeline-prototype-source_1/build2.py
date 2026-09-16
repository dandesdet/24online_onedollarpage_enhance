import re,json,base64,io
from PIL import Image

def load(name):
    return open(''+name).read()

def split(html):
    css=re.search(r'<style>(.*?)</style>',html,re.S).group(1)
    body=re.search(r'<body>(.*?)<script>',html,re.S).group(1)
    js=re.search(r'<script>(.*?)</script>\s*</body>',html,re.S).group(1)
    return css,body,js

def rename_ids(txt,ids,pre):
    for i in sorted(ids,key=len,reverse=True):
        txt=re.sub(r'id="%s"'%i, 'id="%s_%s"'%(pre,i), txt)
        txt=re.sub(r"getElementById\('%s'\)"%i, "getElementById('%s_%s')"%(pre,i), txt)
        txt=re.sub(r"(querySelector(?:All)?\(')#%s\b"%i, r"\1#%s_%s"%(pre,i), txt)
        txt=re.sub(r'(?<![\w-])#%s(?![\w-])'%i, '#%s_%s'%(pre,i), txt)  # css / other selectors
    return txt

def scope_css(css,scope):
    # hoist keyframes
    kf=re.findall(r'@keyframes\s+[\w-]+\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}',css)
    for k in kf: css=css.replace(k,'')
    css=re.sub(r'(^|\n)\s*:root\s*\{', r'\1&{', css)
    css=re.sub(r'(^|\n)\s*body\s*\{', r'\1&{', css)
    return '\n'.join(kf)+'\n'+scope+'{\n'+css+'\n}'

# ---- gallery (step 6)
G=load('gallery-slides-variations_19.html')
gcss,gbody,gjs=split(G)
gids=sorted(set(re.findall(r'id="([\w]+)"',gbody)))
gcss,gbody,gjs=[rename_ids(x,gids,'g') for x in (gcss,gbody,gjs)]
gcss=scope_css(gcss,'.sc-g')
gcss+='''
.sc-g{background:transparent!important;margin:0!important}
.sc-g .page{padding:0;max-width:none}
.sc-g .handoff{margin:18px 0 0 32px;padding:18px 20px;border-radius:12px;background:#f6f6f7;display:none}
.sc-g .handoff.on{display:block;animation:pop .25s ease-out}
.sc-g .handoff h4{margin:0 0 4px;font-size:16px;font-weight:600}
.sc-g .handoff p{margin:0 0 14px;color:#4b4b4f;font-size:14.5px}
.sc-g .handoff .row{display:flex;gap:10px;flex-wrap:wrap}
.sc-g .handoff .btn{height:44px;padding:0 18px;font-size:15px;font-weight:500;border-radius:10px}
.sc-g .handoff .btn.lock{color:#8a8a90;border-style:dashed;gap:8px}
.sc-g .handoff .btn.lock:hover{color:#0f0f10;border-color:#0f0f10}
.sc-g .step.collapsed .handoff{display:none}
'''
# handoff block after slide grid
gbody=gbody.replace('<div class="g" id="g_g"></div>','<div class="g" id="g_g"></div>\n  <div class="handoff" id="g_handoff"><h4>Gallery is done. Your A+ can sell harder.</h4><p>We\'ll find the angle competitors miss and build a second version to test against yours.</p><div class="row"><button class="btn k" onclick="PX.run6()">Create A+ Content</button><button class="btn" onclick="PX.download(\'gallery\',this)">Download gallery &amp; copy</button><button class="btn lock" onclick="PX.upsell()"><i class="ti ti-lock"></i> New brief, second gallery</button></div></div>')
assert 'g_handoff' in gbody
# hooks: expose init, signal completion
gjs=gjs.replace('\n  init();\n})();','\n  window.startGallery=init;\n})();')
gjs=gjs.replace('setInterval(function(){\n    var changed=false;','setInterval(function(){\n    if(!S)return;var changed=false;')
assert 'if(!S)return' in gjs
for q in ['.c','.tl','.step','.lb-tools']:
    gjs=gjs.replace("document.querySelectorAll('%s')"%q,"document.querySelectorAll('.sc-g %s')"%q).replace("document.querySelector('%s')"%q,"document.querySelector('.sc-g %s')"%q)
assert 'window.startGallery' in gjs
gjs=gjs.replace("sm.textContent=d===S.length?S.length+' slides approved':d+' of '+S.length+' ready';st.appendChild(sm);}",
 "sm.textContent=d===S.length?S.length+' slides approved':d+' of '+S.length+' ready';st.appendChild(sm);if(d===S.length&&!window.__gd){window.__gd=1;window.__galleryDone&&window.__galleryDone();}}")
assert '__galleryDone' in gjs

# ---- A+ briefing (step 7)
A=load('aplus-briefing_39.html')
acss,abody,ajs=split(A)
aids=sorted(set(re.findall(r'id="([\w]+)"',abody)))
acss,abody,ajs=[rename_ids(x,aids,'a') for x in (acss,abody,ajs)]
acss=scope_css(acss,'.sc-a')
acss+='''
.sc-a{background:transparent!important;margin:0!important}
.sc-a .wrap{max-width:none;padding:0}
.sc-a .rail{display:none}
.sc-a .step{font-size:16px;margin-bottom:4px}
.sc-a .step b{font-weight:600}
.sc-a .sub{margin-left:32px;font-size:15px;margin-bottom:16px}
.sc-a .list,.sc-a .add,.sc-a .paste,.sc-a .cta,.sc-a .proc,.sc-a .strip,.sc-a .undo{margin-left:32px}
.sc-a .add{width:calc(100% - 32px)}
.sc-a .step::before{content:"";width:22px;height:22px;border-radius:50%;background:#3fa66b;flex:none;display:inline-block}
@media (max-width:768px){.sc-a .sub,.sc-a .list,.sc-a .add,.sc-a .paste,.sc-a .cta,.sc-a .proc,.sc-a .strip,.sc-a .undo{margin-left:0}.sc-a .add{width:100%}}
'''
for q in ['.paste-box textarea','.wrap']:
    ajs=ajs.replace("document.querySelector('%s')"%q,"document.querySelector('.sc-a %s')"%q)
ajs='(function(){\n'+ajs+'\n})();'
ajs=ajs.replace("if(done===n)wrapEl.classList.add('done');","if(done===n){wrapEl.classList.add('done');setTimeout(function(){window.__aplusDone&&window.__aplusDone();},600);}")
assert '__aplusDone' in ajs
# processing message says opening step 8 - good

# ---- images (for my steps 2,3,8)
def b64(path,q,size,box=None):
    im=Image.open(path).convert('RGB')
    if box: im=im.crop(box)
    im=im.resize(size,Image.LANCZOS); bio=io.BytesIO(); im.save(bio,'JPEG',quality=q); return 'data:image/jpeg;base64,'+base64.b64encode(bio.getvalue()).decode()
LST=[b64('img0.jpg',78,(400,400),(80,300,900,1000)), b64('img5.jpg',78,(400,400),(300,250,1024,974)), b64('img2.jpg',78,(400,400)), b64('img3.jpg',78,(400,400))]
MAIN=[b64('img0.jpg',82,(600,600),(60,280,860,1000)), b64('img2.jpg',82,(600,600),(150,300,850,1000)), b64('img4.jpg',82,(600,600),(150,200,850,900))]
AP=[b64(f'img{i}.jpg',78,(776,480),(0,0,1024,634)) for i in [0,1,2,3,4,5,2]]
AM=[b64(f'img{i}.jpg',72,(400,300),(0,0,1024,768)) for i in [0,1,2,3,4,5,2]]

T=open('template2.html').read()
T=T.replace('/*GCSS*/',gcss).replace('/*ACSS*/',acss)
T=T.replace('<!--GBODY-->',gbody).replace('<!--ABODY-->',abody)
T=T.replace('/*GJS*/',gjs).replace('/*AJS*/',ajs)
for k,v in [('__LST__',LST),('__MAIN__',MAIN),('__AP__',AP),('__AM__',AM)]: T=T.replace(k,json.dumps(v))
open('pipeline-prototype.html','w').write(T); print(len(T)//1024,'KB')
