"""Сверка глав v5 с первоисточниками chapters/: чего из источника в тексте нет.

Ловит вещи, на которые не смотрит ни одна другая проверка: числа, годы, имена и термины,
которые были в исходнике и не дошли до речи. Помогает и при вопросе «не потеряли ли мы что-то
по дороге», и при сборке версии из нескольких линий.
"""
import glob, os, re, sys
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v5")

def _chap(name):
    """Глава живёт в одной из частей: ищем по подпапкам, иначе корень v5."""
    import glob as _g
    hits = _g.glob(os.path.join(V4, "*", name))
    return hits[0] if hits else os.path.join(V4, name)

CH = os.path.join(REPO, "chapters")

# глава v4 → первоисточник
MAP = {
    "02-teoriya.md": "Глава 2. Теория.md",
    "03a-emerdzhentnost.md": "Глава 3.1. Эмерджентность.md",
    "03b-mlp-transformer.md": "Глава 3.2. От MLP к Трансформеру.md",
    "03c-dva-rezhima.md": "Глава 3.3. Два режима   Латенты   Итог.md",
    "04-stena.md": "Глава 4. Стена.md",
    "05-rd.md": "Глава 5. R&D  где идёт война.md",
    "06-koding.md": "Глава 6. Кодинг  смерть синтаксиса.md",
    "06b-sborki.md": "Блок 6.5. Сборки ИИ  от API до флота.md",
    "07-fabrika.md": "Глава 7. Фабрика  мультиагентный комбайн.md",
    "07b-lokalny-zapusk.md": "Блок 7.5. Локальный запуск  Dense vs MoE и инференс-движки.md",
    "08-vendorstvo.md": "Глава 8. Вендорство и цензура.md",
    "09-final.md": "Финал  советы (заготовка).md",
}

def words(t):
    return len(re.findall(r"[А-Яа-яЁёA-Za-z][А-Яа-яЁёA-Za-z-]*", t))

def speech(t):
    return t.split("\n---", 1)[-1] if "\n---" in t else t

def tokens(t):
    """Что в источнике стоит «твёрдо»: числа, годы, латиница, слова в кавычках."""
    out = set()
    out |= set(re.findall(r"\b\d{2,}\b", t))
    out |= set(re.findall(r"\b(?:19|20)\d{2}(?:-\w+)?\b", t))
    out |= set(re.findall(r"\b[A-Z][A-Za-z][A-Za-z\-]{2,}\b", t))
    for q in re.findall(r"«([^»]{4,40})»", t):
        out.add("«%s»" % q.strip())
    return {x for x in out if len(x) > 2}

print("%-24s %6s %6s %7s  %s" % ("глава", "источник", "v4", "дельта", "не дошло никуда в v4"))
missing_total = 0
# весь текст v4: чтобы не считать потерей то, что переехало в другую главу
whole_v4 = " ".join(speech(open(p, encoding="utf-8").read())
                    for p in sorted(glob.glob(os.path.join(V4, "*", "0*.md")))).lower()

for ch, src in MAP.items():
    p4, ps = _chap(ch), os.path.join(CH, src)
    if not os.path.exists(ps):
        print("%-24s источник не найден: %s" % (ch, src))
        continue
    t4, ts = speech(open(p4, encoding="utf-8").read()), speech(open(ps, encoding="utf-8").read())
    miss = sorted(x for x in tokens(ts) if x.lower() not in whole_v4)
    missing_total += len(miss)
    print("%-24s %6d %6d %+7d  %d шт." % (ch, words(ts), words(t4), words(t4) - words(ts), len(miss)))
    if miss:
        print("      " + ", ".join(miss[:16]))

# отдельно: интро живёт не в chapters/
intro_src = os.path.join(REPO, "intro", "Интро + дорожка повествования.md")
if os.path.exists(intro_src):
    t4 = speech(open(os.path.join(V4, "00-intro.md"), encoding="utf-8").read())
    ts = speech(open(intro_src, encoding="utf-8").read())
    miss = sorted(x for x in tokens(ts) if x.lower() not in whole_v4)
    missing_total += len(miss)
    print("\n%-24s %6d %6d %+7d  %d шт." % ("00-intro (intro/)", words(ts), words(t4), words(t4) - words(ts), len(miss)))
    if miss:
        print("      " + ", ".join(miss[:16]))

print("\nИТОГ: не дошло из первоисточников никуда в v4: %d единиц" % missing_total)
print("Список к разбору: часть единиц лишняя, часть — потерянный смысл или факт.")
sys.exit(0)
