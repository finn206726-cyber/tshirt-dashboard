import json, re

scratch = r'C:\Users\Administrator\.gemini\antigravity\scratch'

# 1. 检查 app.js 中所有涉及「平台」、「渠道」、「来源」、「source」、「platform」的渲染代码
with open(f'{scratch}/app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

# 2. 读取 dashboard_data.js
with open(f'{scratch}/data/dashboard_data.js', 'r', encoding='utf-8') as f:
    raw_data = f.read()

# 提取 JSON 部分
m = re.search(r'window\.DASHBOARD_DATA\s*=\s*(\{[\s\S]*\});?\s*$', raw_data)
if m:
    data = json.loads(m.group(1))
    print('Loaded dashboard_data keys:', list(data.keys()))
else:
    print('Failed to parse dashboard_data.js')
    data = {}

# 检查 1: 商品榜单 bestsellers / competitors
# 检查 platform 与 source 是否不一致，或者重复项
bestsellers = data.get('bestsellers', [])
print(f'Total bestsellers: {len(bestsellers)}')
mismatches_best = []
for idx, b in enumerate(bestsellers):
    p = b.get('platform')
    s = b.get('source') or b.get('source_channel') or b.get('channel')
    # 检查字段
    if p and s and (p.lower() not in s.lower() and s.lower() not in p.lower()):
        mismatches_best.append((idx, b.get('product'), p, s, b.get('source_url')))

print(f'Bestsellers platform vs source mismatches: {len(mismatches_best)}')
for m in mismatches_best[:10]:
    print('  Mismatch:', m)

# 检查 2: 搜索词 search_rankings
search_rankings = data.get('search_rankings', [])
print(f'\nTotal search rankings: {len(search_rankings)}')
mismatches_search = []
for idx, b in enumerate(search_rankings):
    p = b.get('platform')
    s = b.get('source') or b.get('source_channel') or b.get('channel')
    if p and s and (p.lower() not in s.lower() and s.lower() not in p.lower()):
        mismatches_search.append((idx, b.get('keyword'), p, s))

print(f'Search rankings platform vs source mismatches: {len(mismatches_search)}')
for m in mismatches_search[:10]:
    print('  Mismatch:', m)

# 检查 3: 竞品列表 competitors
competitors = data.get('competitors', [])
print(f'\nTotal competitors: {len(competitors)}')
mismatches_comp = []
for idx, b in enumerate(competitors):
    p = b.get('platform')
    s = b.get('source') or b.get('source_channel')
    if p and s and (p.lower() not in s.lower() and s.lower() not in p.lower()):
        mismatches_comp.append((idx, b.get('product'), p, s))

print(f'Competitors mismatches: {len(mismatches_comp)}')
for m in mismatches_comp[:10]:
    print('  Mismatch:', m)
