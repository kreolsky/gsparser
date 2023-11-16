from gsparser import ConfigJSONConverter
import gsparser
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("test_cases.json", "r") as f:
    cases = json.load(f)

for case in cases:
    for s_in, s_out in case['data']:
        # Обычная версия
        # r = gsparser.jsonify(s_in, mode=case['mode'])
        
        # Версия на классах
        converter = gsparser.ConfigJSONConverter({'mode': case['mode']})
        r = converter.jsonify(s_in)

        try:
            assert json.dumps(r) == json.dumps(s_out)
        except AssertionError:
            print(case['mode'], s_in)
            print(json.dumps(s_out, indent = 4))
    else:
        print(f'{case["mode"]}. Больше ничего нет? Значит все норм!')
