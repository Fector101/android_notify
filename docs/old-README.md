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
- All Notifications can take Functions (version 1.50+) [functions section](#functions).
- Advanced Notification Handling [section](#advanced-features).
- Changing default app notification icon with PNG,
- Support for multiple notification styles:
  - [Simple](#basic-usage)
  - [Progress](#progress-bar-notification)
  - [Big Picture](#notification-with-an-image-big-picture-style)
  - [Inbox](#inbox-notification-style)
  - [Large Icon](#notification-with-an-image-large-icon-style)
  - [Buttons](#notification-with-buttons)
  - [Big Text](#big-text-notification)

- persistenting notification [section](#methods)

This module automatically handles:

- Permission requests for notifications
- Customizable notification channels.
- Opening app on notification click

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
android.api = 35
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
3. `big_picture` - Notification with a large image
4. `large_icon` - Notification with a custom icon
5. `both_imgs` - Combines big picture and large icon
6. `inbox` - List-style notification
7. `big_text` - Expandable notification with long text
8. `custom` - For custom notification styles

### Style Examples

#### Progress Bar notification

```python
from kivy.clock import Clock

progress = 0

notification = Notification(
    title="Downloading...", message="0% downloaded",
    style= "progress",
    progress_current_value=0,progress_max_value=100
    )
notification.send()

def update_progress(dt):
    global progress
    progress = min(progress + 10, 100)
    notification.updateProgressBar(progress, f"{progress}% downloaded")
    return progress < 100  # Stops when reaching 100%

Clock.schedule_interval(update_progress, 3)
```

**Sample Image:**
![progress img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/progress.jpg)

#### Images

##### Notification with an Image (Big Picture Style)

> [!NOTE]
> Online Images should start with `http://` or `https://`  
> And request for permission, `android.permissions = INTERNET`  
> No additionally permissions needed for images in App folder

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

##### Notification with an Image (Large Icon Style)

```python
notification = Notification(
    title="FabianDev_",
    message="A twitter about some programming stuff",
    style="large_icon",
    large_icon_path="assets/imgs/profile.png"
)

```

**Sample Image:**  
![large_icon img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/large_icon.jpg)

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

#### Notification with Buttons

Here's a sample of how to add buttons below, To Remove Buttons Simply Call the `removeButtons` method on the Notification Instance

```python
notification = Notification(title="Jane Dough", message="How to use android-notify #coding #purepython")
def playVideo():
    print('Playing Video')

def turnOffNoti():
    print('Please Turn OFf Noti')

def watchLater():
    print('Add to Watch Later')

notification.addButton(text="Play",on_release=playVideo)
notification.addButton(text="Turn Off",on_release=turnOffNoti)
notification.addButton(text="Watch Later",on_release=watchLater)
notification.send()
```

**Sample Image:**  
![btns img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/btns.jpg)

#### Big text notification

When using `big_text` style `message` acts as sub-title, Then when notification drop down button is pressed `body` is revealed

```python
notification = Notification(
    title="Article",
    message="Histroy of Loerm Ipsuim",
    body="Lorem Ipsum is simply dummy text of the printing and ...",
    style="big_text"
)
```

![big_text img sample](https://raw.githubusercontent.com/Fector101/android_notify/main/docs/imgs/big_text.jpg)

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
# send notification
notification.send()

# Update progress
notification.updateProgressBar(30, "30% downloaded")

# Remove progress bar
# show_on_update to notification briefly after removed progressbar
notification.removeProgressBar("Download Complete",show_on_update=True)
```

### Adding Style even when already sent

This is how you add a new style to notification, If already sent or not

```python
from android_notify import NotificationStyles

notification = Notification(
    title="Download..",
    style="progress"
)
notification.send()

notification.updateTitle("Download Completed")
notification.removeProgressBar()

# Add New Style
notification.large_icon_path="users/imgs/profile1234.png"
notification.addNotificationStyle(NotificationStyles.LARGE_ICON,already_sent=True)

```

### Channel Management

Notifications are organized into channels. You can customize the channel name and ID:

- Custom Channel Name's Gives User ability to turn on/off specific notifications

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

## Functions

```python
from kivymd.app import MDApp
from android_notify import Notification

class Myapp(MDApp):

    def on_start(self):
        Notification(title="Hello", message="This is a basic notification.",callback=self.doSomething).send()

    def doSomething(self):
        print("print in Debug Console")
```

### Get Which Notification was used to Open App - identifer (str)

If you just want to get the Exact Notification Clicked to Open App, you can use NotificationHandler to get unique identifer

```python
from kivymd.app import MDApp
from android_notify import Notification, NotificationHandler

class Myapp(MDApp):
    
    def on_start(self):
        
        notify = Notification(title="Change Page", message="Click to change App page.", identifer='change_app_page')
        notify.send()

        notify1 = Notification(title="Change Colour", message="Click to change App Colour", identifer='change_app_color')
        notify1.send()

    def on_resume(self):
        # Is called everytime app is reopened
        notify_identifer = NotificationHandler.getIdentifer()
        if notify_identifer == 'change_app_page':
            # Code to change Screen
            pass
        elif notify_identifer == 'change_app_color':
            # Code to change Screen Color
            pass
```

### Assist

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

#### To Use New Version Of Android-Notify

To be safe Delete All Old Versions of Android-Notify from `.buildozer` directory

##### On Linux run

`cd .buildozer && find . -type d -name "android_notify*" -print0 | xargs -0 rm -r && cd ..`

##### On Windows (PowerShell) run

- If command prints right folder paths Replace `Write-Output` with `Remove-Item`

```sh
cd .buildozer
Get-ChildItem -Path . -Directory -Filter "android_notify*" | ForEach-Object { Write-Output $_.FullName }
cd ..
```

##### On Windows Git Bash (if installed)

`cd .buildozer && find . -type d -name "android_notify*" -print0 | xargs -0 rm -r && cd ..`

##### On macOS run

`cd .buildozer && find . -type d -name "android_notify*" -exec rm -r {} + && cd ..`

### Development Mode

#### For Logs

When developing on non-Android platforms, the library provides debugging output:

```python
# Enable logs (default is True when not on Android)
Notification.logs = True

# Create notification for testing
notification = Notification(title="Test")
notification.send()
# Will print notification properties instead of sending
```

### Methods

### Instance.**init**

args

- app_icon: If not specified defaults to app icon, To Change Default app icon use PNG format Or Image Will display as a Black Box

### Instance.send

args

- persistent : To make notification stay after user clicks clear All
- close_on_click : To close notification on click

### Instance.addButton

args

- text : Button Text

### Instance.updateTitle

args

- new_title : String to be set as New notification Title

### Instance.updateMessage

args

- new_message : String to be set as New notification Message

### Instance.showInfiniteProgressBar

Displays an Infinite Progress Bar in Notification, Can be Removed using `removeProgressBar` and updated using `updateProgressBar` method

### Instance.updateProgressBar

if updating title,msg with progressbar frequenlty pass them in too to avoid update issues.
According to android docs updates shouldn't be too frequent.

`updateProgressBar` has a built-in delay of 0.5 secs

args

- current_value (str): the value from progressbar current progress
- message (str,optional): defaults to last message
- title (str,optional): defaults to last title

### Instance.removeProgressBar

This Removes Progress bar

args

- message (str, optional): notification message, Defaults to 'last message'.
- show_on_update (bool, optional): To show notification brifely when progressbar removed. Defaults to True.
- title (str, optional): notification title, Defaults to 'last title'.

### Instance.addNotificationStyle

This is useful to add style after Notification is sent or Add more styles to Notification
args

- style: choosen style. All options are in the `NotificationStyles` class `['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs]`
- already_sent: specfiy if notification.send() method has already been called, it defaults to false

## Image Requirements

- Online Images should start with `http://` or `https://`
- Local Images must be located within your app's folder

## Error Handling

The library validates arguments and provides helpful error messages:

- Invalid style names will suggest the closest matching style
- Invalid arguments will list all valid options
- Missing image files will list all files in App Directory

## Limitation

1. Only works on Android devices

## Best Practices

1. Always handle permissions appropriately
2. use `NotificationStyles` to set `style`, use `style=NotificationStyles.LARGE_ICON` instead of `style="large_icon"`
3. Use meaningful channel names for organization
4. Keep progress bar updates reasonable (don't update too frequently)
5. Test notifications on different Android versions
6. Consider using silent notifications for frequent updates

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
