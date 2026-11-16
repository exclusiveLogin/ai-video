import glob, json, os, re, time

REPO = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text"
SESS = os.path.expanduser("~/.pi/agent/sessions")
CHAPS = ["00-intro", "02-teoriya", "03a-emerdzhentnost", "03b-mlp-transformer", "03c-dva-rezhima",
         "04-stena", "05-rd", "06-koding", "06b-sborki", "07-fabrika", "07b-lokalny-zapusk",
         "08-vendorstvo", "09-final"]

# --- 1. вердикты из сессий: последний assistant-текст с блоком role: auditor ---
def texts_from_session(path):
    out = []
    try:
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("type") != "message":
                continue
            m = r.get("message", {})
            if m.get("role") != "assistant":
                continue
            c = m.get("content")
            if isinstance(c, list):
                t = "\n".join(str(x.get("text", "")) for x in c if isinstance(x, dict) and x.get("type") == "text")
            else:
                t = str(c or "")
            if t.strip():
                out.append(t)
    except Exception:
        pass
    return out

def clean(d):
    d = " ".join((d or "").split())
    d = re.sub(r"^[\[\]`\-–\s]*$", "", d)
    if d.strip() in ("", "нет", "- нет"):
        return "нет"
    d = re.sub(r"[`\[\]]+$", "", d).strip()
    return d

verdicts = {}   # chapter -> (mtime, verdict, diffs_text, filename)
files = glob.glob(os.path.join(SESS, "*AI-text*", "**", "*.jsonl"), recursive=True)
for p in files:
    mt = os.path.getmtime(p)
    for t in texts_from_session(p):
        m = re.search(r"verdict:\s*(PASS|FAIL)\s*\n(?:.*?)?role:\s*auditor\s*\nchapter:\s*([0-9a-z\-]+)\s*\ndiffs:\s*(.*)", t, re.S)
        if not m:
            continue
        v, ch, diffs = m.group(1), m.group(2).strip(), m.group(3).strip()
        if ch not in CHAPS:
            continue
        prev = verdicts.get(ch)
        if prev is None or mt > prev[0]:
            verdicts[ch] = (mt, v, diffs, os.path.basename(p))

# --- 2. согласованные отличия из заданий аудиторам ---
checks = {}
for ch in CHAPS:
    p = os.path.join(REPO, ".factory", "logs", "auditor-%s-task.txt" % ch)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"Согласованные отличия[^\n]*\n\n(.*?)(?:\n\n[А-ЯA-Z][^\n]{0,120}\n|$)", t, re.S)
    checks[ch] = (m.group(1).strip() if m else "")
    if not checks[ch]:
        m2 = re.search(r"Согласованные отличия[^\n]*\n\n(.*)", t, re.S)
        checks[ch] = (m2.group(1).strip() if m2 else "")[:1500]

# --- 3. сборка артефакта ---
lines = []
lines.append("# Фактчек v4 по главам")
lines.append("")
lines.append("Дата: 2026-11-16. Метод: на каждую главу — отдельный аудитор. Он сверял факты, даты, числа, имена и термины речи v4 с v3 и отдельно проверял, не появилось ли новых. Аудитор приходил после того, как глава отредактирована целиком.")
lines.append("")
lines.append("Вердикты: ✅ PASS — расхождений сверх согласованных нет · ❌ FAIL — есть расхождения.")
lines.append("")
lines.append("| Глава | Вердикт | Расхождений сверх согласованных |")
lines.append("|---|---|---|")
for ch in CHAPS:
    if ch in verdicts:
        v = verdicts[ch][1]
        d = clean(verdicts[ch][2])
        lines.append("| %s | %s | %s |" % (ch, "✅ PASS" if v == "PASS" else "❌ FAIL", d[:160]))
    else:
        lines.append("| %s | — не найден | |" % ch)
lines.append("")

for ch in CHAPS:
    lines.append("## %s" % ch)
    lines.append("")
    lines.append("- Источник: `v3/%s.md`; проверялось: `v4/%s.md`." % (ch, ch))
    if ch in verdicts:
        mt, v, diffs, fname = verdicts[ch]
        lines.append("- Вердикт аудитора: %s (%s)" % (v, time.strftime("%Y-%m-%d %H:%M", time.localtime(mt))))
        lines.append("- Сессия аудитора: `%s`" % fname)
        dd = clean(diffs)
        if dd != "нет":
            lines.append("- Расхождения сверх согласованных: %s" % dd[:900])
        else:
            lines.append("- Расхождения сверх согласованных: нет.")
    else:
        if ch == "03b-mlp-transformer":
            lines.append("- Вердикт аудитора: не проверялась. Глава сделана пробным проходом до того, как аудит на каждую главу стал обязательным. Новых фактов, дат, чисел и имён в неё не добавлялось: правились род слова и пояснение про мешок слов.")
        else:
            lines.append("- Вердикт аудитора: не найден в сессиях.")
    c = checks.get(ch, "")
    if c:
        lines.append("- Что было согласовано как отличия и проверялось:")
        for ln in [x for x in c.splitlines() if x.strip()][:14]:
            lines.append("    %s" % " ".join(ln.split())[:220])
    lines.append("")

open(os.path.join(REPO, "v4", "фактчек.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("вердиктов найдено:", len(verdicts), "из", len(CHAPS))
for ch in CHAPS:
    print("  %-22s %s" % (ch, verdicts[ch][1] if ch in verdicts else "—"))
print("файл: v4/фактчек.md,", os.path.getsize(os.path.join(REPO, "v4", "фактчек.md")), "байт")
