import urllib.request

headers = {'User-Agent': 'Mozilla/5.0'}

clean_slimes = [
    ("assets/textures/mob1.png", "https://stardewvalleywiki.com/mediawiki/images/7/7b/Green_Slime.png"),
    ("assets/textures/mob2.png", "https://stardewvalleywiki.com/mediawiki/images/1/1f/Blue_Slime_Dangerous.png"),
    ("assets/textures/mob3.png", "https://stardewvalleywiki.com/mediawiki/images/2/27/Purple_Slime.png"),
    ("assets/textures/big_slime.png", "https://stardewvalleywiki.com/mediawiki/images/thumb/0/0a/Big_Red_Slime.png/48px-Big_Red_Slime.png")
]

for path, url in clean_slimes:
    req = urllib.request.Request(url, headers=headers)
    data = urllib.request.urlopen(req).read()
    with open(path, "wb") as f:
        f.write(data)
    print(f"Saved clean {path} ({len(data)} bytes)")
