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

    def test_set_sound_path(self):
        import os
        mock_file = "test_mock_sound.mp3"
        with open(mock_file, "w") as f:
            f.write("mock audio data")

        try:
            Notification.createChannel(
                id="sound_path_test",
                name="Sound Path Test",
                sound_path=mock_file
            )
            n = Notification(
                title="Sound Path Test",
                message="Testing custom sound path",
                channel_id="sound_path_test"
            )
            n.setSound(sound_path=mock_file)
            n.send()
        except Exception as e:
            self.fail(f"Sound path failed: {e}")
        finally:
            if os.path.exists(mock_file):
                os.remove(mock_file)

    def test_set_sound_content_uri(self):
        try:
            content_uri = "content://media/external/audio/media/123"
            Notification.createChannel(
                id="sound_uri_test",
                name="Sound Uri Test",
                sound_path=content_uri
            )
            n = Notification(
                title="Sound Uri Test",
                message="Testing content URI",
                channel_id="sound_uri_test"
            )
            n.setSound(sound_path=content_uri)
            n.send()
        except Exception as e:
            self.fail(f"Sound content URI failed: {e}")
