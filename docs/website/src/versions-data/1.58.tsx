const bigimgcode = `from android_notify import NotificationStyles

notification = Notification(
    title='Picture Alert!',
    message='This notification includes an image.',
    style=NotificationStyles.BIG_PICTURE,
    big_picture_path="assets/imgs/photo.png"
)
notification.send()
`
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
const largeiconcode = `from android_notify import NotificationStyles
notification = Notification(
    title="FabianDev_",
    message="A twitter about some programming stuff",
    style=NotificationStyles.LARGE_ICON,
    large_icon_path="assets/imgs/profile.png"
)`
const inboxcode = `from android_notify import NotificationStyles
notification = Notification(
    title='Inbox Notification',
    message='Line 1\\\\nLine 2\\\\nLine 3',
    style=NotificationStyles.INBOX,
)
notification.send()
`
// TODO : add a gif for big-text notification
// FIXME : type loerm ipsum typos
const bigtextcode = `from android_notify import NotificationStyles
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
const appiconcode = `Notification(
    app_icon="assets/icons/download.png",
    title="Custom Icon",
    message="Also persist notification test"
).send(persistent=True)`



// Advanced Methods Page

export const title_and_message_update = "notification = Notification(title='Initial Title')\nnotification.send()\n\n# Update title\nnotification.updateTitle('New Title')\n\n# Update message\nnotification.updateMessage('New Message')"

export const progress_bar_update = "# Changes progress-bar values\nnotification.updateProgressBar(\n    current_value=30,\n    message='30KB/100KB',\n    title='Download update... 30%'\n)\n# Remove progress bar\n# show_on_update to notification briefly after removed progressbar\nnotification.removeProgressBar('Download Complete',show_on_update=True)\n"
export const adding_image_code = "from android_notify import NotificationStyles\nfrom kivy.clock import Clock\n\nnotification = Notification(\n    title='title',\n    style='message'\n)\nnotification.send()\n\n# Add Image\ndef addImg(dt):\n    notification.large_icon_path='users/imgs/profile1234.png'\n    notification.addNotificationStyle(\n        NotificationStyles.LARGE_ICON,\n        already_sent=True\n    )\nClock.schedule_once(addImg,5)\n"

export const channel_management_code = "Notification(\n    title='Download finished',\n    message='How to Catch a Fish.mp4',\n    channel_name='Download Notifications',  # Will create User-visible name 'Download Notifications'\n    channel_id='downloads_notifications'  # Optional: specify custom channel ID\n)\n"
export const getting_identifer = "\nfrom kivymd.app import MDApp\nfrom android_notify import Notification, NotificationHandler\n\nclass Myapp(MDApp):\n\n    def on_start(self):\n        Notification(\n            title='Change Page',\n            message='Click to change App page.',\n            identifer='change_app_page'\n        ).send()\n\n        Notification(\n            title='Change Color',\n            message='Click to change App Color',\n            identifer='change_app_color'\n        ).send()\n\n    def on_resume(self):\n        # Is called every time app is reopened\n        notify_identifer = NotificationHandler.getIdentifer()\n        if notify_identifer == 'change_app_page':\n            # Code to change Screen\n            pass\n        elif notify_identifer == 'change_app_color':\n            # Code to change Screen Color\n            pass"


// Reference Page
const NOTIFICATION_METHODS = [
    {
        id: 'init',
        signature: "init\n        title: str = ''\n        message: str = ''\n        style: str = 'simple'\n        big_picture_path: str = ''\n        large_icon_path: str = ''\n        progress_current_value: int = 0\n        progress_max_value: int = 100\n        body: str = ''\n        callback: Callable=None\n        channel_name: str = ''\n        channel_id: str = ''\n        app_icon: str = ''\n        logs: bool = True\n",
        description: 'Initializes the notification instance.',
        args: [
            { name: 'title', desc: 'string containing notification title' },
            { name: 'message', desc: 'string containing notification message' },
            { name: 'style', desc: "can be ['simple','progress','inbox','big_text','large_icon','big_picture','both_imgs']" },
            { name: 'big_picture_path', desc: "path or url to big image (for \`BIG_PICTURE\` style)" },
            { name: 'large_icon_path', desc: "path or url to image (for \`LARGE_ICON\` style)" },
            { name: 'progress_current_value', desc: "integer to set progress bar current value (for \`PROGRESS\` style)." },
            { name: 'progress_max_value', desc: "integer for max range for progress value." },
            { name: 'body', desc: "Detailed text (for \`BIG_TEXT\` style)." },
            { name: 'callback', desc: "Function executed on notification tap." },
            { name: 'channel_name', desc: "Human-readable channel name." },
            { name: 'channel_id', desc: "Used to later reference Channel when sending each notification (extracted from channel name if provided or defaults to 'default_channel')." },
            { name: 'app_icon', desc: 'If not specified, defaults to the app icon. To change it, use a PNG—otherwise it will render as a black box.' },
            { name: 'logs', desc: 'Enable debug logs when not on Android.' },

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
            'Shows an indeterminate progress bar. Remove with \`removeProgressBar()\` or update with \`updateProgressBar()\`.',
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
        id: 'updateTitle',
        signature: 'updateTitle(new_title)',
        description: 'Updates the notification title.',
        args: [
            { name: 'new_title', desc: 'String for the new title.' }
        ]
    }
];

const HANDLER_METHODS = [
    {
        id: 'getIdentifer',
        signature: 'NotificationHandler.getIdentifer()',
        description:
            'Returns the unique string identifier for the notification or button that opened the app.'
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
        description: 'Removes the listener set by \`bindNotifyListener()\`.',
    },
    {
        id: 'is_on_android',
        signature: 'NotificationHandler.is_on_android()',
        description:
            'Returns \`true\` if running on Android, \`false\` otherwise—useful for platform checks.'
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
    how_to_add_both_imgs: <p className="paragraph">For Both Images pass in <span className="code">NotificationStyles.BOTH_IMGS</span> as argument to <span className="code">style</span> and provide both paths</p>,
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
            'Updating Notification':"updating-notification",
            'Adding Image':"adding-image",
            'Channel Management':"channel-management",
            'Getting Identifer':"getting-identifer"
        }
    },
    {
        title: 'Reference',
        route: '/reference',
        sections: {
            'Notification Class':"notification-class",
            'NotificationHandler Class':"notificationhandler-class",
            'NotificationStyles Class':"notificationstyles-class"
        }
    },
    {
        title: 'Extras',
        route: '/extras',
        sections: {
            'How to update': 'how-to-update',
            'Debugging Tips': 'debugging-tips',
            'Contributing-Issues': 'contributing-issues',
            'Support Project': 'support-project',
            'Credits': 'credits',

        }
    },


]

export { component_page, advanced_methods_page, reference_page }
