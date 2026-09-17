[app]

# (str) Title of your application
title = CactusTD Remastered

# (str) Package name
package.name = cactustd

# (str) Package domain (needed for android/ios packaging)
package.domain = org.cactusteam

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,wav,ogg,json,txt,ttf,ico

# (list) List of directory inclusions
source.include_patterns = assets/*,saves/*

# (str) Application versioning
version = 0.1.0

# (list) Application requirements
requirements = python3,pygame

# (str) Supported orientation (landscape for Tower Defense)
orientation = landscape

# (bool) Fullscreen mode
fullscreen = 1

# (string) Icon of the application
icon.filename = %(source.dir)s/assets/textures/app_icon.png

# (list) Permissions
android.permissions = WAKE_LOCK

# (int) Target Android API
android.api = 34

# (int) Minimum API supported (Android 5.0+)
android.minapi = 21

# (str) Android NDK API level
android.ndk_api = 21

# (bool) Auto accept SDK license
android.accept_sdk_license = True

# (str) Android architectures to build for
android.archs = arm64-v8a

# (bool) Enable Android backup
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
