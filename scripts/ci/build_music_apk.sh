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

# Seed the accepted SDK license files BEFORE buildozer starts. The 2026-era sdkmanager
# (build-tools;37) no longer honors `yes |` pipes in non-TTY CI; it requires the accepted
# hashes to pre-exist on disk under \$SDK_ROOT/licenses/. We copy the byte-exact hashes from
# this machine's own working SDK (ground truth), which sdkmanager accepts verbatim.
_multi_seed_licenses() {
  local sdk_root="$1"
  local seeds_dir="$2/sdk-licenses-copy"
  local target="$sdk_root/licenses"
  # Buildozer installs the SDK at ~/.buildozer/android/platform/android-sdk; only seed that root.
  [ -n "$sdk_root" ] || return 0
  [ -d "$seeds_dir" ] || return 0
  mkdir -p "$target"
  local f
  for f in "$seeds_dir"/android-*; do
    [ -f "$f" ] && cp -f "$f" "$target/$(basename "${f#android-}")"
  done
}
HOST_SDK_LICENSES_SRC="${HOME}/.buildozer/android/platform/android-sdk/licenses"
_multi_seed_licenses "${HOME}/.buildozer/android/platform/android-sdk" "$HOST_SDK_LICENSES_SRC"

# Pre-accept the Android SDK license so the 2026-era sdkmanager does not EOF-EOF abort
# on build-tools;37 tools (it needs the accepted hash on disk before install).
# Seed from buildozer's OWN accepted copy baked into the kivy/buildozer image, falling
# back to this host's real SDK (the local build used by developers) if present.
SDK_LICENSES="${HOME}/.buildozer/android/platform/android-sdk/licenses"
mkdir -p "$SDK_LICENSES"
if [ -f "${HOME}/buildozer-license-android-sdk-license" ]; then
  cp -f "${HOME}/buildozer-license-android-sdk-license" "$SDK_LICENSES/android-sdk-license"
elif [ -f "$ROOT/scripts/ci/music-smoke/licenses/android-sdk-license" ]; then
  cp -f "$ROOT/scripts/ci/music-smoke/licenses/android-sdk-license" "$SDK_LICENSES/android-sdk-license"
else
  # Canonical accepted hashes (dev-host's own real SDK, byte-for-byte, see local .buildozer).
  printf '%s\n' \
    "8933bad161af4178b1185d1a37fbf41ea5269c55" \
    "d56f5187479451eabf01fb78af6dfcb131a6481e" \
    "24333f8a63b6825ea9c5514f83c2829b004d1fee" \
    > "$SDK_LICENSES/android-sdk-license"
fi
# Preview-license hash also needed by some build-tools (x86_64 aidl path).
printf '%s\n' "84831b9409646a918e30573bab4c9c91346d8abd" > "$SDK_LICENSES/android-sdk-preview-license"

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