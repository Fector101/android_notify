from android_notify import Notification
from .base_test import AndroidNotifyBaseTest, secs5
import time


class TestNotificationSound(AndroidNotifyBaseTest):

    def test_set_sound(self):
        try:
            time.sleep(secs5)
            Notification.createChannel(
                id="sound_test",
                name="Sound Test",
                res_sound_name="sneeze"
            )
            n = Notification(
                title="Sound Test",
                message="Testing custom sound",
                channel_id="sound_test"
            )
            n.setSound("sneeze")
            n.send()
        except Exception as e:
            self.fail(f"Sound failed: {e}")
