#!/usr/bin/env python3
"""Reconstruit docs/index.html à partir des CSV de data/. Aucune dépendance externe."""
import csv, html, datetime, collections, pathlib
R = pathlib.Path(__file__).parent
def rd(n): return list(csv.DictReader(open(R/'data'/n, encoding='utf-8')))
src, conf, beone = rd('sources.csv'), rd('conformite.csv'), {r['indicateur']: r for r in rd('beone.csv')}
e = html.escape
def bars(counter, color):
    m = max(counter.values()) if counter else 1
    return ''.join(f'<div class="bar"><span>{e(k)}</span><div><i style="width:{v/m*100:.0f}%;background:{color}"></i></div><b>{v}</b></div>' for k, v in counter.most_common())
n = len(src)
lus = sum(r['lecture'] == 'lu' for r in src)
part = sum(r['lecture'] == 'partiel' for r in src)
proj = sum(r['publication_projet'] == 'oui' for r in src)
ouverts = sum(r['statut'] in ('Absent', 'Ouvert') for r in conf)
th = collections.Counter(r['theme'] for r in src)
mb = collections.Counter(r['referent'] for r in src)
lc = collections.Counter(r['lecture'] for r in src)
chip = {'Présent': 'ok', 'Partiel': 'warn', 'Existe, non lu': 'warn', 'Absent': 'ko', 'Ouvert': 'ko', 'Constat': 'info'}
def lec(x): return 'ok' if x == 'lu' else 'warn' if x == 'partiel' else 'ko'
rows_s = ''.join(f'<tr data-m="{e(r["referent"])}"><td>{e(r["titre"])}</td><td>{e(r["auteurs"])}</td><td>{e(r["annee"])}</td><td>{e(r["type"])}</td><td>{e(r["theme"])}</td><td>{"●" if r["publication_projet"]=="oui" else ""}</td><td><span class="chip {lec(r["lecture"])}">{e(r["lecture"])}</span></td><td>{e(r["referent"])}</td></tr>' for r in src)
rows_c = ''.join(f'<tr><td>{e(r["controle"])}</td><td><span class="chip {chip.get(r["statut"],"info")}">{e(r["statut"])}</span></td><td>{e(r["constat"])}</td><td>{e(r["source"])}</td><td>{e(r["referent"])}</td></tr>' for r in conf)
iso = int(beone['isolats']['valeur']); sl = int(beone['seuil_listeria']['valeur']); ss = int(beone['seuil_salmonella']['valeur'])
logo = (R/'docs'/'logo.svg').read_text(encoding='utf-8')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%d/%m/%Y à %H:%M UTC')
css = """:root{--bg:#0b1220;--card:#111a2e;--line:#1e2a44;--tx:#e2e8f0;--mut:#94a3b8;--teal:#2dd4bf;--sky:#38bdf8;--rose:#fb7185;--amb:#fbbf24}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.5 Inter,Segoe UI,Helvetica,Arial,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px}header svg{width:100%;max-width:560px;height:auto;display:block}
h2{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--mut);margin:36px 0 12px}
.grid{display:grid;gap:14px}.k{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}.two{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px}
.kpi b{display:block;font-size:34px;line-height:1.1}.kpi span{color:var(--mut);font-size:13px}
.bar{display:grid;grid-template-columns:130px 1fr 28px;gap:10px;align-items:center;margin:7px 0;font-size:13px}.bar div{background:#0d1526;border-radius:99px;height:9px;overflow:hidden}.bar i{display:block;height:100%;border-radius:99px}.bar b{text-align:right}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--mut);font-weight:600}
.chip{padding:2px 9px;border-radius:99px;font-size:12px;white-space:nowrap}.ok{background:#0f3d38;color:var(--teal)}.warn{background:#473a10;color:var(--amb)}.ko{background:#4a1c27;color:var(--rose)}.info{background:#10304a;color:var(--sky)}
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 10px}.filters button{background:#0d1526;color:var(--tx);border:1px solid var(--line);border-radius:99px;padding:5px 12px;cursor:pointer}.filters button.on{border-color:var(--teal);color:var(--teal)}
.scale{position:relative;height:12px;background:#0d1526;border-radius:99px;margin:30px 0 10px}.scale i{position:absolute;top:-5px;width:4px;height:22px;border-radius:2px}.scale em{position:absolute;top:-26px;font-size:12px;font-style:normal;transform:translateX(-50%);white-space:nowrap}
footer{color:var(--mut);font-size:12px;margin:36px 0 8px}.tw{overflow-x:auto}"""
js = """const rows=[...document.querySelectorAll('#t tbody tr')],f=document.getElementById('f');
const ms=['Tous',...new Set(rows.map(r=>r.dataset.m))];
ms.forEach((m,i)=>{const b=document.createElement('button');b.textContent=m;if(!i)b.className='on';b.onclick=()=>{[...f.children].forEach(x=>x.className='');b.className='on';rows.forEach(r=>r.style.display=(!i||r.dataset.m===m)?'':'none')};f.appendChild(b)});"""
page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>O.BeOne != CannotBe, dashboard</title><style>{css}</style></head><body><main>
<header>{logo}</header>
<h2>Vue d'ensemble</h2>
<div class="grid k">
<div class="card kpi"><b>{n}</b><span>sources dans Zotero</span></div>
<div class="card kpi"><b>{proj}</b><span>sources issues du projet</span></div>
<div class="card kpi"><b>{lus}</b><span>sources lues en entier ({part} en partie)</span></div>
<div class="card kpi"><b style="color:var(--rose)">{ouverts}</b><span>points de conformité ouverts</span></div>
<div class="card kpi"><b>{iso:,}</b><span>isolats BeONE publiés</span></div></div>
<h2>Bibliothèque Zotero</h2>
<div class="grid two">
<div class="card"><strong>Par thème</strong>{bars(th,'var(--teal)')}</div>
<div class="card"><strong>Par référent</strong>{bars(mb,'var(--sky)')}</div>
<div class="card"><strong>Statut de lecture</strong>{bars(lc,'var(--amb)')}</div></div>
<div class="card" style="margin-top:14px"><div class="filters" id="f"></div><div class="tw"><table id="t"><thead><tr><th>Titre</th><th>Auteurs</th><th>Année</th><th>Type</th><th>Thème</th><th>Projet</th><th>Lecture</th><th>Référent</th></tr></thead><tbody>{rows_s}</tbody></table></div></div>
<h2>Données BeONE publiques</h2>
<div class="card"><strong>Seuils de différences alléliques pour regrouper deux isolats</strong>
<div class="scale"><i style="left:{sl/20*100}%;background:var(--teal)"></i><em style="left:{sl/20*100}%">Listeria : {sl}</em><i style="left:{ss/20*100}%;background:var(--sky)"></i><em style="left:{ss/20*100}%">Salmonella : {ss}</em></div>
<small style="color:var(--mut)">Score de congruence de 0 à {beone['score_congruence_max']['valeur']}. {beone['bioprojects_ena']['valeur']} BioProjects ENA ({e(beone['bioprojects_ena']['source'])}). Licence {e(beone['licence_donnees']['valeur'])}.</small></div>
<h2>Conformité, éthique et architecture</h2>
<div class="card tw"><table><thead><tr><th>Contrôle</th><th>Statut</th><th>Constat</th><th>Source</th><th>Référent</th></tr></thead><tbody>{rows_c}</tbody></table></div>
<footer>Généré le {now} depuis data/*.csv. Chaque modification d'un CSV relance la génération.</footer>
</main><script>{js}</script></body></html>'''
(R/'docs'/'index.html').write_text(page, encoding='utf-8')
print('ok', n, 'sources')
