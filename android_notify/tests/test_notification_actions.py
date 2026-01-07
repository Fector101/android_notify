from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationActions(AndroidNotifyBaseTest):

    def test_buttons(self):
        try:
            n = Notification(id=self.uid, title="Buttons", message="Testing")
            n.addButton("Play", on_release=lambda: print("Play"))
            n.addButton("Pause", on_release=lambda: print("Pause"))
            n.addButton("Stop", on_release=lambda: print("Stop"))
            n.send()
        except Exception as e:
            self.fail(f"Buttons failed: {e}")

    def test_buttons_broadcast(self):
        try:
            n = Notification(id=self.uid, title="Broadcast Buttons", message="Testing")
            n.addButton("Play", receiver_name="CarouselReceiver", action="ACTION_PLAY")
            n.addButton("Pause", receiver_name="CarouselReceiver", action="ACTION_PAUSE")
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
