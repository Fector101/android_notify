import time
from android_notify import Notification
from .base_test import AndroidNotifyBaseTest, secs2


class TestNotificationProgress(AndroidNotifyBaseTest):

    def test_progress(self):
        try:
            n = Notification(
                id=self.uid,
                title="Downloading",
                message="0%",
                progress_current_value=0,
                progress_max_value=100
            )
            n.send()
            for i in range(0, 101, 20):
                time.sleep(secs2)
                n.updateProgressBar(i, f"{i}% done")
            n.removeProgressBar(title="Done", message="Completed")
        except Exception as e:
            self.fail(f"Progress failed: {e}")

    def test_infinite_progress(self):
        try:
            n = Notification(title="Infinite", message="Loading")
            n.showInfiniteProgressBar()
            n.send()
        except Exception as e:
            self.fail(f"Infinite progress failed: {e}")
