#!/usr/bin/env bash
# Logcat smoke test for the music smoke APK, running inside the `smoke`
# compose container.
#
# Verifies:
#   - android-notify-music-bridge AAR is resolved from Maven
#   - MediaSessionCallback is available
#   - media notification is built
#   - audio playback starts
#   - KEYCODE_MEDIA_PLAY_PAUSE reaches the MediaSession callback
#   - KEYCODE_MEDIA_NEXT reaches the MediaSession callback
#
# Expected log markers:
#
#   MUSIC_BRIDGE_OK
#   MUSIC_NOTIFICATION_BUILT
#   MUSIC_PLAYING
#   MUSIC_STATE: pause
#   MUSIC_STATE: play
#   MUSIC_SKIPPED

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

EMU_HOST="${ADB_CONNECT:-android-notify-android-emulator:5555}"
export ANDROID_SERIAL="${ANDROID_SERIAL:-$EMU_HOST}"

echo "==> Verifying emulator is still up before smoke test"
./scripts/ci/wait_for_android_emulator.sh

ADB="adb -s $ANDROID_SERIAL"
export ADB

LOG_TIMEOUT="${LOG_TIMEOUT:-180}"

apk="$(
    ls -t scripts/ci/music-smoke/bin/*debug*.apk 2>/dev/null |
        head -n1 ||
        true
)"

if [ -z "$apk" ]; then
    echo "No debug APK found under scripts/ci/music-smoke/bin" >&2
    exit 1
fi

echo "==> APK: $apk"

# Build the complete Android package name.
#
# package.name = smokemusic
# package.domain = org.test
#
# therefore:
#
# org.test.smokemusic
#
package_name="$(
    grep '^package\.name' scripts/ci/music-smoke/buildozer.spec |
        sed 's/.*= *//'
)"

package_domain="$(
    grep '^package\.domain' scripts/ci/music-smoke/buildozer.spec |
        sed 's/.*= *//'
)"

pkg="${package_domain}.${package_name}"
activity="${pkg}/org.kivy.android.PythonActivity"

echo "==> Package: $pkg"
echo "==> Activity: $activity"

echo "==> Installing APK on emulator"
$ADB install -r "$apk" >/dev/null

echo "==> Clearing logcat and launching $activity"
$ADB logcat -c

$ADB shell am start -n "$activity" >/dev/null

_logcat_contains() {
    local pattern="$1"

    $ADB logcat -d -v brief 2>/dev/null |
        grep -q "$pattern"
}

# Wait for a particular log marker.
#
# This is intentionally polling rather than checking once because:
#
#   ADB keyevent
#       -> Android MediaSessionService
#       -> MediaSession
#       -> Java callback
#       -> Python callback
#
# is asynchronous.
#
_wait_for_log() {
    local pattern="$1"
    local timeout="${2:-5}"

    local elapsed=0

    while [ "$elapsed" -lt "$timeout" ]; do
        if _logcat_contains "$pattern"; then
            return 0
        fi

        sleep 0.25
        elapsed=$((elapsed + 1))
    done

    return 1
}

_fail() {
    echo "FAIL: $1" >&2

    echo "---- last logcat (grep music/python/MediaSession) ----" >&2

    $ADB logcat -d -v brief 2>/dev/null |
        grep -iE \
            'MusicNotification|MUSIC_|MediaSession|MediaButton|python|AndroidRuntime' |
        tail -100 >&2 ||
        true

    exit 1
}

echo "==> Waiting for startup markers (timeout ${LOG_TIMEOUT}s)"

_elapsed=0

while [ "$_elapsed" -lt "$LOG_TIMEOUT" ]; do

    if \
        _logcat_contains "MUSIC_BRIDGE_OK" &&
        _logcat_contains "MUSIC_NOTIFICATION_BUILT" &&
        _logcat_contains "MUSIC_PLAYING"
    then
        echo "==> Startup markers present (${_elapsed}s)"
        break
    fi

    if _logcat_contains "AndroidRuntime: FATAL EXCEPTION"; then
        _fail "app crashed during startup"
    fi

    echo \
        "    … waiting for startup markers (${_elapsed}s / ${LOG_TIMEOUT}s)"

    sleep 5
    _elapsed=$((_elapsed + 5))
done

if ! _logcat_contains "MUSIC_BRIDGE_OK"; then
    _fail \
        "MUSIC_BRIDGE_OK not found " \
        "(AAR class org/android_notify/music/MediaSessionCallback not resolved)"
fi

if ! _logcat_contains "MUSIC_NOTIFICATION_BUILT"; then
    _fail "MUSIC_NOTIFICATION_BUILT not found"
fi

if ! _logcat_contains "MUSIC_PLAYING"; then
    _fail "MUSIC_PLAYING not found (sound did not start)"
fi

echo "==> Startup checks passed"

# ---------------------------------------------------------------------------
# PLAY / PAUSE
# ---------------------------------------------------------------------------

echo ""
echo "==> Testing KEYCODE_MEDIA_PLAY_PAUSE"

#
# IMPORTANT:
#
# Clear logcat BEFORE sending the event.
#
# Otherwise a previous:
#
#     MUSIC_STATE: play
#
# from startup could make the resume test pass without the callback
# actually being invoked.
#
$ADB logcat -c

echo "==> Sending KEYCODE_MEDIA_PLAY_PAUSE (85) to pause"

$ADB shell input keyevent 85 >/dev/null

if ! _wait_for_log "MUSIC_STATE: pause" 5; then
    _fail \
        "pause not detected after KEYCODE_MEDIA_PLAY_PAUSE"
fi

echo "==> Pause detected"

# ---------------------------------------------------------------------------
# PLAY / RESUME
# ---------------------------------------------------------------------------

$ADB logcat -c

echo "==> Sending KEYCODE_MEDIA_PLAY_PAUSE (85) to resume"

$ADB shell input keyevent 85 >/dev/null

if ! _wait_for_log "MUSIC_STATE: play" 5; then
    _fail \
        "resume not detected after KEYCODE_MEDIA_PLAY_PAUSE"
fi

echo "==> Play detected"

# ---------------------------------------------------------------------------
# NEXT
# ---------------------------------------------------------------------------

$ADB logcat -c

echo "==> Sending KEYCODE_MEDIA_NEXT (87)"

$ADB shell input keyevent 87 >/dev/null

if ! _wait_for_log "MUSIC_SKIPPED" 5; then
    _fail \
        "next (KEYCODE_MEDIA_NEXT) did not reach the session"
fi

echo "==> Next detected"

# ---------------------------------------------------------------------------
# DONE
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# LOG OUTPUT
# ---------------------------------------------------------------------------

echo ""
echo "============================================================"
echo " Android music smoke-test log"
echo "============================================================"

$ADB logcat -d -v brief 2>/dev/null |
    grep -iE \
        'MusicNotification|MUSIC_|MediaSession|MediaButton|python|AndroidRuntime' |
    tail -200 ||
    true

echo "============================================================"
echo ""

echo "PASS: music notification smoke test completed"