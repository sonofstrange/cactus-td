#!/usr/bin/env python3
import os
import io
import shutil
import struct
import subprocess
import tarfile
import zipfile

PROJECT_DIR = "/mnt/c/Users/Mechrevo/.gemini/antigravity/scratch/cactus_td"
STAGING_DIR = "/tmp/cactus_td_staging"
PYC_DIR = os.path.join(STAGING_DIR, "pyc")
BASE_APK = os.path.join(PROJECT_DIR, "dist", "CactusTD_Android_v0.2.0.apk")
UNALIGNED_APK = os.path.join(PROJECT_DIR, "dist", "CactusTD_Android_v0.3.0_unaligned.apk")
OUTPUT_APK = os.path.join(PROJECT_DIR, "dist", "CactusTD_Android_v0.3.0.apk")
BUILD_TOOLS = "/home/mechrevo/.buildozer/android/platform/android-sdk/build-tools/37.0.0"
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner")
KEYSTORE = "/home/mechrevo/android_debug.keystore"

print("1. Preparing staging directory...")
if os.path.exists(STAGING_DIR):
    shutil.rmtree(STAGING_DIR)
os.makedirs(PYC_DIR, exist_ok=True)

# Copy python source files and compile to Python 3.10 bytecode (.pyc)
py_files = [
    "main.py", "config.py", "entities.py", "game_data.py", 
    "tree_data_v02.py", "ui_screens.py"
]
for extra in ["relic_art.py", "sitecustomize.py"]:
    p = os.path.join(PROJECT_DIR, extra)
    if os.path.exists(p):
        py_files.append(extra)

for f in py_files:
    shutil.copy2(os.path.join(PROJECT_DIR, f), os.path.join(PYC_DIR, f))

print("2. Compiling python files to Python 3.10 bytecode (.pyc)...")
subprocess.run(["python3.10", "-m", "compileall", "-b", PYC_DIR], check=True)

# Load compiled .pyc contents
pyc_data = {}
for f in os.listdir(PYC_DIR):
    if f.endswith(".pyc"):
        with open(os.path.join(PYC_DIR, f), "rb") as pyc_f:
            pyc_data[f] = pyc_f.read()
print(f"Compiled {len(pyc_data)} .pyc files: {list(pyc_data.keys())}")

print("3. Updating private.tar based on original v0.2.0 package...")
with zipfile.ZipFile(BASE_APK, "r") as zin:
    old_tar_bytes = zin.read("assets/private.tar")
    old_manifest = zin.read("AndroidManifest.xml")

tin = tarfile.open(fileobj=io.BytesIO(old_tar_bytes))
tar_out_io = io.BytesIO()
tout = tarfile.open(fileobj=tar_out_io, mode="w:gz")

# Collect all files from project assets
proj_assets = {}
assets_dir = os.path.join(PROJECT_DIR, "assets")
for root, dirs, files in os.walk(assets_dir):
    for f in files:
        full_p = os.path.join(root, f)
        rel_p = os.path.relpath(full_p, PROJECT_DIR).replace("\\", "/")
        proj_assets[rel_p] = full_p
print(f"Found {len(proj_assets)} assets in project directory.")

# Process members from old private.tar
seen_names = set()
for member in tin.getmembers():
    seen_names.add(member.name)
    if member.name in pyc_data:
        new_data = pyc_data[member.name]
        ti = tarfile.TarInfo(name=member.name)
        ti.size = len(new_data)
        ti.mtime = member.mtime
        ti.mode = member.mode
        ti.type = member.type
        tout.addfile(ti, io.BytesIO(new_data))
    elif member.name in proj_assets:
        with open(proj_assets[member.name], "rb") as af:
            asset_data = af.read()
        ti = tarfile.TarInfo(name=member.name)
        ti.size = len(asset_data)
        ti.mtime = member.mtime
        ti.mode = member.mode
        ti.type = member.type
        tout.addfile(ti, io.BytesIO(asset_data))
    else:
        f = tin.extractfile(member)
        tout.addfile(member, f)

# Add any new assets from PROJECT_DIR/assets that were not in old private.tar!
new_assets_count = 0
for rel_name, full_path in sorted(proj_assets.items()):
    if rel_name not in seen_names:
        with open(full_path, "rb") as af:
            asset_data = af.read()
        ti = tarfile.TarInfo(name=rel_name)
        ti.size = len(asset_data)
        ti.mode = 0o644
        tout.addfile(ti, io.BytesIO(asset_data))
        seen_names.add(rel_name)
        new_assets_count += 1
        print(f"Added new asset to private.tar: {rel_name} ({len(asset_data):,} bytes)")
print(f"Total new assets added to private.tar: {new_assets_count}")

# Add any new pyc files that were not in old tar
for fname, data in pyc_data.items():
    if fname not in seen_names:
        ti = tarfile.TarInfo(name=fname)
        ti.size = len(data)
        ti.mode = 0o644
        tout.addfile(ti, io.BytesIO(data))

# Also add python source files (.py) so both .pyc and .py are present
for fname in py_files:
    src_path = os.path.join(PROJECT_DIR, fname)
    if os.path.exists(src_path):
        with open(src_path, "rb") as py_f:
            py_bytes = py_f.read()
        ti = tarfile.TarInfo(name=fname)
        ti.size = len(py_bytes)
        ti.mode = 0o644
        tout.addfile(ti, io.BytesIO(py_bytes))

tin.close()
tout.close()
new_tar_bytes = tar_out_io.getvalue()
print(f"Updated private.tar (gzipped): old size = {len(old_tar_bytes):,}, new size = {len(new_tar_bytes):,} bytes")

print("4. Updating AndroidManifest.xml (versionName 0.3.0, versionCode 1021300)...")
old_u16 = '0.2.0'.encode('utf-16le')
new_u16 = '0.3.0'.encode('utf-16le')
assert old_u16 in old_manifest, "old_u16 0.2.0 not found in AndroidManifest.xml"
new_manifest = old_manifest.replace(old_u16, new_u16, 1)

old_vc = struct.pack('<I', 1021200)
new_vc = struct.pack('<I', 1021300)
assert old_vc in new_manifest, "old_vc 1021200 not found in AndroidManifest.xml"
new_manifest = new_manifest.replace(old_vc, new_vc, 1)
print(f"AndroidManifest.xml updated: {len(old_manifest)} -> {len(new_manifest)} bytes")

print("5. Repackaging APK...")
if os.path.exists(UNALIGNED_APK):
    os.remove(UNALIGNED_APK)

with zipfile.ZipFile(BASE_APK, "r") as zin:
    with zipfile.ZipFile(UNALIGNED_APK, "w") as zout:
        for item in zin.infolist():
            if item.filename.startswith("META-INF/"):
                continue
            if item.filename == "assets/private.tar":
                continue
            if item.filename == "AndroidManifest.xml":
                continue
            if item.filename == "res/drawable/presplash.jpg":
                custom_presplash = os.path.join(PROJECT_DIR, "assets", "branding", "presplash.jpg")
                if os.path.exists(custom_presplash):
                    print(f"Injecting custom presplash from {custom_presplash}...")
                    with open(custom_presplash, "rb") as cpf:
                        splash_data = cpf.read()
                    splash_info = zipfile.ZipInfo("res/drawable/presplash.jpg")
                    splash_info.compress_type = zipfile.ZIP_DEFLATED
                    zout.writestr(splash_info, splash_data)
                    continue
            data = zin.read(item.filename)
            zout.writestr(item, data)

        # Write updated AndroidManifest.xml
        mani_info = zipfile.ZipInfo("AndroidManifest.xml")
        mani_info.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(mani_info, new_manifest)

        # Write updated private.tar (DEFLATED)
        tar_info = zipfile.ZipInfo("assets/private.tar")
        tar_info.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(tar_info, new_tar_bytes)

print("6. Running zipalign...")
if os.path.exists(OUTPUT_APK):
    os.remove(OUTPUT_APK)
subprocess.run([ZIPALIGN, "-f", "-p", "4", UNALIGNED_APK, OUTPUT_APK], check=True)
if os.path.exists(UNALIGNED_APK):
    os.remove(UNALIGNED_APK)

print("7. Signing APK with original keystore (apksigner)...")
subprocess.run([
    APKSIGNER, "sign",
    "--ks", KEYSTORE,
    "--ks-pass", "pass:android",
    "--key-pass", "pass:android",
    "--ks-key-alias", "androiddebugkey",
    OUTPUT_APK
], check=True)

print("8. Verifying signed APK...")
res = subprocess.run([APKSIGNER, "verify", "--verbose", OUTPUT_APK], capture_output=True, text=True)
print(res.stdout)
if "DOES NOT VERIFY" in res.stdout or "DOES NOT VERIFY" in res.stderr:
    raise RuntimeError("Verification failed!")

print(f"SUCCESS! Android APK v0.3.0 built at: {OUTPUT_APK}")
print(f"File size: {os.path.getsize(OUTPUT_APK):,} bytes")
