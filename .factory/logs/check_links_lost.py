import subprocess, glob, os

files = [p.replace(os.sep, '/') for p in sorted(glob.glob('v5/*/0*.md'))]
print(f"{'файл':28} {'метки было→стало':>18} {'ссылки было→стало':>18}")
bad = []
for f in files:
    r = subprocess.run(['git', 'show', 'HEAD:' + f], capture_output=True)
    if r.returncode != 0:
        # файл новый (ещё не в HEAD) — сравниваем с предшественником в v4
        alt = 'HEAD:v4/' + os.path.basename(f)
        r = subprocess.run(['git', 'show', alt], capture_output=True)
        if r.returncode != 0:
            print(f"{os.path.basename(f):28} новый файл, сравнивать не с чем")
            continue
    old = r.stdout.decode('utf-8', errors='replace')
    new = open(f, encoding='utf-8').read()
    m0, m1 = old.count('[КАРТА'), new.count('[КАРТА')
    l0, l1 = old.count('http'), new.count('http')
    flag = '' if (m1 >= m0 and l1 >= l0) else '   <- ПОТЕРЯ'
    print(f"{os.path.basename(f):28} {m0:>7}->{m1:<9} {l0:>7}->{l1:<9}{flag}")
    if m1 < m0 or l1 < l0:
        bad.append((os.path.basename(f), m0 - m1, l0 - l1))
print()
print('потери (файл, меток, ссылок):', bad if bad else 'нет')
