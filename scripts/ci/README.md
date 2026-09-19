# Android music notification smoke stack

End-to-end test for the `android-notify-music-bridge` AAR shipped to Maven local, modeled
on [KivMob's](https://github.com/MichaelStott/KivMob) dockerized emulator harness.

What it does (single entry point):

```bash
./scripts/ci/docker_android_test.sh
```

1. Publish `io.github.fector101:android-notify-music-bridge` to your host `~/.m2`
   (via `docker_gradle_bridge.sh`, `cimg/android` image → Gradle 8.14.3 wrapper → AGP 8.11.0).
2. `build_music_apk.sh` copies the local `android_notify` package into `music-smoke/`,
   then builds `music-smoke/bin/smokemusic-0.1-arm64...-debug.apk` with the `kivy/buildozer`
   image. The generated Gradle project resolves the bridge through `mavenLocal()`
   (`music-smoke/buildozer.spec` → `android.gradle_dependencies`).
3. Starts the `halimqarroum/docker-android:api-33-playstore` emulator (KVM passthrough)
   and waits for boot.
4. `emulator_music_test.sh` (in the `smoke` service) installs the APK, starts the app, and
   asserts logcat markers:
   - `MUSIC_BRIDGE_OK` – bridge class `org.android_notify.music.MediaSessionCallback`
     resolved from the AAR (no legacy `android.add_src`),
   - `MUSIC_NOTIFICATION_BUILT` – media notification posted,
   - `MUSIC_PLAYING` / `MUSIC_STATE: pause|play` – audio plays and
     `KEYCODE_MEDIA_PLAY_PAUSE`/`::KEYCODE_MEDIA_NEXT` reach the Java `MediaSession` callback.

## Prerequisites (host)

- Docker Engine with **/dev/kvm** usable by containers (`ls -l /dev/kvm`; on WSL2/VM enable
  nested virtualization). Docker Desktop's own emulation is too slow — native Docker preferred.
- ~10 GB free disk, ≥ 4 GB RAM dedicated to the emulator

## Useful env vars

| Variable | Default | Meaning |
| --- | --- | --- |
| `ANDROID_EMU_MEMORY` | `4096` | emulator RAM MiB |
| `ANDROID_EMU_SHM` | `2gb` | `/dev/shm` size |
| `ANDROID_EMU_CORES` | `2` | vCPU count |
| `ANDROID_EMU_PARTITION_MB` | `4096` | AVD partition size |
| `ANDROID_BOOT_TIMEOUT` | `600` | boot deadline (seconds) |
| `LOG_TIMEOUT` | `180` | logcat marker deadline (seconds) |
| `ANDROID_GRADLE_IMAGE` | `cimg/android:2025.12.1` | Gradle/SDK image |
| `DOCKER_IMAGE` | `kivy/buildozer:latest` | buildozer image |
| `ANDROID_EMU_IMAGE` | `halimqarroum/docker-android:api-33-playstore` | emulator image |
| `SKIP_AUTH` | `true` | emulator auth bypass |

## Individual steps

```bash
./scripts/ci/ensure_docker_emulator.sh        # up + healthy emulator (host side)
./scripts/ci/open_emulator_display.sh          # scrcpy view of the emulator screen
./scripts/ci/docker_gradle_bridge.sh           # publish bridge AAR to ~/.m2
./scripts/ci/build_music_apk.sh                # build the smoke APK
```

Note: Play Store emulator images need shared adb keys — `ensure_docker_adb_keys.sh`
creates `.docker-android/keys/` (gitignored) and the compose file pins them on both the
emulator and the `smoke` container.

## Troubleshooting

- Emulator `Killed` (OOM): `./scripts/ci/docker_compose.sh -f docker-compose.android.yml down -v`
  then retry with `ANDROID_EMU_MEMORY=2048 ANDROID_EMU_SHM=1gb`.
- `adb device unauthorized`: delete `.docker-android/keys` (new keys reset the AVD volume
  automatically on next run) or `docker compose -f docker-compose.android.yml down -v`.
- AVD lock from a previous run: `docker compose -f docker-compose.android.yml down -v`.
- Bridge not resolved at compile time: confirm `~/.m2/io/github/fector101/.../1.0.0/`
  exists; the smoke spec only needs the `mavenLocal()` repo currently.