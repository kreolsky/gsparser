import gsparser
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open("test_cases.json", "r") as f:
    cases = json.load(f)

for case in cases:
    for s_in, s_out in case['data']:
        r = gsparser.jsonify(s_in, mode=case['mode'])

        try:
            assert json.dumps(r) == json.dumps(s_out)
        except AssertionError:
            print(case['mode'], s_in)
            print(json.dumps(s_out, indent = 4))
