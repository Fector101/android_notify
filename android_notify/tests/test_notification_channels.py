from android_notify import Notification
from .base_test import AndroidNotifyBaseTest


class TestNotificationChannels(AndroidNotifyBaseTest):

    def test_create_channel(self):
        try:
            Notification.createChannel(
                id="frm_tests",
                name="Frm Tests",
                description="Created from tests"
            )
        except Exception as e:
            self.fail(f"Create channel failed: {e}")

    def test_channel_exists(self):
        try:
            print(Notification.channelExists("default_channel"))
        except Exception as e:
            self.fail(f"Channel exists failed: {e}")

    def test_do_channels_exist(self):
        try:
            print(Notification.doChannelsExist(
                ["default_channel", "frm_tests", "unknown"]
            ))
        except Exception as e:
            self.fail(f"Do channels exist failed: {e}")

    def test_create_and_use_channel(self):
        try:
            Notification(
                id=self.uid,
                title="Download Done",
                message="Finished",
                channel_id="downloads",
                channel_name="Downloads"
            ).send()
        except Exception as e:
            self.fail(f"Using channel failed: {e}")
