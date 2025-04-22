const bigimgcode=`from android_notify import NotificationStyles

notification = Notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    style=NotificationStyles.BIG_PICTURE,
    big_picture_path="assets/imgs/photo.png"
)
notification.send()
`
const progressbarcode=`from android_notify import NotificationStyles
from kivy.clock import Clock

progress = 0

notification = Notification(
    title="Downloading...",
    message="0% downloaded",
    style=NotificationStyles.PROGRESS,
    progress_current_value=0,progress_max_value=100
    )
notification.send()

def update_progress(dt):
    global progress
    progress = min(progress + 10, 100)
    notification.updateProgressBar(
        progress, f"{progress}% downloaded"
    )
    return progress < 100  # Stops when reaching 100%

Clock.schedule_interval(update_progress, 3)
`
const largeiconcode=`from android_notify import NotificationStyles
notification = Notification(
    title="FabianDev_",
    message="A twitter about some programming stuff",
    style=NotificationStyles.LARGE_ICON,
    large_icon_path="assets/imgs/profile.png"
)`
const inboxcode=`from android_notify import NotificationStyles
notification = Notification(
    title='Inbox Notification',
    message='Line 1\\nLine 2\\nLine 3',
    style=NotificationStyles.INBOX,
)
notification.send()
`
// TODO : add a gif for inbox notification
// FIXME : type loerm ipsum typos
const bigtextcode=`from android_notify import NotificationStyles
notification = Notification(
    title="Article",
    message="Histroy of Loerm Ipsuim",
    body="Lorem Ipsum is simply dummy text of the printing and ...",
    style=NotificationStyles.BIG_TEXT
)`
const buttons_code = `notification = Notification(
    title="Jane Dough",
    message="How to use android-notify #coding #purepython"
)
def playVideo():
    print('Playing Video')

def turnOffNoti():
    print('Please Turn Off Updates')

def watchLater():
    print('Add to Watch Later')

notification.addButton(text="Play",on_release=playVideo)
notification.addButton(text="Turn Off",on_release=turnOffNoti)
notification.addButton(text="Watch Later",on_release=watchLater)
notification.send()`

export {bigimgcode,buttons_code,progressbarcode,largeiconcode,inboxcode,bigtextcode}