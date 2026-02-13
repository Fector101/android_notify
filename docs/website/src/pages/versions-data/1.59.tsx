const bigimgcode = `from android_notify import Notification

notification = Notification(
    title='Picture Alert!',
    message='This notification includes an image.'
)
notification.setBigPicture("assets/imgs/photo.png")
notification.send()`

const progressbarcode = `from kivy.clock import Clock

progress = 0

notification = Notification(
    title="Downloading...",
    message="0% downloaded",
    progress_current_value=0,progress_max_value=100
    )
#notification.send()

def update_progress(dt):
    global progress
    progress = min(progress + 10, 100)
    
    if progress==100:
        notification.removeProgressBar(title="File Downloaded", message="super_large_file.zip")
    elif progress >= 80:
        notification.showInfiniteProgressBar()
    else:
        notification.updateProgressBar(progress, f"{progress}% downloaded")

        return progress < 100  # Stops when reaching 100%

Clock.schedule_interval(update_progress, 3)`

const largeiconcode = `from android_notify import Notification

notification = Notification(
    title="FabianDev_",
    message="A twitter about some programming stuff"
)
notification.setLargeIcon("assets/imgs/profile.png")
notification.send()`
const inboxcode = `notification = Notification(
    title="5 New mails from Frank",
    message="Check them out",
)
notification.addLine("Re: Planning")
notification.addLine("Delivery on its way")
notification.addLine("Follow-up")
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

const appiconcode = `notification = Notification(
    title="custom icon notification",
    message="using .setSmallIcon to set notification icon"
)
notification.setSmallIcon("icons/butterfly.png")
notification.send(persistent=True) # how to persistent notification`



// Advanced Methods Page


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
const NOTIFICATION_METHODS = {
    init: {
        args: [
            { name: 'body -- use setBigText() instead', desc: "Detailed text (for `BIG_TEXT` style)." },            
            { name: 'lines_txt -- use addLine() instead', desc: "Lines of text for (for `INBOX` style) each line should be separated by '\\n'." },
        ]
    },
    
    addLine:{
        signature: 'addLine(text)',
        description: 'sets text for new line for inbox-style notification',
        args: [
            { name: 'text', desc: 'String for new line of text.' }
        ]
    },
    setBigPicture: {
        signature: 'setBigPicture(path)',
        description: 'set a Big Picture at the bottom.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    setLargeIcon:{
        signature: 'setLargeIcon(path)',
        description: 'sets Large icon to the right.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    setSmallIcon:{
        signature: 'setSmallIcon(path)',
        description: 'sets small icon to the top left.',
        args: [
            { name: 'path', desc: 'Image can be `Relative Path` or `URL`.' }
        ]
    },
    setBigText:{
        signature: 'setBigText(body)',
        description: 'Sets a big text for when drop down button is pressed.',
        args: [
            { name: 'body', desc: 'The big text that will be displayed.' }
        ]
    },
    setLines:{
        signature: 'setLines(lines)',
        description: 'Sets a inbox lines texts for when drop down button is pressed, each string will be in a new line',
        args: [
            { name: 'lines', desc: "The List of texts that'll be used to create new lines." }
        ]
    },

    createChannel:{
        signature: 'createChannel(id, name:str, description?,importance:Importance?)',
        description: 'Creates a user visible toggle button for specific notifications, Required For Android 8.0+',
        args: [
            { name: 'id', desc: "Used to identify channel and send other notifications later through same channel." },
            { name: 'name', desc: "user-visible channel name." },
            { name: 'description', desc: "user-visible detail about channel (Not required defaults to empty str)." },
            { name: 'importance', desc: "['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly" },
        ]
    },

    deleteChannel:{
        signature: 'deleteChannel(channel_id)',
        description: 'Uses channel_id to delete notification channel',
        args: [
            { name: 'channel_id', desc: "id for specific channel" }
        ]
    },
    deleteAllChannel:{
        signature: 'deleteAllChannel()',
        description: 'Delete All notification channels',
        args: []
    },
    cancel:{
        signature: 'cancel(_id)',
        description: 'Removes Notification instance from tray.',
        args: [
            { name: '_id', desc: "Not required uses instance id as default" }
        ]
    },
    cancelAll:{
        signature: 'cancelAll()',
        description: 'Removes App Notifications from tray.',
        args: []
    },
    setPriority:{
        signature: 'setPriority(importance)',
        description: 'Sets <div className="reference">Importance</div> For devices less than android 8.',
        args: [
            { name: 'importance', desc: "['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly." }
        ]
    },
};

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
    // {
    //     id: 'simple',
    //     signature: 'NotificationStyles.DEFAULT',
    //     description: 'contains default style "simple"'
    // },
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
    progressbar_code: progressbarcode,
    inbox_style_code: inboxcode,
    big_text_style_code: bigtextcode
}

const advanced_methods_page = {
    adding_image_code,
    channel_management_code,
    getting_identifier_code: getting_identifer,
}

const reference_page = {
    NOTIFICATION_METHODS, HANDLER_METHODS, STYLE_ATTRIBUTES
}


export const Sidebar = [
    {
        title: 'Getting Started',
        route: '/getting-started',
        sections: {
            'Introduction': 'introduction',
            'Features': 'features',
            'Installation': 'installation',
            'Basic Usage': 'basic-usage'
        }
    },
    {
        title: 'Components',
        route: '/components',
        sections: {
            'Images': 'images',
            'Buttons': 'buttons',
            'Progress Bars': 'progress-bars',
            'Texts': 'texts'
        }
    },
    {
        title: 'Advanced Methods',
        route: '/advanced-methods',
        sections: {
            'Updating Notification': 'updating-notification',
            'Adding Image': 'adding-image',
            'Channel Management': 'channel-management',
            'Getting Identifer': 'getting-identifer'
        }
    },
    {
        title: 'Reference',
        route: '/reference',
        sections: {
            'Notification Class': 'notification-class',
            'NotificationHandler Class': 'notificationhandler-class',
            'NotificationStyles Class': 'notificationstyles-class'
        }
    },
    {
        title: 'Help',
        route: '/help',
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