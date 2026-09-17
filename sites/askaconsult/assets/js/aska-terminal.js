/* ASKA shared terminal component (v6.12 — slice2: /back nests to the archived v1.0 tree; /home and /reset stay on v2)
   Single implementation, mountable anywhere. Config: {root, api, commands, hint, theme}.
   Command map is DATA — drives both dispatch and /help (single source of truth). */
(function(){
  if(window.ASKA_Terminal) return;
  window.ASKA_Terminal = function(cfg){
    var root = cfg.root || document.getElementById('askterm');
    if(!root) return;
    // Terminal is visible by default; no no-js gate to clear.
    var out = root.querySelector('.term-body'), line = root.querySelector('.termline-input, .term-input input');
    if(!out || !line) return;
    var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

    // COMMAND MAP (single source of truth)
    var C = cfg.commands || [
      {cmds:['/help','help'], action:'help', label:'show all commands'},
      {cmds:['/digital','/enter','digital','enter'], action:'nav', target:'/digital/', label:'go to ASKA Digital'},
      {cmds:['/physical','physical'], action:'nav', target:'/physical/', label:'go to ASKA Physical'},
      {cmds:['/home','/reset','home','reset'], action:'nav', target:'/', label:'return to the live site (v2)'},
      {cmds:['/back','back'], action:'nav', target:'/back/', label:'open the archived v1.0 site'},
      {cmds:['/portfolio','/proof','portfolio','proof'], action:'nav', target:'/digital/#proof', label:'open live proof artifacts'},
      {cmds:['/contact','/book','/mail','/email','contact','book','mail','email'], action:'mailto', target:'info@askaconsult.com', label:'contact us'},
      {cmds:['/info','info'], action:'nav', target:'/digital/#benefits', label:'what we do, in brief'},
      {cmds:['/faq','faq'], action:'nav', target:'/digital/#faq', label:'frequently asked questions'},
      {cmds:['/game','game'], action:'nav', target:cfg.gameUrl||'https://typejoy.askaconsult.com/demo.html', label:'play our live interactive demo'},
      {cmds:['/github','github'], action:'nav', target:'https://github.com/ahrazzle', label:'our code on GitHub'},
      {cmds:['/call','/phone','call','phone'], action:'tel', target:'289-928-9554', label:'call us directly'}
    ];
    // build lookup: alias -> command record
    var LOOKUP = {};
    C.forEach(function(c){ c.cmds.forEach(function(a){ LOOKUP[a.toLowerCase()] = c; }); });

    function addLine(html){ var p=document.createElement('p'); p.innerHTML=html; out.appendChild(p); out.scrollTop=out.scrollHeight; return p; }
    function typeLine(html){
      var p=document.createElement('p'); p.style.opacity='0'; out.appendChild(p);
      if(reduced){ p.innerHTML=html; p.style.opacity='1'; out.scrollTop=out.scrollHeight; return; }
      var plain=html.replace(/<[^>]+>/g,''); var i=0;
      (function type(){ if(i<plain.length){ p.textContent+=plain[i++]; p.style.opacity='1'; setTimeout(type,16);} else { p.innerHTML=html; out.scrollTop=out.scrollHeight; } })();
    }
    function help(){
      addLine('<span class="tk">$</span> available commands:');
      C.forEach(function(c){
        addLine('  <span class="tc">'+c.cmds[0]+'</span> <span class="dim">— '+c.label+'</span>');
      });
      addLine('or just ask me anything about ASKA.');
    }
    function respond(raw){
      var t=raw.trim(); if(!t) return;
      addLine('<span class="tk">$</span> '+t.replace(/</g,'&lt;'));
      var parts=t.split(/\s+/); var cmd=parts[0].toLowerCase();
      var rec=LOOKUP[cmd];
      if(rec && rec.action==='help'){ help(); return; }
      if(rec){
        var target=rec.target;
        if(rec.action==='mailto'){ window.location.href='mailto:'+target; return; }
        if(rec.action==='tel'){ window.location.href='tel:'+target; return; }
        if(rec.action==='nav'){ addLine('<span class="ok">→</span> navigating…'); window.location.href=target; return; }
      }
      // raw text -> LLM (showcase assistant)
      var api = cfg.api || '/api/ask';
      addLine('<span class="dim">thinking…</span>');
      fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q:t})})
        .then(function(r){ return r.json(); })
        .then(function(d){ typeLine('<span class="dim">'+String(d.a||(d.error ? 'Assistant unavailable right now. Try /help to explore, or /contact to reach us.' : 'No answer received. Try /help.')).replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</span>'); })
        .catch(function(){ addLine('<span class="dim">assistant unavailable — try /help</span>'); });
    }
    line.addEventListener('keydown', function(e){
      if(e.key==='Enter'){ e.preventDefault(); respond(line.value); line.value=''; }
    });
    // click focuses input, never navigates
    root.addEventListener('click', function(e){ e.preventDefault(); e.stopPropagation(); line.focus(); });
    if(cfg.autoFocus !== false) setTimeout(function(){ line.focus(); }, cfg.focusDelay||900);
    // auto-type intro
    if(!reduced && cfg.intro){
      var introP=addLine('<span class="tk">$</span> <span class="typing"></span>');
      var span=introP.querySelector('.typing'); var idx=0;
      (function ti(){ if(idx<cfg.intro.length){ span.textContent+=cfg.intro[idx++]; setTimeout(ti,34);} else { addLine('<span class="ok">✓</span> '+cfg.readyLine+' — type a command below'); line.focus(); } })();
    }
    return {respond:respond, help:help};
  };
})();
