import json, re, os

scratch = r'C:\Users\Administrator\.gemini\antigravity\scratch'
data_path = os.path.join(scratch, 'dashboard_data.js')

with open(data_path, 'r', encoding='utf-8') as f:
    raw_data = f.read()

m = re.search(r'window\.DASHBOARD_DATA\s*=\s*(\{[\s\S]*\});?\s*$', raw_data)
data = json.loads(m.group(1))

for key in ['bestsellers', 'search_rankings', 'competitors', 'live_trends', 'global_trends', 'anime_film', 'calendar', 'news_feed']:
    val = data.get(key)
    print(f'Key: {key}, Type: {type(val).__name__}')
    if isinstance(val, dict):
        print('  Dict keys:', list(val.keys()))
        for subk in list(val.keys())[:3]:
            subval = val[subk]
            if isinstance(subval, list) and subval:
                print(f'    [{subk}] count: {len(subval)}')
                if isinstance(subval[0], dict):
                    print('      Item keys:', list(subval[0].keys()))
                    print('      Sample item:', subval[0])
    elif isinstance(val, list) and val:
        print(f'  List len: {len(val)}')
        if isinstance(val[0], dict):
            print('    Item keys:', list(val[0].keys()))
            print('    Sample item:', val[0])
