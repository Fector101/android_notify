const bigimgcode = `from android_notify import Notification

notification = Notification(
    title='Picture Alert!',
    message='This notification includes an image.'
)
notification.setBigPicture("assets/imgs/photo.png")
notification.send()`

const progressbarcode = `from android_notify import NotificationStyles
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
const largeiconcode = `from android_notify import Notification

notification = Notification(
    title="FabianDev_",
    message="A twitter about some programming stuff"
)
notification.setLargeIcon("assets/imgs/profile.png")
notification.send()`
const inboxcode = `from android_notify import NotificationStyles
notification = Notification(
    title='Inbox Notification',
    message='Line 1\\nLine 2\\nLine 3',
    style=NotificationStyles.INBOX,
)
notification.send()
`
// TODO : add a gif for big-text notification
// FIXME : type loerm ipsum typos
const bigtextcode = `notification = Notification(
    title="Article",
    message="Histroy of Loerm Ipsuim",
)
notification.setBigText("Lorem Ipsum is simply dummy text of the printing and ...")
notification.send()`
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
const appiconcode = `notification = Notification(
    title="custom icon notification",
    message="using .setSmallIcon to set notification icon"
)
notification.setSmallIcon("icons/butterfly.png")
notification.send(persistent=True) # how to persistent notification`



// Advanced Methods Page

export const title_and_message_update = `notification = Notification(title="Initial Title")
notification.send()

# Update title
notification.updateTitle("New Title")

# Update message
notification.updateMessage("New Message")`

export const progress_bar_update = `# Changes progress-bar values
notification.updateProgressBar(
    current_value=30,
    message="30KB/100KB",
    title='Download update... 30%'
)
# Remove progress bar
# show_on_update to notification briefly after removed progressbar
notification.removeProgressBar("Download Complete",show_on_update=True)
`
export const adding_image_code = `from kivy.clock import Clock

notification = Notification(
    title="title",
    style="message"
)
notification.send()

# Add Image
def addImg(dt):
    notification.setLargeIcon("assets/imgs/profile.png")
    notification.refresh()
Clock.schedule_once(addImg,5)
`

export const channel_management_code = `Notification.createChannel(
    channel_id="downloads_notifications",
    channel_name="Download Notifications"  # Will create User-visible name "Download Notifications"
    description="For Receiving download info" # v1.59
)
Notification(
    title="Download finished",
    message="How to Catch a Fish.mp4",
    channel_id="downloads_notifications"
)
`
export const getting_identifer = `
from kivymd.app import MDApp
from android_notify import Notification, NotificationHandler

class Myapp(MDApp):
    
    def on_start(self):
        Notification(
            title="Change Page",
            message="Click to change App page.",
            name='change_app_page'
        ).send()

        Notification(
            title="Change Color",
            message="Click to change App Color",
            name='change_app_color'
        ).send()

    def on_resume(self):
        # Is called every time app is reopened
        name = NotificationHandler.get_name()
        if name == 'change_app_page':
            # Code to change Screen
            pass
        elif name == 'change_app_color':
            # Code to change Screen Color
            pass`


// Reference Page
const NOTIFICATION_METHODS = [
    {
        id: 'init',
        signature: `init
	title: str = ''
	message: str = ''

	app_icon: str = ''
	callback: Callable=None

    \t# Progress-Bar
	progress_max_value: int = 100
	progress_current_value: int = 0

    \t# Style related
	style: str = 'simple'
	big_picture_path: str = ''
	large_icon_path: str = ''
	body: str = ''

    \t# Channel related
	channel_name: str = ''
	channel_id: str = ''

	logs: bool = True
`,
        description: 'Initializes the notification instance.',
        args: [
            { name: 'title', desc: 'string containing notification title' },
            { name: 'message', desc: 'string containing notification message' },
            { name: 'progress_current_value', desc: "integer to set progress bar current value (for `PROGRESS` style)." },
            { name: 'progress_max_value', desc: "integer for max range for progress value." },
            { name: 'style', desc: "can be ['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs]" },
            { name: 'big_picture_path', desc: "path or url to big image (for `BIG_PICTURE` style)" },
            { name: 'large_icon_path', desc: "path or url to image (for `LARGE_ICON` style)" },
            { name: 'body -- use setBigText() instead', desc: "Detailed text (for `BIG_TEXT` style)." },
            { name: 'callback', desc: "Function executed on notification tap." },
            { name: 'channel_name', desc: "Human-readable channel name." },
            { name: 'channel_id', desc: "Channel id (sanitized from name if not provided)." },
            { name: 'app_icon', desc: 'If not specified, defaults to the app icon. To change it, use a PNG—otherwise it will render as a black box.' },
            { name: 'logs', desc: 'Enable debug logs when not on Android.' },

        ]
    },
    {
        id: 'updateTitle',
        signature: 'updateTitle(new_title)',
        description: 'Updates the notification title.',
        args: [
            { name: 'new_title', desc: 'String for the new title.' }
        ]
    },
    {
        id: 'updateMessage',
        signature: 'updateMessage(new_message)',
        description: 'Updates the notification message.',
        args: [
            { name: 'new_message', desc: 'String for the new message.' }
        ]
    },
    {
        id: 'setBigPicture',
        signature: 'setBigPicture(path)',
        description: 'set a Big Picture at the bottom.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    {
        id: 'setLargeIcon',
        signature: 'setLargeIcon(path)',
        description: 'sets Large icon to the right.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    {
        id: 'setSmallIcon',
        signature: 'setSmallIcon(path)',
        description: 'sets small icon to the top left.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    {
        id: 'setBigText',
        signature: 'setBigText(body)',
        description: 'Sets a big text for when drop down button is pressed.',
        args: [
            { name: 'body', desc: 'The big text that will be displayed.' }
        ]
    },
    {
        id: 'addButton',
        signature: 'addButton(text, on_release)',
        description: 'Adds an action button to the notification.',
        args: [
            { name: 'text', desc: 'Label for the button.' },
            { name: 'on_release', desc: 'Callback invoked when the button is tapped.' }
        ]
    },
    {
        id: 'removeButtons',
        signature: 'removeButtons()',
        description: 'Removes all action buttons from the notification.'
    },
    {
        id: 'removeProgressBar',
        signature: 'removeProgressBar(message?, show_on_update?, title?)',
        description:
            'Removes the progress bar and (optionally) updates the title/message.',
        args: [
            { name: 'message', desc: '(Optional) New message; defaults to last.' },
            {
                name: 'show_on_update',
                desc: 'If true, briefly shows the updated notification. Defaults to true.'
            },
            { name: 'title', desc: '(Optional) New title; defaults to last.' }
        ]
    },
    {
        id: 'send',
        signature: 'send(silent?, persistent?, close_on_click?)',
        description: 'Dispatches the notification.',
        args: [
            { name: 'silent', desc: 'If true, suppresses the heads-up alert.' },
            { name: 'persistent', desc: 'If true, the notification survives “Clear All.”' },
            { name: 'close_on_click', desc: 'If true, tapping the notification dismisses it.' }
        ]
    },
    {
        id: 'showInfiniteProgressBar',
        signature: 'showInfiniteProgressBar()',
        description:
            'Shows an indeterminate progress bar. Remove with `removeProgressBar()` or update with `updateProgressBar()`.'
    },

    {
        id: 'addNotificationStyle',
        signature: 'addNotificationStyle(style, already_sent?)',
        description:
            'Applies or updates a notification style (big_text, inbox, images, etc.).',
        args: [
            {
                name: 'style',
                desc:
                    "One of ['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs']"
            },
            {
                name: 'already_sent',
                desc: 'If true, re-dispatches the notification so style changes appear immediately.'
            }
        ]
    },
    {
        id: 'updateProgressBar',
        signature: 'updateProgressBar(current_value, message?, title?, cooldown?)',
        description:
            'Updates a determinate progress bar (0 – max). Internally throttled to 0.5 s.',
        args: [
            { name: 'current_value', desc: 'Current progress (number).' },
            { name: 'message', desc: '(Optional) New message; defaults to last.' },
            { name: 'title', desc: '(Optional) New title; defaults to last.' },
            { name: 'cooldown', desc: "Defaults to 0.5secs,buffer time for when changes happen too fast, shouldn't be changed unless tested on specific device" }
        ]
    },
    
    {
        id: 'createChannel(cls, ):',
        signature: 'createChannel(id, name:str, description?,importance:Importance?)',
        description: 'Creates a user visible toggle button for specific notifications, Required For Android 8.0+',
        args: [
            { name: 'id', desc: "Used to identify channel and send other notifications later through same channel." },
            { name: 'name', desc: "user-visible channel name." },
            { name: 'description', desc: "user-visible detail about channel (Not required defaults to empty str)." },
            { name: 'importance', desc: "['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly" },
        ]
    },
    
    {
        id: 'deleteChannel',
        signature: 'deleteChannel(channel_id)',
        description: 'Uses channel_id to delete notification channel',
        args: [
            { name: 'channel_id', desc: "id for specific channel" }
        ]
    },
    {
        id: 'deleteAllChannel',
        signature: 'deleteAllChannel()',
        description: 'Delete All notification channels',
        args: []
    },
    {
        id: 'cancel',
        signature: 'cancel(_id)',
        description: 'Removes Notification instance from tray.',
        args: [
            { name: '_id', desc: "Not required uses instance id as default" }
        ]
    },
    {
        id: 'cancelAll',
        signature: 'cancelAll()',
        description: 'Removes App Notifications from tray.',
        args: []
    },
    {
        id: 'setPriority',
        signature: 'setPriority(importance)',
        description: 'Sets <div className="reference">Importance</div> For devices less than android 8.',
        args: [
            { name: 'importance', desc: "['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly." }
        ]
    },
];

const HANDLER_METHODS = [
    {
        id: 'get_name',
        signature: 'NotificationHandler.get_name()',
        description:
            'Returns the unique string `name` or `id` for the notification or button that opened the app.'
    },
    {
        id: 'bindNotifyListener',
        signature: 'NotificationHandler.bindNotifyListener()',
        description:
            'Binds by Default, Attaches a global listener to notification taps—your callbacks will fire when any notification is tapped.'
    },
    {
        id: 'unbindNotifyListener',
        signature: 'NotificationHandler.unbindNotifyListener()',
        description: 'Removes the listener set by `bindNotifyListener()`.'
    },
    {
        id: 'is_on_android',
        signature: 'NotificationHandler.is_on_android()',
        description:
            'Returns `true` if running on Android, `false` otherwise—useful for platform checks.'
    }
];

const STYLE_ATTRIBUTES = [
    {
        id: 'simple',
        signature: 'NotificationStyles.DEFAULT',
        description: 'contains default style "simple"'
    },
    {
        id: 'LARGE_ICON',
        signature: 'NotificationStyles.LARGE_ICON',
        description: "contains 'large_icon' value",
    },
    {
        id: 'BIG_PICTURE',
        signature: 'NotificationStyles.BIG_PICTURE',
        description: "contains 'big_picture' value",
    },
    {
        id: 'BOTH_IMGS',
        signature: 'NotificationStyles.BOTH_IMGS',
        description: "contains 'both_imgs' value",
    },
    {
        id: 'PROGRESS',
        signature: 'NotificationStyles.PROGRESS',
        description:
            "contains 'progress' value"
    },
    {
        id: 'INBOX',
        signature: 'NotificationStyles.INBOX',
        description: "contains 'inbox' value",
    },
    {
        id: 'BIG_TEXT',
        signature: 'NotificationStyles.BIG_TEXT',
        description: "contains 'big_text' value",
    },
];



// Containers

const component_page = {
    big_picture_code: bigimgcode,
    large_icon_code: largeiconcode,
    how_to_add_both_imgs: <p className="paragraph">For Both Images use <span className="code">Notification.setBigPicture</span> and <span className="code">Notification.setLargeIcon</span> together</p>,
    small_icon_code: appiconcode,
    buttons_code,
    progressbar_code: progressbarcode,
    inbox_style_code: inboxcode,
    big_text_style_code: bigtextcode
}

const advanced_methods_page = {
    title_and_message_update_code: title_and_message_update,
    progress_bar_update_code: progress_bar_update,
    adding_image_code,
    channel_management_code,
    getting_identifier_code: getting_identifer,
}

const reference_page = {
    NOTIFICATION_METHODS, HANDLER_METHODS, STYLE_ATTRIBUTES
}


export const Sidebar= [
    {
        title: 'Getting Started',
        route: '/getting-started',
        sections: {
            'Introduction':'introduction',
            'Features':'features',
            'Installation':'installation',
            'Basic Usage':'basic-usage'
        }
    },
    {
        title: 'Components',
        route: '/components',
        sections: {
            'Images':'images',
            'Buttons':'buttons',
            'Progress Bars':'progress-bars',
            'Texts':'texts'
        }
    },
    {
        title: 'Advanced Methods',
        route: '/advanced-methods',
        sections: {
            'Updating Notification':'updating-notification',
            'Adding Image':'adding-image',
            'Channel Management':'channel-management',
            'Getting Identifer':'getting-identifer'
        }
    },
    {
        title: 'Reference',
        route: '/reference',
        sections: {
            'Notification Class':'notification-class',
            'NotificationHandler Class':'notificationhandler-class',
            'NotificationStyles Class':'notificationstyles-class'
        }
    }
]

export { component_page, advanced_methods_page, reference_page }
// export {bigimgcode,buttons_code,progressbarcode,largeiconcode,inboxcode,bigtextcode,appiconcode}