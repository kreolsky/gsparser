import ast

# Блок парсера конфигов!
# Перевод из промежуточного формата конфигов в JSON

def define_split_points(string, sep, **params):
    """
    Отпределение позиции всех разделяющих строку символов.
    Игнорирует разделители внутри блоков выделенных скобками br.

    string - исходная строка для разбора
    sep - разделитель. Пример: sep = '|'
    br_block - тип скобок выделяющих подблоки. Пример: br_block = '{}'

    Генератор. Возвращает индексы разделяющих символов.
    """

    br_block = params['br_block']
    br_list = params['br_list']
    raw_pattern = params['raw_pattern']

    # Скобки сгруппированы по типам.
    # Все открывающие увеличивают счетчик, закрывающие - уменьшают
    br = {
        f'{br_block[0]}{br_list[0]}': 1,
        f'{br_block[-1]}{br_list[-1]}': -1
    }

    is_not_raw_block = True
    count = 0

    for i, letter in enumerate(string):
        if letter is raw_pattern:
            is_not_raw_block = not is_not_raw_block

        # Если символ в ключах, то проверяем где именно и изменяем счетчик
        elif letter in ''.join(br.keys()):
                count += [br[x] for x in br.keys() if letter in x][0]

        elif letter == sep and count == 0 and is_not_raw_block:
            yield i

    yield len(string)

def split_string_by_sep(string, sep, **params):
    """
    Разделение строки на массив подстрок по символу разделителю.
    Не разделяет блоки выделенные скобками.

    string - исходная строка для разбора
    sep - разделитель. Пример: sep = '|'
    br - тип скобок выделяющих подблоки. Пример: br = '{}'

    Генератор. Возвращает подстроки.
    """

    prev = 0
    for i in define_split_points(string, sep, **params):
        yield string[prev:i].strip(sep).strip()
        prev = i

def parse_string(s, to_num=True):
    """
    Пытается перевести строку в число, предварительно определив что это было, int или float
    Переводит true\false в "правильный" формат для JSON
    """

    if s.lower() in ('none', 'nan', 'null'):
        return None

    if s.lower() in ('true', 'false'):
        return s.capitalize()

    if not to_num:
        return s

    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s
