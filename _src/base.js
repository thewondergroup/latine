
  // nav state
  var nav=document.getElementById('nav'),mbook=document.getElementById('mbook');
  function onScroll(){var y=window.scrollY;nav.classList.toggle('solid',y>window.innerHeight*0.7);mbook.classList.toggle('show',y>window.innerHeight*0.6)}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();

  // hero slideshow
  var slides=document.querySelectorAll('.hero .slide'),i=0;
  setInterval(function(){slides[i].classList.remove('on');i=(i+1)%slides.length;slides[i].classList.add('on')},6500);

  // reveal
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.rv').forEach(function(el){io.observe(el)});
  setTimeout(function(){document.querySelectorAll('.hero .rv').forEach(function(el){el.classList.add('in')})},150);

  // mobile menu
  var ov=document.getElementById('overlay');
  document.getElementById('burger').onclick=function(){ov.classList.add('open')};
  document.getElementById('close').onclick=function(){ov.classList.remove('open')};
  ov.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){ov.classList.remove('open')})});

  // occasion preselect
  document.querySelectorAll('[data-occasion]').forEach(function(a){a.addEventListener('click',function(){
    var v=a.getAttribute('data-occasion');document.querySelectorAll('#chips input').forEach(function(r){r.checked=(r.value===v)});
  })});

  // forms (front-end only until wired up)
  document.getElementById('enqForm').addEventListener('submit',function(e){e.preventDefault();this.style.display='none';document.getElementById('thanks').style.display='block'});
  document.getElementById('newsForm').addEventListener('submit',function(e){e.preventDefault();this.innerHTML='<span style="padding:12px 0;color:#D9C49A;font-size:14px">Thank you, you\'re on the list.</span>'});

  // christmas sparkles
  var x=document.querySelector('.xmas');
  for(var k=0;k<26;k++){var s=document.createElement('span');s.className='sparkle';s.style.left=(Math.random()*100)+'%';s.style.top=(Math.random()*60)+'%';s.style.animationDelay=(Math.random()*5)+'s';s.style.animationDuration=(4+Math.random()*4)+'s';x.appendChild(s)}

  // duplicate press for seamless loop
  var mq=document.getElementById('marquee');mq.innerHTML+=mq.innerHTML;
