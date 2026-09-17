import urllib.request
import re
import json

url = 'https://stardewvalleywiki.com/Slimes'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')

# Find all img src
imgs = re.findall(r'src="([^"]+\.png)"', html)
slime_imgs = [i for i in imgs if 'slime' in i.lower()]
print("Found slime pngs:", len(slime_imgs))
for s in sorted(set(slime_imgs))[:30]:
    print(s)
