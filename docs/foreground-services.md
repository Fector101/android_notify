# Foreground Services

A foreground service keeps running even when the app is in the background. Android forces it to show a persistent notification, and you are responsible for posting that notification yourself.

Instead of calling `send()` from a service, call `fill_args()` to fill the notification's arguments into a builder **without posting it**, then pass `builder.build()` to `service.startForeground()`:

```python
from android_notify import Notification
from android_notify.config import get_python_service
from android_notify.internal.java_classes import BuildVersion, autoclass

service = get_python_service()

foreground_type = 0
if BuildVersion.SDK_INT >= 34:
    # Required type on Android 14+ (SDK 34), 0 on older devices
    ServiceInfo = autoclass("android.content.pm.ServiceInfo")
    foreground_type = ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE

Notification.createChannel(
    id="service_channel",
    name="Carousel Service",
    description="For Controlling and Previewing Next Wallpaper",
)

notification = Notification(
    title="Starting Carousel...",
    name="from service",
    channel_id="service_channel",
)

builder = notification.fill_args()  # fill args into the builder (nothing posted yet)
service.startForeground(notification.id, builder.build(), foreground_type)
service.setAutoRestartService(True)
```

## Register the service in buildozer.spec

Declare the service in your `buildozer.spec` with the format `Name:path/to/service.py:foreground`. Append `:foregroundServiceType=specialUse` so the type is written into `AndroidManifest.xml` automatically:

```ini
services = CarouselService:./android/services/wallpaper.py:foreground:foregroundServiceType=specialUse
```

The service file lives inside your `source.dir` (e.g. `app_src/android/services/wallpaper.py`).

## Add the required permissions

Add `FOREGROUND_SERVICE` and `POST_NOTIFICATIONS`. When using the `specialUse` type also add `FOREGROUND_SERVICE_SPECIAL_USE`:

```ini
android.permissions = FOREGROUND_SERVICE, FOREGROUND_SERVICE_SPECIAL_USE, POST_NOTIFICATIONS
```

Other foreground service types need their matching permission, e.g. `FOREGROUND_SERVICE_DATA_SYNC` for `dataSync`. Declaring the type in the manifest without its permission, or starting a service without a type on Android 14+, fails with `MissingForegroundServiceTypeException`.

## Foreground service types (Android 14+)

Types are needed on some Android levels. From Android 14 (SDK 34) a foreground service type must be passed as the third argument to `startForeground()` and be declared in the manifest. On older devices pass `0`.

Pick the type that matches what the service does. `specialUse` covers purposes that don't fit the other types and requires declaring why in the `FOREGROUND_SERVICE_SPECIAL_USE` permission.

See the official Android docs:

- [Android 14: Foreground service types required](https://developer.android.com/about/versions/14/changes/fgs-types-required)
- [Foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Foreground services overview](https://developer.android.com/develop/background-work/services/fgs)

## Real-world example

This page follows the production app [Wallpaper Carousel](https://github.com/Fector101/wallpaper-carousel), which runs a foreground service for previewing and changing wallpapers. You can see the full setup (service file, buildozer.spec, p4a hook, broadcast receivers) there.

The service file above is the exact pattern used: create a channel, fill the notification args, then call `service.startForeground(notification.id, builder.build(), foreground_type)`.