#!/usr/bin/env python3
"""Reconstruit docs/index.html à partir des CSV de data/. Aucune dépendance externe."""
import csv, html, datetime, collections, pathlib, json, math
R = pathlib.Path(__file__).parent
def rd(n): return list(csv.DictReader(open(R/'data'/n, encoding='utf-8')))
src, conf, beone = rd('sources.csv'), rd('conformite.csv'), {r['indicateur']: r for r in rd('beone.csv')}
e = html.escape

ROLES = {'Rémi': 'Architecte des données', 'Aziz': 'Data scientist', 'Alexis': 'Data steward et DPO',
         'Romane': 'Référente éthique', 'Lina': 'Coordinatrice scientifique'}
COL = {'Rémi': '#38bdf8', 'Aziz': '#2dd4bf', 'Alexis': '#fbbf24', 'Romane': '#fb7185', 'Lina': '#a78bfa'}
PAL = ['#2dd4bf', '#38bdf8', '#a78bfa', '#fbbf24', '#fb7185', '#34d399', '#f472b6', '#60a5fa', '#f59e0b', '#22d3ee', '#c084fc']

n = len(src)
lus = sum(r['lecture'] == 'lu' for r in src)
part = sum(r['lecture'] == 'partiel' for r in src)
nonlu = sum(r['lecture'] == 'non lu' for r in src)
nonex = sum(r['lecture'] == 'non examiné' for r in src)
proj = sum(r['publication_projet'] == 'oui' for r in src)
ouverts = sum(r['statut'] in ('Absent', 'Ouvert') for r in conf)
ok_conf = sum(r['statut'] == 'Présent' for r in conf)
th = collections.Counter(r['theme'] for r in src)
lc = collections.Counter(r['lecture'] for r in src)
iso = int(beone['isolats']['valeur']); sl = int(beone['seuil_listeria']['valeur']); ss = int(beone['seuil_salmonella']['valeur'])
cmax = int(beone['score_congruence_max']['valeur'])
lecture_pct = round((lus + 0.5 * part) / n * 100)

def donut(counter):
    tot = sum(counter.values()); C = 2 * math.pi * 70; off = 0; arcs = ''; leg = ''
    for i, (k, v) in enumerate(counter.most_common()):
        L = v / tot * C; c = PAL[i % len(PAL)]
        arcs += f'<circle class="arc" r="70" cx="100" cy="100" stroke="{c}" stroke-dasharray="0 {C:.1f}" data-d="{max(L-2,0.5):.1f} {C:.1f}" stroke-dashoffset="{-off:.1f}"><title>{e(k)} : {v}</title></circle>'
        leg += f'<li><i style="background:{c}"></i>{e(k)}<b>{v}</b></li>'
        off += L
    return f'<div class="donutw"><svg viewBox="0 0 200 200" class="donut"><circle r="70" cx="100" cy="100" fill="none" stroke="#0d1526" stroke-width="26"/>{arcs}<text x="100" y="98" text-anchor="middle" class="dn" data-n="{tot}">0</text><text x="100" y="118" text-anchor="middle" class="dl">sources</text></svg><ul class="leg">{leg}</ul></div>'

def ring(pct, color, label, sub):
    C = 2 * math.pi * 42
    return f'<div class="ringw"><svg viewBox="0 0 100 100"><circle r="42" cx="50" cy="50" fill="none" stroke="#0d1526" stroke-width="9"/><circle class="rg" r="42" cx="50" cy="50" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" stroke-dasharray="0 {C:.1f}" data-d="{pct/100*C:.1f} {C:.1f}" transform="rotate(-90 50 50)"/><text x="50" y="56" text-anchor="middle" class="rn" data-n="{pct}" data-s="%">0%</text></svg><div><b>{label}</b><span>{sub}</span></div></div>'

# cartes membres
members = ''
for m in ROLES:
    s = [r for r in src if r['referent'] == m]; c = [r for r in conf if r['referent'] == m]
    lu = sum(r['lecture'] == 'lu' for r in s); pa = sum(r['lecture'] == 'partiel' for r in s)
    themes = ''.join(f'<span>{e(t)}</span>' for t, _ in collections.Counter(r['theme'] for r in s).most_common(3))
    pct = round((lu + 0.5 * pa) / len(s) * 100) if s else 0
    members += (f'<div class="card mem tilt" style="--c:{COL[m]}"><div class="av">{m[0]}</div><h3>{m}</h3><em>{ROLES[m]}</em>'
                f'<div class="mnum"><div><b data-n="{len(s)}">0</b><small>sources</small></div><div><b data-n="{len(c)}">0</b><small>contrôles</small></div><div><b data-n="{pct}" data-s="%">0%</b><small>lu</small></div></div>'
                f'<div class="mbar"><i data-w="{pct}"></i></div><div class="tags">{themes}</div></div>')

chip = {'Présent': 'ok', 'Partiel': 'warn', 'Existe, non lu': 'warn', 'Absent': 'ko', 'Ouvert': 'ko', 'Constat': 'info'}
icon = {'ok': '✓', 'warn': '!', 'ko': '✕', 'info': 'i'}
cc = ''
for r in conf:
    k = chip.get(r['statut'], 'info')
    cc += (f'<div class="card cf {k} tilt"><div class="ci">{icon[k]}</div><div><h4>{e(r["controle"])}</h4>'
           f'<span class="chip {k}">{e(r["statut"])}</span><p>{e(r["constat"])}</p><small>{e(r["source"])} · {e(r["referent"])}</small></div></div>')

def lec(x): return 'ok' if x == 'lu' else 'warn' if x == 'partiel' else 'ko'
rows_s = ''.join(f'<tr data-m="{e(r["referent"])}"><td>{e(r["titre"])}</td><td>{e(r["auteurs"])}</td><td>{e(r["annee"])}</td><td>{e(r["type"])}</td><td>{e(r["theme"])}</td><td>{"●" if r["publication_projet"]=="oui" else ""}</td><td><span class="chip {lec(r["lecture"])}">{e(r["lecture"])}</span></td><td><span class="dot" style="background:{COL.get(r["referent"],"#888")}"></span>{e(r["referent"])}</td></tr>' for r in src)

logo = (R/'docs'/'logo.svg').read_text(encoding='utf-8')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%d/%m/%Y à %H:%M UTC')

css = """:root{--bg:#070d1a;--card:#0f1830cc;--line:#1e2a44;--tx:#e2e8f0;--mut:#94a3b8;--teal:#2dd4bf;--sky:#38bdf8;--rose:#fb7185;--amb:#fbbf24}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.55 Inter,Segoe UI,Helvetica,Arial,sans-serif;overflow-x:hidden}
#bg{position:fixed;inset:0;z-index:0;pointer-events:none}main,nav{position:relative;z-index:1}
nav{position:sticky;top:0;z-index:5;display:flex;gap:6px;justify-content:center;flex-wrap:wrap;padding:10px;background:#070d1acc;backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
nav a{color:var(--mut);text-decoration:none;font-size:13px;padding:6px 14px;border-radius:99px;transition:.25s}nav a:hover,nav a.on{color:var(--teal);background:#0f2a30}
main{max-width:1180px;margin:0 auto;padding:10px 24px 40px}
.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:20px;align-items:center;padding:36px 0 8px}
.hero svg.lg{width:100%;max-width:560px;height:auto;filter:drop-shadow(0 12px 40px #2dd4bf33);animation:float 6s ease-in-out infinite}
.hero p{color:var(--mut);max-width:44ch}.hero h1{margin:0 0 8px;font-size:30px;line-height:1.2}
.live{display:inline-flex;align-items:center;gap:8px;font-size:12px;color:var(--teal);margin-bottom:10px}.live i{width:8px;height:8px;border-radius:50%;background:var(--teal);animation:pulse 1.6s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 #2dd4bf88}100%{box-shadow:0 0 0 12px #2dd4bf00}}@keyframes float{50%{transform:translateY(-8px)}}
h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);margin:54px 0 14px;display:flex;align-items:center;gap:12px}h2:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
.grid{display:grid;gap:14px}.k{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}.two{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}.five{grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px 18px;backdrop-filter:blur(6px);transition:transform .25s,border-color .25s,box-shadow .25s}
.card:hover{border-color:#2dd4bf66;box-shadow:0 10px 40px #2dd4bf14}
.kpi b{display:block;font-size:38px;line-height:1.1;background:linear-gradient(90deg,var(--teal),var(--sky));-webkit-background-clip:text;background-clip:text;color:transparent}.kpi.r b{background:linear-gradient(90deg,var(--rose),var(--amb));-webkit-background-clip:text;background-clip:text}.kpi span{color:var(--mut);font-size:13px}
.rv{opacity:0;transform:translateY(26px);transition:opacity .7s,transform .7s}.rv.in{opacity:1;transform:none}
.donutw{display:flex;gap:18px;align-items:center;flex-wrap:wrap}.donut{width:190px;flex:none}.arc{fill:none;stroke-width:26;transition:stroke-dasharray 1.4s cubic-bezier(.2,.8,.2,1);transform:rotate(-90deg);transform-origin:100px 100px}.arc:hover{stroke-width:31}
.dn{font:700 34px Inter,sans-serif;fill:#e2e8f0}.dl{font:12px Inter,sans-serif;fill:#94a3b8}
.leg{list-style:none;margin:0;padding:0;flex:1;min-width:150px;font-size:13px}.leg li{display:flex;align-items:center;gap:8px;padding:3px 0}.leg i{width:10px;height:10px;border-radius:3px}.leg b{margin-left:auto;color:var(--mut)}
.rings{display:grid;gap:16px}.ringw{display:flex;align-items:center;gap:14px}.ringw svg{width:92px;flex:none}.ringw b{display:block}.ringw span{color:var(--mut);font-size:13px}.rg{transition:stroke-dasharray 1.6s cubic-bezier(.2,.8,.2,1)}.rn{font:700 20px Inter,sans-serif;fill:#e2e8f0}
.lecbar{display:flex;height:16px;border-radius:99px;overflow:hidden;background:#0d1526;margin:14px 0 8px}.lecbar i{display:block;width:0;transition:width 1.4s cubic-bezier(.2,.8,.2,1)}.lleg{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--mut)}.lleg span:before{content:"";display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:6px;background:var(--c)}
.mem{text-align:center;position:relative;overflow:hidden}.mem:before{content:"";position:absolute;inset:0 0 auto 0;height:3px;background:var(--c)}.av{width:54px;height:54px;border-radius:50%;margin:4px auto 8px;display:grid;place-items:center;font:700 22px Inter,sans-serif;color:#07101c;background:var(--c);box-shadow:0 0 0 6px color-mix(in srgb,var(--c) 22%,transparent);animation:ping 3s infinite}
@keyframes ping{50%{box-shadow:0 0 0 12px color-mix(in srgb,var(--c) 6%,transparent)}}
.mem h3{margin:0}.mem em{color:var(--mut);font-size:12px;font-style:normal}.mnum{display:flex;justify-content:space-around;margin:14px 0 8px}.mnum b{display:block;font-size:22px;color:var(--c)}.mnum small{color:var(--mut);font-size:11px}
.mbar{height:6px;border-radius:9px;background:#0d1526;overflow:hidden;margin:6px 0 12px}.mbar i{display:block;height:100%;width:0;background:var(--c);transition:width 1.4s cubic-bezier(.2,.8,.2,1)}.tags{display:flex;gap:5px;flex-wrap:wrap;justify-content:center}.tags span{font-size:11px;padding:2px 8px;border-radius:99px;border:1px solid color-mix(in srgb,var(--c) 40%,transparent);color:var(--c)}
.flow{padding:20px 10px}.flow svg{width:100%;height:auto}.flow text{font:600 13px Inter,sans-serif;fill:#e2e8f0}.flow .s{font:11px Inter,sans-serif;fill:#94a3b8}
.dash{stroke-dasharray:6 6;animation:dash 1.2s linear infinite}@keyframes dash{to{stroke-dashoffset:-24}}
.scale{position:relative;height:14px;background:linear-gradient(90deg,#0f3d38,#10304a 50%,#0d1526);border-radius:99px;margin:44px 6px 34px}.scale i{position:absolute;top:-7px;width:5px;height:28px;border-radius:3px;animation:glow 2s infinite}.scale em{position:absolute;top:-32px;font-size:12px;font-style:normal;transform:translateX(-50%);white-space:nowrap}.scale u{position:absolute;top:24px;font-size:10px;color:var(--mut);text-decoration:none;transform:translateX(-50%)}
@keyframes glow{50%{filter:brightness(1.8)}}
.cfg{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}.cf{display:flex;gap:14px}.cf h4{margin:0 0 6px}.cf p{margin:8px 0 6px;font-size:13px;color:#cbd5e1}.cf small{color:var(--mut);font-size:11px}
.ci{width:38px;height:38px;border-radius:12px;flex:none;display:grid;place-items:center;font-weight:800}.cf.ok .ci{background:#0f3d38;color:var(--teal)}.cf.warn .ci{background:#473a10;color:var(--amb)}.cf.ko .ci{background:#4a1c27;color:var(--rose);animation:alert 1.8s infinite}.cf.info .ci{background:#10304a;color:var(--sky)}.cf.ko{border-color:#fb718544}
@keyframes alert{0%{box-shadow:0 0 0 0 #fb718588}100%{box-shadow:0 0 0 14px #fb718500}}
.chip{padding:2px 9px;border-radius:99px;font-size:12px;white-space:nowrap}.ok.chip{background:#0f3d38;color:var(--teal)}.warn.chip{background:#473a10;color:var(--amb)}.ko.chip{background:#4a1c27;color:var(--rose)}.info.chip{background:#10304a;color:var(--sky)}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600}tbody tr{transition:background .2s}tbody tr:hover{background:#13213d}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.tools{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 12px;align-items:center}.tools button{background:#0d1526;color:var(--tx);border:1px solid var(--line);border-radius:99px;padding:5px 13px;cursor:pointer;transition:.2s}.tools button:hover{border-color:var(--teal)}.tools button.on{border-color:var(--teal);color:var(--teal);background:#0f2a30}
.tools input{background:#0d1526;border:1px solid var(--line);color:var(--tx);border-radius:99px;padding:6px 14px;margin-left:auto;min-width:200px}.tw{overflow-x:auto}
footer{color:var(--mut);font-size:12px;margin:48px 0 8px;text-align:center}
@media(max-width:800px){.hero{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.rv{opacity:1;transform:none}}"""

js = r"""
// fond animé : réseau de nœuds, un nœud détaché (la personne non exposée)
(()=>{const c=document.getElementById('bg'),x=c.getContext('2d');let W,H,P=[],m={x:-999,y:-999};
const rs=()=>{W=c.width=innerWidth;H=c.height=innerHeight;P=Array.from({length:Math.min(70,W*H/20000|0)},()=>({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35}))};
addEventListener('resize',rs);addEventListener('mousemove',e=>{m.x=e.clientX;m.y=e.clientY});rs();
const rose={x:W*.86,y:H*.2,a:0};
(function t(){x.clearRect(0,0,W,H);
P.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;const dx=p.x-m.x,dy=p.y-m.y,d=Math.hypot(dx,dy);if(d<120){p.x+=dx/d*1.2;p.y+=dy/d*1.2}});
for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const d=Math.hypot(P[i].x-P[j].x,P[i].y-P[j].y);if(d<130){x.strokeStyle=`rgba(45,212,191,${.16*(1-d/130)})`;x.beginPath();x.moveTo(P[i].x,P[i].y);x.lineTo(P[j].x,P[j].y);x.stroke()}}
P.forEach(p=>{x.fillStyle='rgba(56,189,248,.55)';x.beginPath();x.arc(p.x,p.y,2.2,0,7);x.fill()});
rose.a+=.02;const rx=rose.x+Math.cos(rose.a)*14,ry=rose.y+Math.sin(rose.a*1.3)*10;
x.setLineDash([4,4]);x.strokeStyle='rgba(251,113,133,.8)';x.lineWidth=1.4;x.beginPath();x.arc(rx,ry,9,0,7);x.stroke();x.setLineDash([]);x.lineWidth=1;
if(!matchMedia('(prefers-reduced-motion:reduce)').matches)requestAnimationFrame(t)})()})();
// compteurs, anneaux, barres : déclenchés à l'apparition
const cnt=el=>{const to=+el.dataset.n,s=el.dataset.s||'',t0=performance.now();(function f(t){const k=Math.min(1,(t-t0)/1300),v=Math.round(to*(1-Math.pow(1-k,3)));el.textContent=v.toLocaleString('fr-FR')+s;if(k<1)requestAnimationFrame(f)})(t0)};
const io=new IntersectionObserver(es=>es.forEach(en=>{if(!en.isIntersecting)return;const o=en.target;o.classList.add('in');
o.querySelectorAll('[data-n]').forEach(cnt);o.querySelectorAll('.arc,.rg').forEach(a=>a.setAttribute('stroke-dasharray',a.dataset.d));
o.querySelectorAll('[data-w]').forEach(b=>b.style.width=b.dataset.w+'%');o.querySelectorAll('.lecbar i').forEach(b=>b.style.width=b.dataset.w+'%');io.unobserve(o)}),{threshold:.2});
document.querySelectorAll('.rv').forEach(o=>io.observe(o));
// inclinaison 3D au survol
document.querySelectorAll('.tilt').forEach(c=>{c.addEventListener('mousemove',e=>{const r=c.getBoundingClientRect(),px=(e.clientX-r.left)/r.width-.5,py=(e.clientY-r.top)/r.height-.5;c.style.transform=`perspective(700px) rotateY(${px*8}deg) rotateX(${-py*8}deg) translateY(-3px)`});c.addEventListener('mouseleave',()=>c.style.transform='')});
// menu actif
const links=[...document.querySelectorAll('nav a')],secs=links.map(a=>document.querySelector(a.hash));
addEventListener('scroll',()=>{let k=0;secs.forEach((s,i)=>{if(s.getBoundingClientRect().top<160)k=i});links.forEach((a,i)=>a.classList.toggle('on',i===k))});
// filtre + recherche
const rows=[...document.querySelectorAll('#t tbody tr')],f=document.getElementById('f'),q=document.getElementById('q');let cur='Tous';
const ap=()=>{const s=q.value.toLowerCase();rows.forEach(r=>r.style.display=((cur==='Tous'||r.dataset.m===cur)&&r.textContent.toLowerCase().includes(s))?'':'none')};
['Tous',...new Set(rows.map(r=>r.dataset.m))].forEach((m,i)=>{const b=document.createElement('button');b.textContent=m;if(!i)b.className='on';b.onclick=()=>{[...f.querySelectorAll('button')].forEach(x=>x.className='');b.className='on';cur=m;ap()};f.insertBefore(b,q)});
q.oninput=ap;
"""

lecbar = ''.join(f'<i data-w="{v/n*100:.1f}" style="background:{c}"></i>' for v, c in [(lus, '#2dd4bf'), (part, '#fbbf24'), (nonlu, '#fb7185'), (nonex, '#64748b')])
lleg = ''.join(f'<span style="--c:{c}">{l} : {v}</span>' for l, v, c in [('lu', lus, '#2dd4bf'), ('partiel', part, '#fbbf24'), ('non lu', nonlu, '#fb7185'), ('non examiné', nonex, '#64748b')])

page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>O.BeOne != CannotBe, dashboard</title><style>{css}</style></head><body><canvas id="bg"></canvas>
<nav><a href="#top">Vue d'ensemble</a><a href="#equipe">Équipe</a><a href="#biblio">Bibliothèque</a><a href="#fil">Fil rouge</a><a href="#beone">BeONE</a><a href="#conf">Conformité</a></nav>
<main id="top">
<section class="hero"><div><div class="live"><i></i>Mis à jour le {now}</div><h1>Relier un cas humain à un aliment, sans exposer personne</h1><p>Suivi de notre analyse critique du projet BeONE : sources, données publiques, conformité RGPD et éthique, avec l'expertise de chaque membre de l'équipe 2.</p></div>
<div>{logo.replace('<svg ','<svg class="lg" ',1)}</div></section>
<div class="grid k rv">
<div class="card kpi tilt"><b data-n="{n}">0</b><span>sources dans Zotero</span></div>
<div class="card kpi tilt"><b data-n="{proj}">0</b><span>sources issues du projet</span></div>
<div class="card kpi tilt"><b data-n="{lus}">0</b><span>lues en entier, {part} en partie</span></div>
<div class="card kpi r tilt"><b data-n="{ouverts}">0</b><span>points de conformité ouverts</span></div>
<div class="card kpi tilt"><b data-n="{iso}">0</b><span>isolats BeONE publiés</span></div></div>

<h2 id="equipe">L'équipe et ses expertises</h2>
<div class="grid five rv">{members}</div>

<h2 id="biblio">Bibliothèque Zotero</h2>
<div class="grid two rv">
<div class="card"><strong>Répartition par thème</strong><br><br>{donut(th)}</div>
<div class="card"><strong>Avancement de la lecture</strong><div class="rings"><br>{ring(lecture_pct, '#2dd4bf', 'Lecture', 'les lectures partielles comptent pour moitié')}{ring(round(proj/n*100), '#38bdf8', 'Sources du projet', f'{proj} sur {n} viennent de BeONE')}</div>
<div class="lecbar">{lecbar}</div><div class="lleg">{lleg}</div></div></div>
<div class="card rv" style="margin-top:14px"><div class="tools" id="f"><input id="q" placeholder="Rechercher une source…"></div><div class="tw"><table id="t"><thead><tr><th>Titre</th><th>Auteurs</th><th>Année</th><th>Type</th><th>Thème</th><th>Projet</th><th>Lecture</th><th>Référent</th></tr></thead><tbody>{rows_s}</tbody></table></div></div>

<h2 id="fil">Le fil rouge : du patient à l'aliment</h2>
<div class="card flow rv"><svg viewBox="0 0 900 230">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#fb7185"/><stop offset="1" stop-color="#2dd4bf"/></linearGradient></defs>
<path class="dash" d="M120 100 H290 M410 100 H520 M640 100 H770" stroke="url(#g)" stroke-width="3" fill="none"/>
<g><circle cx="80" cy="100" r="40" fill="#1b2744" stroke="#fb7185" stroke-width="2"/><text x="80" y="105" text-anchor="middle">Cas humain</text><text class="s" x="80" y="165" text-anchor="middle">identité exclue</text></g>
<g><rect x="290" y="65" width="120" height="70" rx="16" fill="#1b2744" stroke="#38bdf8" stroke-width="2"/><text x="350" y="96" text-anchor="middle">Isolat</text><text class="s" x="350" y="116" text-anchor="middle">lectures masquées</text></g>
<g><rect x="520" y="65" width="120" height="70" rx="16" fill="#1b2744" stroke="#2dd4bf" stroke-width="2"/><text x="580" y="96" text-anchor="middle">Cluster</text><text class="s" x="580" y="116" text-anchor="middle">seuil allélique</text></g>
<g><circle cx="820" cy="100" r="40" fill="#1b2744" stroke="#fbbf24" stroke-width="2"/><text x="820" y="95" text-anchor="middle">Aliment</text><text x="820" y="113" text-anchor="middle">élevage</text><text class="s" x="820" y="165" text-anchor="middle">exploitant non exposé</text></g>
<circle r="6" fill="#2dd4bf"><animateMotion dur="4s" repeatCount="indefinite" path="M80 100 H820"/></circle>
<circle r="6" fill="#38bdf8"><animateMotion dur="4s" begin="1.3s" repeatCount="indefinite" path="M80 100 H820"/></circle>
<circle r="6" fill="#a78bfa"><animateMotion dur="4s" begin="2.6s" repeatCount="indefinite" path="M80 100 H820"/></circle>
<text class="s" x="450" y="205" text-anchor="middle">Schéma de lecture de notre question de recherche. Les points qui circulent représentent les données, pas des chiffres mesurés.</text></svg></div>

<h2 id="beone">Données BeONE publiques</h2>
<div class="grid two rv"><div class="card"><strong>Seuils de différences alléliques pour regrouper deux isolats</strong>
<div class="scale"><i style="left:{sl/20*100}%;background:var(--teal)"></i><em style="left:{sl/20*100}%">Listeria : {sl}</em><i style="left:{ss/20*100}%;background:var(--sky)"></i><em style="left:{ss/20*100}%">Salmonella : {ss}</em><u style="left:0">0</u><u style="left:100%">20</u></div>
<small style="color:var(--mut)">Score de congruence de 0 à {cmax}. Licence {e(beone['licence_donnees']['valeur'])}.</small></div>
<div class="card"><strong>Dépôts publics ENA</strong><div class="tags" style="justify-content:flex-start;margin-top:12px;--c:#38bdf8">{''.join(f'<span>{e(b.strip())}</span>' for b in beone['bioprojects_ena']['source'].replace(';', ',').split(',') if b.strip().startswith('PRJ')) or f'<span>{beone["bioprojects_ena"]["valeur"]} BioProjects</span>'}</div><br><b style="font-size:30px" data-n="{iso}">0</b> <span style="color:var(--mut)">isolats</span></div></div>

<h2 id="conf">Conformité, éthique et architecture</h2>
<div class="grid" style="margin-bottom:14px"><div class="card rv" style="display:flex;gap:26px;flex-wrap:wrap"><div><b style="font-size:28px;color:var(--teal)" data-n="{ok_conf}">0</b> <span style="color:var(--mut)">conformes</span></div><div><b style="font-size:28px;color:var(--rose)" data-n="{ouverts}">0</b> <span style="color:var(--mut)">absents ou ouverts</span></div><div><b style="font-size:28px" data-n="{len(conf)}">0</b> <span style="color:var(--mut)">contrôles suivis</span></div></div></div>
<div class="cfg rv">{cc}</div>
<footer>Généré le {now} depuis data/*.csv. Chaque modification d'un CSV relance la génération.</footer>
</main><script>{js}</script></body></html>'''
(R/'docs'/'index.html').write_text(page, encoding='utf-8')
print('ok', n, 'sources')
