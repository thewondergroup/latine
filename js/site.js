(function(){
  var $=function(s,c){return (c||document).querySelector(s)},$$=function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s))};

  // local preview: make folder links open index.html when viewed from disk
  if(location.protocol==='file:'){$$('a[href]').forEach(function(a){var h=a.getAttribute('href');if(h&&!/^(https?:|mailto:|tel:|#)/.test(h)){var p=h.split('#');if(p[0].slice(-1)==='/'){a.setAttribute('href',p[0]+'index.html'+(p[1]?'#'+p[1]:''))}else if(p[0]===''||p[0]==='.'){}}})}

  // nav + mobile book bar
  var nav=$('#nav'),mbook=$('#mbook'),plain=document.body.classList.contains('plain');
  function onScroll(){var y=window.scrollY;if(nav&&!plain)nav.classList.toggle('solid',y>window.innerHeight*0.55);if(mbook)mbook.classList.toggle('show',y>window.innerHeight*0.5)}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  // videos: load when near the screen, play while visible, pause when not
  var vids=$$('video.vid'),reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load(v){if(!v.getAttribute('src')){v.src=v.getAttribute('data-src');}}
  function play(v){if(reduce)return;load(v);var p=v.play();if(p&&p.catch)p.catch(function(){})}
  if('IntersectionObserver' in window){
    var vo=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)play(e.target);else if(!e.target.paused)e.target.pause()})},{rootMargin:'200px 0px'});
    vids.forEach(function(v){if(v.offsetParent!==null||v.hasAttribute('data-eager'))vo.observe(v)});
  } else {vids.forEach(play)}
  vids.filter(function(v){return v.hasAttribute('data-eager')&&v.offsetParent!==null}).forEach(play);

  // parallax drift on photo bands
  var bands=$$('.parallax');
  if(bands.length&&!(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches)){
    var tick=false;
    function drift(){tick=false;var vh=window.innerHeight;bands.forEach(function(b){var r=b.getBoundingClientRect();if(r.bottom<0||r.top>vh)return;var pr=(r.top+r.height/2-vh/2)/vh;b.querySelectorAll('img').forEach(function(img){img.style.transform='translate3d(0,'+(pr*-9)+'%,0)'})})}
    window.addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(drift)}},{passive:true});drift();
  }

  // menu tabs: highlight the section in view
  var mt=$$('.mtabs a');
  if(mt.length&&'IntersectionObserver' in window){
    var mo=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var id=e.target.id;mt.forEach(function(a){a.classList.toggle('on',a.getAttribute('href')==='#'+id)});var on=$('.mtabs a.on');if(on&&on.scrollIntoView&&window.innerWidth<700){on.parentNode.scrollTo({left:on.offsetLeft-20,behavior:'smooth'})}}})},{rootMargin:'-45% 0px -50% 0px'});
    $$('.mpage').forEach(function(sec){mo.observe(sec)});
  }

  // hero slideshow
  var slides=$$('.hero .slide'),i=0;
  if(slides.length>1)setInterval(function(){slides[i].classList.remove('on');i=(i+1)%slides.length;slides[i].classList.add('on')},6500);

  // reveal
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.1,rootMargin:'0px 0px -40px 0px'});
    $$('.rv').forEach(function(el){io.observe(el)});
  } else {$$('.rv').forEach(function(el){el.classList.add('in')})}
  setTimeout(function(){$$('.hero .rv,.phero .rv').forEach(function(el){el.classList.add('in')})},150);

  // mobile menu
  var ov=$('#overlay');
  if(ov){
    var imgs=$$('.mo-media img',ov);
    function openM(){imgs.forEach(function(i){i.loading='eager'});ov.classList.add('open');ov.setAttribute('aria-hidden','false');document.documentElement.classList.add('small-open')}
    function closeM(){ov.classList.remove('open');ov.setAttribute('aria-hidden','true');document.documentElement.classList.remove('small-open')}
    $('#burger').onclick=openM;$('#close').onclick=closeM;
    document.addEventListener('keydown',function(e){if(e.key==='Escape')closeM()});
    $$('a',ov).forEach(function(a){a.addEventListener('click',closeM)});
    $$('.mo-links a',ov).forEach(function(a){a.addEventListener('mouseenter',function(){var i=a.getAttribute('data-i');imgs.forEach(function(im){im.classList.toggle('on',im.getAttribute('data-i')===i)})})});
  }

  // occasion preselect (also from ?occasion= on page load)
  function setOcc(v){$$('#chips input').forEach(function(r){r.checked=(r.value===v)})}
  $$('[data-occasion]').forEach(function(a){a.addEventListener('click',function(){setOcc(a.getAttribute('data-occasion'))})});

  // forms: posted to the Google Apps Script behind the enquiries sheet
  // the endpoint is kept out of the page markup and each submission carries a check code,
  // so scripts that post straight to the form address are rejected by the Google script
  var EP=['https://script.google','.com/macros/s/','AKfycbxJuxezp2XgzqYO22tVfzeNw8EKvIfsY_Isp0xqpPSo44ozssgDz1rbXOA4F3IJ-64tFQ','/exec'].join('');
  var T0=Date.now();
  function sig(s){var h=2166136261;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return (h>>>0).toString(16)}
  function send(form,ok,fail){
    var btn=form.querySelector('button[type=submit],button');if(btn){btn.disabled=true;btn.style.opacity=.6}
    var fd=new FormData(form),d=String(Date.now()-T0);
    fd.append('page',location.pathname);fd.append('d',d);
    fd.append('k',sig(String(fd.get('email')||'').trim().toLowerCase()+'|'+d+'|latine-w1s'));
    fetch(EP,{method:'POST',body:new URLSearchParams(fd)})
      .then(function(r){return r.json()}).then(function(j){if(j&&j.ok)ok();else throw 0})
      .catch(function(){if(btn){btn.disabled=false;btn.style.opacity=1}fail()});
  }
  var f=$('#enqForm');
  if(f)f.addEventListener('submit',function(e){e.preventDefault();
    send(f,function(){f.style.display='none';$('#thanks').style.display='block';
        // analytics: no personal data, only non-identifying enquiry details
        window.dataLayer=window.dataLayer||[];var g=function(n){var el=f.elements[n];return el?el.value:''};
        window.dataLayer.push({event:'enquiry_submit',form_page:location.pathname,enquiry_occasion:g('occasion'),enquiry_space:g('space'),enquiry_guests:g('guests')})},
      function(){var m=$('#enqErr')||document.createElement('p');m.id='enqErr';m.style.cssText='grid-column:1/-1;color:#A9573A;font-size:14px';
        m.innerHTML='Sorry, that didn\'t send. Please email <a href="mailto:contact@latinemayfair.com" style="border-bottom:1px solid">contact@latinemayfair.com</a> or call 020 3887 3126.';f.appendChild(m)})});
  $$('.news').forEach(function(n){n.addEventListener('submit',function(e){e.preventDefault();
    send(n,function(){n.innerHTML='<span style="padding:12px 0;color:#D9C49A;font-size:14px">Thank you, you\'re on the list.</span>';
        window.dataLayer=window.dataLayer||[];window.dataLayer.push({event:'newsletter_signup',form_page:location.pathname})},
      function(){n.insertAdjacentHTML('afterend','<p style="font-size:13px;color:#D9C49A;margin-top:8px">Sorry, please try again later.</p>')})})});

  // sparkles
  $$('.sparkles').forEach(function(x){for(var k=0;k<26;k++){var s=document.createElement('span');s.className='sparkle';s.style.left=(Math.random()*100)+'%';s.style.top=(Math.random()*60)+'%';s.style.animationDelay=(Math.random()*5)+'s';s.style.animationDuration=(4+Math.random()*4)+'s';x.appendChild(s)}});

  // press marquee loop
  var mq=$('#marquee');if(mq)mq.innerHTML+=mq.innerHTML;

  // gallery filters + lightbox
  var gal=$('.gal');
  if(gal){
    var items=$$('a',gal);
    $$('.filters button').forEach(function(b){b.addEventListener('click',function(){
      $$('.filters button').forEach(function(x){x.classList.remove('on')});b.classList.add('on');
      var c=b.getAttribute('data-f');items.forEach(function(a){a.classList.toggle('hide',c!=='all'&&a.getAttribute('data-c')!==c)})
    })});
    var lb=$('#lb'),lbi=$('#lb img'),cur=0;
    function vis(){return items.filter(function(a){return !a.classList.contains('hide')})}
    function show(n){var v=vis();cur=(n+v.length)%v.length;lbi.src=v[cur].getAttribute('href');lbi.alt=$('img',v[cur]).alt;lb.classList.add('open')}
    items.forEach(function(a){a.addEventListener('click',function(e){e.preventDefault();show(vis().indexOf(a))})});
    $('.x',lb).onclick=function(){lb.classList.remove('open')};
    $('.pv',lb).onclick=function(){show(cur-1)};$('.nx',lb).onclick=function(){show(cur+1)};
    lb.addEventListener('click',function(e){if(e.target===lb)lb.classList.remove('open')});
    document.addEventListener('keydown',function(e){if(!lb.classList.contains('open'))return;if(e.key==='Escape')lb.classList.remove('open');if(e.key==='ArrowLeft')show(cur-1);if(e.key==='ArrowRight')show(cur+1)});
  }
})();

// cookie consent: banner + choices (Google Consent Mode v2 defaults are set inline in <head> before GTM)
(function(){
  var KEY='lm_consent',box=document.getElementById('cc');if(!box)return;
  var main=box.querySelector('.cc-main'),pref=box.querySelector('.cc-pref'),ca=document.getElementById('cc-a'),cm=document.getElementById('cc-m');
  function get(){try{var c=JSON.parse(localStorage.getItem(KEY)||'null');if(c&&c.v===1&&Date.now()-c.t<15552000000)return c}catch(e){}return null}
  function gt(){window.dataLayer=window.dataLayer||[];window.dataLayer.push(arguments)}
  function clear(re){document.cookie.split(';').forEach(function(k){var n=k.split('=')[0].trim();if(!re.test(n))return;
    var d=location.hostname.split('.'),gone='=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/';document.cookie=n+gone;
    while(d.length>1){document.cookie=n+gone+';domain=.'+d.join('.');d.shift()}})}
  function apply(a,m){
    gt('consent','update',{analytics_storage:a?'granted':'denied',ad_storage:m?'granted':'denied',ad_user_data:m?'granted':'denied',ad_personalization:m?'granted':'denied'});
    try{localStorage.setItem(KEY,JSON.stringify({v:1,t:Date.now(),a:a,m:m}))}catch(e){}
    if(!a)clear(/^(_ga|_gid|_gat)/);if(!m)clear(/^(_fbp|_fbc)/);
    window.dataLayer.push({event:'consent_update',consent_analytics:a,consent_marketing:m});
    if(m)window.dataLayer.push({event:'marketing_consent'});else if(window.fbq)window.fbq('consent','revoke');
    box.hidden=true;
  }
  function open(){var c=get();ca.checked=!!(c&&c.a);cm.checked=!!(c&&c.m);main.hidden=false;pref.hidden=true;box.hidden=false;var b=box.querySelector('.cc-go');if(b)b.focus()}
  box.addEventListener('click',function(e){var b=e.target.closest('[data-cc]');if(!b)return;var k=b.getAttribute('data-cc');
    if(k==='accept')apply(true,true);else if(k==='reject')apply(false,false);
    else if(k==='choose'){main.hidden=true;pref.hidden=false}else if(k==='back'){pref.hidden=true;main.hidden=false}
    else if(k==='save')apply(ca.checked,cm.checked)});
  document.addEventListener('click',function(e){var o=e.target.closest('[data-cc-open]');if(o){e.preventDefault();open()}});
  var saved=get();
  if(saved&&saved.m)window.dataLayer.push({event:'marketing_consent'});   // returning visitor who allowed marketing: Meta starts (GTM tag fires only on this event)
  if(!saved)box.hidden=false;
})();
