/* Kai — учёт посещений на гайдах и кейсах. Собирается site_script.py из шаблона, руками не править. */
(function(){
  'use strict';
  var T={"ru":{"text":"Мы используем cookie для аналитики посещаемости. Без твоего согласия они не ставятся — сайт работает и без них. Подробнее в <a href=\"https://aii-crm.com/privacy.html\">Политике конфиденциальности</a>.","accept":"Принять","decline":"Только необходимые","settings":"Настройки cookie"},"en":{"text":"We use cookies for site analytics. Nothing is stored without your consent — the site works fine without them. See our <a href=\"https://aii-crm.com/privacy-en.html\">Privacy Policy</a>.","accept":"Accept","decline":"Only necessary","settings":"Cookie settings"},"de":{"text":"Wir nutzen Cookies für die Website-Analyse. Ohne deine Zustimmung wird nichts gespeichert — die Seite funktioniert auch ohne. Mehr dazu in unserer <a href=\"https://aii-crm.com/privacy-de.html\">Datenschutzerklärung</a>.","accept":"Akzeptieren","decline":"Nur notwendige","settings":"Cookie-Einstellungen"},"fr":{"text":"Nous utilisons des cookies pour l’analyse d’audience du site. Rien n’est stocké sans votre consentement — le site fonctionne très bien sans. Voir notre <a href=\"https://aii-crm.com/privacy-fr.html\">politique de confidentialité</a>.","accept":"Accepter","decline":"Essentiels seulement","settings":"Gérer les cookies"},"es":{"text":"Usamos cookies para la analítica del sitio. No se guarda nada sin tu consentimiento; el sitio funciona bien sin ellas. Consulta nuestra <a href=\"https://aii-crm.com/privacy-es.html\">Política de privacidad</a>.","accept":"Aceptar","decline":"Solo necesarias","settings":"Ajustes de cookies"},"pl":{"text":"Używamy cookies do analityki strony. Nic nie jest zapisywane bez twojej zgody — strona działa bez nich. Zobacz naszą <a href=\"https://aii-crm.com/privacy-pl.html\">Politykę prywatności</a>.","accept":"Akceptuj","decline":"Tylko niezbędne","settings":"Ustawienia cookies"},"pt":{"text":"Usamos cookies para análise de tráfego do site. Nada é armazenado sem o seu consentimento — o site funciona normalmente sem eles. Veja nossa <a href=\"https://aii-crm.com/privacy-pt.html\">Política de Privacidade</a>.","accept":"Aceitar","decline":"Só os necessários","settings":"Configurar cookies"},"it":{"text":"Usiamo i cookie per le statistiche del sito. Nulla viene salvato senza il tuo consenso — il sito funziona bene anche senza. Leggi la nostra <a href=\"https://aii-crm.com/privacy-it.html\">Privacy Policy</a>.","accept":"Accetta","decline":"Solo necessari","settings":"Impostazioni cookie"},"tr":{"text":"Çerezleri site analitiği için kullanıyoruz. Onayın olmadan hiçbir şey saklanmaz — site onlarsız da sorunsuz çalışır. Bkz. <a href=\"https://aii-crm.com/privacy-tr.html\">Gizlilik Politikası</a>.","accept":"Kabul et","decline":"Yalnızca gerekli","settings":"Çerez ayarları"},"be":{"text":"Мы выкарыстоўваем cookie для аналітыкі наведвальнасці. Без тваёй згоды яны не ставяцца — сайт працуе і без іх. Падрабязней у <a href=\"https://aii-crm.com/privacy-by.html\">Палітыцы прыватнасці</a>.","accept":"Прыняць","decline":"Толькі неабходныя","settings":"Налады cookie"},"uk":{"text":"Ми використовуємо cookie для аналітики сайту. Без твоєї згоди нічого не зберігається — сайт працює і без них. Детальніше в <a href=\"https://aii-crm.com/privacy-ua.html\">Політиці конфіденційності</a>.","accept":"Прийняти","decline":"Лише необхідні","settings":"Налаштування cookie"},"ro":{"text":"Folosim cookie-uri pentru analiza traficului. Nimic nu se stochează fără acordul tău — site-ul merge bine și fără ele. Vezi <a href=\"https://aii-crm.com/privacy-ro.html\">Politica de confidențialitate</a>.","accept":"Accept","decline":"Doar necesare","settings":"Setări cookie"}};
  var API='https://app.aii-crm.com/track', KEY='kai_cookie_consent', YM=114121439;
  var d=document, LANG=(d.documentElement.lang||'en').toLowerCase().slice(0,2), t=T[LANG]||T.en;
  function ls(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }
  function lsSet(k,v){ try{ localStorage.setItem(k,v); }catch(e){} }
  function send(o){ try{ navigator.sendBeacon(API,JSON.stringify(o)); }catch(e){} }
  /* владелец и команда: ?me=1 один раз в браузере — дальше этот браузер не считается */
  try{ if(new URLSearchParams(location.search).get('me')==='1') lsSet('kai_no_track','1'); }catch(e){}
  var MUTE=ls('kai_no_track')==='1', consent=ls(KEY);
  try{ if(MUTE&&!ls('kai_me_sent')){ lsSet('kai_me_sent','1'); send({vid:ls('kai_vid')||'',event:'internal_mark'}); } }catch(e){}

  function urlUtm(){ try{ var p=new URLSearchParams(location.search), v=['utm_source','utm_medium','utm_campaign'].map(function(k){ return (p.get(k)||'').slice(0,40); });
    if(!v[0]&&p.get('s')) v=[p.get('s').slice(0,40),'bio','']; return v.some(Boolean)?v.join('/'):''; }catch(e){ return ''; } }
  /* реферер без лишнего: у чужого сайта только адрес сайта, у своей страницы путь без параметров */
  function shortRef(){ try{ if(!d.referrer) return ''; var u=new URL(d.referrer); return (/(^|\.)aii-crm\.com$/.test(u.hostname)?u.origin+u.pathname:u.origin+'/'); }catch(e){ return ''; } }

  /* 1. Обезличенный заход: без cookie и без идентификатора, до согласия. После «Только необходимые» не шлётся. */
  if(!MUTE&&consent!=='declined') send({event:'hit',path:location.pathname,ref:shortRef(),lang:LANG,utm:urlUtm(),wd:navigator.webdriver?1:0});

  /* 3. События по cookie — только после «Принять» */
  var on=false, V='';
  function vid(){ try{ var m=d.cookie.match(/(?:^|; )kai_vid=([a-f0-9-]+)/), v=m?m[1]:(ls('kai_vid')||'');
    if(!v) v=(window.crypto&&crypto.randomUUID)?crypto.randomUUID():Date.now()+'-'+Math.random().toString(16).slice(2);
    lsSet('kai_vid',v); d.cookie='kai_vid='+v+'; max-age=31536000; path=/; SameSite=Lax'; return v; }catch(e){ return ''; } }
  function forget(){ try{ localStorage.removeItem('kai_vid'); localStorage.removeItem('kai_utm'); localStorage.removeItem('kai_utm_ts'); }catch(e){}
    try{ d.cookie='kai_vid=; max-age=0; path=/; SameSite=Lax'; }catch(e){}
    /* отзыв согласия убирает и то, что успела поставить Метрика: её cookie и записи в памяти браузера */
    try{ d.cookie.split(';').forEach(function(c){ var n=c.split('=')[0].trim(); if(n.indexOf('_ym')!==0) return;
      ['','; domain='+location.hostname,'; domain=.'+location.hostname.replace(/^www\./,'')].forEach(function(dm){ d.cookie=n+'=; max-age=0; path=/'+dm; }); }); }catch(e){}
    try{ Object.keys(localStorage).forEach(function(k){ if(k.indexOf('_ym')===0) localStorage.removeItem(k); }); }catch(e){} }
  /* метка ссылки: первая живёт 30 дней (только после согласия), чтобы возврат «напрямую» приписывался каналу */
  function utm(){ var j=urlUtm(); try{ if(j){ if(on){ lsSet('kai_utm',j); lsSet('kai_utm_ts',String(Date.now())); } return j; }
    var ts=+ls('kai_utm_ts')||0; return (ts&&Date.now()-ts<30*864e5)?(ls('kai_utm')||''):''; }catch(e){ return j; } }
  function src(){ var u=utm().split('/'), n=function(x){ return (x||'').toLowerCase().replace(/[^a-z0-9-]+/g,'-').replace(/^-+|-+$/g,''); }, a=n(u[0]);
    if(!a) return ''; var c=n(u[2]); return (c?a+'-'+c:a).slice(0,24).replace(/-+$/,''); }
  function track(ev,val){ if(!on||MUTE) return;
    var DEV=matchMedia('(hover: none)').matches?'mobile':'desktop', TZ=''; try{ TZ=Intl.DateTimeFormat().resolvedOptions().timeZone||''; }catch(e){}
    send({vid:V,event:ev,path:location.pathname+location.hash,ref:d.referrer,lang:LANG,utm:utm(),dev:DEV,sw:screen.width,tz:TZ,val:(val|0),wd:navigator.webdriver?1:0}); }
  function ymStart(){ if(!YM||window.ym||MUTE) return;
    (function(m,e,s,r,i,k,a){ m[i]=m[i]||function(){ (m[i].a=m[i].a||[]).push(arguments); }; m[i].l=1*new Date(); k=e.createElement(s); a=e.getElementsByTagName(s)[0]; k.async=1; k.src=r; a.parentNode.insertBefore(k,a); })(window,d,'script','https://mc.yandex.ru/metrika/tag.js?id='+YM,'ym');
    window.ym(YM,'init',{ssr:true,clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:false}); }
  function start(){ if(on) return; V=vid(); on=true; track('pageview'); ymStart(); }
  function stop(){ on=false; V=''; forget(); }

  /* вовлечённость — как на главной: engaged (10 с и действие или скролл), глубина 50/90, активные секунды на вкладке */
  (function(){
    var sent={}, active=0, last=Date.now(), vis=!d.hidden, inter=false;
    function once(ev,val){ var k=ev+(val||''); if(!on||sent[k]) return; sent[k]=1; track(ev,val); }
    function tick(){ var now=Date.now(); if(vis) active+=now-last; last=now; }
    function depth(){ var h=d.documentElement.scrollHeight-innerHeight; return h<=0?100:Math.round(scrollY/h*100); }
    ['click','keydown','touchstart'].forEach(function(e){ addEventListener(e,function(){ inter=true; },{passive:true,once:true}); });
    addEventListener('scroll',function(){ var x=depth(); if(x>=50) once('scroll',50); if(x>=90) once('scroll',90); },{passive:true});
    setTimeout(function(){ if(inter||depth()>=25) once('engaged'); else { var f=function(){ once('engaged'); }; addEventListener('scroll',f,{once:true,passive:true}); addEventListener('click',f,{once:true}); } },10000);
    function leave(){ tick(); var sec=Math.round(active/1000); active=0; if(sec>0&&on) track('leave',Math.min(sec,1800)); }
    d.addEventListener('visibilitychange',function(){ tick(); vis=!d.hidden; if(d.hidden) leave(); });
    addEventListener('pagehide',leave);
    /* клики: Telegram и веб-чат — целевые действия; в ссылки app едет id посетителя, в диплинк Telegram — источник */
    d.addEventListener('click',function(e){ var a=e.target&&e.target.closest&&e.target.closest('a[href]'); if(!a) return; var h=a.href||'';
      if(h.indexOf('t.me/aiicrm_bot')>=0){ track('tg_click'); var s=src(); if(!s) return;
        try{ var u=new URL(h), st=u.searchParams.get('start')||''; if(/(^|__)s_[a-z0-9-]+$/.test(st)) return; var nx=st?st+'__s_'+s:'s_'+s; if(nx.length<=64){ u.searchParams.set('start',nx); a.href=u.toString(); } }catch(x){}
      } else if(h.indexOf('https://app.aii-crm.com/')===0){ if(h.indexOf('app.aii-crm.com/chat')>=0) track('webchat_open'); if(!on||!V) return;
        try{ var w=new URL(h); if(!w.searchParams.has('v')) w.searchParams.set('v',V); a.href=w.toString(); }catch(x){} }
    },true);
  })();

  /* 2. Баннер cookie: ключ общий с главной, поэтому выбор один на весь сайт */
  var box=null;
  function build(){ if(box) return;
    var st=d.createElement('style');
    st.textContent='.kai-ck{position:fixed;left:0;right:0;bottom:0;z-index:9999;display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;'
      +'padding:16px 24px calc(16px + env(safe-area-inset-bottom,0px));background:var(--bg-1,#100E20);border-top:1px solid var(--border,#241D45);color:var(--text,#CBC5E4);'
      +'font-size:13px;line-height:1.5;transform:translateY(100%);visibility:hidden;transition:transform .4s ease,visibility 0s .4s}'
      +'.kai-ck.on{transform:translateY(0);visibility:visible;transition:transform .4s ease}.kai-ck span{max-width:70ch}.kai-ck a{color:var(--accent-2,#A78BFA)}'
      +'.kai-ck-b{display:flex;gap:8px;flex-shrink:0}.kai-ck button{padding:8px 18px;border-radius:10px;font-family:inherit;font-size:12px;font-weight:600;cursor:pointer;border:1px solid transparent}'
      +'.kai-ck button:hover{opacity:.85}.kai-ck button:focus-visible{outline:2px solid var(--accent-2,#A78BFA);outline-offset:2px}'
      +'.kai-ck-y{background:var(--accent,#7C5CFF);color:#fff}.kai-ck-n{background:var(--bg-2,#171332);border-color:var(--border,#241D45)!important;color:var(--ink,#F4F2FF)}'
      +'@media (max-width:640px){.kai-ck{font-size:12px;padding:12px 16px calc(12px + env(safe-area-inset-bottom,0px));gap:10px}.kai-ck-b{width:100%}.kai-ck button{flex:1}}'
      +'@media (prefers-reduced-motion:reduce){.kai-ck,.kai-ck.on{transition:none}}';
    d.head.appendChild(st);
    box=d.createElement('div'); box.id='kaiCookie'; box.className='kai-ck'; box.setAttribute('role','region'); box.setAttribute('aria-label','Cookie');
    box.innerHTML='<span>'+t.text+'</span><div class="kai-ck-b"><button type="button" class="kai-ck-y">'+t.accept+'</button><button type="button" class="kai-ck-n">'+t.decline+'</button></div>';
    d.body.appendChild(box);
    box.querySelector('.kai-ck-y').addEventListener('click',function(){ lsSet(KEY,'accepted'); consent='accepted'; hide(); start(); });
    box.querySelector('.kai-ck-n').addEventListener('click',function(){ lsSet(KEY,'declined'); consent='declined'; hide(); stop(); });
  }
  /* без requestAnimationFrame: во вкладке, открытой в фоне, он не срабатывает и баннер так и не появился бы */
  function show(){ build(); void box.offsetHeight; box.classList.add('on'); }
  function hide(){ if(box) box.classList.remove('on'); }
  /* отозвать согласие должно быть так же просто, как дать: ссылка «Настройки cookie» в подвале страницы */
  (function(){ var f=d.querySelector('footer'); if(!f) return; var a=d.createElement('a'); a.href='#'; a.id='kaiCookieSettings'; a.textContent=t.settings; a.style.color='inherit';
    a.addEventListener('click',function(e){ e.preventDefault(); show(); }); f.appendChild(d.createTextNode(' · ')); f.appendChild(a); })();

  if(consent==='accepted') start(); else if(consent==='declined') forget(); else setTimeout(show,1000);
})();
