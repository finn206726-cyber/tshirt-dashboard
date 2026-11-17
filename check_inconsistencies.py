import json, re, os

scratch = r'C:\Users\Administrator\.gemini\antigravity\scratch'
data_path = os.path.join(scratch, 'dashboard_data.js')

with open(data_path, 'r', encoding='utf-8') as f:
    raw_data = f.read()

m = re.search(r'window\.DASHBOARD_DATA\s*=\s*(\{[\s\S]*\});?\s*$', raw_data)
data = json.loads(m.group(1))

print("==================================================")
print("1. 检查【获取渠道与显示平台不一致】的问题")
print("==================================================")

# A. bestsellers: 字典 {'Lazada': [...], 'Shopee': [...], 'TikTok': [...]}
bs = data.get('bestsellers', {})
for plat, items in bs.items():
    for idx, it in enumerate(items):
        src = str(it.get('source') or it.get('source_channel') or '')
        url = str(it.get('link') or it.get('url') or '')
        # 如果 plat 是 Shopee，但 source 或 url 写了 Lazada 或其他
        plats = ['Shopee', 'Lazada', 'TikTok', 'Amazon', '淘宝', '拼多多', '1688']
        for p in plats:
            if p.lower() != plat.lower() and (p.lower() in src.lower() or p.lower() in url.lower()):
                print(f"[bestsellers] 分类平台是【{plat}】，但条目 #{idx+1} '{it.get('product')}' 来源渠道写着: '{src}'，链接: '{url}'")

# B. search_rankings: 字典 {'Lazada': [...], 'Shopee': [...], 'TikTok': [...]}
sr = data.get('search_rankings', {})
for plat, items in sr.items():
    for idx, it in enumerate(items):
        src = str(it.get('source') or it.get('source_channel') or '')
        url = str(it.get('link') or it.get('url') or '')
        for p in ['Shopee', 'Lazada', 'TikTok', 'Amazon']:
            if p.lower() != plat.lower() and (p.lower() in src.lower() or p.lower() in url.lower()):
                print(f"[search_rankings] 分类平台是【{plat}】，但条目 #{idx+1} '{it.get('keyword')}' 来源渠道写着: '{src}'，链接: '{url}'")

# C. competitors: 列表
comps = data.get('competitors', [])
for idx, it in enumerate(comps):
    plat = it.get('platform') or ''
    src = str(it.get('source') or it.get('link') or '')
    for p in ['Shopee', 'Lazada', 'TikTok']:
        if p.lower() != plat.lower() and p.lower() in src.lower():
            print(f"[competitors] 平台是【{plat}】，但条目 '{it.get('product')}' 来源是: '{src}'")

# D. global_trends: 字典 {'TikTok': [...], 'YouTube': [...], 'Netflix': [...], 'Shopping': [...]}
gt = data.get('global_trends', {})
for plat, items in gt.items():
    for idx, it in enumerate(items):
        src = str(it.get('source') or '')
        link = str(it.get('link') or '')
        # 看看 TikTok 下面是不是来源是微博或者其他平台
        if plat == 'TikTok' and 'weibo.com' in link:
            print(f"[global_trends - TikTok] 条目 #{idx+1} 标题/内容: '{it.get('content')[:30]}...' 来源却是: '{src}', 链接: '{link}'")
        if plat == 'Shopping' and ('shopee' in link.lower() or 'lazada' in link.lower()):
            # 看看 shopping 里的平台归属
            pass

print("\n==================================================")
print("2. 检查【信息重复】的问题")
print("==================================================")

for sec_name, items in [('competitors', data.get('competitors', [])), 
                        ('calendar', data.get('calendar', [])),
                        ('ip_hotspots', data.get('ip_hotspots', [])),
                        ('anime_film', data.get('anime_film', []))]:
    seen = {}
    for idx, it in enumerate(items):
        name = it.get('name') or it.get('product') or it.get('title')
        if not name: continue
        if name in seen:
            print(f"[{sec_name}] 重复条目: '{name}' (首次出现于 #{seen[name]+1}，再次出现于 #{idx+1})")
        else:
            seen[name] = idx

# 检查字典类型的重复
for dname in ['bestsellers', 'search_rankings']:
    d = data.get(dname, {})
    for plat, items in d.items():
        seen = {}
        for idx, it in enumerate(items):
            k = it.get('product') or it.get('keyword')
            if not k: continue
            if k in seen:
                print(f"[{dname} - {plat}] 重复条目: '{k}' (#{seen[k]+1} & #{idx+1})")
            else:
                seen[k] = idx

print("\n==================================================")
print("3. 检查【信息落后 / 时间停留在很久以前】的问题")
print("==================================================")
# 遍历各板块的时间戳，看看有哪些落后得离谱（比如 2024 年甚至更早）
for sec_name, items in [('competitors', data.get('competitors', [])), 
                        ('news_feed', data.get('news_feed', {}).get('items', [])),
                        ('calendar', data.get('calendar', [])),
                        ('anime_film', data.get('anime_film', []))]:
    stale_count = 0
    oldest = None
    for it in items:
        ts = str(it.get('t') or it.get('verified_at') or it.get('published') or it.get('source_time') or '')
        m_year = re.search(r'(202[0-9])', ts)
        if m_year:
            yr = int(m_year.group(1))
            if yr < 2026:
                stale_count += 1
                if oldest is None or ts < oldest:
                    oldest = ts
    if stale_count:
        print(f"[{sec_name}] 发现 {stale_count} 条落后于当前年份(2026)的数据，最早时间: {oldest}")
