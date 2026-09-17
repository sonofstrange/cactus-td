import urllib.request
import json
import re
import os

os.makedirs("assets/textures", exist_ok=True)
os.makedirs("assets/sounds", exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://roblox-grass-cutting-incremental.fandom.com/wiki/Soundtracks'
}

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        print(f"  Successfully saved {dest_path} ({os.path.getsize(dest_path)} bytes)")
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False

# 1. Download Cactus and Stellar Cactus
cactus_url = "https://static.wikia.nocookie.net/roblox-grass-cutting-incremental/images/a/a6/Cactus.png/revision/latest?cb=20240919033539"
stellar_url = "https://static.wikia.nocookie.net/roblox-grass-cutting-incremental/images/4/4e/Stellar_Cactus.png/revision/latest?cb=20240923051851"

download_file(cactus_url, "assets/textures/Cactus.png")
download_file(stellar_url, "assets/textures/Stellar_Cactus.png")

# 2. Get soundtrack direct links from Fandom API
with open("soundtracks_wikitext.txt", "r", encoding="utf-8") as f:
    wikitext = f.read()

media_files = re.findall(r'Media:([^\|\]]+\.(?:ogg|mp3))', wikitext, re.IGNORECASE)
media_files = list(dict.fromkeys(media_files))

audio_urls = {}
for i in range(0, len(media_files), 10):
    batch = media_files[i:i+10]
    titles = "|".join(["File:" + name for name in batch])
    api_url = f"https://roblox-grass-cutting-incremental.fandom.com/api.php?action=query&titles={urllib.parse.quote(titles)}&prop=imageinfo&iiprop=url&format=json"
    req = urllib.request.Request(api_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for pid, pdata in pages.items():
            title = pdata.get('title', '')
            imageinfo = pdata.get('imageinfo', [])
            if imageinfo:
                file_url = imageinfo[0].get('url', '')
                filename = title.replace('File:', '')
                audio_urls[filename] = file_url
    except Exception as e:
        print("API error:", e)

print(f"\nResolved {len(audio_urls)} direct audio URLs!")

# Let's save a list of all tracks so the game can also shuffle or switch tracks per map!
track_registry = {}

tracks_to_download = [
    ("Normal Realm music v0.5.ogg", "main_music.ogg"),
    ("Cool Realm soundtrack including transition intro.ogg", "cool_realm.ogg"),
    ("Anti Realm music v0.5.ogg", "anti_realm.ogg"),
    ("InTheSnow.ogg", "in_the_snow.ogg"),
    ("StarRealm0.9.ogg", "star_realm.ogg"),
    ("Grassland0.9.ogg", "grassland.ogg"),
    ("Desert 0.9.ogg", "desert.ogg"),
    ("0.9 accel.mp3", "accel.mp3")
]

for src_name, local_name in tracks_to_download:
    url = audio_urls.get(src_name)
    if not url:
        for k, v in audio_urls.items():
            if k.lower() == src_name.lower():
                url = v
                break
    if url:
        success = download_file(url, f"assets/sounds/{local_name}")
        if success:
            track_registry[local_name] = src_name
    else:
        print(f"URL not found for {src_name}")

with open("assets/sounds/soundtracks.json", "w", encoding="utf-8") as f:
    json.dump(track_registry, f, indent=4, ensure_ascii=False)

print("\nDownloaded tracks registry saved!")
