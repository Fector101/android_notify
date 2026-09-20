#!/usr/bin/env bash
# Build a debug APK of the music notification smoke app via Docker buildozer (emulator profile).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP_DIR="$ROOT/scripts/ci/music-smoke"
DOCKER_IMAGE="${DOCKER_IMAGE:-kivy/buildozer:latest}"
BOZER_VOLUME="android-notify-music-smoke-buildozer"
CLEAN="${CI_ANDROID_CLEAN:-0}"
if [ "${1:-}" = "--clean" ] || [ "${1:-}" = "clean" ]; then
  CLEAN=1
fi

# Sync the android_notify package (the code under test) into the smoke app.
rm -rf "$APP_DIR/android_notify"
cp -a "$ROOT/android_notify" "$APP_DIR/android_notify"

if [ "$CLEAN" = "1" ]; then
  echo "Removing Docker volume $BOZER_VOLUME and local build dirs"
  docker volume rm "$BOZER_VOLUME" 2>/dev/null || true
  rm -rf "$APP_DIR/.buildozer" "$APP_DIR/bin" 2>/dev/null || true
fi

# Recreate the volume so stale Gradle/native state cannot break packageDebug on warm runners.
docker volume rm "$BOZER_VOLUME" 2>/dev/null || true
docker volume create "$BOZER_VOLUME" >/dev/null

# .buildozer on a named volume avoids parallel-make races on bind mounts (openssl .d.tmp).
DOCKER_VOLUMES=(
  -v "$ROOT:/home/user/project"
  -v "${BOZER_VOLUME}:/home/user/project/scripts/ci/music-smoke/.buildozer"
  -v "${HOME}/.buildozer:/home/user/.buildozer"
  -v "${HOME}/.m2:/root/.m2"
)
WORK_DIR="/home/user/project/scripts/ci/music-smoke"

mkdir -p "$APP_DIR/bin"
DIST="$(grep '^package\.name' "$APP_DIR/buildozer.spec" | sed 's/.*= *//')"
APK_GLOB="/vol/android/platform/build-x86_64/dists/${DIST}/build/outputs/apk/debug/*debug*.apk"

set +e
docker run --rm \
  --entrypoint buildozer \
  "${DOCKER_VOLUMES[@]}" \
  -w "$WORK_DIR" \
  -e HOME=/home/user \
  -e TAR_OPTIONS=--no-same-owner \
  -e CCACHE_DISABLE=1 \
  -e NDK_CCACHE=0 \
  -e MAKEFLAGS=-j2 \
  "$DOCKER_IMAGE" \
  --profile emulator android debug
_bozer_status=$?
set -e

# Buildozer often builds the APK in the .buildozer volume but fails copying to bin/ on bind mounts.
docker run --rm \
  -v "${BOZER_VOLUME}:/vol" \
  -v "$APP_DIR/bin:/out" \
  --entrypoint sh \
  "$DOCKER_IMAGE" \
  -c "cp -f ${APK_GLOB} /out/ 2>/dev/null || true; chown -R $(id -u):$(id -g) /out 2>/dev/null || true"

apk="$(ls -t "$APP_DIR"/bin/*debug*.apk 2>/dev/null | head -n1)"
if [ -z "$apk" ] && [ "$_bozer_status" -ne 0 ]; then
  echo "buildozer exited $_bozer_status and no APK was found in bin/ or the Docker volume" >&2
  exit "$_bozer_status"
fi
if [ -z "$apk" ]; then
  echo "No debug APK produced under $APP_DIR/bin" >&2
  exit 1
fi
if [ "$_bozer_status" -ne 0 ]; then
  echo "Note: buildozer exited $_bozer_status after APK copy; recovered APK from Docker volume."
fi
echo "Built $apk"