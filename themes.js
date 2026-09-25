(function(){
  var KEY='house-theme';
  var THEMES={
    midnight:{ink:'#0b1214',soft:'#121a19',muted:'#1a2423',gold:'#2ee6c7',goldwarm:'#6fe0c4',golddim:'rgba(46,230,199,.28)',text:'#e8fbf6',textmuted:'#9ab3ad'},
    dawn:{ink:'#f4f1ea',soft:'#fffaf3',muted:'#ece6da',gold:'#0f766e',goldwarm:'#0f766e',golddim:'rgba(15,118,110,.22)',text:'#1a1814',textmuted:'#5c574e'},
    nord:{ink:'#2e3440',soft:'#3b4252',muted:'#434c5e',gold:'#88c0d0',goldwarm:'#88c0d0',golddim:'rgba(136,192,208,.28)',text:'#eceff4',textmuted:'#88c0d0'},
    solarized:{ink:'#002b36',soft:'#073642',muted:'#0a3d49',gold:'#b58900',goldwarm:'#b58900',golddim:'rgba(181,137,0,.28)',text:'#eee8d5',textmuted:'#93a1a1'},
    dracula:{ink:'#282a36',soft:'#21222c',muted:'#343746',gold:'#50fa7b',goldwarm:'#bd93f9',golddim:'rgba(80,250,123,.28)',text:'#f8f8f2',textmuted:'#bd93f9'},
    ocean:{ink:'#0b1c24',soft:'#12262e',muted:'#16313b',gold:'#2ec4b6',goldwarm:'#2ec4b6',golddim:'rgba(46,196,182,.28)',text:'#d8f3ff',textmuted:'#7fadb8'}
  };
  var LABELS={midnight:'Midnight',dawn:'Dawn',nord:'Nord',solarized:'Solarized',dracula:'Dracula',ocean:'Ocean'};
  var ORDER=['midnight','dawn','nord','solarized','dracula','ocean'];
  function apply(name){
    if(!(name in THEMES)) name='midnight';
    var t=THEMES[name];
    var r=document.documentElement;
    r.setAttribute('data-theme',name);
    r.style.setProperty('--ink',t.ink);
    r.style.setProperty('--ink-soft',t.soft);
    r.style.setProperty('--ink-muted',t.muted);
    r.style.setProperty('--gold',t.gold);
    r.style.setProperty('--gold-warm',t.goldwarm);
    r.style.setProperty('--gold-dim',t.golddim);
    r.style.setProperty('--text',t.text);
    r.style.setProperty('--text-muted',t.textmuted);
    if(document.body){document.body.style.background=t.ink;document.body.style.color=t.text;}
    try{localStorage.setItem(KEY,name);}catch(e){}
    document.querySelectorAll('[data-theme-item]').forEach(function(el){
      el.classList.toggle('on', el.getAttribute('data-theme-item')===name);
    });
    var cur=document.getElementById('themeCur');
    if(cur) cur.textContent=LABELS[name];
  }
  function mount(){
    if(document.getElementById('themeMenu')) return;
    var css=document.createElement('style');
    css.textContent=[
      '.topbar{width:100%;max-width:calc(40rem + 4rem);padding:12px 1rem;display:flex;align-items:center;gap:8px;flex-wrap:nowrap}',
      '.lang-switch{display:flex;gap:4px;flex-wrap:wrap}',
      '.lang-btn{background:transparent;border:1px solid var(--gold-dim);color:var(--text-muted);min-width:36px;min-height:32px;padding:6px 8px;border-radius:8px;font:600 12px Outfit,system-ui;cursor:pointer}',
      '.lang-btn.on{color:var(--text);border-color:var(--gold)}',
      '.theme-wrap{position:relative;margin-left:auto}',
      '.theme-btn{display:flex;align-items:center;gap:6px;background:var(--ink-soft);color:var(--text);border:1px solid var(--gold-dim);border-radius:999px;min-height:32px;padding:6px 12px;font:600 13px Outfit,system-ui;cursor:pointer}',
      '.theme-dot{width:10px;height:10px;border-radius:50%;background:var(--gold)}',
      '.theme-panel{display:none;position:absolute;right:0;top:calc(100% + 8px);min-width:200px;background:#16181d;border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:10px;z-index:80}',
      '.theme-wrap.open .theme-panel{display:block}',
      '.theme-panel p{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:#8b93a0;margin:0 8px 8px}',
      '.theme-item{display:flex;align-items:center;gap:10px;width:100%;border:0;background:transparent;color:#e8eef2;padding:10px;border-radius:12px;font:600 14px Outfit,system-ui;cursor:pointer;text-align:left}',
      '.theme-item.on{background:#14302c;color:#2ee6c7}',
      '.theme-item i{width:14px;height:14px;border-radius:50%;display:block}',
      '.theme-item .ck{margin-left:auto;opacity:0}',
      '.theme-item.on .ck{opacity:1}'
    ].join('');
    document.head.appendChild(css);
    var bar=document.getElementById('topbar');
    var wrap=document.createElement('div');
    wrap.className='theme-wrap';
    wrap.id='themeMenu';
    wrap.innerHTML='<button type="button" class="theme-btn" id="themeOpen"><i class="theme-dot"></i><span id="themeCur">Midnight</span></button>';
    var panel=document.createElement('div');
    panel.className='theme-panel';
    panel.innerHTML='<p>Choose theme</p>';
    ORDER.forEach(function(k){
      var b=document.createElement('button');
      b.type='button';
      b.className='theme-item';
      b.setAttribute('data-theme-item',k);
      b.innerHTML='<i style="background:'+THEMES[k].gold+'"></i><span>'+LABELS[k]+'</span><span class="ck">✓</span>';
      b.onclick=function(){apply(k);wrap.classList.remove('open');};
      panel.appendChild(b);
    });
    wrap.appendChild(panel);
    bar.appendChild(wrap);
    document.getElementById('themeOpen').onclick=function(e){e.stopPropagation();wrap.classList.toggle('open');};
    document.addEventListener('click',function(){wrap.classList.remove('open');});
  }
  var start='midnight';
  try{start=localStorage.getItem(KEY)||'midnight';}catch(e){}
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',function(){mount();apply(start);});
  }else{mount();apply(start);}
})();
