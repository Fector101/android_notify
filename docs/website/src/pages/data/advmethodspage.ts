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

notification = Notification(
    title="title",
    style="message"
)
notification.send()

# Add Image
notification.large_icon_path="users/imgs/profile1234.png"
notification.addNotificationStyle(
    NotificationStyles.LARGE_ICON,
    already_sent=True
)
`