# -*- coding: utf-8 -*-
"""Точечная правка v4/06-koding.md: лестница и шов, живые абзацы не переписываются."""
from pathlib import Path

path = Path("v4/06-koding.md")
raw = path.read_bytes()
text = raw.decode("utf-8")
idx = text.find("---")
if idx < 0:
    raise SystemExit("no dash")
prefix = text[: idx + 3]
rest = text[idx + 3 :]
if not rest.startswith("\r\n\r\n"):
    raise SystemExit("unexpected separator after dash: " + repr(rest[:20]))
parts = rest.split("\r\n\r\n")
if parts[0] != "":
    raise SystemExit("expected empty head piece")
paras = parts[1:]
if paras[-1].endswith("\r\n"):
    paras[-1] = paras[-1][:-2]
    trailing = "\r\n"
else:
    trailing = ""

old_iface = "Форма интерфейса всегда продиктована физикой процесса."
new_iface = "Форма интерфейса продиктована физикой процесса."
if paras[4].count(old_iface) != 1:
    raise SystemExit("iface sentence missing")
paras[4] = paras[4].replace(old_iface, new_iface, 1)

old_arch = "Архитектура неотделима от языка"
if not paras[5].startswith(old_arch):
    raise SystemExit("arch paragraph moved")
paras[5] = (
    "Идея спускается по уровням, пока не станет поведением, которое можно принять. "
    + paras[5]
)

old_cheap = "сам набор текста на языке программирования всегда был дешёвым ремеслом"
new_cheap = "сам набор текста на языке программирования был дешёвым ремеслом"
if paras[15].count(old_cheap) != 1:
    raise SystemExit("cheap sentence missing")
paras[15] = paras[15].replace(old_cheap, new_cheap, 1)

crystal = (
    "Именно промежуточный человеческий язык держал эту лестницу. "
    "Он стоял там, чтобы замысел кристаллизовался во что-то исполнимое: "
    "пока идея размазана по словам, её нельзя ни проверить, ни передать, "
    "и код был кристаллом — точкой, где поведение становилось детерминированным. "
    "Теперь буквы кристаллом быть перестали, а кристалл переехал туда, где мы принимаем результат, "
    "и кристаллом стала приёмка. "
    "Отсюда две новости, и обе неверные — что код больше не важен и что без своего кода всё посыпется. "
    "Верно другое: буквы перестали быть точкой, где идея застывает, "
    "и этой точкой стало то, как вы решаете, что результат годен."
)

rice = paras[13]
needle = "Это Райс, пятьдесят третий год."
if not rice.endswith(needle):
    raise SystemExit("rice ending changed: " + rice[-80:])
rice = (
    rice
    + " Лестница замыкается здесь, потому что поведение по тексту не поручишь: "
    "держаться она будет на том уровне, который нельзя отдать машине."
)

who = paras[11]
linguist = paras[12]
if "лингвист" not in linguist:
    raise SystemExit("linguist paragraph missing")
linguist = (
    linguist
    + " Тыквой к следующему году станет не опыт. "
    "Тыквой станет каталог методов, библиотек и того, куда ставить скобку."
)

daily = (
    "И отдельный проход для того, кто каждый день тащит фичи, а не выбирает барбершоп или авиакомпанию. "
    "Со стола уходит шаблон и черновик по задаче, которую уже решили, "
    "уходит чтение чужого файла только чтобы понять, как это устроено, "
    "и уходит тест, собранный по уже готовой спецификации: "
    "это машина делает быстрее и не устаёт. "
    "На столе остаётся граница между узлами, приёмка и то, чего в тикете нет, — "
    "что именно вы решили не делать."
)

# 0..10 живые, затем шов, Райс, панч, будний проход, дальше прежний хвост без старого Райса.
new_paras = paras[0:11] + [crystal, rice, who, linguist, daily, paras[14], paras[15]] + paras[16:]
out = prefix + "\r\n\r\n" + "\r\n\r\n".join(new_paras) + trailing
if "\n---\n" in out.replace("\r\n", "\n"):
    pass
path.write_bytes(out.encode("utf-8"))
print("bytes", len(raw), "->", len(out.encode("utf-8")))
print("paras", len(paras), "->", len(new_paras))
print("header_same", out[: idx + 3] == text[: idx + 3])
