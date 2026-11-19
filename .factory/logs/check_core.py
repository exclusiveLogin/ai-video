"""Сверка ментальной модели с текстом — по выпискам, а не поиском слов.

У каждой опорной точки модели есть выписка: дословная фраза из речи. Если выписка в тексте
не находится — это сигнал разбираться: либо текст уехал от замысла, либо модель устарела.
Скрипт ничего не принимает, он только указывает место для чтения.
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v5")
MODEL = os.path.join(V4, "ментальная-модель.md")

norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()

def chapter_text():
    parts = {}
    for p in sorted(glob.glob(os.path.join(V4, "*", "0*.md"))):
        t = open(p, encoding="utf-8").read()
        parts[os.path.basename(p)] = norm(t.split("\n---", 1)[-1] if "\n---" in t else t)
    return parts

CHAPTERS = chapter_text()
WHOLE = " ".join(CHAPTERS.values())

model = open(MODEL, encoding="utf-8").read()
points = re.findall(r"^- \*\*(.+?)\*\*.*$", model, re.M)

cites, stale, absent = [], [], []
cur = None
for line in model.splitlines():
    m = re.match(r"^- \*\*(.+?)\*\*", line)
    if m:
        cur = m.group(1).strip().rstrip(".")
        continue
    c = re.match(r"^\s+- Выписка:\s*«(.+?)»\s*—\s*гл\.\s*(\S+)", line)
    if c:
        cites.append((cur, c.group(1), c.group(2)))
        continue
    if re.match(r"^\s+- Выписка:\s*нет в тексте", line):
        absent.append(cur)

print("=== СВЕРКА МОДЕЛИ С ТЕКСТОМ ===")
print("опорных точек в модели: %d | с выпиской: %d | без выписки (сказано словами «нет в тексте»): %d" %
      (len(points), len(cites), len(absent)))

for point, quote, ch in cites:
    if norm(quote) in WHOLE:
        continue
    head = norm(quote)[:50]
    where = "начало выписки в тексте есть, хвост разошёлся" if head in WHOLE else "в тексте не нашлось"
    stale.append((point, ch, where, quote))

print("\n=== ГДЕ РАСХОДИТСЯ ===")
if not stale:
    print("  выписки на месте: каждая опорная точка подтверждается дословной фразой текста")
else:
    for point, ch, where, quote in stale:
        print("  • %-46s гл. %-4s %s" % (point[:46], ch, where))
        print("      выписка: «%s…»" % quote[:90])

print("\nПометка: расхождение — повод прочитать место глазами, а не приговор. Текст мог уехать")
print("от модели, а могла устареть сама модель: решает автор или аудитор по смыслу.")
sys.exit(0 if not stale else 1)
