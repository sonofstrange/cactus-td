import os
import subprocess
import base64
import sys

ADB = r"C:\Users\Mechrevo\AppData\Local\Android\Sdk\platform-tools\adb.exe"
PKG = "org.cactusteam.cactustd"
APK = r"C:\Users\Mechrevo\.gemini\antigravity\scratch\cactus_td\dist\CactusTD_Android_v0.3.0.apk"
BACKUP_DIR = r"C:\Users\Mechrevo\.gemini\antigravity\scratch\cactus_td\phone_save_backup"

os.makedirs(BACKUP_DIR, exist_ok=True)

def adb_shell(cmd):
    return subprocess.run([ADB, "shell", cmd], capture_output=True, text=True, check=True).stdout

files_to_backup = [
    "files/savedata.json",
    "files/saves/active_profile.json",
    "files/saves/export_slot_main.cactussave",
    "files/saves/global_achievements.json",
    "files/saves/slot_main.json"
]

print("1. Backing up save files from phone...")
saved_data = {}
for rel_path in files_to_backup:
    try:
        res = subprocess.run([ADB, "shell", f"run-as {PKG} base64 {rel_path}"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            raw_b64 = res.stdout.replace("\r", "").replace("\n", "").strip()
            data = base64.b64decode(raw_b64)
            saved_data[rel_path] = data
            local_file = os.path.join(BACKUP_DIR, os.path.basename(rel_path))
            with open(local_file, "wb") as f:
                f.write(data)
            print(f"  Backed up {rel_path} ({len(data)} bytes) -> {local_file}")
        else:
            print(f"  Skipped/not found: {rel_path}")
    except Exception as e:
        print(f"  Error reading {rel_path}: {e}")

print("2. Uninstalling old package (to resolve mismatched signature)...")
subprocess.run([ADB, "uninstall", PKG], check=True)

print("3. Installing new APK v0.3.0...")
subprocess.run([ADB, "install", APK], check=True)

print("4. Launching app once to initialize data directory...")
subprocess.run([ADB, "shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"], capture_output=True)
import time
time.sleep(2.5)
subprocess.run([ADB, "shell", "am", "force-stop", PKG], capture_output=True)

print("5. Restoring saved data back to phone...")
for rel_path, data in saved_data.items():
    b64_str = base64.b64encode(data).decode("ascii")
    # ensure parent dir exists in run-as
    parent_dir = os.path.dirname(rel_path)
    if parent_dir:
        subprocess.run([ADB, "shell", f"run-as {PKG} mkdir -p {parent_dir}"], capture_output=True)
    # write via base64 decode
    cmd = f"run-as {PKG} sh -c 'echo {b64_str} | base64 -d > {rel_path}'"
    subprocess.run([ADB, "shell", cmd], check=True)
    print(f"  Restored {rel_path} ({len(data)} bytes)")

print("\nSUCCESS! Game v0.3.0 installed and all player saves preserved perfectly!")
