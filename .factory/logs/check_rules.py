"""Проверка глав v4 против правил v4/STYLE.md: стоп-лист, выдуманные слова, образы, эхо."""
import glob, os, re, collections

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v4")
CH = sorted(os.path.basename(p) for p in glob.glob(os.path.join(V4, "0*.md")))

STOP = ["всегда", "априори", "незаменим", "в современном мире", "давайте погрузимся",
        "не секрет, что", "в конечном счёте", "резюмируя", "стоит отметить", "важно понимать"]
# свои выдуманные слова, которых в ролике быть не должно
COINED = ["флит"]
# как называть сборку — роем, стаей или флотом — решено не нормировать:
# важно устройство (иерархия или горизонталь) и кто кого проверяет, а не название
CONTEXT_BAN = []
CONTEXT_NEED = ["агент", "флот", "фабрик", "харнес"]
# слова, которые можно, но при первом употреблении надо пояснить
NEEDS_GLOSS = {"комбайн": ["workflow", "пайплайн", "суть одна", "так зовут"]}
# образы: где им разрешено стоять
IMAGE_RULE = {
    "оракул":  (["09-final.md"], "только финал, значение «чёрный ящик, который не объясняет»"),
    "поводок": (["08-vendorstvo.md", "09-final.md"], "гл. 8 и финал, в первой половине запрещён"),
    "зеркал":  (["04-stena.md", "05-rd.md", "09-final.md"], "начиная с гл. 4"),
    "тыкв":    (["00-intro.md", "06-koding.md", "09-final.md"], "трижды: хук, панч гл. 6, финал"),
}

raw = {f: open(os.path.join(V4, f), encoding="utf-8").read() for f in CH}
titles = {f: t.splitlines()[0] for f, t in raw.items()}
# служебная шапка (заголовок, Статус, Правка, Долги) до первого --- в озвучку не идёт
texts = {f: (t.split("\n---", 1)[1] if "\n---" in t else t) for f, t in raw.items()}
ok = True

def wc(word, t):
    return len(re.findall(r"(?<![а-яё])" + word + r"[а-яё]*", t, re.I))

print("=== 1. СТОП-ЛИСТ ===")
for f, t in texts.items():
    hits = [w for w in STOP if re.search(r"(?<![а-яё])" + w, t, re.I)]
    if hits:
        ok = False
        print("  %-22s %s" % (f, hits))
print("  чисто во всех главах" if ok else "  есть нарушения")

print("\n=== 2. ВЫДУМАННЫЕ СЛОВА ===")
clean = True
for f, t in texts.items():
    for w in COINED:
        n = wc(w, t)
        if n:
            clean = False
            for m in re.finditer(r".{0,60}(?<![а-яё])" + w + r"[а-яё]*.{0,60}", t, re.I):
                print("  %-22s %-8s …%s…" % (f, w, " ".join(m.group(0).split())))
    for w in CONTEXT_BAN:
        for m in re.finditer(r".{0,60}(?<![а-яё])" + w + r"[\s.,;:!?].{0,60}", t, re.I):
            frag = " ".join(m.group(0).split())
            if any(k in frag.lower() for k in CONTEXT_NEED):
                clean = False
                print("  %-22s %-8s …%s…" % (f, w, frag))
if clean:
    print("  ни одного выдуманного слова")
ok &= clean

print("\n=== 2б. СЛОВА, НУЖНЫЕ С ПОЯСНЕНИЕМ ===")
# пояснение ищем в сквозном тексте ролика: один раз объяснили — дальше можно
full = "\n\n".join(texts[f] for f in CH)
for w, keys in NEEDS_GLOSS.items():
    first = re.search(r"(?<![а-яё])" + w + r"[а-яё]*", full, re.I)
    if not first:
        continue
    tail = full[first.start():]
    pos = min([tail.lower().find(k) for k in keys if k in tail.lower()] or [-1])
    if pos >= 0:
        print("  %-8s пояснение есть, через %d знаков после первого вхождения" % (w, pos))
    else:
        print("  %-8s БЕЗ ПОЯСНЕНИЯ" % w)
        ok = False

print("\n=== 3. ОБРАЗЫ: где стоят ===")
for img, (allowed, rule) in IMAGE_RULE.items():
    st = {f: wc(img, t) for f, t in texts.items() if wc(img, t)}
    banned = {f: n for f, n in st.items() if f not in allowed}
    verdict = "нарушение: %s" % banned if banned else "ок"
    if banned:
        ok = False
    print("  %-9s всего=%-3d %-52s %s" % (img, sum(st.values()), str(st), verdict))

print("\n=== 4. ЭХО до трёх: сколько раз образ звучит словом ===")
for img, want in (("тыкв", 3), ("поводок", 2)):
    n = sum(wc(img, t) for t in texts.values())
    flag = "ок" if n == want else "РАСХОЖДЕНИЕ с законом (записано: %d)" % want
    print("  %-9s словом %d раз(а) — %s" % (img, n, flag))

print("\n=== 5. ВНУТРЕННИЕ СЛОВА ЗАВОДА В ТЕКСТЕ РОЛИКА ===")
for w in ["бриф", "доска", "цели", "задание", "приёмк", "харнес", "обвязк", "флот", "фабрик", "субагент"]:
    per = {f: wc(w, t) for f, t in texts.items() if wc(w, t)}
    print("  %-10s %s" % (w, per or "нет"))

print("\nИТОГ:", "ВСЁ ВАЛИДНО" if ok else "ЕСТЬ НАРУШЕНИЯ (см. выше)")
