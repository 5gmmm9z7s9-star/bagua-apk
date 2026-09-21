[app]
title = Bagua
package.name = bagua
package.domain = org.bagua
source.dir = .
source.main = main.py
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pyjnius,hostpython3
android.arch = arm64-v8a
android.api = 31
android.minapi = 21
android.bootstrap = sdl2
orientation = portrait
fullscreen = 0
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
