# Installation

The package is available on PyPI. Pick the platform you are building for and get going in seconds:

:::{code-tabs}
PIP
```bash
pip install android-notify
```

Kivy
```ini
# Add requirements list
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# AndroidX is optional - the library auto-detects it at runtime and
# falls back to the built-in Android APIs when it is not present.
```

Flet
```toml
[tool.flet.android]
dependencies = [
  "pyjnius", "android-notify"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```

Pydroid 3
```
# In the Pydroid 3 pip section, add:
android-notify
```
:::

## Kivy apps

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add requirements list
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# AndroidX is optional - the library auto-detects it at runtime and
# falls back to the built-in Android APIs when it is not present.
```

## Flet apps

In your `pyproject.toml` file, ensure you include the following:

```toml
[tool.flet.android]
dependencies = [
  "pyjnius", "android-notify"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```

See an example of a [complete flet pyproject.toml](https://github.com/Fector101/flet-app/blob/main/pyproject.toml).

## On Pydroid 3

The [Pydroid 3](https://play.google.com/store/apps/details?id=ru.iiec.pydroid3) mobile app lets you run Python code on Android, where some features can be tested.

- In the pip section where you're asked to insert `Libary name`, paste `android-notify`.
- Minimal working example:

```python
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android_notify import Notification, NotificationHandler


class AndroidNotifyDemoApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Button(
            text="Ask Notification Permission",
            on_release=self.request_permission
        ))
        layout.add_widget(Button(
            text="Send Notification",
            on_release=self.send_notification
        ))
        return layout

    def request_permission(self, *args):
        NotificationHandler.asks_permission()

    def send_notification(self, *args):
        Notification(
            title="Hello from Android Notify",
            message="This is a basic notification."
        ).send()


if __name__ == "__main__":
    AndroidNotifyDemoApp().run()
```

## Desktop

For IDE IntelliSense, the package can be installed via pip on a normal desktop Python:

```bash
pip install android_notify
android-notify -v
```

## Command-line interface

Installing the package on desktop also installs an `android-notify` command:

```bash
android-notify --version   # or -v, prints the installed version
android-notify --help
```

To remove old `android_notify` build artifacts (stale `android_notify-*.*.*` folders inside `.buildozer/android/platform/build-*` that are no longer part of the requirements) when the build folder gets large:

```bash
android-notify prune          # clean the current project's .buildozer
android-notify prune -p path  # point at a specific project directory
```

`prune` scans the `.buildozer` build paths, lists every `android_notify*` item it finds, and asks for confirmation before deleting anything; nothing is removed without your `y`. The `buildozer` builds themselves are left intact.

## Dev version

To use the latest development version from GitHub:

```ini
requirements = python3, kivy, pyjnius, https://github.com/Fector101/android_notify/archive/main.zip
```