import json, re, os

scratch = r'C:\Users\Administrator\.gemini\antigravity\scratch'
data_path = os.path.join(scratch, 'dashboard_data.js')

with open(data_path, 'r', encoding='utf-8') as f:
    raw_data = f.read()

m = re.search(r'window\.DASHBOARD_DATA\s*=\s*(\{[\s\S]*\});?\s*$', raw_data)
data = json.loads(m.group(1))

print("=== 深度排查【获取渠道与显示平台不一致】的具体条目 ===")

# 1. global_trends
gt = data.get('global_trends', {})
for cat_key, items in gt.items():
    for idx, it in enumerate(items):
        src = it.get('source', '')
        link = it.get('link', '')
        # 如果大分类是 TikTok，但链接/来源包含 微博、小红书、微信、知乎、YouTube、Netflix、Shopee 等
        if cat_key == 'TikTok':
            for wrong in ['weibo', 'xiaohongshu', 'wechat', 'bilibili', 'youtube', 'netflix', 'lazada', 'shopee']:
                if wrong in src.lower() or wrong in link.lower():
                    print(f"1. [全球趋势-TikTok] 分类为 TikTok，但条目 #{idx+1} 来源为 '{src}'，链接为 '{link}'，内容: '{it.get('content')[:35]}...'")
        elif cat_key == 'YouTube':
            for wrong in ['weibo', 'tiktok', 'netflix', 'bilibili', 'shopee']:
                if wrong in src.lower() or wrong in link.lower():
                    print(f"2. [全球趋势-YouTube] 分类为 YouTube，但条目 #{idx+1} 来源为 '{src}'，链接为 '{link}'")
        elif cat_key == 'Netflix':
            for wrong in ['weibo', 'tiktok', 'youtube', 'shopee', 'lazada']:
                if wrong in src.lower() or wrong in link.lower():
                    print(f"3. [全球趋势-Netflix] 分类为 Netflix，但条目 #{idx+1} 来源为 '{src}'，链接为 '{link}'")
        elif cat_key == 'Shopping':
            # 看看 shopping 平台下都是什么链接
            print(f"4. [全球趋势-Shopping] 条目 #{idx+1} 来源 '{src}', 链接 '{link}'")

# 2. competitors (竞品监控)
comps = data.get('competitors', [])
for idx, it in enumerate(comps):
    plat = it.get('platform', '')
    link = it.get('link', '')
    # 如果平台是 Lazada，链接是 shopee
    if 'lazada' in plat.lower() and 'shopee' in link.lower():
        print(f"5. [竞品监控] 平台是 {plat}，但链接是 Shopee: {link}")
    elif 'shopee' in plat.lower() and 'lazada' in link.lower():
        print(f"6. [竞品监控] 平台是 {plat}，但链接是 Lazada: {link}")
    elif 'tiktok' in plat.lower() and ('lazada' in link.lower() or 'shopee' in link.lower()):
        print(f"7. [竞品监控] 平台是 {plat}，但链接是: {link}")

# 3. bestsellers 与 search_rankings 里的重复和伪造数据
bs = data.get('bestsellers', {})
print("\n=== 排查【爆款榜单 bestsellers】跨平台/跨国家重复的条目 ===")
# 检查是否同一款商品被直接复制到了多个平台和国家
prod_occurrences = {}
for plat, countries in bs.items():
    for country, items in countries.items():
        for idx, it in enumerate(items):
            pname = it.get('product')
            if not pname: continue
            if pname not in prod_occurrences: prod_occurrences[pname] = []
            prod_occurrences[pname].append((plat, country, it.get('rank'), it.get('price')))

for pname, occ in prod_occurrences.items():
    if len(occ) > 1:
        print(f"[bestsellers 重复商品] 《{pname}》 出现了 {len(occ)} 次:")
        for o in occ:
            print(f"    - 平台: {o[0]} | 国家: {o[1]} | 排名: #{o[2]} | 价格: {o[3]}")

# 4. 检查 search_rankings 跨平台/跨国家重复
sr = data.get('search_rankings', {})
print("\n=== 排查【搜索词 search_rankings】跨平台/跨国家重复的条目 ===")
word_occurrences = {}
for plat, countries in sr.items():
    for country, items in countries.items():
        for idx, it in enumerate(items):
            word = it.get('word') or it.get('keyword')
            if not word: continue
            if word not in word_occurrences: word_occurrences[word] = []
            word_occurrences[word].append((plat, country, it.get('rank')))

for word, occ in word_occurrences.items():
    if len(occ) > 2: # 出现超过2次
        print(f"[search_rankings 重复搜索词] 「{word}」 出现了 {len(occ)} 次: {[f'{o[0]}-{o[1]}' for o in occ]}")
