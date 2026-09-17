
import urllib.request, re
url = 'https://stardewvalleywiki.com/Slimes'
html = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
idx = html.find('Variations')
print(html[idx:idx+2500])
