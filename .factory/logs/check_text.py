"""Проверка по всему тексту v4: дубли между главами, однообразные зачины, лейтмотив, повторные пояснения.

Ловит то, что не видно при чтении одной главы. Работает по репликам речи: служебная шапка до первого «---» не берётся.
"""
import collections, glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v5")

def speech(path):
    t = open(path, encoding="utf-8").read()
    return t.split("\n---", 1)[-1] if "\n---" in t else t

def paragraphs(path):
    return [p for p in re.split(r"(?:\r?\n){2,}", speech(path)) if p.strip()]

chapters = sorted(glob.glob(os.path.join(V4, "*", "0*.md")))
problems = 0

# 1. дословные и почти дословные повторы между главами
print("=== 1. ПОВТОРЫ МЕЖДУ ГЛАВАМИ ===")
seen = {}
dups = []
for path in chapters:
    name = os.path.basename(path)
    for p in paragraphs(path):
        s = " ".join(p.split())
        if len(s) < 80 or s.startswith(("#", "[", "|")):
            continue
        key = s[:60]
        if key in seen and seen[key][0] != name:
            dups.append((seen[key][0], name, s))
        else:
            seen[key] = (name, s)
for first, second, s in dups:
    print("  %s ↔ %s: «%s…»" % (first, second, s[:70]))
if not dups:
    print("  повторов нет")
problems += len(dups)

# 2. однообразные зачины абзацев
print("\n=== 2. ЧАСТЫЕ ЗАЧИНЫ (3 и больше раз) ===")
openings = collections.Counter()
for path in chapters:
    for p in paragraphs(path):
        s = " ".join(p.split())
        m = re.match(r"((?:И|Но|А|Так|Вот|Поэтому|Значит|Именно|Плюс|Минус|Первое|Второе|Третье|Четвёртое)[^.,;:—]{0,30})", s)
        if m:
            openings[m.group(1).strip()] += 1
for k, n in openings.most_common(12):
    if n >= 3:
        print("  %2d × «%s»" % (n, k[:50]))
        problems += 1
if not any(n >= 3 for n in openings.values()):
    print("  зачинов-повторов нет")

# 3. лейтмотив назван словами
print("\n=== 3. ЛЕЙТМОТИВ ===")
full = " ".join(speech(p) for p in chapters)
for word in ("декларативн", "императивн"):
    n = len(re.findall(word, full, re.I))
    print("  %-16s вхождений: %d" % (word, n))
    if n == 0:
        problems += 1

# 4. термины: сколько раз и объяснены ли дважды
print("\n=== 4. ТЕРМИНЫ С ПОЯСНЕНИЕМ ===")
gloss = {"харнес": ("то есть", "назовём", "называют"), "комбайн": ("workflow", "пайплайн", "зовут"),
         "тулинг": ("называют одним словом",), "граф-инжиниринг": ("называют",),
         "второй мозг": ("не приложение", "папка")}
for term, markers in gloss.items():
    hits = []
    for path in chapters:
        t = speech(path)
        for m in re.finditer(term, t, re.I):
            window = t[m.start():m.start() + 160]
            if any(x in window for x in markers):
                hits.append(os.path.basename(path))
    if len(set(hits)) > 1:
        print("  %-16s объясняется в %s" % (term, sorted(set(hits))))
        problems += 1
if problems == 0:
    print("  двойных пояснений нет")

print("\nИТОГ:", "ЧИСТО" if problems == 0 else "НАЙДЕНО ЗАМЕЧАНИЙ: %d" % problems)
sys.exit(0 if problems == 0 else 1)
