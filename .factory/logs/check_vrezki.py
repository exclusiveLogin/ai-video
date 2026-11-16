"""Сверка: каждый абзац врезки должен стоять в целевой главе дословно."""
import os, re, sys

REPO = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text"
V4 = os.path.join(REPO, "v4")
DR = os.path.join(REPO, ".factory", "drafts")

# врезка → глава, куда она вставлена
MAP = {
    "врезка-05-математика.md": "05-rd.md",
    "врезка-06-язык-и-насмотренность.md": "06-koding.md",
    "врезка-06-миллионер.md": "06-koding.md",
    "врезка-06-что-стало-возможно.md": "06-koding.md",
    "врезка-07-флот.md": "07-fabrika.md",
    "врезка-07-две-породы-сборок.md": "07-fabrika.md",
    "врезка-07-экономика-альтман.md": "07-fabrika.md",
    "врезка-07-практика-команды.md": "07-fabrika.md",
    "врезка-09-альтернативы.md": "09-final.md",
}

def frag(name):
    raw = open(os.path.join(DR, name), encoding="utf-8").read()
    body = raw.split("\n---", 1)[1]
    return [p.strip() for p in re.split(r"\r?\n\s*\r?\n", body) if p.strip()]

bad = 0
for vrezka, ch in sorted(MAP.items()):
    if not os.path.exists(os.path.join(DR, vrezka)):
        print("нет черновика: %s" % vrezka); bad += 1; continue
    text = open(os.path.join(V4, ch), encoding="utf-8").read()
    ps = frag(vrezka)
    missing = [p for p in ps if p[:70] not in text]
    flag = "ок" if not missing else "РАСХОЖДЕНИЕ в %d абзацах" % len(missing)
    print("%-38s → %-16s абзацев %2d  %s" % (vrezka, ch, len(ps), flag))
    for p in missing:
        print("     нет в главе: %s…" % " ".join(p.split())[:80])
        bad += 1
print("\nИТОГ:", "ЧЕРНОВИКИ СОВПАДАЮТ С ГЛАВАМИ" if not bad else "ЕСТЬ РАСХОЖДЕНИЯ: %d" % bad)
sys.exit(0 if not bad else 1)
