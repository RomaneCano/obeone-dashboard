const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
// fond : réseau léger, un nœud détaché
(()=>{const c=$('#bg'),x=c.getContext('2d');let W,H,P=[],m={x:-999,y:-999},a=0,on=true;
const rs=()=>{W=c.width=innerWidth;H=c.height=innerHeight;P=Array.from({length:Math.min(45,W*H/32000|0)},()=>({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3}))};
addEventListener('resize',rs);addEventListener('mousemove',e=>{m.x=e.clientX;m.y=e.clientY});document.addEventListener('visibilitychange',()=>{on=!document.hidden;if(on)t()});rs();
function t(){if(!on)return;x.clearRect(0,0,W,H);
P.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;const dx=p.x-m.x,dy=p.y-m.y,d=Math.hypot(dx,dy);if(d<110&&d>0){p.x+=dx/d;p.y+=dy/d}});
x.lineWidth=1;for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const d=Math.hypot(P[i].x-P[j].x,P[i].y-P[j].y);if(d<130){x.strokeStyle=`rgba(45,212,191,${.15*(1-d/130)})`;x.beginPath();x.moveTo(P[i].x,P[i].y);x.lineTo(P[j].x,P[j].y);x.stroke()}}
x.fillStyle='rgba(56,189,248,.5)';P.forEach(p=>{x.beginPath();x.arc(p.x,p.y,2,0,7);x.fill()});
a+=.02;x.setLineDash([4,4]);x.strokeStyle='rgba(251,113,133,.8)';x.beginPath();x.arc(W*.9+Math.cos(a)*12,H*.18+Math.sin(a*1.3)*9,9,0,7);x.stroke();x.setLineDash([]);
if(!reduce)requestAnimationFrame(t)}t()})();
// animations rejouées à chaque ouverture d'onglet
const cnt=el=>{const to=+el.dataset.n,s=el.dataset.s||'',t0=performance.now();if(reduce){el.textContent=to.toLocaleString('fr-FR')+s;return}(function f(t){const k=Math.min(1,(t-t0)/1100);el.textContent=Math.round(to*(1-Math.pow(1-k,3))).toLocaleString('fr-FR')+s;if(k<1)requestAnimationFrame(f)})(t0)};
function play(root){$$('[data-n]',root).forEach(cnt);
$$('.arc,.rg',root).forEach(a=>{a.style.transition='none';a.setAttribute('stroke-dasharray','0 999')});
$$('[data-w]',root).forEach(b=>{b.style.transition='none';b.style.width='0'});
requestAnimationFrame(()=>requestAnimationFrame(()=>{$$('.arc,.rg',root).forEach(a=>{a.style.transition='';a.setAttribute('stroke-dasharray',a.dataset.d)});$$('[data-w]',root).forEach(b=>{b.style.transition='';b.style.width=b.dataset.w+'%'})}))}
// onglets
const tabs=$$('.tabs button'),panels=$$('.panel');
function show(id,push){const p=$('#p-'+id)||panels[0];id=p.id.slice(2);tabs.forEach(b=>b.classList.toggle('on',b.dataset.t===id));panels.forEach(q=>q.classList.toggle('on',q===p));scrollTo({top:0});if(push)history.replaceState(null,'','#'+id);play(p);if(id==='resume')story()}
tabs.forEach(b=>b.onclick=()=>show(b.dataset.t,1));
// sous-onglets (tâches)
$$('.sub button').forEach(b=>b.onclick=()=>{const g=b.parentElement;$$('button',g).forEach(x=>x.classList.toggle('on',x===b));$$('.subp').forEach(p=>p.classList.toggle('on',p.id==='s-'+b.dataset.s))});
// résumé animé : machine à écrire + rotation des constats
let tw=0,rot=0;
function story(){const el=$('#type');if(!el)return;clearTimeout(tw);const lines=JSON.parse(el.dataset.l);let i=0,j=0,del=false;
(function k(){const s=lines[i];if(reduce){el.textContent=s;return}
el.textContent=s.slice(0,j);if(!del&&j<s.length){j++;tw=setTimeout(k,28)}else if(!del){del=true;tw=setTimeout(k,2200)}else if(j>0){j-=2;if(j<0)j=0;tw=setTimeout(k,10)}else{del=false;i=(i+1)%lines.length;tw=setTimeout(k,250)}})();
const its=$$('.find .it'),ds=$$('.dots i');clearInterval(rot);let n=0;const go=()=>{its.forEach((q,z)=>q.classList.toggle('on',z===n));ds.forEach((q,z)=>q.classList.toggle('on',z===n));n=(n+1)%its.length};go();if(!reduce)rot=setInterval(go,4200)}
// cases à cocher (cet appareil)
$$('.task input').forEach(c=>{let v=0;try{v=localStorage.getItem('ob_'+c.dataset.k)}catch(e){}if(v==='1'){c.checked=true;c.closest('.task').classList.add('done')}
c.onchange=()=>{c.closest('.task').classList.toggle('done',c.checked);try{localStorage.setItem('ob_'+c.dataset.k,c.checked?'1':'0')}catch(e){}}});
// tableau : filtre + recherche
const rows=$$('#t tbody tr'),f=$('#f'),q=$('#q');let cur='Tous';
const ap=()=>{const s=q.value.toLowerCase();rows.forEach(r=>r.style.display=((cur==='Tous'||r.dataset.m===cur)&&r.textContent.toLowerCase().includes(s))?'':'none')};
['Tous',...new Set(rows.map(r=>r.dataset.m))].forEach((m,i)=>{const b=document.createElement('button');b.textContent=m;if(!i)b.className='on';b.onclick=()=>{$$('button',f).forEach(x=>x.className='');b.className='on';cur=m;ap()};f.insertBefore(b,q)});q.oninput=ap;
// tilt léger
$$('.tilt').forEach(c=>{c.addEventListener('mousemove',e=>{const r=c.getBoundingClientRect(),px=(e.clientX-r.left)/r.width-.5,py=(e.clientY-r.top)/r.height-.5;c.style.transform=`perspective(700px) rotateY(${px*6}deg) rotateX(${-py*6}deg)`});c.addEventListener('mouseleave',()=>c.style.transform='')});
show(location.hash.slice(1)||'resume');
