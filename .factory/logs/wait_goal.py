"""Ждёт, пока артефакт прогона появится и допишется, и только потом выходит.

Зачем: прогон Pi идёт в отдельном окне и о финише не сообщает. Запускать так:

    python .factory/logs/wait_goal.py <каталог> <подстрока имени> [секунд стабильности]

в фоне с notify_on_complete — тогда Hermes получает сигнал ровно в тот момент, когда
отчёт готов, а не когда кто-то вспомнил его проверить.

Выход: 0 — файл готов (путь и размер в stdout) · 1 — не дождались за отведённое время.
"""
import os, sys, time

DEFAULT_TIMEOUT = 45 * 60      # сколько всего ждать
POLL = 10                      # как часто смотреть
STABLE_DEFAULT = 25            # сколько секунд размер должен не меняться

def main():
    if len(sys.argv) < 3:
        print("нужно: <каталог> <подстрока имени> [секунд стабильности]")
        return 2
    folder, needle = sys.argv[1], sys.argv[2]
    stable_need = int(sys.argv[3]) if len(sys.argv) > 3 else STABLE_DEFAULT
    started = time.time()
    seen = None            # (путь, размер, время последнего изменения)
    while time.time() - started < DEFAULT_TIMEOUT:
        cands = []
        if os.path.isdir(folder):
            for name in os.listdir(folder):
                if needle in name:
                    p = os.path.join(folder, name)
                    try:
                        cands.append((os.path.getmtime(p), p))
                    except OSError:
                        pass
        if cands:
            cands.sort()
            path = cands[-1][1]
            try:
                size = os.path.getsize(path)
            except OSError:
                time.sleep(POLL)
                continue
            if seen and seen[0] == path and seen[1] == size:
                if time.time() - seen[2] >= stable_need:
                    print("ГОТОВ: %s (%d байт)" % (path, size))
                    return 0
            else:
                seen = (path, size, time.time())
        time.sleep(POLL)
    print("НЕ ДОЖДАЛИСЬ за %d мин: %s/%s*" % (DEFAULT_TIMEOUT // 60, folder, needle))
    return 1

if __name__ == "__main__":
    sys.exit(main())
