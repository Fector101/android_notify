[app]

title = ANTester
package.name = androidNotify
package.domain = vercel.app
author = Fabian © Copyright Info
version = 1.0.1

source.dir = app_src

presplash.filename = %(source.dir)s/assets/icons/presplash.png
icon.filename = %(source.dir)s/assets/icons/icon.png

source.include_exts = py,png,jpg,kv,atlas,ttf,json,xml,wav
source.exclude_dirs = bin, venv,lab, worked, __pycache__, .idea, dist, for-download,laner-linux, .filereader, wallpapers


requirements = python3,kivy,https://github.com/kivymd/KivyMD/archive/master.zip,python-osc,https://github.com/kivy/plyer/archive/master.zip,materialyoucolor,asynckivy,asyncgui,pyjnius, docutils,netifaces,filetype,requests_toolbelt,websockets,pillow, android-widgets, https://github.com/Fector101/android_notify/archive/feat-add-data-to-notification.zip
services = Wallpapercarousel:./android/services/wallpaper.py:foreground, Test:./android/services/test.py:foreground

osx.python_version = 3
osx.kivy_version = 1.9.1

fullscreen = 1
orientation = portrait

android.api = 35
android.permissions = INTERNET, VIBRATE, USE_EXACT_ALARM, SCHEDULE_EXACT_ALARM, FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC, POST_NOTIFICATIONS, SET_WALLPAPER, READ_MEDIA_IMAGES, (name=android.permission.READ_EXTERNAL_STORAGE;maxSdkVersion=32), (name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=28)
android.add_src = %(source.dir)s/android/src
android.add_resources = %(source.dir)s/android/res
android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0, androidx.work:work-runtime:2.9.0
p4a.hook = %(source.dir)s/android/p4a/hook.py

android.archs = arm64-v8a
android.allow_backup = True


ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
