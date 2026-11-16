"""Вставка врезок в главы по якорям. Повторяемо: операции описаны таблицей."""
import os, re, sys

REPO = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text"
V4 = os.path.join(REPO, "v4")
DR = os.path.join(REPO, ".factory", "drafts")

def frag(name):
    raw = open(os.path.join(DR, name), encoding="utf-8").read()
    body = raw.split("\n---", 1)[1] if "\n---" in raw else raw
    return [p.strip() for p in re.split(r"\r?\n\s*\r?\n", body) if p.strip()]

def load(ch):
    raw = open(os.path.join(V4, ch), encoding="utf-8").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    return raw, nl

def split_paras(raw):
    return [p for p in re.split(r"(?:\r?\n){2,}", raw)]

def find_para(paras, anchor):
    for i, p in enumerate(paras):
        if p.strip().startswith(anchor):
            return i
    return -1

def do_insert(ch, mode, anchor, block_name, report):
    raw, nl = load(ch)
    paras = split_paras(raw)
    block = frag(block_name)
    if block[0][:60] in raw:
        report.append("—  %-20s %-7s «%s…» уже вставлено, пропуск" % (ch, mode, block[0][:28]))
        return True
    i = find_para(paras, anchor)
    if i < 0:
        report.append("ПРОВАЛ %s: якорь «%s» не найден" % (ch, anchor[:40]))
        return False
    at = i if mode == "before" else i + 1
    paras[at:at] = block
    before = len(split_paras(raw))
    open(os.path.join(V4, ch), "w", encoding="utf-8", newline="").write((nl + nl).join(paras))
    after = len([p for p in split_paras(open(os.path.join(V4, ch), encoding="utf-8").read()) if p.strip()])
    if after != before + len(block):
        report.append("ПРОВАЛ %s: абзацев было %d, вставлено %d, стало %d" % (ch, before, len(block), after))
        return False
    report.append("ok %-20s %-7s «%s…» ← %s (%d абз., стало %d)" % (ch, mode, anchor[:28], block_name, len(block), after))
    return True

report = []
# 1. математика в гл. 5 — перед закрывающим абзацем
do_insert("05-rd.md", "before", "Пока всё это хрипко", "врезка-05-математика.md", report)
# 2. язык и насмотренность в гл. 6
do_insert("06-koding.md", "after", "Язык — это не просто набор линейных", "врезка-06-язык-и-насмотренность.md", report)
# 3. миллионер — сразу после врезки про язык
do_insert("06-koding.md", "after", "И тут надо поправить себя", "врезка-06-миллионер.md", report)
# 4. что стало возможно — после абзаца про инди и домохозяйку
do_insert("06-koding.md", "after", "Но этот «домашний» софт не годится для продажи", "врезка-06-что-стало-возможно.md", report)
# 5. флот в гл. 7 — перед «В моём комбайне»
do_insert("07-fabrika.md", "before", "В моём комбайне", "врезка-07-флот.md", report)
# 6. две породы сборок — сразу после врезки про флот
do_insert("07-fabrika.md", "after", "И вот здесь стоит остановиться", "врезка-07-две-породы-сборок.md", report)
# 7. экономика в гл. 7 — после абзаца про счёт
do_insert("07-fabrika.md", "after", "Экономика — отдельная опора", "врезка-07-экономика-альтман.md", report)
# 8. альтернативы в финал — перед суровой реальностью
do_insert("09-final.md", "before", "Но между этой картиной будущего", "врезка-09-альтернативы.md", report)
# 11. практика команды: роли, разные инструменты, инфраструктура, второй мозг
do_insert("07-fabrika.md", "after", "И если вспомнить машину Лекуна", "врезка-07-практика-команды.md", report)

# 9. правка неверного довода в гл. 7 и слова про рой
p = os.path.join(V4, "07-fabrika.md")
t = open(p, encoding="utf-8").read()
old = "Рой нельзя собрать из закрытых коробок."
new = ("И вот здесь важно не спутать. Собрать флот можно и на закрытых: ACP работает с любым вендором. "
       "Дело не в открытости коробок, а в ставке. Ты ставишь на свою экспертизу и контроль — или на магию вендора, "
       "которому сдаёшь продукт. Закрытая коробка страшна не тем, что из неё не построить, а тем, что внутри неё "
       "решают за тебя, что тебе можно.")
if old in t:
    t = t.replace(old, new)
    report.append("ok 07-fabrika.md        правка   неверный довод про закрытые коробки заменён")
elif "а в ставке" in t:
    report.append("—  07-fabrika.md        правка   довод уже заменён, пропуск")
else:
    report.append("ПРОВАЛ 07-fabrika.md: нет ни старой фразы про коробки, ни новой про ставку")
if "тащить в огромный рой" in t:
    t = t.replace("тащить в огромный рой", "тащить в целый флот")
    report.append("ok 07-fabrika.md        правка   «огромный рой» → «целый флот»")
elif "тащить в целый флот" in t:
    report.append("—  07-fabrika.md        правка   «целый флот» уже стоит, пропуск")
open(p, "w", encoding="utf-8", newline="").write(t)

# 10. снять маркер злобы в 03b (проверенного якоря под ту мысль нет)
p = os.path.join(V4, "03b-mlp-transformer.md")
t = open(p, encoding="utf-8").read()
m = re.search(r"\s*\[ЗЛОБА:[^\]]*\]", t)
if m:
    t = t[:m.start()] + t[m.end():]
    open(p, "w", encoding="utf-8", newline="").write(t)
    report.append("ok 03b-mlp-transformer.md снят маркер злобы (якоря нет)")
else:
    report.append("—  03b-mlp-transformer.md маркера нет, пропуск")

print("\n".join(report))
bad = [r for r in report if r.startswith("ПРОВАЛ")]
print("\nИТОГ:", "ВСТАВЛЕНО" if not bad else "ЕСТЬ ПРОВАЛЫ")
sys.exit(1 if bad else 0)
