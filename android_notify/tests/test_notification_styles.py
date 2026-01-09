from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationStyles(AndroidNotifyBaseTest):

    def test_big_text(self):
        try:
            n = Notification(id=self.uid, title="Big Text", message="Testing")
            n.setBigText("Lorem ipsum big text style")
            n.send()
        except Exception as e:
            self.fail(f"Big text failed: {e}")

    def test_big_picture(self):
        try:
            n = Notification(id=self.uid, title="Big Picture", message="Testing")
            n.setBigPicture("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Big picture failed: {e}")

    def test_both_imgs(self):
        try:
            n = Notification(id=self.uid, title="Both Images", message="Testing")
            n.setLargeIcon("assets/icons/icon.png")
            n.setBigPicture("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Both images failed: {e}")

    def test_inbox(self):
        try:
            n = Notification(id=self.uid, title="Inbox", message="Inbox")
            n.setLines(["Line 1", "Line 2", "Line 3"])
            n.send()
        except Exception as e:
            self.fail(f"Inbox failed: {e}")

    def test_inbox_add_line(self):
        try:
            n = Notification(id=self.uid, title="Inbox addLine", message="Testing")
            n.addLine("First")
            n.addLine("Second")
            n.addLine("Third")
            n.send()
        except Exception as e:
            self.fail(f"Inbox addLine failed: {e}")
