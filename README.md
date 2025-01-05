# Android Notify

`android_notify` is a Python module designed to simplify sending Android notifications using Kivy and Pyjnius. It supports multiple notification styles, including text, images, and inbox layouts.

## Features

- Send Android notifications with custom titles and messages.
- Support for multiple notification styles:
  - Big Text
  - Big Picture
  - Large Icon
  - Inbox
- Supports including images in notifications.
- Compatible with Android 8.0+ (Notification Channels).
- Customizable notification channels.

## Installation

This package is available on PyPI and can be installed via pip:

```bash
pip install android-notify
```

## **Dependencies**

**Prerequisites:**  

- Buildozer  
- Kivy

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add pyjnius so it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependencies (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core:1.6.0, androidx.core:core-ktx:1.15.0
android.enable_androidx = True
```

---

### Example Notification

#### Basic Notification

```python
from android_notify import send_notification

# Send a basic notification
send_notification("Hello", "This is a basic notification.")
```

**Example Image:**  
![basic notification img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/basicnoti.jpg)
#### Notification with an Image (Big Picture Style)

```python
# Send a notification with an image
send_notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    style='big_picture',
    img_path='assets/imgs/icon.png'
)
```

**Example Image:**
![big_picture img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/bigpicturenoti.jpg)
#### Notification with an Image (Large Icon Style)

```python
# Send a notification with Large Icon
send_notification(
    title='Completed download',
    message='profile.jpg',
    style='large_icon',
    img_path='assets/imgs/icon.png'
)
```

**Example Image:**  
![large_icon img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/large_icon.jpg)

#### Inbox Notification Style

```python
# Send a notification with inbox style
send_notification(
    title='Inbox Notification',
    message='Line 1\nLine 2\nLine 3',
    style='inbox'
)
```

**Example Image:**
![Inbox Notification sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/inboxnoti.jpg)

#### Big Text Notification

- (This will default to normal text if big text unsupported on device)

```python
# Send a Big Text notification
send_notification(
    title='Hello!',
    message='This is a sample notification.',
    style='big_text'
)
```
<!-- 
**Example Image:**  
![Big Text Notification sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/big_text.jpg) -->

---

### Advanced Usage

#### Channel Name (channel_name)

- Can be found in App Settings where user can turn on/off specific Notifications

```python
#  if not specified Channel Name default's to "Default Channel"
send_notification(
    title="Download finished"
    message="How to Catch a Fish.mp4"
    channel_name="Download Notifications"
)
```

**Sample Image:**  
![channels img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/channel_name.jpg)

#### Channel Name (channel_id)

You can customize notification channels for different types of notifications.(In later version channel_id will be used to reference notification)

```python
send_notification(
    title='Custom Channel Notification',
    message='This uses a custom notification channel.',
    channel_id='custom_channel'
)
```

---

### **Assist**

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
from android_notify import send_notification, NotificationStyles
send_notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    img_path='assets/imgs/icon.png'
    style=NotificationStyles.BIG_PICTURE,
)
```

---

### **Functions Reference**

### 1. `asks_permission_if_needed()`

**Description:**

- Checks if notification permissions are granted and requests them if missing.

**Usage:**

```python
asks_permission_if_needed()
```

---

### 2. `get_image_uri(relative_path)`

**Description:**

- Resolves the absolute URI for an image in the app's storage.

**Parameters:**

- `relative_path` *(str)*: Path to the image (e.g., `assets/imgs/icon.png`).

**Returns:**

- `Uri`: Android URI object for the image.

**Usage:**

```python
uri = get_image_uri('assets/imgs/icon.png')
```

---

### 3. `send_notification(title, message, style=None, img_path=None, channel_id='default_channel')`

**Description:**

- Sends an Android notification with optional styles and images.

**Parameters:**

- `title` *(str)*: Notification title.
- `message` *(str)*: Notification message.
- `style` *(str, optional)*: Notification style (`big_text`, `big_picture`, `inbox`, `large_icon`).
- `img_path` *(str, optional)*: Path to the image resource.(for `big_picture` or `large_icon` styles).
- `channel_id` *(str, optional)*: Notification channel ID.

Returns - notification id

## Contribution

Feel free to open issues or submit pull requests for improvements!

## 🐛 Reporting Issues

Found a bug? Please open an issue on our [GitHub Issues](https://github.com/Fector101/android_notify/issues) page.

## Author

- Fabian - <fector101@yahoo.com>
- GitHub: <https://github.com/Fector101/android_notify>
- Twitter: <https://x.com/CodewithFabian> -- 😊 I'm sure to answer

For feedback or contributions, feel free to reach out!

---

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! Or Giving it a star on 🌟 [GitHub](https://github.com/Fector101/android_notify/) Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>

---

## Acknowledgments

- This Project was "Made For Android" and thoroughly "Tested by" the [Laner Project](https://github.com/Fector101/Laner/) - Laner is an application that creates a secure connection between your PC and Phone to Transfer Files Wirelessly.
- Thanks to the Kivy and Pyjnius communities for their support.

---

## 🌐 **Links**

- **PyPI:** [android-notify on PyPI](https://pypi.org/project/android-notify/)
- **GitHub:** [Source Code Repository](https://github.com/Fector101/android_notify/)
