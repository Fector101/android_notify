print('install --> "https://github.com/Fector101/android_notify/archive/without-androidx.zip" for pydroid')

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
import os
import random

if platform == "android":
    from jnius import autoclass

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    context = PythonActivity.mActivity
    Notification = autoclass('android.app.Notification')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    PendingIntent = autoclass('android.app.PendingIntent')
    Intent = autoclass('android.content.Intent')
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    NotificationBuilder = autoclass('android.app.Notification$Builder')
    BigTextStyle = autoclass('android.app.Notification$BigTextStyle')
    InboxStyle = autoclass('android.app.Notification$InboxStyle')
    BigPictureStyle = autoclass('android.app.Notification$BigPictureStyle')
    Uri = autoclass('android.net.Uri')
else:
    print("Not running on Android. Notifications will be skipped.")


from android_notify import Notification,send_notification

class NotificationTestApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=20)

        message = "This is the main notification message."

        # Buttons for different styles
        styles = [
            ("Default", "", ""),  # style_text, extra message
            ("Big Text", "This is extra text for BigText style.", "bigtext"),
            ("Inbox", "Line 1\nLine 2\nLine 3", "inbox"),
            ("Big Picture", "", "light.jpeg"),  # replace with valid local path if testing big picture
        ]

        for text, extra, style_type in styles:
            btn = Button(text=text, size_hint=(1, 0.25))
            def callback(inst, t=text, m=message, e=extra, st=style_type):
                
                if st == "bigtext":
                    Notification(title=f"{t} Notification", message=m, body=e,channel_id="lame",channel_name="lame").send()
                    
                elif st == "inbox":
                    send_notification(title=f"{t} Notification", message=m, lines=e)
                elif st == "bigpicture":
                    # Replace with a valid path to test
                    send_notification(title=f"{t} Notification", message=m, big_picture_path=e)
                    
                    
                else:
                    send_notification(title=f"{t} Notification", message=m)
                
            btn.bind(on_release=callback)
            layout.add_widget(btn)

        return layout

if __name__ == "__main__":
    NotificationTestApp().run()
