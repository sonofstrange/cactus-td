import urllib.request
import re

headers = {'User-Agent': 'Mozilla/5.0'}
for name in ['Blue_Slime.png', 'Frost_Slime.png', 'Frost_Jelly.png', 'Slime.png']:
    url = f'https://stardewvalleywiki.com/File:{name}'
    try:
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req).read().decode('utf-8')
        m = re.search(r'href="(/mediawiki/images/[^"]+\.png)"', html)
        if m:
            print(f"{name} -> {m.group(1)}")
    except Exception as e:
        print(f"{name}: {e}")
