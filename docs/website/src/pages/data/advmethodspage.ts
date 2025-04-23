export const title_and_message_update=`notification = Notification(title="Initial Title")
notification.send()

# Update title
notification.updateTitle("New Title")

# Update message
notification.updateMessage("New Message")`

export const progress_bar_update=`# Changes progress-bar values
notification.updateProgressBar(
    current_value=30,
    message="30KB/100KB",
    title='Download update... 30%'
)
# Remove progress bar
# show_on_update to notification briefly after removed progressbar
notification.removeProgressBar("Download Complete",show_on_update=True)
`
export const adding_image_code=`from android_notify import NotificationStyles
from kivy.clock import Clock

notification = Notification(
    title="title",
    style="message"
)
notification.send()

# Add Image
def addImg(dt):
    notification.large_icon_path="users/imgs/profile1234.png"
    notification.addNotificationStyle(
        NotificationStyles.LARGE_ICON,
        already_sent=True
    )
Clock.schedule_once(addImg,5)
`

export const channel_management_code=`Notification(
    title="Download finished",
    message="How to Catch a Fish.mp4",
    channel_name="Download Notifications",  # Will create User-visible name "Download Notifications"
    channel_id="downloads_notifications"  # Optional: specify custom channel ID
)
`
export const getting_identifer=`
from kivymd.app import MDApp
from android_notify import Notification, NotificationHandler

class Myapp(MDApp):
    
    def on_start(self):
        Notification(
            title="Change Page",
            message="Click to change App page.",
            identifer='change_app_page'
        ).send()

        Notification(
            title="Change Color",
            message="Click to change App Color",
            identifer='change_app_color'
        ).send()

    def on_resume(self):
        # Is called every time app is reopened
        notify_identifer = NotificationHandler.getIdentifer()
        if notify_identifer == 'change_app_page':
            # Code to change Screen
            pass
        elif notify_identifer == 'change_app_color':
            # Code to change Screen Color
            pass`