#!/usr/bin/env bash
# Stream the docker-android emulator display to the host with scrcpy (optional companion to
# emulator_music_test.sh - lets you watch the notification/buttons live during a smoke test).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if ! command -v scrcpy >/dev/null 2>&1; then
  echo "ERROR: scrcpy is required (sudo apt install scrcpy, or https://github.com/Genymobile/scrcpy)" >&2
  exit 1
fi

COMPOSE=(./scripts/ci/docker_compose.sh -f "$ROOT/docker-compose.android.yml")

echo "==> Starting emulator (if not already running)"
./scripts/ci/ensure_docker_emulator.sh

EMU_ADB_PORT="${ANDROID_EMU_ADB_PORT:-5555}"
echo "==> Forwarding the emulator's adb port to localhost:$EMU_ADB_PORT"
$COMPOSE exec -d emulator sh -c "apt-get install -y -qq socat >/dev/null 2>&1; socat TCP-LISTEN:$EMU_ADB_PORT,fork,reuseaddr TCP:127.0.0.1:5555" 2>/dev/null \
  || $COMPOSE exec -d emulator sh -c "apt-get update -qq && apt-get install -y -qq socat >/dev/null; socat TCP-LISTEN:$EMU_ADB_PORT,fork,reuseaddr TCP:127.0.0.1:5555"

adb connect "127.0.0.1:$EMU_ADB_PORT" >/dev/null 2>&1 || true
sleep 2

echo "==> Starting scrcpy (Ctrl+C to quit)"
exec scrcpy --serial "127.0.0.1:$EMU_ADB_PORT" "$@"