"""Сверка смыслового ядра с текстом ролика: обещания хука, образы, ключевые формулировки."""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v4")

def body(name):
    t = open(os.path.join(V4, name), encoding="utf-8").read()
    return t.split("\n---", 1)[1] if "\n---" in t else t

def cnt(word, t):
    return len(re.findall(r"(?<![а-яё])" + word + r"[а-яё]*", t, re.I))

CH = sorted(os.path.basename(p) for p in glob.glob(os.path.join(V4, "0*.md")))
full = "\n\n".join(body(f) for f in CH)
# слова, обещанные в хуке, ищем вне хука: там они и должны зазвучать
full_wo_hook = "\n\n".join(body(f) for f in CH if f != "00-intro.md")
b = {f: body(f) for f in CH}
hook, finale, g6, g7 = b["00-intro.md"], b["09-final.md"], b["06-koding.md"], b["07-fabrika.md"]
ok = True

def check(name, cond, note=""):
    global ok
    print("  %-52s %s%s" % (name, "ок" if cond else "НЕТ", (" — " + note) if note and not cond else ""))
    ok &= bool(cond)

print("=== обещания хука ===")
check("вопрос про тыкву звучит в хуке", "тыкв" in hook.lower())
# пять слов: либо названы словом, либо закрыты по смыслу (слова нет — не провал, а решение)
NAMED = {"DSL": "06-koding.md", "OpenSpec": "06-koding.md", "SDD": "06-koding.md"}
BY_MEANING = {"граф-инжиниринг": "06b-sborki.md", "тулинг": "07-fabrika.md"}
for word, where in NAMED.items():
    check("пять слов: %s назван словом" % word, word.lower() in b[where].lower())
warns = []
for word, where in BY_MEANING.items():
    in_text = word.lower() in full_wo_hook.lower()
    if in_text:
        print("  %-52s назван словом вне хука" % ("пять слов: %s" % word))
    else:
        warns.append(word)
        print("  %-52s закрыт по смыслу (гл. %s), слова вне хука нет — решить" % ("пять слов: %s" % word, where.split("-")[0]))
check("закрытые коробки молчат (гл. 8)", "закрыт" in b["08-vendorstvo.md"].lower())
check("одно дело на вечер в финале", "одно дело" in finale.lower())
check("«владейте инструментом, не кнопкой»", "владейте" in finale.lower() and "кнопк" in finale.lower())

print("\n=== красная линия ===")
check("тыква трижды", sum(cnt("тыкв", t) for t in b.values()) == 3)
check("«инженер не умирает, он переезжает»", "не умирает" in finale.lower())
check("шагать вверх придётся вам", "шагать вверх" in finale.lower())
check("есть автор истории (замысел наш)", "есть автор" in finale.lower())

print("\n=== образы по правилам ===")
check("зеркало только с гл. 4", all(f in ("04-stena.md", "05-rd.md", "09-final.md") for f in b if cnt("зеркал", b[f])))
check("оракул только в финале", all(f == "09-final.md" for f in b if cnt("оракул", b[f])))
check("поводок дважды", sum(cnt("поводок", t) for t in b.values()) == 2)
check("миллионер только в гл. 6 или финале", all(f in ("06-koding.md", "09-final.md") for f in b if "миллионер" in b[f].lower()))

print("\n=== три потолка в финале ===")
for k, label in (("sequoia", "Sequoia"), ("epoch", "Epoch AI"), ("мегаватт", "электричество")):
    check("финал: %s" % label, k in finale.lower())

print("\n=== якоря и доски на месте ===")
for f in ("ссылки.md", "ссылки.md", "фактчек.md", "ментальная-модель.md", "STYLE.md"):
    check("v4/%s" % f, os.path.exists(os.path.join(V4, f)))

print("\nИТОГ:", ("ЯДРО СВЕРЯЕТСЯ С ТЕКСТОМ" if ok else "ЕСТЬ РАСХОЖДЕНИЯ") +
      (" | ждут решения: " + ", ".join(warns) if warns else ""))
sys.exit(0 if ok else 1)
