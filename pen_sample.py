import json
import gsparser

string = [
    # '{life = {}}',
    # '0, 6| 7 = 7, zr = 0, one, tw = {2 = d}, tv = {2 = dv | 3 = tr} | a, b',
    # 'one[] = two, item = {itemsCount = 4.5, price = 100.123456, name[] = {name1 = my_name}}'
    'one[] = two, item = {itemsCount = 4.5, price = 100.123456, name = {name1 = my_name, second = other}}, six[] = {name3 = my_thirs_name, second = other}, test = {itemsCount = 4, price = 100, name[] = {{itemsCount = 4, price = 100}, name[] = {count = 4, total = 10}}}, count = 4, total = 10',
    # '9.1, 6.0, 6| 7 = 7, zero = 0, one, two = {2 = dva}, tree = {2 = dva | 3 = tree} | a, b, f',
    # '{9.1, 6.0, 6}, {7 = 7, zero = 0, one, two = {2 = dva}, tree = {{2 = dva}, {3 = tree}}}, {a, b, f}',
    # 'five = {three = 3, two = 2}',
    # 'life',
    # '{life = {TRUE}}',
    # '8',
    # 9999,
    # '8 = 8',
    # '20:00',
    # 'connection = {hostname = my.server.host, port = 22, username = user}, command = {stop = sfs2x-service stop, start = sfs2x-service start}, path = /opt/SFS_dev/SFS2X/, health_status_url = https://my.server.host:8444/healthcheck/get',
    # 'allow = {124588016, -283746251}, superuser = {124588016, 211631602, 106874883, 231976253}',
    # 'name = {{itemsCount = 4, price = 100}, name = {count = 4, total = FALSE}}',
    # 'id = act00040, trigger = {and = {eq = {08.04.2019, now} | more = {50, hands} | or = {more = {10, consecutiveDays} | more = {100, gold}}}} | id = act00050, trigger = {and = {more = {50, hands}}}',
    # 'id = act00040, trigger = {and = {eq = {now = 10.04.2019} | more = {hands = 50} | or = {more = {consecutiveDays = 50} | more = {gold = 100}}}} | id = act00050, trigger = {and = {more = {hands = 50}}}',
    # 'a = nan',
    # 'popup_icon = {left = -1, top = -28}, widget_icon = {{pen, 0, 0, 0}, {sample, 8, 8, 8}, top = 10}, mobile_banner = {title_position = {left = "0x90532022", "oppa", "work!", right = 10, top = 11}}, popup_scheme = "0xFF000000,0xFF000000,0xFF000000,0x30c77263,0xFFf56b45,0xFF152645,0xFFe48f72,0xFF3d407a,0xFF000000"',
    # '"payload.cash_delta_ratio", ">=", 10"o"0 | payload.bankroll_delta, ">=", 50000',
    # '"<color=#6aefff>{New, new2 = 5} round</color> has | begun"',
    # 'minSmallBlind = 0, maxSmallBlind = 3, chipsIdList = ChipsSet_01, chipsPrefix = Chips_1_, chipsAmountList = {1, 5, 10, 10, 10, 25, 25, 50, 50, 50} | minSmallBlind = 3, maxSmallBlind = 12.5, chipsIdList = ChipsSet_02, chipsPrefix = Chips_2_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 12.5, maxSmallBlind = 60, chipsIdList = ChipsSet_03, chipsPrefix = Chips_3_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 60, maxSmallBlind = 300, chipsIdList = ChipsSet_04, chipsPrefix = Chips_4_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 300, maxSmallBlind = 1250, chipsIdList = ChipsSet_05, chipsPrefix = Chips_5_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 1250, maxSmallBlind = 6000, chipsIdList = ChipsSet_06, chipsPrefix = Chips_6_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 6000, maxSmallBlind = 30000, chipsIdList = ChipsSet_07, chipsPrefix = Chips_7_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 30000, maxSmallBlind = 125000, chipsIdList = ChipsSet_08, chipsPrefix = Chips_8_, chipsAmountList = {1, 5, 10, 5, 10, 10, 25, 50, 50, 50} | minSmallBlind = 125000, maxSmallBlind = 350000, chipsIdList = ChipsSet_09, chipsPrefix = Chips_9_, chipsAmountList = {1, 5, 10, 1, 1, 5, 5, 10, 25, 50} | minSmallBlind = 750000, maxSmallBlind = 1000000, chipsIdList = ChipsSet_10, chipsPrefix = Chips_10_, chipsAmountList = {1, 5, 10, 5, 5, 10, 25, 50, 50, 50} | minSmallBlind = 1000000, maxSmallBlind = 999999999999, chipsIdList = ChipsSet_11, chipsPrefix = Chips_11_, chipsAmountList = {1, 5, 10, 5, 5, 5, 10, 25, 50, 50}'
    ]

string_txt = [
    '<color=#6aefff>New round</color> has | begun',
    '{0} made a <color=#B451E9>bet</color> {1}',
    ]

string_sep = [
    '"  hand =   {three     = 3, two = 2 | four = 5, five = 5}"',
    ' hand =   "{three     = 3, two = 2 | four = 5, five = 5}"',
    'hand =    {three     = 3, two             = 2 | four = 5, five[] = {four = 5, five = 5}}',
    '"<color=#6aefff>New round</color> has | begun"',
    '"{0} made a <color=#B451E9>bet</color> {1}"',
    ]

for line in string:
    data = gsparser.dumps(line, unwrap_list=False, mode='v1')
    print(json.dumps(data, indent=4))
    print('------------------------')


# for line in string_txt:
#     print(json.dumps(config_to_json(line, is_raw=True)))
