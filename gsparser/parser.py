from . import tools

# Блок парсера конфигов!
# Перевод из промежуточного формата конфигов в JSON

def parse_command(command, result):
    """
    Парсер команд, которые будут применены к содержимому ключа.
    В данный момент поддерживает команды:
    'list' - заворачить содержимое в список если это не список
    'flist' - всегда заворачивает в список, даже списки!
    """

    key_commands = {
        'dummy': lambda x: x,
        'list': lambda x: [x] if type(x) not in (list, tuple, ) else x,
        'flist': lambda x: [x],
    }

    return key_commands[command](result)

def parse_block(string, **params):
    """
    Used inside the base function jsonify.
    Parses a block (a fragment of the original string to be parsed) separated by commas.

    Args:
        string (str): The original string to be parsed.
        params (dict): Parsing parameters. See base function jsonify.

    Returns:
        list: A list of config elements, usually dictionaries.
    """

    def parse_raw(line):
        return line[1:-1]

    def parse_nested_block(line):
        return jsonify(line[1:-1], _unwrap_it=True, **params)

    def parse_dict(line):
        # For v1, always wrap dictionaries from the list
        # For v2, unwrap, then depends on the command in the key
        unwrap_it = params.get('mode') == 'v2'
        command = 'dummy'

        key, substring = tools.split_string_by_sep(line, params['sep_dict'], **params)
        result = jsonify(substring, _unwrap_it=unwrap_it, **params)

        if unwrap_it and params['sep_func'] in key:
            key, command = key.split(params['sep_func'])
        out_dict[key] = parse_command(command, result)

    def parse_string(line):
        return tools.parse_string(line, params['to_num'])

    out = []
    out_dict = {}

    # Define a mapping of conditions to corresponding parsing functions
    condition_mapping = {
        lambda line: line.startswith(params['raw_pattern']): parse_raw,
        lambda line: line.startswith(params['br_block'][0]): parse_nested_block,
        lambda line: params['sep_dict'] in line: parse_dict
    }

    # Split the string into fragments by the base separator
    for line in tools.split_string_by_sep(string, params['sep_base'], **params):
        # Iterate through conditions and execute the corresponding function if the condition is True
        for condition, action in condition_mapping.items():
            if condition(line):
                result = action(line)
                if result is not None:
                    out.append(result)
                break
        else:
            out.append(parse_string(line))

    if out_dict:
        out.append(out_dict)

    return out[0] if len(out) == 1 else out

def jsonify(string: str, _unwrap_it=None, **params) -> dict:
    """
    ## Парсер из конфига в JSON
    Парсит строку конфига и складывает результат в список словарей.
    Исходный формат крайне упрощенная и менее формальная версия JSON.
    Внутри каждого блока может быть призвольное количество подблоков выделенных
    скобками определения блока.

    Пример: '{i = 4, p = 100}, {t = 4, e = 100, n = {{m = 4, r = 100}, n = name}}'
    Пример: 'value1, value2, value3'

    ## Режимы работы

    ### mode = 'v1'. По умолчанию.
    Все словари всегда будут завернуты в список!

    Строка: 'one = two, item = {count = 4.5, price = 100, name = {name1 = name}}'
    Результат:
    {
        "one": "two",
        "item": [
            {
                "itemsCount": 4.5,
                "price": 100,
                "name": [
                    {
                        "name1": "my_name"
                    }
                ]
            }
        ]
    }

    ### mode = 'v2'
    Разворачивает все списки единичной длины.
    Для заворачивания необходимо указать в ключе команду 'list'.
    Сама команда (все что после указателя команды) в итоговом JSON будет отрезано.
    см. sep_func указатель

    Строка: 'one!list = two, item = {сount = 4.5, price = 100, name!list = {n = m, l = o}}'

    Результат:
    {
        "one": [
            "two"
        ],
        "item": {
            "count": 4.5,
            "price": 100,
            "name": [
                {
                    "n": "m",
                    "l": "o"
                }
            ]
        }
    }

    ## Параметры:

    ### always_unwrap
    Нужно ли вытаскивать словари из списков единичной длины.
    False (по умолчанию) вытаскивает из списков все обьекты КРОМЕ словарей.
    True - вынимает из список ВСЕ типы обьектов, включая словари.
    ВАЖНО! Игнорирует команды mode = v2, если список можно развернуть, он будет развернут!

    Строка: 'one!list = two, item = {count = 4.5, price = 100, name!list = {name1 = name}}'

    Результат:
    {
        "one": "two",
        "item": {
            "count": 4.5,
            "price": 100,
            "name": {
                "name1": "my_name"
            }
        }
    }

    ### br_block
    Тип скобок выделяющих подблоки. '{}' по умолчанию.

    ### br_list
    Тип скобок выделяющих списки. '[]' по умолчанию.

    ВАЖНО! Нельзя переопределять значение по умолчанию!
    Внутри допустима любая вложенность, но исключительно в синтаксисе питона.
    Недопустимо использовать одновременно упрощенный синтаксис и квадратные скобки.
    Строки обязательно обрамлены кавычками. Словари с полным соблюдением синтаксиса.

    Строка: ['one', ['two', 3, 4], {'one': 'the choose one!'}]

    Результат:
    [
        "one",
        [
            "two",
            3,
            4
        ],
        {
            "one": "the choose one!"
        }
    ]

    Аналогичного результата можно достигнуть и классическим, упрощенным синтаксисом
    Строка {one, {two, 3, 4}, {one = the choose one!}} дасть идентичный верхнему результат.
    Может пригодиться для задания, например, пустых списков или простых конструкций.

    ### sep_base
    Базовый разделитель элементов. ',' по умолчанию.

    ### sep_dict
    Разделитель ключ-значение элементов словаря. '=' по умолчанию.

    ### sep_block
    Синтаксический сахар для разделения блоков. '|' по умолчанию.
    Запись:
    '0, 6| 7 = 7, zr = 0, one, tw = {2 = d}, tv = {2 = dv | 3 = tr} | a, b',
    будет идентична:
    '{0, 6}, {7 = 7, zr = 0, one, tw = {2 = d}, tv = {{2 = dv}, {3 = tr}}}, {a, b}',

    ### sep_func
    Разделитель указания функций. '!' по умолчанию.
    Например: key!list означает, что содержимое ключа key обязательно будет списком.

    См. все доступные команды в parse_command()

    ### to_num
    Нужно ли пытаться преобразовывать значения в числа.
    True (по умолчанию) - пытается преобразовать.

    ### raw_pattern
    Символ маркирующий строку которую не нужно разбирать,
    '"' (двойная кавычка) по умолчанию.
    Строки начинающиеся с символа raw_pattern не парсятся и сохраняются как есть.

    ### is_raw
    Указание надо ли парсить строку или нет. False по умолчанию.
    False (по умолчанию) - парсит строку по всем правилам, с учётом raw_pattern.
    True - не парсит, возвращает как есть.

    ### _unwrap_it
    Указание нужно ли разворачивать получившуюся после парсинга структуру.
    """

    # Выйти сразу если не нужно парсить
    if params.get('is_raw', False):
        return string

    string = str(string)

    # Только при первом запуске. Заполняеет параметры значениями по умолчанию
    if _unwrap_it is None:
        default_params = {
            'br_list': '[]',
            'br_block': '{}',
            'sep_func': '!',
            'sep_block': '|',
            'sep_base': ',',
            'sep_dict': '=',
            'raw_pattern': '"',
            'to_num': True,
            'always_unwrap': False,
            'mode': 'v1',
        }
        params = {**default_params, **params}
        _unwrap_it = {'v1': True, 'v2': True}[params['mode']]

    out = []
    for line in tools.split_string_by_sep(string, params['sep_block'], **params):
        out.append(parse_block(line, **params))

    """
    Проверяем что нужно разворачивать, а что нет в зависимости от того, какие
    элементы структуры разбираем. Значения внутри словарей зависит от режима и версии

    v1. Всё, кроме словарей, разворачиваем по умолчанию
    v2. Всегда разворачиваем. Дополнительные действия зависят от команды в ключе
    См. parse_block() для деталей
    """
    unwrap_v1 = params['mode'] == 'v1' and (type(out[0]) not in (dict, ) or _unwrap_it)
    unwrap_v2 = params['mode'] == 'v2' and _unwrap_it
    if len(out) == 1 and (params['always_unwrap'] or unwrap_v1 or unwrap_v2):
        return out[0]

    """
    КОСТЫЛЬ! Последствия того, что перед парсингом в gsconfig всё заворачивается
    в скобки блока и на выход попадают массивы с пустой строкой - [""]
    """
    if isinstance(out, list) and out[0] == '':
        return []

    return out
