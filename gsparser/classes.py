from . import tools

class CommandParser:
    def __init__(self):
        self.key_commands = {
            'dummy': lambda x: x,
            'list': lambda x: [x] if type(x) not in (list, tuple,) else x,
            'flist': lambda x: [x],
        }

    def parse_command(self, command, result):
        return self.key_commands[command](result)

class BlockParser:
    def __init__(self, params):
        self.command_parser = CommandParser()
        self.params = params

    def parse_raw(self, line):
        return line[1:-1]

    def parse_nested_block(self, line, converter):
        return converter.jsonify(line[1:-1], _unwrap_it=True)

    def parse_dict(self, line, out_dict, converter):
        unwrap_it = self.params.get('mode') == 'v2'
        command = 'dummy'

        key, substring = tools.split_string_by_sep(line, self.params['sep_dict'], **self.params)
        result = converter.jsonify(substring, _unwrap_it=unwrap_it)

        if unwrap_it and self.params['sep_func'] in key:
            key, command = key.split(self.params['sep_func'])
        out_dict[key] = self.command_parser.parse_command(command, result)

    def parse_string(self, line):
        return tools.parse_string(line, self.params['to_num'])

    def parse_block(self, string, converter):
        out = []
        out_dict = {}

        condition_mapping = {
            lambda line: line.startswith(self.params['raw_pattern']): self.parse_raw,
            lambda line: line.startswith(self.params['br_block'][0]): lambda x: self.parse_nested_block(x, converter),
            lambda line: self.params['sep_dict'] in line: lambda x: self.parse_dict(x, out_dict, converter),
        }

        for line in tools.split_string_by_sep(string, self.params['sep_base'], **self.params):
            for condition, action in condition_mapping.items():
                if condition(line):
                    result = action(line)
                    if result is not None:
                        out.append(result)
                    break
            else:
                out.append(self.parse_string(line))

        if out_dict:
            out.append(out_dict)

        return out[0] if len(out) == 1 else out

class ConfigJSONConverter:
    def __init__(self, params=None):
        self.default_params = {
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
        self.params = {**self.default_params, **(params or {})}
        self.block_parser = BlockParser(self.params)

    def jsonify(self, string: str, is_raw: bool = False, _unwrap_it = None) -> dict:
        if is_raw:
            return string

        string = str(string)

        if _unwrap_it is None:
            _unwrap_it = {'v1': True, 'v2': True}[self.params['mode']]

        out = []
        for line in tools.split_string_by_sep(string, self.params['sep_block'], **self.params):
            out.append(self.block_parser.parse_block(line, self))

        unwrap_v1 = self.params['mode'] == 'v1' and (type(out[0]) not in (dict, ) or _unwrap_it)
        unwrap_v2 = self.params['mode'] == 'v2' and _unwrap_it
        if len(out) == 1 and (self.params['always_unwrap'] or unwrap_v1 or unwrap_v2):
            return out[0]

        if isinstance(out, list) and out[0] == '':
            return []

        return out
