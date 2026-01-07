
import unittest, threading
from android_notify.tests.android_notify_test import TestAndroidNotifyFull
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from android_notify import Notification, NotificationHandler
from android_notify.core import asks_permission_if_needed
# android_notify.logger.setLevel(logging.INFO)
# logging.getLogger("android_notify").setLevel(logging.WARNING)

if platform == 'linux':
    from kivy import Config

    # Linux has some weirdness with the touchpad by default... remove it
    options = Config.options('input')
    for option in options:
        if Config.get('input', option) == 'probesysfs':
            Config.remove_option('input', option)
    Window.size = (370, 700)




class AndroidNotifyDemoApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.count = 0

    def on_start(self):
        print("on_start...")
        try:
            from kivymd.toast import toast
            name = NotificationHandler.get_name(on_start=True)
            print("name", name)
            toast(text=f"name: {name}", length_long=True)
        except Exception as error_getting_notify_name:
            print("Error getting notify name:", error_getting_notify_name)

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        layout.add_widget(Button(
            text="Ask Notification Permission",
            on_release=self.request_permission
        ))
        layout.add_widget(Button(
            text="Send Notification",
            on_release=self.send_notification
        ))
        layout.add_widget(Button(
            text="Mass Test",
            on_release=self.mass_test
        ))
        return layout

    def mass_test(self, *args):
        def run_tests():
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAndroidNotifyFull)
            unittest.TextTestRunner(verbosity=2).run(suite)

        if self.count == 3:
            self.count = 0
            # threading.Thread(target=run_tests, daemon=True).start()
            run_tests()
        self.count += 1

    def request_permission(self, *args):
        asks_permission_if_needed()

    def send_notification(self, *args):
        N = Notification(
            title="Hello",
            message="This is a basic notification.",
            channel_id="android_notify_demo",
            channel_name="Android Notify Demo"
        )
        N.title = N.title +' '+ str(N.id)
        N.send()

    def on_resume(self):
        print("on_resume...")
        try:
            from kivymd.toast import toast
            name = NotificationHandler.get_name()
            print("name", name)
            toast(text=f"name: {name}", length_long=True)
        except Exception as error_getting_notify_name:
            print("Error getting notify name:", error_getting_notify_name)


if __name__ == "__main__":
    AndroidNotifyDemoApp().run()
