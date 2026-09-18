from android_notify import Notification, logger
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
            logger.info(f"Channel exists: {Notification.channelExists('default_channel')}")
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

    def test_get_channels_structure(self) -> None:
        prefix = f"getch_{self.uid}"
        Notification.createChannel(
            id=prefix,
            name="GetChannels Sample",
            description="Created by get_channels sample"
        )
        Notification.createChannel(
            id=f"{prefix}_vib",
            name="Vib Channel",
            importance="high",
            vibrate=True
        )

        channels = Notification.getChannels()
        logger.debug(channels)
        self.assertIsInstance(channels, list)
        self.assertTrue(channels, "getChannels() returned no channels")

        expected_keys = {"id", "name", "description", "state", "j_obj"}
        for channel in channels:
            self.assertIsInstance(channel, dict)
            self.assertEqual(set(channel.keys()), expected_keys)
            self.assertIsInstance(channel["state"], bool)   # on/off
            self.assertIsInstance(channel["name"], str)
            self.assertTrue(channel["description"] is None or isinstance(channel["description"], str))
            print(
                f"channel: id={channel['id']} name={channel['name']} state={channel['state']} "
                f"description={channel['description']}"
            )

        created = {c["id"] for c in channels}
        self.assertIn(prefix, created)
        self.assertIn(f"{prefix}_vib", created)
        Notification.deleteChannel(prefix)
        Notification.deleteChannel(f"{prefix}_vib")
