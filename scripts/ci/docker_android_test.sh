#!/usr/bin/env bash
# Build the bridge + music smoke APK, start a docker-android emulator, and run the logcat smoke test.
set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "ERROR: $0 requires bash (arrays and pipefail)." >&2
  exec /usr/bin/env bash "$0" "$@"
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

export COMPOSE_FILE="${COMPOSE_FILE:-$ROOT/docker-compose.android.yml}"
SKIP_AUTH="${SKIP_AUTH:-true}"
# Fresh .buildozer trees on GHA avoid stale dist state after docker volume prune races.
CLEAN="${CLEAN:-$([ -n "${GITHUB_ACTIONS:-}" ] && echo 1 || echo 0)}"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is not running or not accessible." >&2
  exit 1
fi

COMPOSE=(./scripts/ci/docker_compose.sh -f "$COMPOSE_FILE")

# Play Store emulator images always need matching adb keys on emulator + smoke (SKIP_AUTH is not enough).
./scripts/ci/ensure_docker_adb_keys.sh
if [ -f "$ROOT/.docker-android/keys/.generated" ]; then
  echo "==> New adb keys: resetting emulator volume so the AVD trusts them"
  "${COMPOSE[@]}" down -v 2>/dev/null || true
  rm -f "$ROOT/.docker-android/keys/.generated"
fi

chmod +x scripts/ci/*.sh
export SKIP_AUTH

# Compose pulls show plain interleaved "layerid Downloading X MB" lines. Use docker pull
# first so interactive terminals get the usual per-layer progress bars (DOCKER_PROGRESS=tty).
_pull_image_if_missing() {
  local img="$1"
  if docker image inspect "$img" >/dev/null 2>&1; then
    echo "==> Image already present: $img"
    return 0
  fi
  echo "==> Pulling $img (first run only; may take several minutes)..."
  if [ -t 1 ] && [ -z "${GITHUB_ACTIONS:-}" ]; then
    export DOCKER_PROGRESS="${DOCKER_PROGRESS:-tty}"
  fi
  docker pull "$img"
}

GRADLE_IMAGE="${ANDROID_GRADLE_IMAGE:-cimg/android:2025.12.1}"
EMU_IMAGE="${ANDROID_EMU_IMAGE:-halimqarroum/docker-android:api-33-playstore}"
BOZER_IMAGE="${DOCKER_IMAGE:-kivy/buildozer:latest}"

echo "==> Ensuring Docker images for android CI (build phase)"
_pull_image_if_missing "$GRADLE_IMAGE"
_pull_image_if_missing "$BOZER_IMAGE"

echo "==> Publishing android-notify-music-bridge to Maven local"
./scripts/ci/docker_gradle_bridge.sh :android-notify-music-bridge:publishToMavenLocal

echo "==> Building music smoke APK (emulator not started yet - avoids idle/OOM during build)"
CI_ANDROID_CLEAN="$CLEAN" ./scripts/ci/build_music_apk.sh

echo "==> Ensuring emulator image for smoke test"
_pull_image_if_missing "$EMU_IMAGE"

_root_free_mb="$(df -BM "$ROOT" 2>/dev/null | awk 'NR==2 {gsub(/M$/,"",$4); print $4}' || echo 0)"
if [ "${_root_free_mb:-0}" -lt 8000 ] 2>/dev/null; then
  echo "WARNING: low free disk on $(df -h "$ROOT" | awk 'NR==2 {print $1" ("$4" free)"}') - API 33 AVD needs ~7.4GB in the emulator volume." >&2
  echo "         Try: docker system prune -af && ./scripts/ci/docker_compose.sh -f docker-compose.android.yml down -v" >&2
fi

echo "==> Starting emulator for smoke test"
if ! ./scripts/ci/ensure_docker_emulator.sh; then
  echo "" >&2
  echo "If logs show 'Killed', the emulator was OOM-killed. Try:" >&2
  echo "  ./scripts/ci/docker_compose.sh -f docker-compose.android.yml down -v" >&2
  echo "  ANDROID_EMU_MEMORY=2048 ANDROID_EMU_SHM=1gb ./scripts/ci/docker_android_test.sh" >&2
  exit 1
fi

echo "==> Running music smoke test"
"${COMPOSE[@]}" run --rm smoke \
  ./scripts/ci/emulator_music_test.sh

echo "PASS: music notification smoke test completed"