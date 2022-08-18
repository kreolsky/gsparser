from . import tools

# Блок парсера конфигов!
# Перевод из промежуточного формата конфигов в JSON

def parse_block(string, **params):
    """
    Используется внутри функции базовой функции config_to_json.
    Парсит блок (фрагмент исходной строки для разбора) разделенный запятыми.

    string - исходная строка для разбора.
    params - параметры парсинга. См. базоую функцию config_to_json

    Возвращает список с элементами конфига, обычно это словари.
    """

    br = params['br']
    sep_base = params['sep_base']
    sep_dict = params['sep_dict']
    to_num = params['to_num']
    raw_pattern = params['raw_pattern']
    list_marker = params['list_marker']
    is_mode_v2 = params['mode'] == 'v2'

    out = []
    out_dict = {}

    # Строка делится на фрагменты по базовому разделителю элементов
    for line in tools.split_string_by_sep(string, sep_base, **params):
        # Нужно ли вообще парсить фрагмент или вернуть как есть
        if line.startswith(raw_pattern):
            out.append(line[1:-1])

        # Проверка наличия блока. Блок всегда начинается с открывающей скобки блока
        elif line.startswith(br[0]):
            # Отрезаем скобки и парсим содержимое.
            # Внутренний блок всегда разворачиваем из лишних списков,
            # иначе лезут паразитные вложения.
            substring = config_to_json(line[1:-1], _force_unwrap=True, **params) or []
            out.append(substring)

        # Проверка на словарь
        elif sep_dict in line:
            # Когда мы пришли из словаря нужно проверить надо ли его вытаскивать из списка
            key, substring = tools.split_string_by_sep(line, sep_dict, **params)
            unwrap_it = not key.endswith(list_marker) and is_mode_v2
            key = key.strip(list_marker)

            out_dict[key] = config_to_json(substring, _force_unwrap=unwrap_it, **params)

        # Остались только строки
        else:
            out.append(tools.parse_string(line, to_num))

    if out_dict:
        out.append(out_dict)

    if len(out) == 1:
        return out[0]

    return out


def config_to_json(string, _force_unwrap=False, **params):
    """
    Парсит строку конфига и складывает результат в список словарей.
    Исходный формат крайне упрощенная и менее формальная версия JSON.
    Внутри каждого блока может быть призвольное количество подблоков выделенных
    скобками определения блока.

    Пример: '{i = 4, p = 100}, {t = 4, e = 100, n = {{m = 4, r = 100}, n = name}}'
    Пример: 'value1, value2, value3'

    ## mode = 'v1'. По умолчанию
    Все словари будут завернуты в словарь

    Строка: 'one = two, item = {сount = 4.5, price = 100, name = {name1 = name}}'
    Результат:
    [
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
    ]

    ## mode = 'v2'
    По умолчанию разворачивает все списки единичной длины кроме корневого.
    Для заворачивания необходимо указать в ключе суффикс '[]'. Суффик будет отрезан
    ВАЖНО! Опция не заворчивает другие типы данных, только для словарей!
    См. ключи one[] и name[] в примере

    Строка: 'one[] = two, item = {сount = 4.5, price = 100, name[] = {name1 = name}}'
    Результат:
    [
        {
            "one": "two",
            "item": {
                "itemsCount": 4.5,
                "price": 100,
                "name": [
                    {
                        "name1": "my_name"
                    }
                ]
            }
        }
    ]

    ## unwrap_list - нужно ли вытаскивать словари из списков единичной длины.
    False (по умолчанию) вытаскивает из списков все обьекты КРОМЕ словарей.
    True - вынимает из список ВСЕ типы обьектов, включая словари.

    Строка: 'one = two, item = {сount = 4.5, price = 100, name = {name1 = name}}'
    Результат:
    {
        "one": "two",
        "item": {
            "itemsCount": 4.5,
            "price": 100,
            "name": {
                "name1": "my_name"
            }
        }
    }

    ## Параметры:

    br - тип скобок выделяющих подблоки. '{}' по умолчанию.

    sep_base - базовый разделитель элементов. ',' по умолчанию.

    sep_dict - разделитель ключ\значение элементов словаря. '=' по умолчанию.

    sep_block - синтаксический сахар для разделения блоков. '|' по умолчанию.
    Запись:
    '0, 6| 7 = 7, zr = 0, one, tw = {2 = d}, tv = {2 = dv | 3 = tr} | a, b',
    будет идентична:
    '{0, 6}, {7 = 7, zr = 0, one, tw = {2 = d}, tv = {{2 = dv}, {3 = tr}}}, {a, b}',

    to_num - нужно ли пытаться преобразовывать значения в числа.
    True (по умолчанию) пытается преобразовать.

    raw_pattern - символ маркирующий строку которую не нужно разбирать,
    '"' (двойная кавычка) по умолчанию.
    Строки начинающиеся с символа raw_pattern не парсятся и сохраняются как есть.

    list_marker - только для mode = 'v2'.
    Суффикс пометки ключа для заворачивания содержимого в словарь.
    '[]' по умолчанию.

    is_raw - указание надо ли парсить строку или нет. False по умаолчанию.
    False (по умолчанию) - парсит строку по всем правилам, с учётом raw_pattern.
    True - не парсит, возвращает как есть.

    _force_unwrap - указатель, что пришли из внутреннего блока который
    всегда нужно разворачивать.
    """

    string = str(string)
    is_raw = params.get('is_raw', False)
    unwrap_list = params.get('unwrap_list', False)

    params['br'] = params.get('br', '{}')
    params['sep_block'] = params.get('sep_block', '|')
    params['sep_base'] = params.get('sep_base', ',')
    params['sep_dict'] = params.get('sep_dict', '=')
    params['raw_pattern'] = params.get('raw_pattern', '"')
    params['list_marker'] = params.get('list_marker', '[]')
    params['to_num'] = params.get('to_num', True)
    params['mode'] = params.get('mode', 'v1')

    if is_raw:
        return string

    out = []
    for line in tools.split_string_by_sep(string, params['sep_block'], **params):
        out.append(parse_block(line, **params))

    # Все списки длины 1 и внутри не словарь разворачиваем по умолчанию.
    # Для словарей дополнительная проверка, что не нужно разворачивать по умолчанию
    # и что пришли не из разбора словаря
    unwrap_v1 = params['mode'] == 'v1' and (type(out[0]) not in (dict, ) or _force_unwrap)
    unwrap_v2 = params['mode'] == 'v2' and (type(out[0]) not in (dict, ) or _force_unwrap)
    unwrap_it_now = unwrap_list or unwrap_v1 or unwrap_v2
    if len(out) == 1 and unwrap_it_now:
        return out[0]

    return out
