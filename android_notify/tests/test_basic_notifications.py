import time
from android_notify import Notification,send_notification
from android_notify.widgets.texts import set_title, set_message
from .base_test import AndroidNotifyBaseTest, secs3, secs5


class TestBasicNotifications(AndroidNotifyBaseTest):



    def test_core(self):
        send_notification("Hello from core", "Message from core")

    def test_cancel_with_id(self):
        try:
            n = Notification(id=self.uid, title="Cancel with id", message="Cancel")
            n.send()
            time.sleep(secs3)
            n.cancel(_id=n.id)
        except Exception as e:
            self.fail(f"Cancel with id failed: {e}")

    def test_refresh(self):

        try:
            n = Notification(id=self.uid, title="Testing refresh", message="Refresh")
            set_title(n.builder, "New Title from refresh")
            n.send()
            set_message(n.builder, "New Message from refresh")
            time.sleep(secs3)
            n.refresh()
        except Exception as e:
            self.fail(f"Refresh failed: {e}")

    def test_title_message_update(self):
        try:
            n = Notification(id=self.uid, title="Old Title", message="Old Message")
            n.send()
            time.sleep(secs5)
            n.updateTitle("New Title")
            n.updateMessage("New Message")
        except Exception as e:
            self.fail(f"Update title/message failed: {e}")
