import urllib.request, os, re

base = 'https://d956b40113a545df8a3ba048a84ab9aa.sg.agentos-app.run/?sharecode=HCG6UQ3QHO'
scratch = r'C:\Users\Administrator\.gemini\antigravity\scratch'
index_path = os.path.join(scratch, 'index.html')

if not os.path.exists(index_path):
    urllib.request.urlretrieve(base, index_path)

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

with open(os.path.join(scratch, 'app.js'), 'r', encoding='utf-8') as f:
    app_js = f.read()

# 1. 检查 app.js 中所有 $('#id') 是否在 index.html 中存在
ids_in_app = re.findall(r"\$\(['\"]#([a-zA-Z0-9_-]+)['\"]\)", app_js)
ids_in_app = sorted(list(set(ids_in_app)))

print(f'Total DOM IDs queried: {len(ids_in_app)}')
missing_ids = []
for i in ids_in_app:
    if f'id="{i}"' not in html and f"id='{i}'" not in html:
        missing_ids.append(i)

print('=== Missing DOM IDs in index.html ===')
for m in missing_ids:
    print('Missing ID:', m)

# 2. 检查未被转义直接 innerHTML 拼接的地方 (XSS / 特殊字符渲染 Bug)
print('\n=== Potentially unescaped innerHTML ===')
lines = app_js.split('\n')
for idx, l in enumerate(lines):
    if 'innerHTML' in l and ('+' in l):
        # 查找明显的属性未加 esc 的情况
        if re.search(r'\+\s*([a-zA-Z0-9_]+\.(?:title|name|desc|text|query|product|theme|metric|source|tag|keyword|reason|note))\s*\+', l):
            matches = re.findall(r'\+\s*([a-zA-Z0-9_]+\.(?:title|name|desc|text|query|product|theme|metric|source|tag|keyword|reason|note))\s*\+', l)
            print(f'Line {idx+1}: Unescaped {matches} in: {l.strip()[:100]}')
