import glob, math, collections, re, json

V4 = 'v4'
CHAPTERS = [
    ('00-intro', 'Интро'), ('02-teoriya', 'Гл. 2. Теория'),
    ('03a-emerdzhentnost', 'Гл. 3.1'), ('03b-mlp-transformer', 'Гл. 3.2'),
    ('03c-dva-rezhima', 'Гл. 3.3'), ('04-stena', 'Гл. 4'),
    ('05-rd', 'Гл. 5'), ('06-koding', 'Гл. 6'), ('06b-sborki', 'Гл. 6б'),
    ('07-fabrika', 'Гл. 7'), ('07b-lokalny-zapusk', 'Гл. 7б'),
    ('08-vendorstvo', 'Гл. 8'), ('09-final', 'Гл. 9'),
]
WORD = re.compile(r'[а-яёa-z]{4,}', re.I)
toks = lambda s: [w.lower() for w in WORD.findall(s)]
norm = lambda s: re.sub(r'\s+', ' ', s).strip()

# --- модель: точки и выписки
model = open(f'{V4}/ментальная-модель.md', encoding='utf-8').read()
units = []          # (kind, text, point_title)
cur = ''
for line in model.splitlines():
    m = re.match(r'^- \*\*(.+?)\*\*', line)
    if m:
        cur = m.group(1).strip().rstrip('.')
        units.append(('point', m.group(1), cur))
        continue
    q = re.match(r'^\s+- Выписка:\s*«(.+?)»', line)
    if q:
        units.append(('quote', q.group(1), cur))

# idf по параграфам речи
paras = []
for key, title in CHAPTERS:
    t = open(f'{V4}/{key}.md', encoding='utf-8').read().split('\n---', 1)[-1]
    t = re.sub(r'\[КАРТА:[^\]]*\]', '', t)
    t = re.sub(r'(?m)^Экран:[^\n]*$', '', t)
    for p in re.split(r'\n\s*\n', t):
        p = norm(p)
        if len(p) > 120:
            paras.append((title, key, p))

df = collections.Counter()
for _, _, p in paras:
    df.update(set(toks(p)))
N = len(paras)
idf = {w: math.log(1 + N / (1 + c)) for w, c in df.items()}

def weight(ws):
    return sum(idf.get(w, 3.0) for w in ws)

verdict = []
for title, key, p in paras:
    pt = set(toks(p))
    best, best_u = 0.0, None
    for kind, text, point in units:
        ut = set(toks(text))
        if not ut:
            continue
        inter = pt.intersection(ut)
        if not inter:
            continue
        score = weight(inter) / min(weight(pt), weight(ut))
        if score > best:
            best, best_u = score, point
    verdict.append((title, key, p, best, best_u))

covered = [v for v in verdict if v[3] >= 0.45]
partial = [v for v in verdict if 0.22 <= v[3] < 0.45]
bare = [v for v in verdict if v[3] < 0.22]

print(f'абзацев речи: {len(verdict)}')
print(f'  держатся моделью (>=0.45): {len(covered)}')
print(f'  частично (0.22-0.45):      {len(partial)}')
print(f'  не отражены (<0.22):       {len(bare)}')
print()
print('--- НЕ ОТРАЖЕНЫ В МОДЕЛИ, по главам ---')
by = collections.Counter(v[0] for v in bare)
for title in [t for _, t in CHAPTERS]:
    if by.get(title):
        print(f'\n{title}: {by[title]}')
        for v in [x for x in bare if x[0] == title][:4]:
            print('   •', v[2][:150])
print()
print('--- ЧАСТИЧНО, по главам ---')
byp = collections.Counter(v[0] for v in partial)
for title, c in byp.most_common():
    print(f'  {title}: {c}')
print()
print('Мера лексическая: считает совпадение содержательных слов, а не смысл.')
print('Примеры, личный опыт, продукты и переходы в модель не входят по замыслу —')
print('здесь ищутся только тезисы, которых в модели нет.')
