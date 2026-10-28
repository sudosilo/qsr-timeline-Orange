# Adds the pre quick service menu entries (1880 to 1920) and menu photo strip to the timeline page.
# Run from the qsr-timeline-Orange folder. Reads ../menu-names/menu-names.csv and ../menu-names/menu-map.csv.
import csv, re, json, collections

PAGE = 'qsr-timeline-Orange.html'
SRC = '../menu-names/'

pages = collections.defaultdict(list)
for r in csv.DictReader(open(SRC + 'menu-map.csv')):
    p = r['page_number']
    pages[r['menu_id']].append((int(p) if p.isdigit() else 999, r['image_id']))

def norm(n):
    n = n.upper().replace('-', ' ').replace("'", '')
    n = re.sub(r'[^A-Z0-9& ]', ' ', n)
    n = re.sub(r'\b(THE|CO|COMPANY|INC)\b', ' ', n)
    return re.sub(r'\s+', ' ', n).strip()

def title(s):
    s = re.sub(r'\s+', ' ', s.strip().rstrip(';').strip())
    return ' '.join(w.capitalize() for w in s.lower().split(' '))

brands = collections.defaultdict(list)
for r in csv.DictReader(open(SRC + 'menu-names.csv', encoding='utf-8')):
    n = norm(r['name'])
    if not n or 'NOT GIVEN' in n or r['menu_id'] not in pages:
        continue
    brands[n].append((r['date'], r['menu_id'], r['name'], r['place']))

entries = []
for b, v in sorted(brands.items()):
    by_year = {}
    for x in sorted(v):
        by_year.setdefault(x[0][:4], x)
    years = sorted(by_year)
    if len(years) < 3:
        continue
    k = min(4, len(years))
    ps = [by_year[years[i]] for i in sorted(set(round(j * (len(years) - 1) / (k - 1)) for j in range(k)))]
    name = collections.Counter(title(p[2]) for p in ps).most_common(1)[0][0]
    menus = [{'year': int(p[0][:4]), 'photo': 'menu-photos/' + b.replace(' ', '_') + '_' + p[0] + '.jpg'} for p in ps]
    y0, y1 = menus[0]['year'], menus[-1]['year']
    places = sorted(set(title(p[3]) for p in ps if p[3].strip()))[:3]
    where = (' Seen at ' + ', '.join(places) + '.') if places else ''
    entries.append({'name': name, 'cat': 'premenu', 'founded': y0, 'closed': y1,
        'tagline': f'Menus on file {y0} to {y1}.',
        'desc': 'Pre quick service establishment from the library menu collection. Years shown are the dates of its earliest and latest menus on file, not founding or closing dates.' + where,
        'menus': menus})

h = open(PAGE, encoding='utf-8').read()
if "premenu:" in h:
    print('page already has the menu entries, nothing changed')
    raise SystemExit
a = "  hygiene:  { label:'HYGIENE/UNIFORM',  color:'#558855' },\n"
b = "const chains = [\n"
c = "  locEl.innerHTML = rows.join('');\n"
assert h.count(a) == 1 and h.count(b) == 1 and h.count(c) == 1
h = h.replace(a, a + "  premenu:  { label:'BEFORE QSR (MENUS)', color:'#8a6a3a' },\n")
h = h.replace(b, b + "// pre quick service establishments, 1880 to 1920, from the library menu collection\n"
    + ',\n'.join('  ' + json.dumps(e, ensure_ascii=False) for e in entries) + ",\n")
strip = """  // menu photos across the years, if this entry has them
  if (chain.menus && chain.menus.length) {
    rows.push('<div class="tip-loc-row"><span class="tip-loc-label">MENUS ON FILE</span></div>');
    rows.push('<div style="display:flex;gap:6px;overflow-x:auto;padding:4px 0">' + chain.menus.map(m =>
      `<a href="${m.photo}" target="_blank" style="flex:0 0 auto;text-align:center;text-decoration:none;color:inherit">` +
      `<img src="${m.photo}" loading="lazy" alt="Menu ${m.year}" style="height:120px;width:auto;border:1px solid #ccc;border-radius:3px;display:block" onerror="this.parentNode.style.display='none'">` +
      `<div style="font-size:11px">${m.year}</div></a>`).join('') + '</div>');
  }
"""
h = h.replace(c, strip + c)
open(PAGE, 'w', encoding='utf-8').write(h)
print(len(entries), 'menu entries added to', PAGE)
