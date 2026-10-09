(function(){
var r=document.documentElement;
try{var t=localStorage.getItem('bn-theme');if(t)r.dataset.theme=t}catch(e){}
var b=document.getElementById('theme');
function dark(){return r.dataset.theme==='dark'||(!r.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches)}
function sync(){if(b)b.textContent=dark()?'☀':'☾'}
if(b)b.onclick=function(){r.dataset.theme=dark()?'light':'dark';try{localStorage.setItem('bn-theme',r.dataset.theme)}catch(e){}sync()};
sync();
var q=document.getElementById('q'),items=[].slice.call(document.querySelectorAll('[data-s]')),groups=[].slice.call(document.querySelectorAll('section.group')),empty=document.querySelector('.empty'),chips=[].slice.call(document.querySelectorAll('.chip')),cat='';
function run(){
 var v=(q?q.value:'').trim().toLowerCase(),n=0;
 items.forEach(function(e){var ok=(!v||e.dataset.s.indexOf(v)>-1)&&(!cat||e.dataset.k===cat);e.style.display=ok?'':'none';if(ok)n++});
 groups.forEach(function(g){var any=[].some.call(g.querySelectorAll('[data-s]'),function(e){return e.style.display!=='none'});g.style.display=any?'':'none';var c=g.querySelector('.count');if(c){var m=[].filter.call(g.querySelectorAll('[data-s]'),function(e){return e.style.display!=='none'}).length;c.textContent=m+' টি'}});
 if(empty)empty.style.display=n?'none':'block';
}
if(q)q.addEventListener('input',run);
chips.forEach(function(c){c.onclick=function(){
 var g=c.dataset.go;
 if(g){var el=document.getElementById(g);if(el)el.scrollIntoView();return}
 cat=c.dataset.cat||'';chips.forEach(function(x){x.classList.toggle('on',x===c)});run()}});
document.addEventListener('keydown',function(e){if(e.key==='/'&&q&&document.activeElement!==q){e.preventDefault();q.focus()}});
})();
