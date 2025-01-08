<div align="center">
    <br>
    <h1> Android-Notifiy </h1>
    <p> A Python library for effortlessly creating and managing Android notifications in Kivy android apps.</p>
    <p>Supports various styles and ensures seamless integration and customization.</p>
    <!-- <br> -->
    <!-- <img src="https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/democollage.jpg"> -->
</div>

## Features

- Also Compatible with Android 8.0+.
- Supports including images in notifications.
- Support for multiple notification styles:
  - [Simple](#basic-usage)
  - [Progress](#progress-bar-notification)
  - [Big Picture](#notification-with-an-image-big-picture-style)
  - [Inbox](#inbox-notification-style)
  - [Large Icon](#notification-with-an-image-large-icon-style)
  - [Big Text](#big-text-notification-will-display-as-simple-text-if-device-dosent-support)

This module automatically handles:

- Permission requests for notifications
- Customizable notification channels.

## Installation

This package is available on PyPI and can be installed via pip:

```bash
pip install android-notify
```

## **Dependencies**

**Prerequisites:**  

- Kivy

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add pyjnius so ensure it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependencies (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core:1.6.0, androidx.core:core-ktx:1.15.0
android.enable_androidx = True
```

---

## Basic Usage

```python
from android_notify import Notification

# Create a simple notification
notification = Notification(
    title="Hello",
    message="This is a basic notification."
)
notification.send()
```

**Sample Image:**  
![basic notification img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/basicnoti.jpg)

## Notification Styles

The library supports multiple notification styles:

1. `simple` - Basic notification with title and message
2. `progress` - Shows a progress bar
3. `big_text` - Expandable notification with long text
4. `inbox` - List-style notification
5. `big_picture` - Notification with a large image
6. `large_icon` - Notification with a custom icon
7. `both_imgs` - Combines big picture and large icon
8. `custom` - For custom notification styles

### Style Examples

#### Progress Bar notification

```python
import time
notification = Notification(
    title="Downloading...",
    message="0% downloaded",
    style="progress",
    progress_max_value=100,
    progress_current_value=0
)
notification.send()
time.sleep(350)
notification.updateProgressBar(30, "30% downloaded")
```

**Sample Image:**
![progress img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/progress.jpg)

#### Notification with an Image (Big Picture Style)

```python
# Image notification
notification = Notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    style="big_picture",
    big_picture_path="assets/imgs/photo.png"
)
notification.send()

```

**Sample Image:**
![big_picture img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/bigpicturenoti.jpg)

#### Inbox Notification Style

```python
# Send a notification with inbox style
notification = Notification(
    title='Inbox Notification',
    message='Line 1\nLine 2\nLine 3',
    style='inbox'
)
notification.send()

```

**Sample Image:**
![Inbox Notification sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/inboxnoti.jpg)

#### Big text notification (Will Display as simple text if Device dosen't support)

```python
notification = Notification(
    title="Article",
    message="Long article content...",
    style="big_text"
)
```

#### Notification with an Image (Large Icon Style)

```python
notification = Notification(
    title="Completed download",
    message="profile.jpg",
    style="large_icon",
    large_icon_path="assets/imgs/profile.png"
)

```

**Sample Image:**  
![large_icon img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/large_icon.jpg)

## Advanced Features

### Updating Notifications

```python
notification = Notification(title="Initial Title")
notification.send()

# Update title
notification.updateTitle("New Title")

# Update message
notification.updateMessage("New Message")
```

### Progress Bar Management

```python
notification = Notification(
    title="Download..",
    style="progress"
)

# Update progress
notification.updateProgressBar(30, "30% downloaded")

# Remove progress bar
notification.removeProgressBar("Download Complete")
```

### Channel Management

Notifications are organized into channels. You can customize the channel name and ID:

- Custom Channel Name's Gives User ability to turn on/off specific

```python
notification = Notification(
    title="Download finished",
    message="How to Catch a Fish.mp4",
    channel_name="Download Notifications",  # Will create User-visible name "Download Notifications"
    channel_id="downloads_notifications"  # Optional: specify custom channel ID
)
```

**Sample Image:**  
![channels img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/channel_name.jpg)

### Silent Notifications

To send a notification without sound or heads-up display:

```python
notification = Notification(title="Silent Update")
notification.send(silent=True)
```

### Assist

- How to Copy image to app folder

```python
import shutil,os # These modules come packaged with python
from android.storage import app_storage_path # type: ignore -- This works only on android 

app_path = os.path.join(app_storage_path(),'app')
image_path= "/storage/emulated/0/Download/profile.png"

shutil.copy(image_path, os.path.join(app_path, "profile.png"))
```

- Avoiding Human Error when using different notification styles

```python
from android_notify import Notification, NotificationStyles
Notification(
    title="New Photo",
    message="Check out this image",
    style=NotificationStyles.BIG_PICTURE,
    big_picture_path="assets/imgs/photo.png"
).send()
```

## Development Mode

When developing on non-Android platforms, the library provides debugging output:

```python
# Enable logs (default is True when not on Android)
Notification.logs = True

# Create notification for testing
notification = Notification(title="Test")
notification.send()
# Will print notification properties instead of sending
```

## Image Requirements

- Images must be located within your app's folder
- Supported paths are relative to your app's storage path
- Example: `assets/imgs/icon.png`

## Error Handling

The library validates arguments and provides helpful error messages:

- Invalid style names will suggest the closest matching style
- Invalid arguments will list all valid options
- Missing image files will raise FileNotFoundError with the attempted path

## Limitations

1. Only works on Android devices
2. Images must be within the app's storage path
3. Channel names are limited to 40 characters
4. Channel IDs are limited to 50 characters

## Best Practices

1. Always handle permissions appropriately
2. Use meaningful channel names for organization
3. Keep progress bar updates reasonable (don't update too frequently)
4. Test notifications on different Android versions
5. Consider using silent notifications for frequent updates

## Debugging Tips

1. Enable logs during development: `Notification.logs = True`
2. Check channel creation with Android's notification settings
3. Verify image paths before sending notifications
4. Test different styles to ensure proper display

Remember to check Android's notification documentation for best practices and guidelines regarding notification frequency and content.

## Contribution

Feel free to open issues or submit pull requests for improvements!

## Reporting Issues

Found a bug? Please open an issue on our [GitHub Issues](https://github.com/Fector101/android_notify/issues) page.

## Author

- Fabian - <fector101@yahoo.com>
- GitHub: [Android Notify Repo](https://github.com/Fector101/android_notify)
- Twitter: [FabianDev_](https://twitter.com/intent/user?user_id=1246911115319263233)

For feedback or contributions, feel free to reach out!

---

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! 😊 Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>

---

## Acknowledgments

- This Project was thoroughly Tested by the [Laner Project](https://github.com/Fector101/Laner/) - A application for Securely Transfering Files Wirelessly between your PC and Phone.
- Thanks to the Kivy and Pyjnius communities.

---

## 🌐 **Links**

- **PyPI:** [android-notify on PyPI](https://pypi.org/project/android-notify/)
- **GitHub:** [Source Code Repository](https://github.com/Fector101/android_notify/)
