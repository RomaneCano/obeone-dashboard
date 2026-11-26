#!/usr/bin/env python3
"""Reconstruit docs/index.html à partir de data/*.csv, static/style.css et static/app.js. Aucune dépendance externe."""
import csv, html, datetime, collections, pathlib, math, json, re
R = pathlib.Path(__file__).parent
def rd(n): return list(csv.DictReader(open(R/'data'/n, encoding='utf-8')))
src, conf, plan, extra, liens = rd('sources.csv'), rd('conformite.csv'), rd('plan.csv'), rd('taches.csv'), rd('liens.csv')
beone = {r['indicateur']: r for r in rd('beone.csv')}
e = html.escape

ROLES = {'Rémi': 'Architecte des données', 'Aziz': 'Data scientist', 'Alexis': 'Data steward et DPO',
         'Romane': 'Référente éthique', 'Lina': 'Coordinatrice scientifique'}
COL = {'Rémi': '#38bdf8', 'Aziz': '#2dd4bf', 'Alexis': '#fbbf24', 'Romane': '#fb7185', 'Lina': '#a78bfa'}
PAL = ['#2dd4bf', '#38bdf8', '#a78bfa', '#fbbf24', '#fb7185', '#34d399', '#f472b6', '#60a5fa', '#f59e0b', '#22d3ee', '#c084fc']
TEAM = ('Tous', 'Chacun', 'Chaque responsable')

# ---------- chiffres calculés ----------
n = len(src)
proj = sum(r['publication_projet'] == 'oui' for r in src)
ouverts = sum(r['statut'] in ('Absent', 'Ouvert') for r in conf)
th = collections.Counter(r['theme'] for r in src)
iso = int(beone['isolats']['valeur']); sl = int(beone['seuil_listeria']['valeur']); ss = int(beone['seuil_salmonella']['valeur'])
cmax = int(beone['score_congruence_max']['valeur'])
na = len(plan); fait = sum(r['statut'] == 'Fait' for r in plan); cours = sum(r['statut'] == 'En cours' for r in plan); afaire = sum(r['statut'] == 'À faire' for r in plan); prep = sum(r['statut'] == 'Préparé' for r in plan)
pct = round(fait / na * 100)

def who(qui):
    return [m for m in ROLES if re.search(m, qui)]

def donut(counter):
    tot = sum(counter.values()); C = 2 * math.pi * 70; off = 0; arcs = ''; leg = ''
    for i, (k, v) in enumerate(counter.most_common()):
        L = v / tot * C; c = PAL[i % len(PAL)]
        arcs += f'<circle class="arc" r="70" cx="100" cy="100" stroke="{c}" stroke-dasharray="0 999" data-d="{max(L-2,0.5):.1f} {C:.1f}" stroke-dashoffset="{-off:.1f}"><title>{e(k)} : {v}</title></circle>'
        leg += f'<li><i style="background:{c}"></i>{e(k)}<b>{v}</b></li>'
        off += L
    return f'<div class="donutw"><svg viewBox="0 0 200 200" class="donut"><circle r="70" cx="100" cy="100" fill="none" stroke="#0d1526" stroke-width="26"/>{arcs}<text x="100" y="98" text-anchor="middle" class="dn" data-n="{tot}">0</text><text x="100" y="118" text-anchor="middle" class="dl">sources</text></svg><ul class="leg">{leg}</ul></div>'

def ring(p, color, label, sub):
    C = 2 * math.pi * 42
    return f'<div class="ringw"><svg viewBox="0 0 100 100"><circle r="42" cx="50" cy="50" fill="none" stroke="#0d1526" stroke-width="9"/><circle class="rg" r="42" cx="50" cy="50" fill="none" stroke="{color}" stroke-width="9" stroke-linecap="round" stroke-dasharray="0 999" data-d="{p/100*C:.1f} {C:.1f}" transform="rotate(-90 50 50)"/><text x="50" y="56" text-anchor="middle" class="rn" data-n="{p}" data-s="%">0%</text></svg><div><b>{label}</b><span>{sub}</span></div></div>'

# ---------- RÉSUMÉ ----------
seances = list(dict.fromkeys(r['seance'] for r in plan))
tl = ''
for s in seances:
    rs = [r for r in plan if r['seance'] == s]; t = len(rs)
    f_, p_, c_, a_ = (sum(r['statut'] == k for r in rs) for k in ('Fait', 'Préparé', 'En cours', 'À faire'))
    tl += (f'<div class="tr"><span>{e(s)}</span><div class="bb"><i class="f" data-w="{f_/t*100:.1f}"></i><i class="p" data-w="{p_/t*100:.1f}"></i><i class="c" data-w="{c_/t*100:.1f}"></i><i class="t" data-w="{a_/t*100:.1f}"></i></div><b>{f_}/{t}</b></div>')
lines = [f'{na} actions planifiées sur 6 séances, la préparation et la soutenance.',
         f'{fait} actions faites, {prep} préparées (rédigées, acte humain restant), {cours} en cours, {afaire} à faire.',
         f'{n} sources réunies dans notre bibliothèque Zotero.',
         f'{ouverts} points de conformité restent ouverts dans BeONE.',
         'Notre question : relier un cas humain à un aliment sans exposer personne.']
finds = ''; dots = ''
for r in [r for r in conf if r['statut'] in ('Absent', 'Ouvert')]:
    finds += f'<div class="it"><h4>{e(r["controle"])} ({e(r["statut"].lower())})</h4><p>{e(r["constat"])}</p><small style="color:var(--mut)">{e(r["source"])}</small></div>'
    dots += '<i></i>'
resume = f'''<div class="story"><div class="card"><div class="type" id="type" data-l='{json.dumps(lines, ensure_ascii=False)}'></div></div>
<div class="card"><strong>Ce que notre analyse a relevé</strong><div class="find" style="margin-top:12px">{finds}</div><div class="dots">{dots}</div></div></div>
<div class="grid k" style="margin-top:14px">
<div class="card kpi tilt"><b data-n="{pct}" data-s="%">0%</b><span>du plan réalisé ({fait} actions sur {na})</span></div>
<div class="card kpi tilt"><b data-n="{n}">0</b><span>sources dans Zotero ({proj} issues du projet)</span></div>
<div class="card kpi tilt"><b data-n="{len(ROLES)}">0</b><span>membres, cinq expertises</span></div>
<div class="card kpi r tilt"><b data-n="{ouverts}">0</b><span>points de conformité ouverts</span></div>
<div class="card kpi tilt"><b data-n="{iso}">0</b><span>isolats BeONE publiés</span></div></div>
<div class="card" style="margin-top:14px"><strong>Avancement par séance</strong><div class="lleg" style="margin:6px 0 12px"><span style="--c:#10b981">fait</span><span style="--c:#38bdf8">préparé</span><span style="--c:#fbbf24">en cours</span><span style="--c:#475569">à faire</span></div><div class="tl">{tl}</div></div>'''

# ---------- ÉQUIPE ----------
members = ''
for m in ROLES:
    mine = [r for r in plan if m in who(r['qui'])]
    f_ = sum(r['statut'] == 'Fait' for r in mine); c_ = sum(r['statut'] == 'En cours' for r in mine); t = len(mine)
    p = round(f_ / t * 100) if t else 0
    done = ''.join(f'<li>{e(r["seance"])} : {e(r["production"])}</li>' for r in mine if r['statut'] == 'Fait')
    s = [r for r in src if r['referent'] == m]
    members += (f'<div class="card mem tilt" style="--c:{COL[m]}"><div class="av">{m[0]}</div><h3>{m}</h3><em>{ROLES[m]}</em>'
                f'<div class="mnum"><div><b data-n="{f_}">0</b><small>actions faites</small></div><div><b data-n="{c_}">0</b><small>en cours</small></div><div><b data-n="{len(s)}">0</b><small>sources suivies</small></div></div>'
                f'<div class="mbar"><i data-w="{p}"></i></div><ul class="done">{done}</ul></div>')
equipe = f'<p style="color:var(--mut);margin:6px 0 14px">Actions nominatives du plan (les actions « Tous » ne sont comptées pour personne). Sources suivies : répartition proposée, à valider.</p><div class="grid five">{members}</div>'

# ---------- BIBLIOTHÈQUE ----------
rows_s = ''.join(f'<tr data-m="{e(r["referent"])}"><td>{e(r["titre"])}</td><td>{e(r["auteurs"])}</td><td>{e(r["annee"])}</td><td>{e(r["type"])}</td><td>{e(r["theme"])}</td><td>{"●" if r["publication_projet"]=="oui" else ""}</td><td><span class="dot" style="background:{COL.get(r["referent"],"#888")}"></span>{e(r["referent"])}</td></tr>' for r in src)
biblio = f'''<div class="grid two"><div class="card"><strong>Répartition par thème</strong><br><br>{donut(th)}</div>
<div class="card"><strong>Origine des sources</strong><div style="margin-top:16px;display:grid;gap:16px">{ring(round(proj/n*100), '#38bdf8', 'Issues du projet', f'{proj} sur {n} publiées par BeONE')}{ring(round(len(th)/12*100), '#2dd4bf', 'Thèmes couverts', f'{len(th)} thèmes dans la bibliothèque')}</div></div></div>
<div class="card" style="margin-top:14px"><div class="tools" id="f"><input id="q" placeholder="Rechercher une source…"></div><div class="tw" style="max-height:48vh;overflow:auto"><table id="t"><thead><tr><th>Titre</th><th>Auteurs</th><th>Année</th><th>Type</th><th>Thème</th><th>Projet</th><th>Référent proposé</th></tr></thead><tbody>{rows_s}</tbody></table></div></div>'''

# ---------- BEONE ----------
enas = ''.join(f'<span>{e(b.strip())}</span>' for b in beone['bioprojects_ena']['source'].split(',') if b.strip().startswith('PRJ'))
beone_p = f'''<div class="card flow"><svg viewBox="0 0 900 200">
<path class="dash" d="M122 90 H290 M410 90 H520 M640 90 H778" stroke="#38bdf8" stroke-width="3" fill="none"/>
<g><circle cx="80" cy="90" r="42" fill="#16213b" stroke="#fb7185" stroke-width="2"/><text x="80" y="95" text-anchor="middle" style="font-size:12px">Cas humain</text><text class="s" x="80" y="156" text-anchor="middle">identité exclue</text></g>
<g><rect x="290" y="55" width="120" height="70" rx="16" fill="#16213b" stroke="#38bdf8" stroke-width="2"/><text x="350" y="86" text-anchor="middle">Isolat</text><text class="s" x="350" y="106" text-anchor="middle">lectures masquées</text></g>
<g><rect x="520" y="55" width="120" height="70" rx="16" fill="#16213b" stroke="#2dd4bf" stroke-width="2"/><text x="580" y="86" text-anchor="middle">Cluster</text><text class="s" x="580" y="106" text-anchor="middle">seuil allélique</text></g>
<g><circle cx="820" cy="90" r="42" fill="#16213b" stroke="#fbbf24" stroke-width="2"/><text x="820" y="86" text-anchor="middle" style="font-size:12px">Aliment</text><text x="820" y="102" text-anchor="middle" style="font-size:12px">élevage</text><text class="s" x="820" y="156" text-anchor="middle">exploitant non exposé</text></g>
<circle r="5" cy="90" fill="#2dd4bf"><animate attributeName="cx" values="125;775" dur="5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="5s" repeatCount="indefinite"/></circle>
<circle r="5" cy="90" fill="#a78bfa"><animate attributeName="cx" values="125;775" dur="5s" begin="2.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="5s" begin="2.5s" repeatCount="indefinite"/></circle>
<text class="s" x="450" y="190" text-anchor="middle">Schéma de lecture de notre question de recherche. Les points représentent les données qui circulent.</text></svg></div>
<div class="grid two" style="margin-top:14px"><div class="card"><strong>Seuils de différences alléliques pour regrouper deux isolats</strong>
<div class="scale"><i style="left:{sl/20*100}%;background:var(--teal)"></i><em style="left:{sl/20*100}%">Listeria : {sl}</em><i style="left:{ss/20*100}%;background:var(--sky)"></i><em style="left:{ss/20*100}%">Salmonella : {ss}</em><u style="left:0">0</u><u style="left:100%">20</u></div>
<small style="color:var(--mut)">Score de congruence de 0 à {cmax}. Licence {e(beone['licence_donnees']['valeur'])}.</small></div>
<div class="card"><strong>Dépôts publics ENA</strong><div class="tags" style="justify-content:flex-start;margin-top:12px;--c:#38bdf8">{enas}</div><br><b style="font-size:30px" data-n="{iso}">0</b> <span style="color:var(--mut)">isolats publiés</span></div></div>'''

# ---------- CONFORMITÉ ----------
chip = {'Présent': 'ok', 'Partiel': 'warn', 'Existe, non lu': 'warn', 'Absent': 'ko', 'Ouvert': 'ko', 'Constat': 'info'}
icon = {'ok': '✓', 'warn': '!', 'ko': '✕', 'info': 'i'}
cc = ''.join(f'<div class="card cf {chip.get(r["statut"],"info")}"><div class="ci">{icon[chip.get(r["statut"],"info")]}</div><div><h4>{e(r["controle"])}</h4><span class="chip {chip.get(r["statut"],"info")}">{e(r["statut"])}</span><p>{e(r["constat"])}</p><small>{e(r["source"])} · {e(r["referent"])}</small></div></div>' for r in conf)
conf_p = f'<div class="cfg">{cc}</div>'

# ---------- À FAIRE ----------
SEA = {}
for s in seances:
    if s.startswith('S'):
        SEA[s] = next((l['url'] for l in liens if l['label'].startswith('Séance ' + s[1:] + ' :') and 'drive/folders' in l['url']), '')
def tasks_for(m):
    out = []
    for i, r in enumerate(plan):
        if r['statut'] == 'Fait': continue
        mine = m in who(r['qui']); team = any(r['qui'].startswith(t) for t in TEAM) and not mine
        if m == 'Tous':
            if team: out.append((f'p{i}', r, 'équipe'))
        elif mine or team:
            out.append((f'p{i}', r, 'équipe' if team else 'perso'))
    return out
def task_html(k, r, tag):
    l = SEA.get(r['seance'], '')
    link = f' · <a href="{l}" target="_blank" rel="noopener" style="color:var(--sky)">dossier de la séance</a>' if l else ''
    c = 'ko' if r['statut'] == 'À faire' else ('info' if r['statut'] == 'Préparé' else 'warn')
    return (f'<div class="task"><input type="checkbox" data-k="{k}"><div><div class="tt"><span class="tag">{e(r["seance"])}</span>{e(r["action"])}</div>'
            f'<small>{e(r["resultat"])}{link}</small></div><span class="chip {c}">{e(r["statut"])}</span></div>')
def extra_html(m):
    return ''.join(f'<div class="task"><input type="checkbox" data-k="x{i}"><div><div class="tt"><span class="tag">ajout</span>{e(r["tache"])}</div><small>{e(r["note"])}</small></div><span class="chip ko">{e(r["statut"])}</span></div>' for i, r in enumerate(extra) if r['personne'] == m)
def links_html(m):
    cats = collections.OrderedDict()
    for l in liens:
        if l['personne'] == m: cats.setdefault(l['categorie'], []).append(l)
    return ''.join(f'<div style="margin-top:12px"><small style="color:var(--mut)">{e(c)}</small><div class="lk">' + ''.join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in ls) + '</div></div>' for c, ls in cats.items())
people = ['Tous'] + list(ROLES)
btn = ''.join(f'<button data-s="{p}" style="--c:{COL.get(p,"#2dd4bf")}" class="{"on" if i==0 else ""}">{"Équipe" if p=="Tous" else p}</button>' for i, p in enumerate(people))
subs = ''
for i, p in enumerate(people):
    ts = tasks_for(p); body = ''.join(task_html(*t) for t in ts) + extra_html(p)
    cnt = len(ts) + sum(1 for r in extra if r['personne'] == p)
    titre = "Actions pour toute l'équipe" if p == 'Tous' else f'{p} : {ROLES[p]}'
    vide = "<small>Rien d'ouvert.</small>"
    head = f'<div class="card"><strong>{titre}</strong> <span style="color:var(--mut);font-size:13px">({cnt} à traiter)</span><div style="margin-top:8px">{body or vide}</div></div>'
    if p != 'Tous':
        head += f'<div class="card" style="margin-top:14px"><strong>Liens Drive utiles pour {p}</strong>{links_html(p)}{links_html("Tous")}</div>'
    subs += f'<div class="subp {"on" if i==0 else ""}" id="s-{p}">{head}</div>'
afaire_p = f"<p style=\"color:var(--mut);margin:6px 0 0\">Tirées automatiquement du plan : tout ce qui n'est pas « Fait ». « Préparé » : le document est rédigé, il reste l'acte humain (débat, oral, validation), qui n'est pas compté comme fait. Les cases se cochent sur cet appareil seulement.</p><div class=\"sub\">{btn}</div>{subs}"

# ---------- DRIVE ----------
cats = collections.OrderedDict()
for l in liens:
    if l['personne'] == 'Tous': cats.setdefault(l['categorie'], []).append(l)
drive_p = '<div class="grid two">' + ''.join(f'<div class="card"><strong>{e(c)}</strong><div class="lk">' + ''.join(f'<a href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>' for l in ls) + '</div></div>' for c, ls in cats.items()) + '</div>'

logo = (R/'docs'/'logo.svg').read_text(encoding='utf-8')
now = datetime.datetime.now(datetime.timezone.utc).strftime('%d/%m/%Y à %H:%M UTC')
nopen = sum(1 for r in plan if r['statut'] != 'Fait') + len(extra)
TABS = [('resume', 'Résumé', resume), ('equipe', 'Équipe', equipe), ('biblio', 'Bibliothèque', biblio), ('beone', 'Données BeONE', beone_p),
        ('conf', 'Conformité', conf_p), ('afaire', f'À faire ({nopen})', afaire_p), ('drive', 'Liens Drive', drive_p)]
nav = ''.join(f'<button data-t="{i}">{t}</button>' for i, t, _ in TABS)
panels = ''.join(f'<section class="panel" id="p-{i}">{b}</section>' for i, _, b in TABS)
css = (R/'static'/'style.css').read_text(encoding='utf-8'); js = (R/'static'/'app.js').read_text(encoding='utf-8')
page = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>O.BeOne != CannotBe, dashboard</title><link rel="icon" type="image/svg+xml" href="favicon.svg"><link rel="icon" type="image/png" sizes="192x192" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png"><meta name="theme-color" content="#0b1220"><style>{css}</style></head><body><canvas id="bg"></canvas>
<main><div class="hdr">{logo}<div><div class="live"><i></i>Mis à jour le {now}</div><h1>Relier un cas humain à un aliment, sans exposer personne</h1></div></div></main>
<div class="tabs">{nav}</div>
<main>{panels}<footer>Généré le {now} depuis data/*.csv. Chaque modification d'un CSV relance la génération.</footer></main><script>{js}</script></body></html>'''
(R/'docs'/'index.html').write_text(page, encoding='utf-8')
print('ok', n, 'sources', na, 'actions')
