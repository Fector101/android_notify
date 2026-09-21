import time
from android_notify import Notification, send_notification
from .base_test import AndroidNotifyBaseTest, secs3


class TestClearNotifications(AndroidNotifyBaseTest):


    def test_cancel(self):
        try:
            n = Notification(id=self.uid, title="Cancel in 3s", message="Cancel")
            n.send()
            s=secs3
            for i in range(0,secs3):
                time.sleep(1)
                s-=1
                n.updateTitle(f"Cancel in {s}s")

            n.cancel()
            time.sleep(secs3)
        except Exception as e:
            self.fail(f"Cancel failed: {e}")

    def test_cancel_with_id(self):
        try:
            n = Notification(id=self.uid, title="Cancel with id", message="Cancel")
            n.send()
            time.sleep(secs3)
            Notification().cancel(_id=n.id)
            time.sleep(secs3)
        except Exception as e:
            self.fail(f"Cancel with id failed: {e}")

    def test_cancel_all(self):
        try:
            Notification.cancelAll()
        except Exception as e:
            self.fail(f"Cancel all failed: {e}")


    def test_delete_channel(self):
        try:
            send_notification("about to nuke default","")
            time.sleep(5)
            Notification.deleteChannel("default_channel")
        except Exception as e:
            self.fail(f"Delete channel failed: {e}")

    def test_delete_channel_all(self):
        try:
            send_notification("about to nuke default","")
            time.sleep(5)
            Notification.deleteAllChannel()
        except Exception as e:
            self.fail(f"test_delete_channel_all failed: {e}")
