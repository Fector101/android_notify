#!/usr/bin/env bash
# Run Gradle in the Android bridge module via Docker (no host ANDROID_HOME).
#
# Uses the Android Gradle image that ships the SDK. Mounts the repo and your
# local Maven repo (~/.m2) so `publishToMavenLocal` results are available to
# buildozer demo builds (add `mavenLocal()` to android.add_gradle_repositories).
#
# Usage examples:
#   scripts/build_bridge.sh                          # default: publishToMavenLocal
#   scripts/build_bridge.sh build build -x lint      # any gradle task
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${ANDROID_GRADLE_IMAGE:-cimg/android:2025.12.1}"
TASKS="${*:-:android-notify-music-bridge:publishToMavenLocal}"

docker run --rm -u 0:0 \
  -v "$ROOT:/workspace" \
  -v "${HOME}/.m2:/root/.m2" \
  -w /workspace/bridges/android \
  "$IMAGE" \
  bash -ec "chmod +x gradlew && ./gradlew $TASKS --no-daemon"