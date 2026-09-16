import re,json,base64,io
from gpatch import patch as gpatch, BRIEF_CSS
OLD_OB='<button class="ob \'+(s.note?\'on\':\'\')+\'" data-a="note" title="Regenerate"><i class="ti ti-refresh"></i></button>'
NEW_OB='<button class="ob ob-txt \'+(s.note?\'on\':\'\')+\'" data-a="note" title="Comment and regenerate this slide"><i class="ti ti-pencil"></i>Comment</button>'
from PIL import Image
src=open('build2.py').read().split('# ---- images')[0]
exec(src)  # gcss,gbody,gjs,acss,abody,ajs (A instance, ids a_)
gcss=gcss.replace('to{background-position:-100% 0}}','')
abody=abody.replace('Step 7/8 <b>Briefing A+ Sections</b>','6/6 <b>Briefing A+ Sections</b>')
ajs=ajs.replace('Opening Step 8…','Building the page…')
ajs=ajs.replace('function render(){','window.APL={get:function(i){return items[i]},set:function(i,t,d,rows){items[i].t=t;if(rows){items[i].rows=rows}else{items[i].d=d}render();},count:function(){return items.length}};\nfunction render(){',1)
assert 'window.APL' in ajs

abody=abody.replace('      Have your own structure? Paste it instead\n','      <span class="pl-long">Have your own structure? Paste it instead</span><span class="pl-short">Paste your own structure</span>\n',1)
assert 'pl-short' in abody

# A+ section images: attach one uploaded 970x600 banner to each of the 6 original sections, by position
ajs=ajs.replace("const list=document.getElementById('a_list');","var APIMG=__APIMG__;\nconst list=document.getElementById('a_list');",1)
# reveal each section's image as its module finishes after Approve (placeholders until then)
ajs=ajs.replace("t.classList.remove('busy'); t.classList.add('done'); done++;","t.classList.remove('busy'); t.classList.add('done'); done++; (function(k){var real=items.filter(function(x){return !x.state});var it=real[k];if(it&&APIMG[k]&&!it.img){it.img=APIMG[k];var c=list.querySelectorAll('.card')[k];var sl=c&&c.querySelector('.slide');if(sl&&!sl.querySelector('.simg')){sl.classList.add('has-img');sl.insertAdjacentHTML('afterbegin','<img class=\"simg\" src=\"'+it.img+'\" alt=\"\">');}t.classList.add('has-img');t.style.backgroundImage='url('+it.img+')';}})(k);",1)
assert 'sl.classList.add' in ajs
assert 'APIMG=__APIMG__' in ajs
ajs=ajs.replace("const slide=(it,i,withChip=true)=>`<div class=\"slide\">${withChip?chip(it,i):''}<span class=\"ratio\">970×600</span></div>`;",
                "const slide=(it,i,withChip=true)=>`<div class=\"slide${it.img?' has-img':''}\">${it.img?`<img class=\"simg\" src=\"${it.img}\" alt=\"\">`:''}${withChip?chip(it,i):''}<span class=\"ratio\">970×600</span></div>`;",1)
assert 'has-img' in ajs

# approve: scroll the section under the header first, collapse 420ms later
ajs=ajs.replace("document.getElementById('a_approve').onclick=function(){","document.getElementById('a_approve').onclick=function(){if(window.__aplusApprove)window.__aplusApprove(a_approveRun);else a_approveRun();};function a_approveRun(){",1)
assert 'a_approveRun' in ajs

ajs=ajs.replace('<p class="vis" contenteditable data-f="v"','<p class="vis" data-f="v"')
assert 'class="vis" contenteditable' not in ajs

abody=re.sub(r'(<button class="fold" id="a_fold" title="Collapse">).*?(</button>)',r'\1<i class="ti ti-chevron-up"></i>\2',abody,flags=re.S)

gbody=gbody.replace('Rendering gallery slides','Generating Gallery Slides')
gbody=gbody.replace('Step 5/7','5/6').replace('5/7 <b>','5/6 <b>')
abody=abody.replace('Step 6/7 <b>','6/6 <b>')
gjs=gjs.replace('Rendering gallery slides','Generating Gallery Slides')
gjs=gjs.replace("<span class=\"pill\">Rendering '+s.p+'%","<span class=\"pill\">Creating '+s.p+'%")
gjs,gbody=gpatch(gjs,gbody)
gjs=gjs.replace("function lbFocus(){var inp=document.querySelector('#g_lbnote input');if(inp&&document.getElementById('g_lbnote').classList.contains('open')){inp.value='';inp.focus();}}","function lbFocus(){var inp=document.querySelector('#g_lbnote input');if(inp&&document.getElementById('g_lbnote').classList.contains('open')){inp.value='';if(!matchMedia('(hover:none)').matches)inp.focus();}}")
assert "if(!matchMedia('(hover:none)').matches)inp.focus()" in gjs
# ---- monetization: per-slide limits (3 regenerations, 3 comments), locks -> upsell ----
def _rep(a,c,n=1):
    global gjs
    assert a in gjs, a[:60]
    gjs=gjs.replace(a,c,n)
_rep("function regen(s){s.busy=true;",
     "function regen(s){if(s.left==null)s.left=3;if(!s._free){if(s.left<=0){window.PX&&PX.upsell('regen');return}s.left--;}s._free=false;s.busy=true;")
_rep("document.getElementById('g_csend').addEventListener('click',function(){var s=S[LB.i];",
     "document.getElementById('g_csend').addEventListener('click',function(){var s=S[LB.i];if(s.cmUsed==null)s.cmUsed=0;if(s.cmUsed>=3){window.PX&&PX.upsell('comment');return}s.cmUsed++;s._free=true;")
_rep("function cmOpen(){var s=S[LB.i];if(s.st!=='done'||s.busy)return;",
     "function cmOpen(){var s=S[LB.i];if(s.st!=='done'||s.busy)return;if((s.cmUsed||0)>=3){window.PX&&PX.upsell('comment');return}")
_rep('ctl=\'<div class="ctl"><button data-a="cm" class="ed" title="Comment on the image"><i class="ti ti-message-2"></i><span>Comment</span></button><button data-a="note" class="\'+(s.note?\'on\':\'\')+\'" title="Regenerate"><i class="ti ti-refresh"></i></button>',
     'var _cl=3-(s.cmUsed||0),_rl=(s.left==null?3:s.left);ctl=\'<div class="ctl"><button data-a="cm" class="ed\'+(_cl<=0?\' lk\':\'\')+\'" title="\'+(_cl<=0?\'No comments left\':\'Comment on the image · \'+_cl+\' left\')+\'"><i class="ti \'+(_cl<=0?\'ti-lock\':\'ti-message-2\')+\'"></i><span>Comment\'+(_cl>0?\' · \'+_cl:\'\')+\'</span></button><button data-a="note" class="\'+(s.note?\'on\':\'\')+(_rl<=0?\' lk\':\'\')+\'" title="\'+(_rl<=0?\'No regenerations left\':\'Regenerate · \'+_rl+\' left\')+\'"><i class="ti \'+(_rl<=0?\'ti-lock\':\'ti-refresh\')+\'"></i></button>')
assert '<button class="btn k" data-a="go">Regenerate</button>' in gbody
gbody=gbody.replace('<button class="btn k" data-a="go">Regenerate</button>','<button class="btn k" data-a="go" id="g_lbgo">Regenerate</button>',1)
_rep("""<button class="btn k" data-a="go">Regenerate</button></div>':'';""","""<button class="btn k" data-a="go">Regenerate · '+(s.left==null?3:s.left)+' left</button></div>':'';""")
_rep("document.getElementById('g_lbnote').className='lb-note'+(s.st==='done'&&!s.busy?' open':'');",
     "document.getElementById('g_lbnote').className='lb-note'+(s.st==='done'&&!s.busy?' open':'');var _g=document.getElementById('g_lbgo');if(_g){var _l=(s.left==null?3:s.left);_g.innerHTML=_l<=0?'<i class=\"ti ti-lock\"></i> Regenerate':'Regenerate · '+_l+' left';}")
_rep("window.GAL={prepare:prepare,","window.GAL={left:function(i){return S[i].left==null?3:S[i].left},regen:function(i){regen(S[i]);},prepare:prepare,")
gcss+="""
.sc-g .ctl button.lk{color:#b0b0b4}
"""

# ---- Escape ladder: draft -> comment mode -> zoom -> lightbox (single capture handler) ----
gjs+="""
;document.addEventListener('keydown',function(ev){if(ev.key!=='Escape'||!LB.open)return;ev.preventDefault();ev.stopPropagation();ev.stopImmediatePropagation();if(CM.open){if(CM.draft||CM.edit!=null){CM.draft=null;CM.edit=null;cmRender();}else cmClose();}else if(typeof ZOOMED!=='undefined'&&ZOOMED)zoomSet(false);else lbClose();},true);
"""
_rep("""<button class="btn" data-a="cancel">Cancel</button><button class="btn k" data-a="go">Regenerate · ""","""<button class="rowmic" type="button" title="Dictate"><i class="ti ti-microphone"></i></button><button class="btn" data-a="cancel">Cancel</button><button class="btn k" data-a="go">Regenerate · """)
assert '<button class="btn k" data-a="go" id="g_lbgo">Regenerate</button>' in gbody
gbody=gbody.replace('<button class="btn k" data-a="go" id="g_lbgo">Regenerate</button>','<button class="rowmic" type="button" title="Dictate"><i class="ti ti-microphone"></i></button><button class="btn k" data-a="go" id="g_lbgo">Regenerate</button>',1)
gcss+="""
.sc-g .ft .rowmic,.sc-g .lb-note .rowmic{flex:none}
"""
# ---- mobile-first touch UX for the gallery lightbox / comment mode ----
gcss+='''
@media (max-width:640px){
.sc-g .sh .w{display:none}
.sc-g .step.collapsed .strip{flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;scroll-snap-type:x proximity;scrollbar-width:none;margin:0 -12px;padding:2px 12px 6px;gap:8px}
.sc-g .strip::-webkit-scrollbar{display:none}
.sc-g .strip .tl{flex:none;scroll-snap-align:start;width:88px;height:88px;border-radius:8px}
.sc-g .ctl{gap:0;margin-left:6px}
.sc-g .ctl button{width:40px;height:40px;font-size:20px}
.sc-g .ctl .ed{width:40px;height:40px;padding:0;font-size:20px;gap:0}
.sc-g .ctl .ed span{display:none}
.sc-g .ctl .ed i,.sc-g .ctl button i{font-size:20px}
.sc-g .ob{width:44px;height:44px;font-size:20px}
.sc-g .ob.ob-txt{height:44px;font-size:16px;padding:0 18px 0 14px}
.sc-g .lb-x{width:44px;height:44px;font-size:22px}
.sc-g .lb-tools button{height:44px;font-size:15px;padding:0 14px 0 12px}
.sc-g .lb-tools button i{font-size:20px}
.sc-g .lb-arr{width:44px;height:44px;font-size:26px;background:rgba(0,0,0,.55)}
.sc-g .lb-ctl .btn{height:44px;font-size:15px}
.sc-g .lb-note input{height:48px;font-size:16px}
.sc-g .lb-note .btn{height:48px;font-size:16px}
.sc-g .cpill{width:calc(100vw - 24px);max-width:none;box-sizing:border-box;gap:8px;padding:6px 6px 6px 16px;font-size:15px;margin-top:10px}
.sc-g .cpill #g_cpt{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sc-g .csend{height:44px;padding:0 18px;flex:none;font-size:16px}
.sc-g .cx{width:44px;height:44px;flex:none;font-size:28px}
.sc-g .cstage{padding:12px 0 96px}
.sc-g .cimg{width:94vw;height:94vw}
.sc-g .pin{width:34px;height:34px;margin:-17px 0 0 -17px;font-size:14px}
.sc-g .pin .tip{display:none!important}
.sc-g .pbox,.sc-g .pbox.flip{position:fixed;left:12px!important;right:12px;top:auto!important;bottom:calc(12px + env(safe-area-inset-bottom) + var(--kb,0px));margin:0;width:auto;max-width:none;box-sizing:border-box;padding:6px 6px 6px 16px;gap:6px;z-index:60;border-radius:28px}
.sc-g .pbox input{height:44px;font-size:17px;min-width:0}
.sc-g .pbox .ok,.sc-g .pbox .no,.sc-g .pbox .del{width:44px;height:44px;flex:none;font-size:20px;border-radius:50%}
.sc-g .pbox .sep{height:24px}
}
'''
gjs+='''
;(function(){var cf=document.getElementById('g_cf');if(cf){var sx=0,sy=0,t0=0;
var drag=false,hz=null;
cf.addEventListener('touchstart',function(e){var t=e.touches[0];sx=t.clientX;sy=t.clientY;t0=Date.now();drag=true;hz=null;cf.style.transition='none'},{passive:true});
cf.addEventListener('touchmove',function(e){if(!drag)return;var t=e.touches[0];var dx=t.clientX-sx,dy=t.clientY-sy;if(hz===null){if(Math.abs(dx)<6&&Math.abs(dy)<6)return;hz=Math.abs(dx)>Math.abs(dy)*1.2}if(!hz)return;cf.style.transform='translateX('+(dx*0.55)+'px)'},{passive:true});
cf.addEventListener('touchend',function(e){if(!drag)return;drag=false;var t=e.changedTouches[0];var dx=t.clientX-sx,dy=t.clientY-sy;cf.style.transition='transform .45s cubic-bezier(.22,.9,.25,1)';cf.style.transform='translateX(0)';if(hz&&Math.abs(dx)>40&&Date.now()-t0<900){var b=document.getElementById(dx<0?'g_lbnx':'g_lbp');if(b&&!b.disabled)b.click()}},{passive:true});
cf.addEventListener('touchcancel',function(){drag=false;cf.style.transition='transform .3s';cf.style.transform='translateX(0)'},{passive:true});}
if(window.visualViewport){var f=function(){var vv=visualViewport;document.documentElement.style.setProperty('--kb',Math.max(0,window.innerHeight-vv.height-vv.offsetTop)+'px')};visualViewport.addEventListener('resize',f);visualViewport.addEventListener('scroll',f);f()}
})();
'''

# per-slide icons by meaning (fallback: tag icon)
ICONT="const ICONT={'Rapid 3000W Boil':'ti-bolt','German-Engineered Reliability':'ti-certificate','Design That Belongs in Your Kitchen':'ti-sparkles','Triple Safety Protection':'ti-shield-lock','1.7L With Clear Cup Indicator':'ti-cup','Limescale Filter & 360° Base':'ti-rotate-360','Keep-warm function':'ti-flame','Wide lid, easy to clean':'ti-droplet','Quiet, steady boil':'ti-volume-off'};"
n=gjs.count("(ICON[s.tag]||'ti-photo')"); assert n>=3,n
gjs=gjs.replace("(ICON[s.tag]||'ti-photo')","(ICONT[s.t]||ICON[s.tag]||'ti-photo')").replace("(ICON[x.tag]||'ti-photo')","(ICONT[x.t]||ICON[x.tag]||'ti-photo')")
gjs2=re.sub(r"(var ICON=\{[^}]*\};?)",lambda m:m.group(1)+ICONT,gjs,count=1); assert gjs2!=gjs; gjs=gjs2
# comment mode: click on empty area = step back (cancel draft → close comment mode)
anchor="document.getElementById('g_cx').addEventListener('click',cmClose);"
assert anchor in gjs
gjs=gjs.replace(anchor,anchor+"document.getElementById('g_cmode').addEventListener('click',function(ev){var t=ev.target;if(t.id==='g_cmode'||t.classList.contains('cstage')){if(CM.draft||CM.edit!=null){CM.draft=null;CM.edit=null;cmRender();}else cmClose();}});",1)
gcss+=BRIEF_CSS
gcss+='''
.sc-g .page{padding:0;max-width:none}
.sc-g .step{border:0;padding:0;border-radius:0;background:transparent}
.sc-g .sh{font-size:17px;min-height:22px;margin-bottom:8px;padding-top:3px;cursor:pointer;user-select:none}.sc-g .sh .w{font-size:17px}
.sc-g .dot{display:none}
.sc-g .sub{margin-left:0;font-size:16px;color:#8a8a90;margin-bottom:26px}
.sc-g .g,.sc-g .strip,.sc-g .handoff{margin-left:0}
@media (max-width:640px){.sc-g .page{padding:0}.sc-g .step{padding:0}}
.sc-g .step.collapsed .g{display:block}
.sc-g .pv{background:linear-gradient(135deg,#efeff1 0%,#f7f7f8 35%,#ffffff 50%,#f7f7f8 65%,#efeff1 100%);background-size:250% 250%;animation:gloop 1.8s ease-in-out infinite}
.sc-g .ph{color:#d5d5d8}
.sc-g .c .n{display:none}
.sc-g .c .d{margin-left:0}
.sc-g .c .m{margin-left:0}
.sc-g .g .c:nth-child(3n+1):not(:first-child){margin-top:36px}
.sc-g .ob.ob-txt{width:auto;height:38px;padding:0 16px 0 13px;border-radius:999px;gap:8px;font-size:15px;font-weight:500;font-family:inherit}
.sc-g .ob.ob-txt i{font-size:17px}
.sc-g .pv .sk{background:linear-gradient(135deg,#efeff1 0%,#f7f7f8 35%,#ffffff 50%,#f7f7f8 65%,#efeff1 100%);background-size:250% 250%;animation:gloop 1.8s ease-in-out infinite alternate}
.sc-g .pv .sk::after{display:none}
.sc-g .g,.sc-g .strip{transition:height .38s cubic-bezier(.4,0,.2,1),opacity .28s ease}
'''
ajs=ajs.replace("document.getElementById('a_approve').onclick=function(){if(window.__aplusApprove)window.__aplusApprove(a_approveRun);else a_approveRun();};",
                "document.getElementById('a_approve').onclick=function(){if(this.dataset.done)return;this.dataset.done='1';this.disabled=true;this.innerHTML='<i class=\"ti ti-lock\"></i> Approved';window.APL_APPROVED=true;var ab=document.getElementById('a_addBtn');if(ab){ab.classList.add('lk');ab.innerHTML='<i class=\"ti ti-lock\"></i> Add Section';}if(window.__aplusApprove)window.__aplusApprove(a_approveRun);else a_approveRun();};",1)
assert "APL_APPROVED=true" in ajs
ajs=ajs.replace("document.getElementById('a_addBtn').onclick=()=>{","document.getElementById('a_addBtn').onclick=()=>{if(window.APL_APPROVED){PX.upsell('add');return}",1)
assert "PX.upsell('add')" in ajs
ajs=ajs.replace("case 'regen': it.regen=it.regen??'';","case 'regen': if(it.regen!=null){delete it.regen;break;} if(window.APL_APPROVED){it.left=it.left??3;if(it.left<=0){PX.upsell('regen');return}} it.regen=it.regen??'';",1)
ajs=ajs.replace("case 'dogen': { it.regen=card.querySelector('[data-f=regen]').value;","case 'dogen': { if(window.APL_APPROVED){it.left=(it.left??3)-1;} it.regen=card.querySelector('[data-f=regen]').value;",1)
assert "it.left=(it.left??3)-1" in ajs
ajs=ajs.replace("window.APL={","window.APL={left:function(i){var it=items.filter(function(x){return !x.state})[i];return it?(it.left==null?3:it.left):3},regen:function(i){var it=items.filter(function(x){return !x.state})[i];if(!it)return;it.left=(it.left==null?3:it.left)-1;it.state='gen';it.hint='';render();setTimeout(function(){it.state=null;render();},1100)},",1)
assert "window.APL={left:" in ajs
abody=abody.replace('<div class="cta"><button class="btn dark lg" id="a_approve">','<div class="lockhint"><i class="ti ti-lock"></i> Brief locks after approval · up to 3 regenerations and 3 comments per module</div>\n  <div class="cta"><button class="btn dark lg" id="a_approve">',1)
assert 'lockhint' in abody
acss+="""
.sc-a .lockhint{font-size:13px;color:var(--ink-3);display:flex;align-items:center;gap:6px;margin:14px 0 8px}
.sc-a .wrap.collapsed .lockhint,.sc-a .wrap.done .lockhint{display:none}
.sc-a .add.lk{color:var(--ink-3);border-color:var(--line)}
.sc-a .btn:disabled{opacity:1;background:var(--bg-2);color:var(--ink-3);border-color:var(--line)}
"""

# whole card: click to edit, drag from anywhere (except table cells); Edit button like the gallery brief
ajs=ajs.replace("if(e.target.closest('button,input,select,textarea,a,[contenteditable]'))return;\n  drag={el:c,","if(e.target.closest('button,input,select,textarea,a'))return;\n  if(e.pointerType==='touch'&&!e.target.closest('.grip'))return;\n  if(window.getSelection)window.getSelection().removeAllRanges();\n  drag={el:c,",1)
assert "closest('button,input,select,textarea,a'))return;" in ajs
ajs=ajs.replace('<button class="ib" title="Regenerate" data-a="regen" data-i="${i}">${IC.regen}</button>','<button class="ib ib-txt" title="Edit text" data-a="edit" data-i="${i}"><i class="ti ti-pencil"></i><span>Edit</span></button><button class="ib" title="Regenerate" data-a="regen" data-i="${i}">${IC.regen}</button>',1)
assert 'data-a="edit"' in ajs
acss+="""
.sc-a .ttl h3[contenteditable],.sc-a .desc[contenteditable]{cursor:pointer;user-select:none;pointer-events:none;background:none!important;box-shadow:none!important;outline:none!important}
.sc-a .ttl h3[contenteditable]:hover::after,.sc-a .desc[contenteditable]:hover::after{display:none!important}
.sc-a .card{cursor:grab;user-select:none;-webkit-user-select:none}
.sc-a .card input,.sc-a .card textarea{user-select:text;-webkit-user-select:text}
body.is-grabbing,body.is-grabbing *,.sc-a .list.is-sorting,.sc-a .list.is-sorting *{user-select:none!important;-webkit-user-select:none!important}
.sc-a .card.is-dragging{cursor:grabbing}
.sc-a .card .specs,.sc-a .card .tools,.sc-a .card button{cursor:default}
.sc-a .card .tools .ib{cursor:pointer}
"""
ajs=ajs.replace('placeholder="e.g. shorter, more premium, less about warranty — or leave empty for a fresh take"><button class="btn dark" data-a="dogen"','placeholder="e.g. shorter, more premium, less about warranty — or leave empty for a fresh take"><button class="rowmic" type="button" title="Dictate"><i class="ti ti-microphone"></i></button><button class="btn dark" data-a="dogen"',1)
assert 'rowmic' in ajs
acss+="""
.sc-a .foot{display:flex;gap:8px;align-items:center}
.sc-a .foot input{flex:1;min-width:0}
.sc-a .foot .rowmic{height:44px;width:44px}
"""
acss+="""
.sc-a .specs tr:hover td{background:transparent}
.sc-a .specs td span[contenteditable]{pointer-events:none;background:none!important;box-shadow:none!important}
.sc-a .specs td span[contenteditable]:hover::after{display:none!important}
.sc-a .specs .rm,.sc-a .specs .addrow,.sc-a [data-a="addrow"]{display:none!important}
.sc-a .card .specs{cursor:pointer}
"""
ajs=ajs.replace('data-sortable="${it.regen==null}"','data-sortable="${!it.state}"',1)
assert 'data-sortable="${!it.state}"' in ajs
acss+="""
@media (max-width:640px){.sc-a .card{touch-action:pan-y}.sc-a .grip{touch-action:none;width:40px;height:40px}}
"""
# A+ delete: arm Undo bar (8s)
ajs=ajs.replace("case 'del': items.splice(i,1); break;","case 'del': prevItems=items.map(function(x){return Object.assign({},x)}); document.getElementById('a_undoMsg').innerHTML='Removed <b>'+(it.t||'section')+'</b>.'; undo.classList.add('is-on'); clearTimeout(window.__aUndoT); window.__aUndoT=setTimeout(function(){undo.classList.remove('is-on');prevItems=null;},8000); items.splice(i,1); break;",1)
assert "a_undoMsg" in ajs
acss+='''
.sc-a .step::before{display:none}
.sc-a .step{font-size:17px;min-height:22px;margin-bottom:8px;padding-top:3px;cursor:pointer;user-select:none}
.sc-a .wrap.done .fold{display:grid}
.sc-a .fold,.sc-u .fold{font-size:16px;line-height:1}
.sc-a .card .body{cursor:pointer}
.sc-a .card.is-open .body{cursor:default}
.sc-a .tools .ib-txt,.sc-u .tools .ib-txt{width:auto;padding:0 10px 0 8px;gap:6px;grid-auto-flow:column;font-size:13px;font-weight:500;color:var(--ink-2)}
.sc-a .tools .ib-txt:hover,.sc-u .tools .ib-txt:hover{color:var(--ink)}

.sc-a .sub{margin-left:0;font-size:16px;color:#8a8a90;margin-bottom:26px}
.sc-a .slide .simg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.sc-a .slide.has-img .ratio{display:none}
.sc-a .strip .tl.has-img,.sc-a .strip .tl.has-img.done{background-size:cover;background-position:center;background-color:var(--bg-3)}
.sc-a .vis{cursor:default}
.sc-a .vis:hover::after{display:none!important}
.sc-a .list,.sc-a .add,.sc-a .paste,.sc-a .cta,.sc-a .proc,.sc-a .strip,.sc-a .undo{margin-left:0}
.sc-a .add{width:100%}
.sc-a .wrap.collapsed .list{display:flex}.sc-a .wrap.collapsed .add{display:block}.sc-a .wrap.collapsed .paste{display:block}
.sc-a .list,.sc-a .add,.sc-a .paste,.sc-a .undo{transition:height .38s cubic-bezier(.4,0,.2,1),opacity .28s ease}
.sc-a .btn:active{transform:scale(.985)}
'''
# ---- U instance (USPs) from the same A+ file
A=load('aplus-briefing_39.html'); ucss,ubody,ujs=split(A)
uids=sorted(set(re.findall(r'id="([\w]+)"',ubody)))
ucss,ubody,ujs=[rename_ids(x,uids,'u') for x in (ucss,ubody,ujs)]
ubody=ubody.replace('Step 7/8 <b>Briefing A+ Sections</b>','Step 5/8 <b>Identification USPs</b>')
ubody=re.sub(r'(<button class="fold" id="u_fold" title="Collapse">).*?(</button>)',r'\1<i class="ti ti-chevron-up"></i>\2',ubody,flags=re.S)
ubody=ubody.replace('We looked at how competitors pitch products like yours and picked the points that make yours the better buy. Edit, regenerate, reorder or add — then approve.','We derived these selling points from the listing. Edit, regenerate, reorder or add — then approve.')
ubody=ubody.replace('+ Add Section','+ Add USP').replace('Approve &amp; Generate A+','Approve &amp; Generate Gallery Slides').replace('Each line becomes one section','Each line becomes one USP').replace('Build sections','Build USPs')
ubody=ubody.replace('we\'ll build the sections from your text','we\'ll build the USPs from your text').replace('we&#39;ll build the sections','we&#39;ll build the USPs')
assert 'Identification USPs' in ubody and 'Generate Gallery Slides' in ubody
for q in ['.paste-box textarea','.wrap']:
    ujs=ujs.replace("document.querySelector('%s')"%q,"document.querySelector('.sc-u %s')"%q)
items='''let items=[
 {type:'text',t:'Rapid 3000W Boil',v:'',tag:'Performance',d:'A powerful 3000-watt element brings your water to the boil fast, so tea and coffee are ready in moments.'},
 {type:'text',t:'German-Engineered Reliability',v:'',tag:'Trust',d:'Precision-built by Bosch and backed by a 1-year manufacturer warranty for lasting peace of mind.'},
 {type:'text',t:'Design That Belongs in Your Kitchen',v:'',tag:'Design',d:'Black stainless steel with the clean DesignLine silhouette — a kettle that looks as good on the counter as it works.'},
 {type:'text',t:'Triple Safety Protection',v:'',tag:'Safety',d:'Automatic shut-off, overheat and boil-dry protection, plus lift switch-off keep you and your kettle safe.'},
 {type:'text',t:'1.7L With Clear Cup Indicator',v:'',tag:'Sizing',d:'A generous 1.7-litre capacity with an easy-to-read cup indicator lets you fill and heat exactly the amount you need.'},
 {type:'text',t:'Limescale Filter & 360° Base',v:'',tag:'Convenience',d:'A removable spout filter blocks limescale, while the 360-degree base and under-base cord storage make everyday use effortless.'}
];'''
ujs2=re.sub(r'let items=\[.*?\];',lambda m:items,ujs,count=1,flags=re.S); assert ujs2!=ujs; ujs=ujs2
ujs=ujs.replace('<span class=\\"tg\\">${esc(it.tag)}</span>','<span class=\\"tg\\">${esc(it.t)}</span>')
assert 'esc(it.t)}</span><span class="ok">' in ujs
ujs=ujs.replace("section${real.length===1?'':'s'}","USP${real.length===1?'':'s'}").replace('Generating A+ content','Generating gallery slides').replace('modules ready','slides ready').replace('Opening Step 8…','Opening Step 5…').replace('New section — what is it about?','New USP — what is it about?').replace('Section headline','USP headline')
ujs=ujs.replace("if(done===n)wrapEl.classList.add('done');","if(done===n){wrapEl.classList.add('done');setTimeout(function(){window.__uspDone&&window.__uspDone();},600);}")
ujs=ujs.replace("wrapEl.classList.add('collapsed','processing'); document.getElementById('u_undo').classList.remove('is-on');","wrapEl.classList.add('collapsed','done'); document.getElementById('u_undo').classList.remove('is-on'); document.querySelectorAll('#u_strip .tl').forEach(t=>t.classList.add('done')); window.__uspDone&&window.__uspDone(); return;")
assert 'return;' in ujs and '__uspDone' in ujs
ujs=ujs.replace('<button class=\"ib\" title=\"Regenerate\" data-a=\"regen\" data-i=\"${i}\">${IC.regen}</button>','<button class=\"ib ib-txt\" title=\"Rewrite this text\" data-a=\"regen\" data-i=\"${i}\">${IC.regen}<span>Rewrite</span></button>')
assert 'ib-txt' in ujs
ujs='(function(){\n'+ujs+'\n})();'
# scope U css separately (.sc-u) — same rules as A, plus USP tweaks
ucss=scope_css(ucss,'.sc-u')+'''
.sc-u{background:transparent!important;margin:0!important}
.sc-u .wrap{max-width:none;padding:0}
.sc-u .rail{display:none}
.sc-u .step::before{display:none}
.sc-u .step{font-size:17px;min-height:22px;margin-bottom:8px;padding-top:0;cursor:pointer;user-select:none}
.sc-u .step b{font-weight:600}
.sc-u .sub{margin-left:0;font-size:17px;margin-bottom:30px}
.sc-u .list,.sc-u .add,.sc-u .paste,.sc-u .cta,.sc-u .proc,.sc-u .strip,.sc-u .undo{margin-left:0}
.sc-u .add{width:100%}
.sc-u .wrap.collapsed .list{display:flex}.sc-u .wrap.collapsed .add{display:block}.sc-u .wrap.collapsed .paste{display:block}
.sc-u .list,.sc-u .add,.sc-u .paste,.sc-u .undo{transition:height .38s cubic-bezier(.4,0,.2,1),opacity .28s ease}
.sc-u .slide{display:none}
.sc-u .row{grid-template-columns:1fr}
.sc-u .wrap.done .cta{display:none}
.sc-u .strip .tl{width:auto;aspect-ratio:auto;height:30px;padding:0 30px 0 12px;border-radius:999px;background:var(--bg-2);display:inline-flex;align-items:center}
.sc-u .strip .tl .tg{position:static;font-size:13px;font-weight:500;letter-spacing:0;text-transform:none;background:transparent;padding:0;max-width:220px;color:var(--ink)}
.sc-u .strip .tl .ok,.sc-u .strip .tl .rg{right:8px;bottom:auto;top:50%;transform:translateY(-50%)}
.sc-u .row>div:first-child{display:none}
.sc-u .btn:active{transform:scale(.985)}
'''
# ---- assets
def b64(im,q=85):
    bio=io.BytesIO(); im.convert('RGB').save(bio,'JPEG',quality=q); return 'data:image/jpeg;base64,'+base64.b64encode(bio.getvalue()).decode()
LST=[b64(Image.open(f'a_lst{i}.png')) for i in range(4)]
for f,box in [('img1.jpg',(0,0,1024,1024)),('img4.jpg',(120,120,1000,1000)),('img5.jpg',(0,0,1024,1024)),('./Group_86.jpg',None),('img2.jpg',(0,0,1024,1024))]:
    im=Image.open(f).convert('RGB'); im=im.crop(box) if box else im; LST.append(b64(im.resize((400,400),Image.LANCZOS),78))
MAIN=[b64(Image.open('./Group_86.jpg'),88)]
for f in ['./e5b7c0b0-8fec-454c-a79b-762a0124dc55.png','./ac9afbd2-4204-420c-934d-2a293da5a005-2.png']:
    MAIN.append(b64(Image.open(f).convert('RGB').resize((800,800),Image.LANCZOS),85))
APD=b64(Image.open('a_apd.png'),88); APM=b64(Image.open('a_apm.png'),88)
APIMG=[b64(Image.open(f'ap{i}.jpg').convert('RGB').resize((485,300),Image.LANCZOS),82) for i in range(1,7)]
T=open('template4.html').read()
T=T.replace('/*GCSS*/',gcss).replace('/*ACSS*/',acss).replace('/*UCSS*/','')
T=T.replace('<!--GBODY-->',gbody).replace('<!--ABODY-->',abody).replace('<!--UBODY-->','')
T=T.replace('/*GJS*/',gjs).replace('/*AJS*/',ajs).replace('/*UJS*/','')
T=T.replace('__LST__',json.dumps(LST)).replace('__MAIN__',json.dumps(MAIN)).replace('__APD__',APD).replace('__APM__',APM).replace('__APIMG__',json.dumps(APIMG))
open('pipeline-prototype.html','w').write(T); print(len(T)//1024,'KB')
