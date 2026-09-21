from android_notify import Notification
from .base_test import AndroidNotifyBaseTest, toast

class TestNotificationActions(AndroidNotifyBaseTest):

    def test_buttons(self):
        try:
            n = Notification(id=self.uid, title="Buttons", message="Testing")
            n.addButton("Play", on_release=lambda: toast("Play"))
            n.addButton("Pause", on_release=lambda: toast("Pause"))
            n.addButton("Stop", on_release=lambda: toast("Stop"))
            n.send()
        except Exception as e:
            self.fail(f"Buttons failed: {e}")

    def test_buttons_broadcast(self):
        try:
            n = Notification(id=self.uid, title="Broadcast Buttons", message="Testing")
            n.addButton("Play", receiver_name="CarouselReceiver", action="ACTION_PLAY")
            n.addButton("Pause", receiver_name="CarouselReceiver", action="ACTION_PAUSE")
            n.addButton("Nothing", receiver_name="CarouselReceiver", action="NOT_IN_XML")
            n.send()
        except Exception as e:
            self.fail(f"Broadcast buttons failed: {e}")

    def test_custom_name(self):
        try:
            Notification(
                id=self.uid,
                title="Custom name",
                message="Click me",
                name="change_app_page"
            ).send()
        except Exception as e:
            self.fail(f"Custom name failed: {e}")

    def test_custom_name1(self):
        try:
            Notification(
                id=self.uid,
                title="Custom name",
                message="Click me",
                name="change_page_color"
            ).send()
        except Exception as e:
            self.fail(f"Custom name1 failed: {e}")

    def test_callback(self):
        try:
            Notification(
                id=self.uid,
                title="With Callback",
                message="Tap to run callback",
                callback=lambda: toast("Callback invoked")
            ).send()
        except Exception as e:
            self.fail(f"Callback failed: {e}")

    def test_callback1(self):
        try:
            Notification(
                id=self.uid,
                title="With Callback Dude",
                message="Tap to run callback Dude",
                callback=lambda: toast("I'm callback, I ran Dude")
            ).send()
        except Exception as e:
            self.fail(f"Callback failed: {e}")