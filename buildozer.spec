[app]
title = Bagua
package.name = bagua
package.domain = org.bagua
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.10.12,kivy==2.3.1,pyjnius==1.7.0,hostpython3==3.10.12
android.arch = arm64-v8a
android.api = 31
android.minapi = 21
android.ndk = 23b
android.bootstrap = sdl2
android.buildtools_version = 30.0.3
android.accept_sdk_license = True
orientation = portrait
fullscreen = 0
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
