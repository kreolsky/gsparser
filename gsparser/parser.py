from . import tools

# Блок парсера конфигов!
# Перевод из промежуточного формата конфигов в JSON

def cmd_list(result):
    if type(result) not in (list, tuple, ):
        return [result]
    return result

def cmd_flist(result):
    return [result]

key_commands = {
    'list': cmd_list,
    'flist': cmd_flist,
}

def parse_command(command, result):
    """
    Парсер команд, которые будут применены к содержимому ключа.
    В данный момент поддерживает команды:
    'list' - заворачить содержимое в список если это не список
    'flist' - всегда заворачивает в список, даже списки!
    """

    if not command:
        return result

    return key_commands[command](result)

def parse_block(string, **params):
    """
    Используется внутри функции базовой функции config_to_json.
    Парсит блок (фрагмент исходной строки для разбора) разделенный запятыми.

    string - исходная строка для разбора.
    params - параметры парсинга. См. базоую функцию config_to_json

    Возвращает список с элементами конфига, обычно это словари.
    """

    is_mode_v2 = params['mode'] == 'v2'
    out = []
    out_dict = {}

    # Строка делится на фрагменты по базовому разделителю элементов
    for line in tools.split_string_by_sep(string, params['sep_base'], **params):
        # Нужно ли вообще парсить фрагмент или вернуть как есть
        if line.startswith(params['raw_pattern']):
            out.append(line[1:-1])

        # Проверка наличия блока. Всегда начинается с открывающей скобки блока
        elif line.startswith(params['br_block'][0]):
            # Отрезаем скобки и парсим содержимое
            # Внутренний блок всегда разворачиваем из списков, иначе паразитные вложения
            substring = config_to_json(line[1:-1], _unwrap_it=True, **params)
            out.append(substring)

        # Проверка на словарь
        elif params['sep_dict'] in line:
            # Когда мы пришли из словаря нужно проверить надо ли его вытаскивать из списка
            # v1. Всегда False. Никогда НЕ разворачиваем. Команды не поддерживает
            # v2. Всегда True. Разворачиваем и применяем действие переданной команды
            unwrap_it = True if is_mode_v2 else False
            command = None

            key, substring = tools.split_string_by_sep(line, params['sep_dict'], **params)
            if is_mode_v2 and params['sep_func'] in key:
                key, command = key.split(params['sep_func'])

            result = config_to_json(substring, _unwrap_it=unwrap_it, **params)
            out_dict[key] = parse_command(command, result)

        # Остались только строки
        else:
            out.append(tools.parse_string(line, params['to_num']))

    if out_dict:
        out.append(out_dict)

    if len(out) == 1:
        return out[0]

    return out


def config_to_json(string: str, _unwrap_it=None, **params) -> dict:
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
    always_unwrap = params.get('always_unwrap', False)

    # Только при первом запуске
    if _unwrap_it is None:
        # Настройка разворачивания самого верхнего уровня
        init_unwrap = {'v1': True, 'v2': True }
        _unwrap_it = init_unwrap[params['mode']]

        params['br_list'] = '[]'  # Нельзя переопределять формат скобок питонячих списков!
        params['br_block'] = params.get('br_block', '{}')
        params['sep_func'] = params.get('sep_func', '!')
        params['sep_block'] = params.get('sep_block', '|')
        params['sep_base'] = params.get('sep_base', ',')
        params['sep_dict'] = params.get('sep_dict', '=')
        params['raw_pattern'] = params.get('raw_pattern', '"')
        params['to_num'] = params.get('to_num', True)
        params['mode'] = params.get('mode', 'v1')

    out = []
    for line in tools.split_string_by_sep(string, params['sep_block'], **params):
        out.append(parse_block(line, **params))

    """
    Проверяем, что нужно разворачивать, а что нет в зависимости от того, какие
    элементы структуры разбираем. Значения внутри словарей зависит от режима и версии

    v1. Всё, кроме словарей, разворачиваем по умолчанию
    v2. Всегда разворачиваем. Дополнительные действия зависят от команды в ключе
    См. parse_block() для деталей
    """
    unwrap_v1 = params['mode'] == 'v1' and (type(out[0]) not in (dict, ) or _unwrap_it)
    unwrap_v2 = params['mode'] == 'v2'
    if len(out) == 1 and (always_unwrap or unwrap_v1 or unwrap_v2):
        return out[0]

    """
    КОСТЫЛЬ!
    Последствия того, что перед парсингом в gsconfig всё заворачивается
    в скобки блока и на выход попадают массивы с пустой строкой - [""]
    """
    if type(out) is list and out[0] == '':
        return []

    return out
