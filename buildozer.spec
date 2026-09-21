[app]
title = Bagua
package.name = bagua
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.10.12,kivy==2.3.1,pyjnius==1.7.0,hostpython3==3.10.12,pygame
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.accept_sdk_license = True
# 删掉或注释掉 osx.kivy_version

[buildozer]
log_level = 2
warn_on_root = 0
