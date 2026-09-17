import urllib.request
import json
import re
import os

print("Fetching soundtrack page wikitext from Fandom API...")
url = 'https://roblox-grass-cutting-incremental.fandom.com/api.php?action=parse&page=Soundtracks&prop=wikitext&format=json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    wikitext = data['parse']['wikitext']['*']
    print(f"Wikitext fetched! Length: {len(wikitext)}")

    # Let's save wikitext to inspect
    with open("soundtracks_wikitext.txt", "w", encoding="utf-8") as f:
        f.write(wikitext)

    # Let's find audio links, filenames or templates
    lines = wikitext.split("\n")
    print("Total lines:", len(lines))
    for line in lines[:60]:
        if line.strip():
            print(line[:120])

except Exception as e:
    print("Error:", e)
