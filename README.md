# Парсер из конфига в JSON
Парсит строку конфига и складывает результат в список словарей. Исходный формат крайне упрощенная и менее формальная версия JSON. Внутри каждого блока может быть произвольное количество подблоков выделенных скобками определения блока.

Пример: ```string = '{i = 4, p = 100}, {t = 4, e = 100, n = {{m = 4, r = 100}, n = name}}'```

Пример: ```string = 'value1, value2, value3'```

Основная функция: ```jsonify(string, _unwrap_it=None, **params)```, где:

 * string - исходная строка для парсинга
 * params - параметры парсинга, в том числе режим работы.

Пример: ```config_json = gsparser.jsonify(string, mode='v2', to_num=False)```

Т.е. будет использовать парсинг версии 2 и числовые значения останутся не будут переведены в числа (останутся строками).

## Режимы работы

### mode = 'v1'. По умолчанию.
Все словари всегда будут завернуты в список!

Строка: ```'one = two, item = {count = 4.5, price = 100, name = {name1 = name}}'```

Результат:
```
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
```
### mode = 'v2'
Разворачивает все списки единичной длины. Для заворачивания необходимо указать в ключе команду 'list'.

Сама команда (все что после указателя команды) в итоговом JSON будет отрезано. См. символ sep_func

Строка: ```'one!list = two, item = {сount = 4.5, price = 100, name!list = {n = m, l = o}}'```

Результат:
```
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
```

#### Команды в режиме v2

 * list - заворачивает содержимое в список только если это не список
 * flist - всегда заворачивает в дополнительный список, даже списки!

## Параметры парсинга:

### _unwrap_it
**ВАЖНО!** Служебный параметр, указание нужно ли разворачивать получившуюся после парсинга структуру. Определяется автоматически.

### always_unwrap
Нужно ли вытаскивать словари из списков единичной длины.

False (по умолчанию) - вытаскивает из списков все обьекты КРОМЕ словарей.

True - вынимает из список ВСЕ типы объектов, включая словари. **ВАЖНО!** Настройка игнорирует команды mode = v2, если список можно развернуть, то он обязательно будет развернут!

Строка: ```'one!list = two, item = {count = 4.5, price = 100, name!list = {name1 = name}}'```

Результат:
```
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
```
### br_block
Тип скобок выделяющих подблоки. '{}' по умолчанию.

### br_list
Тип скобок выделяющих списки. '[]' по умолчанию.

**ВАЖНО!** Нельзя переопределять значение по умолчанию!

Внутри допустима любая вложенность, но исключительно в синтаксисе python.

Нельзя одновременно использовать упрощенный синтаксис и квадратные скобки! Строки обязательно обрамлены кавычками, словари с полным соблюдением синтаксиса!

Строка: ```['one', ['two', 3, 4], {'one': 'the choose one!'}]```

Результат:
```
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
```
Аналогичного результата можно достигнуть и классическим, упрощенным синтаксисом. Строка ```{one, {two, 3, 4}, {one = the choose one!}}``` дасть идентичный верхнему результат. Может пригодиться для задания, например, пустых списков или простых конструкций.

### sep_base
Базовый разделитель элементов. ',' - по умолчанию.

### sep_dict
Разделитель ключ-значение элементов словаря. '=' - по умолчанию.

### sep_block
Синтаксический сахар для разделения блоков. '|' - по умолчанию.

Запись: ```'0, 6| 7 = 7, zr = 0, one, tw = {2 = d}, tv = {2 = dv | 3 = tr} | a, b'```,

будет идентична: ```'{0, 6}, {7 = 7, zr = 0, one, tw = {2 = d}, tv = {{2 = dv}, {3 = tr}}}, {a, b}'```,

### sep_func
Разделитель указания функций. '!' - по умолчанию.

Например: key!list означает, что содержимое ключа key обязательно будет списком.

См. все актуальные доступные команды в функции parse_command()

### to_num
Нужно ли пытаться преобразовывать значения в числа.

True (по умолчанию) - пытается преобразовать.

False - не преобразовывать. **ВАЖНО!** Также отключает обработку br_list

### raw_pattern
Символ маркирующий строку которую не нужно разбирать.

'"' (двойная кавычка) - по умолчанию.

Строки начинающиеся с символа raw_pattern не парсятся и сохраняются как есть.

### is_raw
Указание надо ли парсить строку или нет. False по умолчанию.

False (по умолчанию) - парсит строку по всем правилам, с учётом raw_pattern.

True - не парсит, возвращает как есть.
