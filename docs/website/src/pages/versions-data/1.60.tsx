import { IReferencePage } from "../../assets/js/mytypes";

const subtextcode = `from android_notify import Notification

notification = Notification(
    title="Downloading...",
    message="70% downloaded",
    progress_max_value=100
)
notification.setSubText("19 secs left")

notification.setColor("#00FF00")
notification.updateProgressBar(70)
notification.send()`
const an_colored_basic_small = `<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="0dp"
        android:layout_weight="1"
    />

</LinearLayout>`
const an_colored_basic_large = `<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <TextView
        android:id="@+id/title"
        android:layout_width="wrap_content"
        android:layout_height="0dp"
        android:layout_weight="1"

    />

    <TextView
        android:id="@+id/message"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginTop="4dp"
    />

</LinearLayout>`
const colored_text_code = `from android_notify import Notification

Notification(title="Title Color", message="Testing Color",title_color="red").send()`

const component_page = {
    sub_text_code: subtextcode,
    an_colored_basic_small,
    an_colored_basic_large,
    colored_text_code
}


const NOTIFICATION_METHODS = {
    addButton: {
        signature: 'addButton(text, on_release)',
        description: 'Adds an action button to the notification.',
        args: [
            { name: 'text', desc: 'Label for the button.' },
            { name: 'on_release', desc: 'Callback invoked when the button is tapped.' },
            { name: "receiver_name", desc: "Optional string to specify a custom BroadcastReceiver for the button action, defaults to None" },
            { name: "action", desc: "Optional string to specify a custom intent action for receiver_name BroadcastReceiver, defaults to None" }
        ]
    },
    setBigText: {
        signature: 'setBigText(body)',
        description: 'Sets a big text for when drop down button is pressed.',
        args: [
            { name: 'body', desc: 'The big text that will be displayed.' },
            { name: "title", desc: "You can also set title for big text style, if not provided it nothing displays." },
            { name: "summary", desc: "You can also set summary for big text style, if not provided it nothing displays." }
        ]
    },
    createChannel: {
        signature: 'createChannel(id, name:str, description?,importance:Importance?)',
        description: 'Creates a user visible toggle button for specific notifications, Required For Android 8.0+',
        args: [
            { name: 'id', desc: "Used to identify channel and send other notifications later through same channel." },
            { name: 'name', desc: "user-visible channel name." },
            { name: 'description', desc: "user-visible detail about channel (Not required defaults to empty str)." },
            { name: 'importance', desc: "['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly" },
            { name: 'vibrate', desc: "Boolean if to vibrate when sent for channel, defaults to False" },
            { name: 'sound', desc: "String of audio name in your app res/raw to be played when sent from channel, defaults to regular system notification sound" }
        ]
    },

    setWhen: {
        signature: 'setWhen(secs_ago)',
        description: 'Changes the time the notification was created, it accepts seconds ago as argument so that it can show up as if it was created in the past.',
        args: [
            { name: 'secs_ago', desc: "Int of Seconds ago from current time, it can be used to make notification look like it was created in the past." }
        ]
    },
    channelExists: {
        signature: 'channelExists(channel_id)',
        description: 'Checks if a channel with given id exists',
        args: [
            { name: 'channel_id', desc: "id for specific channel" }
        ]
    },
    doChannelsExist: {
        signature: 'doChannelsExist(ids)',
        description: 'Accepts a list of channel IDs and returns those that do not exist',
        args: [
            { name: 'ids', desc: "List of channel ids" }
        ]
    },
    setSubText: {
        signature: 'setSubText(text)',
        description: 'Adds small text near the title (e.g. download time remaining).',
        args: [
            { name: 'text', desc: "The subtext that will be displayed." }
        ]
    },
    setColor: {
        signature: 'setColor(color)',
        description: 'changes app icon color using hex code.',
        args: [
            { name: 'color', desc: "either string (red,green,blue) or color in hex code." }
        ]
    },
    setData: {
        signature: 'setData(data_object)',
        description: 'Attach a dictionary of data for possible later use.',
        args: [
            { name: 'data_object', desc: "A dictionary of data that can be accessed later via NotificationHandler's data_object property." }
        ]
    },
    fVibrate: {
        signature: 'fVibrate(pattern)',
        description: 'For when regular notifications vibrate turned off in device settings (useful for Alarms). Uses Single 500ms vibration for pattern.',// not provided.',
        args: [
            // { name: 'pattern', desc: "Vibration pattern, it accepts a list of ints representing vibration and pause durations in milliseconds, defaults to a single vibration of 500ms if not provided." }
        ]
    },
    fill_args: {
        signature: 'fill_args(**kwargs)',
        description: <>Takes same Arguments as send method, Returns builder object.<br /> It fills notification args without sending, useful for when you want to fill arguments without sending right away.<br /> For example calling startForeground from service you need to pass in notification.id and builder.build.</>,
        args: [
            { name: '**kwargs', desc: "Same arguments as send method." }
        ]
    },
    setVibrate: {
        signature: 'setVibrate(pattern)',
        description: 'For devices less than Android 8, sets vibration pattern for notification, defaults to a single vibration of 500ms if not provided.',
        args: [
            { name: 'pattern', desc: "Vibration pattern, it accepts a list of ints representing vibration and pause durations in milliseconds, defaults to a single vibration of 500ms if not provided." }
        ]
    },
    setSound: {
        signature: 'setSound(res_sound_name)',
        description: 'For devices less than Android 8, changes the default notification sound to a custom sound from app resources.',
        args: [
            { name: 'res_sound_name', desc: "The name of the sound resource in your app (without file extension)." }
        ]
    }

};


const HANDLER_METHODS = [
    {
        id: 'get_name',
        signature: 'NotificationHandler.get_name()',
        description:
            'Returns the unique string `name` or `id` for the notification or button that opened the app.',
        args: [
            { name: 'on_start', desc: 'must be True when called from App.on_start(), defaults to False.' },
        ]
    },

];


export const getting_identifer = `
from kivymd.app import MDApp
from android_notify import Notification, NotificationHandler


def use_name(name):
    if name == 'change_app_page':
        # Code to change Screen
        pass
    elif name == 'change_app_color':
        # Code to change Screen Color
        pass


class Myapp(MDApp):

    def on_start(self):
        name = NotificationHandler.get_name(on_start=True)
        use_name(name)

    def build(self):
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
        use_name(name)`

const advanced_methods_page = {
    getting_identifier_code: getting_identifer,
}


// const reference_page = {
//     NOTIFICATION_METHODS,
//     HANDLER_METHODS
// }


const reference_page: IReferencePage = {
    NOTIFICATION_METHODS,
    HANDLER_METHODS,
    STYLE_ATTRIBUTES: undefined
};

export { component_page, reference_page, advanced_methods_page }
