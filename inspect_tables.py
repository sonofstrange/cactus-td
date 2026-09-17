import urllib.request
import re

url = 'https://stardewvalleywiki.com/Slimes'
html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
tables = re.findall(r'<table class="wikitable[^>]*>(.*?)</table>', html, re.DOTALL)
print('Found wikitables:', len(tables))

for idx, t in enumerate(tables):
    rows = re.findall(r'<tr>(.*?)</tr>', t, re.DOTALL)
    print(f'=== Table {idx}: {len(rows)} rows ===')
    for r in rows:
        imgs = re.findall(r'src="([^"]+\.png)"', r)
        text = re.sub(r'<[^<]+?>', '', r).strip()
        first_line = text.split('\n')[0] if text else ''
        if any('slime' in i.lower() for i in imgs):
            print(f"  {first_line:30} -> {imgs}")
