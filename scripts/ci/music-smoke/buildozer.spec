[buildozer]
warn_on_root = 0

[app]
title = Music Smoke
package.name = smokemusic
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy,pyjnius

# Local pre-publication test: the AAR must already be in ~/.m2 (scripts/ci/docker_gradle_bridge.sh).
# Once published to Maven Central no repo block is needed; this line becomes a no-op only if removed.
android.add_gradle_repositories = mavenLocal()

# The bridge artifact replaces the legacy copy-pasted Java file (android.add_src).
android.gradle_dependencies = io.github.fector101:android-notify-music-bridge:1.0.0

android.permissions = POST_NOTIFICATIONS

android.api = 33
android.minapi = 21
android.archs = x86_64
android.ndk_api = 21

android.allow_backup = True
android.entrypoint = org.kivy.android.PythonActivity