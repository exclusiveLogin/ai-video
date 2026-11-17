"""Смысловая сверка глав с первоисточниками: какие мысли источника не нашли отражения в v4.

Для каждого абзаца источника ищется ближайший абзац v4 по пересечению значимых слов.
Если пересечение низкое — мысль помечается как кандидат в потерянные (её читает человек,
скрипт только сужает список до обозримого).
"""
import glob, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
V4 = os.path.join(REPO, "v4")
CH = os.path.join(REPO, "chapters")

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

STOP = set("""это этот эта эти тот та то и в во не что он на я с со как а то все она так его но да ты
к у же вы за бы по только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг ли если уже
или ни быть был него до вас нибудь опять уж вам ведь там потом себя ничего ей может они тут где есть надо
ней для мы тебя их чем была сам чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому
этого какой совсем ним здесь этом один почти мой тем чтобы нее кажется сейчас были куда зачем всех никогда
можно при наконец два об другой хоть после над больше тот через эти нас про всего них какая много разве
три эту моя впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда конечно всю
между это чтобы свои свою он она оно мы вы они который которые который""".split())

def speech(t): return t.split("\n---", 1)[-1] if "\n---" in t else t
def paras(t): return [" ".join(p.split()) for p in re.split(r"(?:\r?\n){2,}", speech(t)) if p.strip()]
def sig(t): return {w for w in re.findall(r"[а-яёa-z]{5,}", t.lower()) if w not in STOP}

report = []
for ch, src in MAP.items():
    ps = os.path.join(CH, src)
    if not os.path.exists(ps):
        report.append("%s: источник не найден" % ch); continue
    src_paras = [p for p in paras(open(ps, encoding="utf-8").read()) if len(p.split()) >= 8]
    v4_paras = [p for p in paras(open(os.path.join(V4, ch), encoding="utf-8").read()) if len(p.split()) >= 5]
    v4_sigs = [sig(p) for p in v4_paras]
    lost = []
    for p in src_paras:
        s = sig(p)
        if not s:
            continue
        best = max((len(s & x) / len(s) for x in v4_sigs), default=0.0)
        if best < 0.34:
            lost.append((round(best, 2), p))
    report.append("%-24s абзацев в источнике %2d | без отражения в v4: %d" % (ch, len(src_paras), len(lost)))
    for score, p in sorted(lost)[:6]:
        report.append("      [%s] %s…" % (score, p[:110]))

print("\n".join(report))
print("\nПометка: низкое пересечение — сигнал, а не приговор. Абзац мог быть сказан иначе,")
print("сведён с соседним или сознательно убран. Список читает человек.")
