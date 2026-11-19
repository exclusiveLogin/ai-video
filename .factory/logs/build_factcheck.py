"""Сборка v4/фактчек.md из речи и реестра.

Не аудит и не сводка: рабочий документ. Для каждой главы вытаскивает твёрдые
утверждения (числа, даты, имена) и показывает, есть ли под ними основание в
v4/ссылки.md. Обновляется из менталки и реестра, ничего своего не выдумывает.
"""
import os, re

REPO = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text"
V4 = os.path.join(REPO, "v4")
CHAPTERS = [
    ("00-intro", "Интро"), ("02-teoriya", "Глава 2. Теория"),
    ("03a-emerdzhentnost", "Глава 3.1. Эмерджентность"),
    ("03b-mlp-transformer", "Глава 3.2. От перцептрона к трансформеру"),
    ("03c-dva-rezhima", "Глава 3.3. Два режима"), ("04-stena", "Глава 4. Стена"),
    ("05-rd", "Глава 5. R&D"), ("06-koding", "Глава 6. Кодинг"),
    ("06b-sborki", "Глава 6б. Сборки"), ("07-fabrika", "Глава 7. Фабрика"),
    ("07b-lokalny-zapusk", "Глава 7б. Локальный запуск"),
    ("08-vendorstvo", "Глава 8. Вендорство"), ("09-final", "Глава 9. Финал"),
]

DIGITS = {
    "сорок": 40, "пятьдесят": 50, "шестьдесят": 60, "семьдесят": 70,
    "восемьдесят": 80, "девяносто": 90, "двадцать": 20, "тридцать": 30,
    "тысяча девятьсот": 1900,
}
ORD = {
    "первом": 1, "втором": 2, "третьем": 3, "четвёртом": 4, "четвертом": 4,
    "пятом": 5, "шестом": 6, "седьмом": 7, "восьмом": 8, "девятом": 9,
    "десятом": 10,
}
NAMES = ("OpenAI", "Anthropic", "Meta", "Google", "DeepMind", "NVIDIA", "Apple",
         "AMD", "GitHub", "Linux", "Microsoft", "Amazon", "Tesla", "Epoch",
         "AlphaGo", "BERT", "T5", "LSTM", "GRU", "ResNet", "Sora", "Suno",
         "Encraw", "DJI", "Bambu", "Cursor", "Claude", "Codex", "Hinton",
         "ЛеКун", "Лекун", "Хинтон", "Минский", "Паперт", "Розенблатт",
         "Шмидхубер", "Хохрайтер", "Цыбенко", "Планк", "Карпатый", "Канеман",
         "Павлов", "Райс", "Гёдель", "Лёб", "Тьюринг", "Альтман")


def body(path):
    t = open(path, encoding="utf-8").read()
    t = t.split("\n---", 1)[-1] if "\n---" in t else t
    t = re.sub(r"\[КАРТА:[^\]]*\]", "", t)
    t = re.sub(r"(?m)^Экран:[^\n]*$", "", t)
    return t


def spelled_years(s):
    """Годы, написанные словами: «в сорок третьем», «в двадцать пятом»."""
    out = []
    for m in re.finditer(r"(сорок|пятьдесят|шестьдесят|семьдесят|восемьдесят|девяносто|двадцать|тридцать)\s+([а-яё]+)", s, re.I):
        tens_word = m.group(1).lower()
        tens = DIGITS.get(tens_word)
        suffix = m.group(2).lower()
        for word, val in ORD.items():
            if suffix.startswith(word[:5]):
                if tens:
                    base = 1900 if tens >= 40 else 2000
                    out.append(base + tens + val)
                break
    for m in re.finditer(r"тысяча девятьсот\s+([а-яё]+)", s, re.I):
        for word, val in ORD.items():
            if m.group(1).lower().startswith(word[:5]):
                out.append(1900 + val)
    return out


def hard_claims(text):
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", re.sub(r"\s+", " ", text)) if len(s.strip()) > 40]
    claims = []
    for s in sents:
        years = [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", s)] + spelled_years(s)
        nums = re.findall(r"\d+[.,]?\d*\s*(?:%|процент\w*|млрд|млн|миллион\w*|миллиард\w*|тысяч\w*|трлн)", s)
        names = [n for n in NAMES if re.search(r"(?<![A-Za-zА-Яа-яЁё])" + re.escape(n), s)]
        if years or nums or names:
            claims.append((s, years, nums, names))
    return claims


def registry():
    reg = open(os.path.join(V4, "ссылки.md"), encoding="utf-8").read()
    return reg, reg.lower()


def anchor_for(reg_low, years, nums, names):
    for y in years:
        if str(y) in reg_low:
            return f"год {y} — в реестре"
    for n in nums:
        core = re.sub(r"[^\d.,]", "", n).strip(".,")
        if core and core in reg_low:
            return f"число {core} — в реестре"
    for nm in names:
        if nm.lower() in reg_low:
            return f"«{nm}» — в реестре"
    return ""


def main():
    reg, reg_low = registry()
    lines = [
        "# Фактчек: твёрдые утверждения речи против реестра",
        "",
        "Документ рабочий, не сводка. Собирается скриптом `.factory/logs/build_factcheck.py`",
        "из глав и `v4/ссылки.md`: для каждой главы — утверждения с числами, датами и именами,",
        "и под каждым либо основание в реестре, либо пометка «якоря нет».",
        "",
        "Как читать статусы: **в реестре** — адрес есть, при правке сверять по нему;",
        "**якоря нет** — либо наше суждение (тогда так и должно быть), либо дырка, которую надо закрыть.",
        "Личный опыт и выводы автора якоря не требуют — это класс 3 реестра.",
        "",
    ]
    total = 0
    unanchored = 0
    for key, title in CHAPTERS:
        path = os.path.join(V4, key + ".md")
        if not os.path.exists(path):
            continue
        text = body(path)
        claims = hard_claims(text)
        if not claims:
            continue
        lines += [f"## {title}", "", "| Утверждение | Основание |", "|---|---|"]
        for s, years, nums, names in claims:
            total += 1
            a = anchor_for(reg_low, years, nums, names)
            if not a:
                unanchored += 1
                a = "**якоря нет**"
            cell = s if len(s) <= 240 else s[:237] + "…"
            lines.append(f"| {cell} | {a} |")
        lines.append("")
    lines += [
        "---",
        "",
        f"Всего твёрдых утверждений: {total}. Без основания в реестре: {unanchored}.",
        "",
        "Проверяются утверждения, где есть число, дата или имя. Оценки, метафоры и личный опыт",
        "сюда не попадают: у них другая мера — класс утверждения из шапки `v4/ссылки.md`.",
    ]
    out = os.path.join(V4, "фактчек.md")
    open(out, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    print(f"собрано: {out} | утверждений {total} | без якоря {unanchored}")


if __name__ == "__main__":
    main()
