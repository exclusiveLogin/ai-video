"""Проверка артефакта «смыслы и тезисы по главам» против приёмки брифа."""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(REPO, ".factory", "goals", "2026-11-16T1551-smysly-i-tezisy.md")
V4 = os.path.join(REPO, "v4")

def body(name):
    t = open(os.path.join(V4, name), encoding="utf-8").read()
    return t.split("\n---", 1)[1] if "\n---" in t else t

def paragraphs(name):
    out = []
    for p in re.split(r"\n\s*\n", body(name)):
        s = p.strip()
        if not s or s.startswith("[") or s.startswith("#"):
            continue
        out.append(s)
    return out

chapters = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(V4, "0*.md")))
art = open(ART, encoding="utf-8").read() if os.path.exists(ART) else ""
sections = re.split(r"\n## ", art)[1:]
sec = {}
for s in sections:
    title = s.splitlines()[0].strip()
    sec[title] = s
ok = True

def check(name, cond, note=""):
    global ok
    print("  %-56s %s%s" % (name, "ок" if cond else "НЕТ", (" — " + note) if note else ""))
    ok &= bool(cond)

print("=== структура артефакта ===")
print("  размер: %d байт, разделов: %d" % (len(art), len(sections)))
check("тринадцать глав плюс сводка", len(sections) >= 14, "найдено %d" % len(sections))

print("\n=== таблицы против абзацев ===")
missing = []
for ch in chapters:
    if ch not in sec:
        missing.append(ch)
        continue
    rows = len([l for l in sec[ch].splitlines() if l.startswith("| ") and "---" not in l]) - 1
    paras = len(paragraphs(ch + ".md"))
    flag = "" if rows >= paras else "  <- таблица короче текста"
    print("  %-22s строк таблицы %-3d абзацев %-3d %s" % (ch, rows, paras, flag))
    if rows < paras:
        missing.append(ch)
check("в каждой главе таблица не короче числа абзацев", not missing, "проблемные: " + ", ".join(missing))

print("\n=== обещанные строки и списки ===")
check("строка «не найдено: 0» есть в каждой главе",
      all("не найдено" in sec.get(ch, "") for ch in chapters if ch in sec))
check("в каждой главе есть блок фактов", all(("Факты" in sec.get(ch, "") or "факт" in sec.get(ch, "").lower()) for ch in chapters if ch in sec))
check("в каждой главе есть переход", all("ереход" in sec.get(ch, "") for ch in chapters if ch in sec))
check("есть раздел Сводка с таблицей", "Сводка" in sec and sec["Сводка"].count("| ") >= 13)
check("verdict присутствует", "verdict" in art.lower())

print("\n=== сверка чисел и дат с текстом ===")
num_miss = num_all = 0
for ch in chapters:
    if ch not in sec:
        continue
    text = body(ch + ".md")
    lines = sec[ch].splitlines()
    facts = []
    grab = False
    for l in lines:
        if l.strip().startswith("**") and "акт" in l:
            grab = True
            continue
        if grab and l.strip().startswith("##"):
            grab = False
        elif grab and l.strip():
            facts.append(l)
    for f in facts:
        for tok in re.findall(r"\d{2,}", f):
            num_all += 1
            if tok not in text:
                num_miss += 1
                if num_miss <= 6:
                    print("    в гл. %s нет числа %s" % (ch, tok))
print("  чисел в списках фактов: %d, не найдено в тексте: %d" % (num_all, num_miss))
check("числа из списков фактов есть в тексте", num_all > 0 and num_miss == 0, "проверено %d" % num_all)

print("\n=== сверка утверждений с текстом (длинные слова) ===")
checked = miss = 0
for ch in chapters:
    if ch not in sec:
        continue
    text = body(ch + ".md").lower()
    for line in [l for l in sec[ch].splitlines() if l.startswith("| ") and "---" not in l][1:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower().startswith(("абзац", "не найдено")):
            continue
        longs = [w for w in re.findall(r"[А-Яа-яЁё]{7,}", cells[1]) if w.lower() not in ("российский", "который", "например")]
        if not longs:
            continue
        checked += 1
        if not any(w.lower() in text for w in longs):
            miss += 1
            if miss <= 5:
                print("    нет ни одного слова из утверждения (гл. %s): «%s…»" % (ch, cells[1][:60]))
print("  проверено утверждений: %d, без опоры на текст: %d" % (checked, miss))
check("утверждения опираются на текст (не меньше 90%)", checked > 0 and miss <= checked * 0.1)

print("\nИТОГ:", "АРТЕФАКТ ПРОХОДИТ ПРИЁМКУ" if ok else "ЕСТЬ ЗАМЕЧАНИЯ (см. выше)")
