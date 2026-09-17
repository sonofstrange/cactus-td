import urllib.request
import re

url = 'https://stardewvalleywiki.com/Slimes'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

sections = re.split(r'<h[23][^>]*>', html)
for sec in sections:
    if not sec.strip(): continue
    title_match = re.match(r'(.*?)</h[23]>', sec)
    if title_match:
        title = re.sub('<[^<]+?>', '', title_match.group(1)).strip()
        imgs = re.findall(r'src="([^"]+\.png)"', sec)
        if imgs:
            print(f"=== SECTION: {title} ===")
            for img in imgs:
                if 'slime' in img.lower():
                    print("  ", img)
