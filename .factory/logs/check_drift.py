"""Проверка дрифта канона против речи.

Ось 1: термины, которые ментальная модель считает названными словами в тексте.
Если модель говорит «это лейтмотив, названный словами», а в речи термина нет —
карта богаче текста, и это надо решать, а не носить в карте.

Ось 2: служебные шапки глав — печатаются строки, где встречаются слова из списка
изменённых смыслов. Их читают глазами: заголовок или шапка не должны утверждать
то, что модель уже переформулировала.

Ничего не пишет на диск, только печатает. Числа — не приёмка, а адрес для чтения.
"""
import sys
import os

V4 = 'v5'

def _chap(name):
    """Глава живёт в одной из частей: ищем по подпапкам, иначе корень v5."""
    import glob as _g
    hits = _g.glob(os.path.join(V4, "*", name))
    return hits[0] if hits else os.path.join(V4, name)

CHAPTERS = ['00-intro', '02-teoriya', '03a-emerdzhentnost', '03b-mlp-transformer',
            '03c-dva-rezhima', '04-stena', '05-rd', '06-koding', '06b-sborki',
            '07-fabrika', '07b-lokalny-zapusk', '08-vendorstvo', '09-final']

# Термины и формулы, которые модель объявляет названными в речи.
# Стебли, не полные фразы: «исчезающ» ловит и «исчезающий градиент», и
# «исчезающего градиента»; иначе проверка врёт на словоформах.
TERMS = [
    ('градиент декларативности', 'градиент декларативн'),
    ('декларативность', 'декларативн'),
    ('императивность', 'императивн'),
    ('эмерджентность', 'эмерджентн'),
    ('один вес — один голос', 'один вес — один голос'),
    ('исчезающий градиент', 'исчезающ'),
    ('Grounding Problem', 'grounding problem'),
    ('residual', 'residual'),
    ('бюджет ошибок (FAIL)', 'бюджет'),
    ('приёмка как договор', 'приёмка — не галочка'),
    ('контекстное окно', 'контекстн'),
    ('латентное пространство', 'латентн'),
    ('байесовский фильтр', 'байесовск'),
    ('бесплатный обед', 'бесплатн'),
]

# Слова, по которым ищем служебные строки про изменённые смыслы.
WATCH = ['тыкв', 'синтаксис', 'трансформер', 'режим', 'стен', 'предел', 'язык',
         'планк', 'интеллект', 'обещани', 'пять слов', 'лестниц', 'декларатив']

speech = {}
for name in CHAPTERS:
    t = open(_chap(f'{name}.md'), encoding='utf-8').read()
    body = t.split('\n---', 1)[-1] if '\n---' in t else t
    speech[name] = body.lower().replace('ё', 'е')

whole = ' '.join(speech.values())

print('ось 1. термины, которые модель считает названными')
absent = []
for label, stem in TERMS:
    hits = [ch for ch, body in speech.items() if stem.lower().replace('ё', 'е') in body]
    mark = 'есть' if hits else 'НЕТ В РЕЧИ'
    where = ', '.join(c.split('-')[0] for c in hits[:4])
    print(f'   {mark:11} {label:28} {where}')
    if not hits:
        absent.append(label)

print()
print('ось 2. служебные шапки про изменённые смыслы')
for name in CHAPTERS:
    lines = open(_chap(f'{name}.md'), encoding='utf-8').read().split('\n---')[0].splitlines()
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if any(w in low for w in WATCH) and len(line.strip()) > 40 and not line.startswith('#'):
            print(f'   {name}:{i} {line.strip()[:170]}')
