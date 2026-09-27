import os
import subprocess
import base64
import time

ADB = r"C:\Users\Mechrevo\AppData\Local\Android\Sdk\platform-tools\adb.exe"
PKG = "org.cactusteam.cactustd"
BACKUP_DIR = r"C:\Users\Mechrevo\.gemini\antigravity\scratch\cactus_td\phone_save_backup"

# Check if app is installed
res = subprocess.run([ADB, "shell", f"pm path {PKG}"], capture_output=True, text=True)
if not res.stdout.strip():
    print(f"App {PKG} is not installed yet. Please install it on the phone first.")
    exit(1)

print("App is installed! Initializing directories...")
# Launch app for 2 seconds to initialize folder structure if needed
subprocess.run([ADB, "shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1"], capture_output=True)
time.sleep(2)
subprocess.run([ADB, "shell", "am", "force-stop", PKG], capture_output=True)

# Files to restore
mappings = [
    ("savedata.json", "files/savedata.json"),
    ("active_profile.json", "files/saves/active_profile.json"),
    ("export_slot_main.cactussave", "files/saves/export_slot_main.cactussave"),
    ("global_achievements.json", "files/saves/global_achievements.json"),
    ("slot_main.json", "files/saves/slot_main.json")
]

for src_name, dst_path in mappings:
    src_file = os.path.join(BACKUP_DIR, src_name)
    if not os.path.exists(src_file):
        print(f"Skipping {src_name} (not found in backup)")
        continue
    with open(src_file, "rb") as f:
        data = f.read()
    b64_str = base64.b64encode(data).decode("ascii")
    parent_dir = os.path.dirname(dst_path)
    if parent_dir:
        subprocess.run([ADB, "shell", f"run-as {PKG} mkdir -p {parent_dir}"], capture_output=True)
    cmd = f"run-as {PKG} sh -c 'echo {b64_str} | base64 -d > {dst_path}'"
    subprocess.run([ADB, "shell", cmd], check=True)
    print(f"Restored {dst_path} ({len(data)} bytes)")

print("\nAll player saves restored successfully!")
