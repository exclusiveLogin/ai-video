import os, glob, subprocess, sys

REPO = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text"
V3, V4 = os.path.join(REPO, "v3"), os.path.join(REPO, "v4")

SCOPE = ["02-teoriya.md", "03a-emerdzhentnost.md", "03b-mlp-transformer.md", "03c-dva-rezhima.md",
         "04-stena.md", "05-rd.md", "06b-sborki.md", "07-fabrika.md", "07b-lokalny-zapusk.md",
         "08-vendorstvo.md"]
MINE = ["00-intro.md", "06-koding.md", "09-final.md"]

STOP = ["в современном мире", "давайте погрузимся", "не секрет, что", "революционный прорыв",
        "на стыке технологий", "в конечном счёте", "резюмируя вышесказанное", "стоит отметить",
        "важно понимать"]

def read(p):
    return open(p, encoding="utf-8", errors="replace").read()

def long_lines(txt):
    return [l.strip() for l in txt.splitlines() if len(l.strip()) > 60]

print("=== DoD 1: стоп-лист ===")
hits = 0
for f in SCOPE + MINE:
    t = read(os.path.join(V4, f)).lower()
    for s in STOP:
        if s in t:
            print("  НАЙДЕНО %-24s <- %s" % (f, s))
            hits += 1
print("  итог: %d вхождений" % hits)

print("\n=== DoD 2: заголовки совпадают с v3 ===")
for f in SCOPE:
    a = [l for l in read(os.path.join(V3, f)).splitlines() if l.startswith("#")]
    b = [l for l in read(os.path.join(V4, f)).splitlines() if l.startswith("#")]
    print("  %-26s %s" % (f, "OK" if a == b else "РАСХОЖДЕНИЕ v3=%d v4=%d" % (len(a), len(b))))

print("\n=== DoD 6: переписан ли текст (дословные совпадения) ===")
print("  %-26s %7s %7s %6s %8s" % ("файл", "строк>60", "дословно", "доля", "изменено"))
for f in SCOPE:
    v3l = long_lines(read(os.path.join(V3, f)))
    v4set = set(long_lines(read(os.path.join(V4, f))))
    same = sum(1 for l in v3l if l in v4set)
    pct = 100.0 * same / max(1, len(v3l))
    r = subprocess.run(["git", "-C", REPO, "diff", "--numstat", "v4-base", "--", "v4/" + f],
                       capture_output=True, text=True)
    parts = r.stdout.split()
    chg = (int(parts[0]) + int(parts[1])) if len(parts) >= 2 and parts[0].isdigit() else -1
    flag = ""
    if pct > 20:
        flag += " ДОСЛОВНО>20%"
    if chg < 0:
        flag += " нет-диффа"
    print("  %-26s %7d %7d %5.1f%% %8d%s" % (f, len(v3l), same, pct, chg, flag))

print("\n=== не назначенные разработчикам главы ===")
for f in ("03b-mlp-transformer.md", "06b-sborki.md"):
    st = os.stat(os.path.join(V4, f))
    import time
    print("  %-26s изменён в %s" % (f, time.strftime("%H:%M:%S", time.localtime(st.st_mtime))))

print("\n=== маркеры [ЗЛОБА: ===")
tot = 0
for f in SCOPE + MINE:
    n = read(os.path.join(V4, f)).count("[ЗЛОБА:")
    tot += n
    if n:
        print("  %-26s %d" % (f, n))
print("  всего: %d" % tot)
