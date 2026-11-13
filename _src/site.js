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

  // forms: front-end only until wired to an inbox / Google Sheet
  var f=$('#enqForm');
  if(f)f.addEventListener('submit',function(e){e.preventDefault();f.style.display='none';$('#thanks').style.display='block'});
  $$('.news').forEach(function(n){n.addEventListener('submit',function(e){e.preventDefault();n.innerHTML='<span style="padding:12px 0;color:#D9C49A;font-size:14px">Thank you, you\'re on the list.</span>'})});

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
