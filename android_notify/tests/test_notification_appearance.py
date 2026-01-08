from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationAppearance(AndroidNotifyBaseTest):

    def test_custom_icon(self):
        try:
            n = Notification(id=self.uid, title="Icon", message="Custom")
            n.setSmallIcon("assets/icons/bell.png")
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

    def test_set_sub_text_and_set_when(self):
        try:
            n = Notification(id=self.uid, title="SubText and When", message="Testing")
            n.setSubText("101 secs left")
            n.setWhen(60 * 60)
            n.send()
        except Exception as e:
            self.fail(f"SubText failed: {e}")

    def test_text_color_both(self):
        try:
            n = Notification(title="Title and Message Color", message="Testing")
            n.title_color="red"
            n.message_color = "blue"
            n.send()
        except Exception as e:
            self.fail(f"test_text_color_both failed: {e}")

    def test_text_color_title(self):
        try:
            n = Notification(id=self.uid, title="Title Color", message="Testing Color")
            n.title_color = "red"
            n.send()
        except Exception as e:
            self.fail(f"Text Color Title failed: {e}")

    def test_text_color_msg(self):
        try:
            n = Notification(id=self.uid, title="Message Color", message="Testing Color")
            n.message_color = "red"
            n.send()
        except Exception as e:
            self.fail(f"Text Color Message failed: {e}")