# patches applied to the gallery block (gjs/gbody) to add "brief" mode
SHORT={'A powerful 3000-watt element brings your water to the boil fast, so tea and coffee are ready in moments.': '3000 W element boils a full kettle in about four minutes.', 'Precision-built by Bosch and backed by a 1-year manufacturer warranty for lasting peace of mind.': 'Built by Bosch, backed by a one-year warranty.', 'Black stainless steel with the clean DesignLine silhouette \\u2014 a kettle that looks as good on the counter as it works.': 'Black stainless steel in the clean DesignLine silhouette.', 'Automatic shut-off, overheat and boil-dry protection, plus lift switch-off keep you and your kettle safe.': 'Auto shut-off, overheat and boil-dry protection built in.', 'A generous 1.7-litre capacity with an easy-to-read cup indicator lets you fill and heat exactly the amount you need.': '1.7 litres with a clear cup gauge on the side.', 'A removable spout filter blocks limescale, while the 360-degree base and under-base cord storage make everyday use effortless.': 'Removable limescale filter and a cordless 360\\u00b0 base.'}
def patch(gjs,gbody):
    def rep(old,new):
        nonlocal gjs
        assert old in gjs, old[:80]
        gjs=gjs.replace(old,new)
    rep(r"""if(s.st==='render')pv='<div class="sk"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i>';""",
        r"""if(s.st==='brief')pv='<div class="sk brief"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i>';else if(s.st==='render')pv='<div class="sk"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i>';""")
    rep(r"""if(s.st==='render')meta='<span class="st wk">'""",
        r"""if(s.st==='brief'){meta='';ctl='<div class="ctl"><button data-a="edit" class="ed" title="Edit text"><i class="ti ti-pencil"></i><span>Edit</span></button><button data-a="del" title="Remove"><i class="ti ti-x"></i></button></div>';}
    else if(s.st==='render')meta='<span class="st wk">'""")
    rep(r"""document.getElementById('g_hs').textContent=b?b+' of '+S.length+' in progress \u00b7 '+fmt(Math.floor(el())):'All done';""",
        r"""var brief=S.some(function(s){return s.st==='brief'});document.getElementById('g_hs').textContent=brief?S.length+' USPs':(b?b+' of '+S.length+' in progress \u00b7 '+fmt(Math.floor(el())):'All done');document.getElementById('g_hs').classList.toggle('alldone',!brief&&!b);if(brief)return 0;""")
    rep(r"""else t.innerHTML='<div class="sk"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i><span class="rg">'+ring(s.busy?s.p/100:curve(el(),s.tau))+'</span>';""",
        r"""else if(s.st==='brief')t.innerHTML='<div class="sk brief"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i>';else t.innerHTML='<div class="sk"></div><i class="ti '+(ICON[s.tag]||'ti-photo')+' ph"></i><span class="rg">'+ring(s.busy?s.p/100:curve(el(),s.tau))+'</span>';""")
    rep(r"""g.addEventListener('click',function(ev){if(ev.target.closest('[data-a], .ft, input, button'))return;var c=ev.target.closest('.c');if(!c)return;var i=+c.dataset.i;if(S[i].st==='done'&&!S[i].busy)lbOpen(i);});""",
        r"""g.addEventListener('click',function(ev){var c=ev.target.closest('.c');if(!c)return;var i=+c.dataset.i;var a=ev.target.closest('[data-a]');if(a&&a.dataset.a==='edit'){window.__galEdit&&window.__galEdit(i);return;}if(a&&a.dataset.a==='del'&&(S[i].st==='brief'||(S[i].st==='done'&&!S[i].busy))){if(S.length<2){return;}window.__galBefore&&window.__galBefore('Removed \u201c'+S[i].t+'\u201d.');S.splice(i,1);DEF.splice(i,1);render();return;}if(S[i].st==='brief'&&ev.target.closest('.bd')){window.__galEdit&&window.__galEdit(i);return;}if(ev.target.closest('[data-a], .ft, input, button'))return;if(S[i].st==='done'&&!S[i].busy)lbOpen(i);});""")

    # card tools: Comment button with text next to regen icon
    rep(r"""ctl='<div class="ctl"><button data-a="note" class="'+(s.note?'on':'')+'" title="Regenerate"><i class="ti ti-refresh"></i></button><button data-a="zoom" class="mob" title="View full size"><i class="ti ti-arrows-maximize"></i></button></div>';""",
        r"""ctl='<div class="ctl"><button data-a="cm" class="ed" title="Comment on the image"><i class="ti ti-message-2"></i><span>Comment</span></button><button data-a="note" class="'+(s.note?'on':'')+'" title="Regenerate"><i class="ti ti-refresh"></i></button><button data-a="del" title="Remove this slide"><i class="ti ti-x"></i></button></div>';""")
    # image overlay: two round icons — regenerate and comment
    rep(r"""<button class="ob '+(s.note?'on':'')+'" data-a="note" title="Regenerate"><i class="ti ti-refresh"></i></button><button class="ob mob" data-a="zoom" title="View full size"><i class="ti ti-arrows-maximize"></i></button>""",
        r"""<button class="ob '+(s.note?'on':'')+'" data-a="note" title="Regenerate"><i class="ti ti-refresh"></i></button><button class="ob" data-a="cm" title="Comment on the image"><i class="ti ti-message-2"></i></button>""")
    # click: cm opens lightbox in comment mode
    rep(r"""if(a&&a.dataset.a==='edit'){window.__galEdit&&window.__galEdit(i);return;}""",
        r"""if(a&&a.dataset.a==='edit'){window.__galEdit&&window.__galEdit(i);return;}if(a&&a.dataset.a==='cm'){if(S[i].st==='done'&&!S[i].busy){lbOpen(i);setTimeout(cmOpen,60);}return;}""")
    rep(r"""function init(){T0=Date.now();S=DEF.map(function(d){var s=Object.assign({},d);s.st='render';""",
        r"""function prepare(){g.classList.add('brief');S=DEF.map(function(d){var s=Object.assign({},d);s.st='brief';s.vars=[];s.vi=0;s.busy=false;s.p=0;s.note=false;return s;});render();}
  function init(){T0=Date.now();S=DEF.map(function(d){var s=Object.assign({},d);s.st='render';""")
    rep("window.startGallery=init;",
        r"""window.startGallery=init;window.GAL={prepare:prepare,get:function(i){return S[i]},set:function(i,t,d){S[i].t=t;S[i].d=d;DEF[i].t=t;DEF[i].d=d;render();},add:function(t,d,tag){var it={t:t,d:d,tag:tag||'Convenience',img:DEF[0].img};DEF.push(it);var s=Object.assign({},it);s.st='brief';s.vars=[];s.vi=0;s.busy=false;s.p=0;s.note=false;S.push(s);render();},count:function(){return S?S.length:0},all:function(){return DEF.map(function(d){return {t:d.t,d:d.d,tag:d.tag}})},replace:function(list){DEF.length=0;list.forEach(function(x){DEF.push({t:x.t,d:x.d,tag:x.tag||'Convenience',img:IMG0})});prepare();}};var IMG0=DEF[0].img;""")
    rep("if(!S)return;var changed=false;","if(!S||S.some(function(s){return s.st==='brief'}))return;var changed=false;")
    old='<div class="g" id="g_g"></div>'
    assert old in gbody
    gbody=gbody.replace(old,old+'\n  <div class="brief-cta" id="g_briefcta"><button class="addusp" onclick="PX.galAdd()">+ Add USP</button><div class="gpaste" id="g_paste"><button class="plink" onclick="PX.galPasteOpen()"><i class="ti ti-list"></i> <span class=\"pl-long\">Have your own list? Paste it instead</span><span class=\"pl-short\">Paste your own list</span></button><div class="gpbox" id="g_pbox"><textarea id="g_ptext" placeholder="One point per line, e.g.&#10;&#10;Rapid 3000W boil \u2014 heats a full kettle in under 3 minutes&#10;Triple safety \u2014 auto shut-off, boil-dry, overheat protection&#10;Keep-warm mode \u2014 holds temperature for 30 min&#10;&#10;Headline only is fine too."></textarea><div class="pfoot"><span>Each line becomes one USP. This replaces the list above.</span><button class="btn" onclick="PX.galPasteClose()">Cancel</button><button class="btn k" onclick="PX.galPasteBuild()">Build USPs</button></div></div></div><div class="gundo" id="g_undo"><span id="g_undotx"></span><button class="btn" onclick="PX.galUndo()">Undo</button></div><div class="lockhint"><i class="ti ti-lock"></i> Brief locks after approval &middot; up to 3 regenerations and 3 comments per slide</div><div class="cta"><button class="btn k lg" onclick="PX.galApprove()">Approve &amp; Generate Gallery Slides</button></div></div>')
    gbody=gbody.replace('Step 6/8','5/6')
    for a,bb in SHORT.items():
        if "d:'"+a+"'" in gjs: gjs=gjs.replace("d:'"+a+"'","d:'"+bb+"'")
    return gjs,gbody

BRIEF_CSS=r"""
.sc-g .pv .sk.brief{animation:none;background:#f3f3f4}
.sc-g .pv{transition:width .45s cubic-bezier(.4,0,.2,1),height .45s cubic-bezier(.4,0,.2,1)}
.sc-g .g.brief .pv{width:72px;height:72px;border-radius:8px}
.sc-g .g.brief .pv .ph{font-size:22px}
.sc-g .g.brief .c .r{align-items:flex-start}
@media (max-width:640px){.sc-g .g.brief .pv{width:72px;height:72px;aspect-ratio:auto}.sc-g .g.brief .c .r{flex-direction:row;gap:14px}.sc-g .g.brief .c .bd{width:auto;flex:1;min-width:0}}
.sc-g .ctl .ed{width:auto;padding:0 10px 0 8px;gap:6px;display:inline-flex;align-items:center;font-size:13px;font-weight:500;border-radius:6px}
.sc-g .c .bd{cursor:default}
.sc-g .c{position:relative}
.sc-g .g:not(.brief) .c .ctl{position:static;right:auto;bottom:auto;z-index:auto}
@media (max-width:640px){.sc-g .g:not(.brief) .c .ctl{position:static;margin-top:8px;justify-content:flex-end}}
.sc-g .brief-cta{display:none;margin-top:14px}
.sc-g .brief-cta.on{display:block}
.sc-g .addusp{height:52px;width:100%;border:1px dashed #96969c;border-radius:14px;background:#fff;font:inherit;font-size:16px;font-weight:500;color:var(--ink);cursor:pointer}
.sc-g .addusp:hover{background:#f6f6f7}
.sc-g .brief-cta .cta{margin-top:26px}
.sc-g .gpaste{margin-top:22px}
.sc-g .plink{display:inline-flex;align-items:center;gap:8px;background:none;border:0;padding:0;font:inherit;font-size:17px;color:#2f6cf6;cursor:pointer}
.sc-g .plink:hover{text-decoration:underline}
.sc-g .gpbox{display:none;margin-top:14px;border:1px solid #2f6cf6;border-radius:14px;overflow:hidden;box-shadow:0 0 0 3px #e9f0ff}
.sc-g .gpaste.open .gpbox{display:block}
.sc-g .gpaste.open .plink{display:none}
.sc-g .gpbox textarea{display:block;width:100%;min-height:160px;padding:16px;border:0;resize:vertical;font:inherit;font-size:15px;line-height:1.5;outline:none}
.sc-g .pfoot{display:flex;align-items:center;gap:10px;padding:10px 14px;border-top:1px solid var(--line);background:#f7f7f7;font-size:13px;color:#8a8a90}
.sc-g .pfoot span{flex:1}
.sc-g .gundo{display:none;align-items:center;gap:12px;margin-top:16px;padding:10px 14px;border-radius:12px;background:#f7f7f7;font-size:15px}
.sc-g .gundo.on{display:flex}
.sc-g .gundo span{flex:1}
.sc-g .gundo .btn{height:34px;padding:0 12px;font-size:14px}
.sc-g .gundo.on{animation:pop .2s ease-out}
.sc-g .btn.k.lg{height:52px;padding:0 20px;font-size:17px;font-weight:500;border-radius:10px}
.sc-g .step.collapsed .brief-cta{display:none}
@media (max-width:640px){.sc-g .c .r{flex-direction:column;gap:12px}.sc-g .pv{width:100%;height:auto;aspect-ratio:1/1;border-radius:10px}.sc-g .c .bd{width:100%}}
"""
