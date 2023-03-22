import ast

# Блок парсера конфигов!
# Перевод из промежуточного формата конфигов в JSON

def define_split_points(string, sep, **params):
    """
    Define the positions of all separator characters in the string.
    Ignores separators inside blocks enclosed by brackets.

    Args:
        string (str): The original string to be parsed.
        sep (str): The separator. Example: sep = '|'
        params (dict): Additional parameters, including:
            - br_block (str): Brackets for highlighting sub-blocks. Example: br_block = '{}'
            - br_list (str): Brackets for highlighting lists. Example: br_list = '[]'
            - raw_pattern (str): Raw pattern to avoid parsing. Example: raw_pattern = '!'

    Yields:
        int: Indices of separator characters.
    """

    br_block = params.get('br_block')
    br_list = params.get('br_list')
    raw_pattern = params.get('raw_pattern')

    # Brackets are grouped by types.
    # All opening brackets increase the counter, closing brackets decrease it
    br = {
        br_block[0]: 1,
        br_block[1]: -1,
        br_list[0]: 1,
        br_list[1]: -1
    }

    is_not_raw_block = True
    count = 0

    for i, letter in enumerate(string):
        if letter == raw_pattern:
            is_not_raw_block = not is_not_raw_block

        elif (delta := br.get(letter)) is not None:
            count += delta

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

    string_mapping = {
        'none': None,
        'nan': None,
        'null': None,
        'true': True,
        'false': False
    }

    if s.lower() in string_mapping:
        return string_mapping[s.lower()]

    if not to_num:
        return s

    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s
