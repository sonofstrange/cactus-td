import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

official_slimes = [
    ("assets/textures/mob1.png", "https://stardewvalleywiki.com/mediawiki/images/7/7b/Green_Slime.png"),
    ("assets/textures/mob2.png", "https://stardewvalleywiki.com/mediawiki/images/9/9d/Frost_Jelly.png"),
    ("assets/textures/mob3.png", "https://stardewvalleywiki.com/mediawiki/images/2/27/Purple_Slime.png"),
    ("assets/textures/big_slime.png", "https://stardewvalleywiki.com/mediawiki/images/0/0a/Big_Red_Slime.png")
]

for dest, url in official_slimes:
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    with open(dest, "wb") as f:
        f.write(data)
    print(f"Downloaded {dest} from {url} ({len(data)} bytes)")
