# Android Notify

`android_notify` is a Python module designed to simplify sending Android notifications using Kivy and Pyjnius. It supports multiple notification styles, including text, images, and inbox layouts.

## Features

- Send Android notifications with custom titles and messages.
- Support for multiple notification styles:
  - Big Text
  - Big Picture
  - Inbox
- Ability to include images in notifications.
- Compatible with Android 8.0+ (Notification Channels).
- Customizable notification channels.
- Support for large icons in notifications.

## Installation

Make sure you have the required dependencies installed:

```bash
pip install android-notify
```

## Usage

**Prerequisites:**  

- Buildozer  
- Kivy

In your **`buildozer.spec`** file, ensure you include the following:

```ini
# Add pyjnius so it's packaged with the build
requirements = python3,kivy,pyjnius

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependencies (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core:1.6.0
android.enable_androidx = True
```

### Example Notification

```python
from android_notify.core import send_notification

# Send a basic notification
send_notification("Hello", "This is a basic notification.")

# Send a notification with an image
send_notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    style='big_picture',
    img_path='assets/imgs/icon.png'
)

# Send a notification with inbox style
send_notification(
    title='Inbox Notification',
    message='Line 1\nLine 2\nLine 3',
    style='inbox'
)

# Send a Big Text notification (Note this send as a normal notification if not supported on said device)
send_notification(
    title='Hello!',
    message='This is a sample notification.',
    style='big_text'
)
```

### Function Reference

#### `send_notification`

- **title** (*str*): Notification title.
- **message** (*str*): Notification message body.
- **style** (*str*): Notification style (`big_text`, `big_picture`, `inbox`, `large_icon`).
- **img_path** (*str*): Path to the image (for `big_picture` or `large_icon` styles).
- **channel_id** (*str*): Notification channel ID.

#### `get_image_uri`

- Resolves the absolute URI of an image resource.
- **relative_path** (*str*): The relative path to the image.

### Advanced Usage

You can customize notification channels for different types of notifications.

```python
send_notification(
    title='Custom Channel Notification',
    message='This uses a custom notification channel.',
    channel_id='custom_channel'
)
```

## Contribution

Feel free to open issues or submit pull requests for improvements!

## 🐛 Reporting Issues

Found a bug? Please open an issue on our [GitHub Issues](https://github.com/Fector101/android_notify/issues) page.

## ☕ Support the Project

If you find this project helpful, consider buying me a coffee! Your support helps maintain and improve the project.

<a href="https://www.buymeacoffee.com/fector101" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60">
</a>

## Author

- Fabian - <fector101@yahoo.com>
- GitHub: <https://github.com/Fector101/android_notify>

## Acknowledgments

- Thanks to the Kivy and Pyjnius communities for their support.
