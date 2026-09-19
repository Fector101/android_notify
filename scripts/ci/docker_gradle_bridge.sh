#!/usr/bin/env bash
# Publish the android-notify-music-bridge AAR to the host's Maven local repo (dockerized Gradle).
# The buildozer smoke container mounts $HOME/.m2 at /root/.m2 so the smoke build.spec can
# resolve the bridge via mavenLocal().
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GRADLE_IMAGE="${ANDROID_GRADLE_IMAGE:-cimg/android:2025.12.1}"
TASK="${1:-:android-notify-music-bridge:publishToMavenLocal}"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running or not accessible." >&2
  exit 1
fi

if [ ! -d "$HOME/.m2" ]; then
  mkdir -p "$HOME/.m2"
fi

echo "==> Publishing bridge to Maven local (docker image: $GRADLE_IMAGE)"
if [ -t 1 ] && [ -z "${GITHUB_ACTIONS:-}" ]; then
  export DOCKER_PROGRESS="${DOCKER_PROGRESS:-tty}"
fi

docker run --rm \
  -v "$ROOT:/workspace" \
  -v "$HOME/.m2:/root/.m2" \
  -u "0:0" \
  -w /workspace \
  --entrypoint bash \
  "$GRADLE_IMAGE" \
  -ec '
    chmod +x /workspace/bridges/android/gradlew
    cd /workspace/bridges/android
    ./gradlew '"$TASK"' --no-daemon
  '