# from jnius import cast, autoclass
# import logging
# import traceback
# from android_notify import Notification

# android_notify.logger.setLevel(logging.INFO)
# logging.getLogger("android_notify").setLevel(logging.WARNING)
import unittest
import time, traceback
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button

from android_notify import Notification, NotificationHandler
from android_notify.core import asks_permission_if_needed

# ---- IMPORT YOUR SPLIT TEST FILES (TestCase CLASSES) ----
from android_notify.tests.android_notify_test import TestAndroidNotifyFull
from android_notify.tests.test_notification_styles import TestNotificationStyles
from android_notify.tests.test_notification_actions import TestNotificationActions
from android_notify.tests.test_basic_notifications import TestBasicNotifications
from android_notify.tests.test_notification_channels import TestNotificationChannels
from android_notify.tests.test_notification_appearance import TestNotificationAppearance
from android_notify.tests.test_notification_behavior import TestNotificationBehavior
from android_notify.tests.test_notification_progress import TestNotificationProgress
from android_notify.tests.test_notification_sound import TestNotificationSound
from android_notify.tests.test_notification_clear import TestClearNotifications
from android_notify.tests.test_notification_permission import NOTIFICATION_PERMISSION_TESTS
from kivy.clock import Clock

# -----------------------------
# Linux input fix
# -----------------------------
if platform == 'linux':
    from kivy import Config

    for option in Config.options('input'):
        if Config.get('input', option) == 'probesysfs':
            Config.remove_option('input', option)

    Window.size = (370, 700)


# -----------------------------
# Triple click button
# -----------------------------
class TripleClickButton(Button):
    def __init__(self, callback, max_interval=1.0, **kwargs):
        """
        :param callback: function to run after triple click
        :param max_interval: max seconds allowed between clicks
        """
        super().__init__(**kwargs)
        self.callback = callback
        self.max_interval = max_interval
        self._click_count = 0
        self._last_click_time = 0
        self.bind(on_release=self._on_release)

    def _on_release(self, instance):
        if not self.disabled:
            now = time.time()
            if now - self._last_click_time > self.max_interval:
                # Too much time since last click, reset counter
                self._click_count = 0
            self._click_count += 1
            self._last_click_time = now

            if self._click_count == 3:
                # Triple click reached
                self._click_count = 0
                self.disabled = True  # disable button immediately
                self.callback(self)


# -----------------------------
# App
# -----------------------------
class AndroidNotifyDemoApp(MDApp):

    def on_start(self):
        print('starting app...')
        try:
            from kivymd.toast import toast
            name = NotificationHandler.get_name(on_start=True)
            toast(text=f"name: {name}", length_long=True)
        except Exception as e:
            print("Error getting notify name:", e)

        print('on_start','-'*33)

        def android_service():

            try:
                import socket
                from android import mActivity
                from jnius import autoclass

                def get_free_port_():
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.bind(("", 0))  # bind to a random free port
                    port = s.getsockname()[1]
                    s.close()
                    return port

                port = get_free_port_()
                context = mActivity.getApplicationContext()
                service_name = "Wallpapercarousel"
                service = autoclass(context.getPackageName() + '.Service' + service_name.capitalize())
                service.start(mActivity,str(port))

            except Exception as error_call_service_on_start:
                print(error_call_service_on_start)
                traceback.print_exc()

        Clock.schedule_once(lambda dt: android_service(), 2)


    def build(self):
        root = ScrollView(do_scroll_x=False)

        main = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=10,
            spacing=10
        )
        main.bind(minimum_height=main.setter("height"))
        root.add_widget(main)

        # --- Control Buttons ---
        main.add_widget(self._btn("Ask Notification Permission", self.request_permission))
        main.add_widget(self._btn("Send Demo Notification", self.send_notification))

        # --- Test Buttons ---
        self.test_buttons = []  # keep reference for enabling/disabling

        tests = [
            ("Basic Notifications", TestBasicNotifications),
            ("Styles & Layouts", TestNotificationStyles),
            ("Buttons & Actions", TestNotificationActions),
            ("Channels", TestNotificationChannels),
            ("Appearance", TestNotificationAppearance),
            ("Behavior", TestNotificationBehavior),
            ("Progress", TestNotificationProgress),
            ("Sound", TestNotificationSound),
            ("Clear", TestClearNotifications),
            ("One Ring to", TestAndroidNotifyFull),
        ]

        for label, test_case in tests:
            btn = self._btn(f"Run Tests: {label}", lambda _, tc=test_case, b=None: self.run_test_case(tc, b))
            self.test_buttons.append(btn)
            main.add_widget(btn)

        # Permission request needs human inputs for tests
        for label, action in NOTIFICATION_PERMISSION_TESTS.items():
            btn = self._btn(
                f"Run: {label}",
                lambda _, fn=action: self.run_action(fn, _)
            )
            main.add_widget(btn)
        return root

    def run_action(self, action_fn, btn_instance):
        btn_instance.disabled = True
        print(f"\n▶ Running action: {action_fn.__name__}")

        try:
            action_fn()
        except Exception as error_running_action:
            print("error_running_action:", error_running_action)
            traceback.print_exc()
        finally:
            # Re-enable AFTER user interaction finishes
            btn_instance.disabled = False

    def _btn(self, text, callback, height=80):
        return TripleClickButton(
            text=text,
            height=dp(height),
            size_hint_y=None,
            callback=callback
        )

    # -----------------------------
    # Test runner
    # -----------------------------
    def run_test_case(self, test_case, button_instance=None):
        # Disable all test buttons while running
        for btn in self.test_buttons:
            btn.disabled = True

        print(f"\n▶ Running {test_case.__name__}")
        try:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)
        finally:
            # Re-enable all buttons after test finishes
            for btn in self.test_buttons:
                btn.disabled = False

    def request_permission(self, btn_instance):
        asks_permission_if_needed()
        btn_instance.disabled = False

    def send_notification(self, btn_instance):
        n = Notification(
            title="Hello",
            message="This is a basic notification.",
            channel_id="android_notify_demo",
            channel_name="Android Notify Demo"
        )
        n.title = f"{n.title} {n.id}"
        n.send()
        btn_instance.disabled = False

    def on_resume(self):
        print('resuming app..')
        try:
            from kivymd.toast import toast
            name = NotificationHandler.get_name()

            toast(text=f"name: {name}, Permission:{NotificationHandler.has_permission()}", length_long=True)
        except Exception as e:
            print("Error getting notify name:", e)
        print('on_resume','-'*33)



if __name__ == "__main__":
    AndroidNotifyDemoApp().run()
