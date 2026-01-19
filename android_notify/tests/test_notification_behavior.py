from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationBehavior(AndroidNotifyBaseTest):

    def test_set_priority(self):
        try:
            n = Notification(id=self.uid, title="setPriority method: high", message="High")
            n.setPriority("high")
            n.send()
        except Exception as e:
            self.fail(f"Set priority failed: {e}")

    def test_persistent(self):
        try:
            Notification(id=self.uid, title="Persistent: True", message="Testing").send(
                persistent=True
            )
        except Exception as e:
            self.fail(f"Persistent failed: {e}")

    def test_close_on_click(self):
        try:
            Notification(id=self.uid, title="Close false", message="Testing").send(
                close_on_click=False
            )
        except Exception as e:
            self.fail(f"Close on click failed: {e}")
