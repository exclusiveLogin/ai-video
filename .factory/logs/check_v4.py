import os, glob, json, subprocess, time

V4 = r"C:\Users\Fox\OneDrive\Рабочий стол\AI\text\v4"
print("=== v4 файлы ===")
for f in sorted(glob.glob(os.path.join(V4, "*.md"))):
    st = os.stat(f)
    print("%-26s %7d  %s" % (os.path.basename(f), st.st_size, time.strftime("%H:%M:%S", time.localtime(st.st_mtime))))

HANDLES = {
    "dev-1": "term_dc3bcd5b-42e3-4387-ae35-4b0cd53607e0",
    "dev-2": "term_2d80bc9f-2458-44e2-b763-abdd696b0a0b",
    "dev-3": "term_47369ea2-6536-4362-91cc-f2a8140b31ff",
}
for name, h in HANDLES.items():
    try:
        raw = subprocess.run(["orca", "terminal", "read", "--terminal", h, "--json"],
                             capture_output=True, text=True, timeout=30).stdout
        t = json.loads(raw)["result"]["terminal"]
        print("\n=== %s (%s) status=%s ===" % (name, h[-8:], t.get("status")))
        for l in [x for x in t.get("tail", []) if x.strip()][-10:]:
            print("   ", l[:150])
    except Exception as e:
        print("\n=== %s: ошибка чтения: %s" % (name, e))
