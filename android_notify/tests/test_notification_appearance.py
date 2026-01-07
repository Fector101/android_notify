from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationAppearance(AndroidNotifyBaseTest):

    def test_custom_icon(self):
        try:
            n = Notification(id=self.uid, title="Icon", message="Custom")
            n.setSmallIcon("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Custom icon failed: {e}")

    def test_set_color(self):
        try:
            n = Notification(title="Color", message="Colored icon")
            n.setColor("red")
            n.send()
        except Exception as e:
            self.fail(f"Set color failed: {e}")

    def test_set_sub_text(self):
        try:
            n = Notification(id=self.uid, title="SubText", message="Testing")
            n.setSubText("101 secs left")
            n.send()
        except Exception as e:
            self.fail(f"SubText failed: {e}")

    def test_set_when(self):
        try:
            n = Notification(title="When", message="Testing")
            n.setWhen(60 * 60)
            n.send()
        except Exception as e:
            self.fail(f"Set when failed: {e}")
