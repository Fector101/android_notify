"""
Comprehensive test suite for Android-Notify Tester (Laner.use_android_notify)
Covers all notification styles, callbacks, and behaviors.
"""
import unittest
import time
import traceback

from android_notify import Notification, NotificationStyles, NotificationHandler, send_notification


class TestAndroidNotifyFull(unittest.TestCase):
    def tearDown(self):
        time.sleep(3)

    def setUp(self):
        max_int = 2_147_483_647
        self.uid = int(time.time() * 1000) % max_int

    def test_simple(self):
        try:
            n = Notification( id=self.uid,title="Simple", message="Simple message test")
            n.send()
        except Exception as e:
            self.fail(f"Simple notification failed: {e}")

    def test_progress(self):
        try:
            n = Notification( id=self.uid,title="Downloading...", message="0% downloaded", progress_current_value=0, progress_max_value=100)
            n.send()
            for i in range(0, 101, 10):
                time.sleep(2)
                n.updateProgressBar(i, f"{i}% done")
            n.removeProgressBar(message="Done", title="Download Complete")
        except Exception as e:
            self.fail(f"Progress notification failed: {e}")

    def test_big_picture(self):
        try:
            n = Notification( id=self.uid,title="Big Picture", message="Testing big picture")
            n.setBigPicture("assets/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Big picture failed: {e}")

    def test_inbox(self):
        try:
            n = Notification( id=self.uid,title="Inbox", message="Inbox notification")
            n.setLines(["Line 1", "Line 2", "Line 3"])
            n.send()
        except Exception as e:
            self.fail(f"Inbox notification failed: {e}")

    def test_inbox_from_file_message(self):
        try:
            lines = "Test1\nTest2\nTest3"
            n = Notification( id=self.uid,title="Inbox File", message="File Inbox Test", lines_txt=lines)
            n.send()
        except Exception as e:
            self.fail(f"Inbox from file failed: {e}")

    def test_inbox_add_line(self):
        try:
            n = Notification( id=self.uid,title="Inbox AddLine", message="Testing addLine()")
            n.addLine("First line")
            n.addLine("Second line")
            n.addLine("Third line")
            n.send()
        except Exception as e:
            self.fail(f"Inbox addLine failed: {e}")

    def test_large_icon(self):
        try:
            n = Notification( id=self.uid,title="Large Icon", message="Testing large icon")
            n.setLargeIcon("assets/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Large icon failed: {e}")

    def test_big_text(self):
        try:
            n = Notification( id=self.uid,title="Big Text", message="Testing big text")
            n.setBigText("Lorem Ipsum is dummy text for testing BigTextStyle display.")
            n.send()
        except Exception as e:
            self.fail(f"Big text failed: {e}")

    def test_buttons(self):
        try:
            n = Notification( id=self.uid,title="With Buttons", message="Testing action buttons")
            n.addButton(text="Play", on_release=lambda: print("Playing"))
            n.addButton(text="Pause", on_release=lambda: print("Paused"))
            n.addButton(text="Stop", on_release=lambda: print("Stopped"))
            n.send()
        except Exception as e:
            self.fail(f"Buttons failed: {e}")

    def test_both_imgs(self):
        try:
            n = Notification( id=self.uid,title="Both Images", message="Testing both large & big picture")
            n.setLargeIcon("assets/icon.png")
            n.setBigPicture("assets/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Both imgs failed: {e}")

    def test_custom_icon(self):
        try:
            n = Notification( id=self.uid,title="Custom Icon", message="Testing custom app icon")
            n.setSmallIcon("assets/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Custom icon failed: {e}")

    def test_title_message_update(self):
        try:
            n = Notification( id=self.uid,title="Old Title", message="Old Message")
            n.send()
            time.sleep(2)
            n.updateTitle("New Title")
            n.updateMessage("New Message")
        except Exception as e:
            self.fail(f"Update title/message failed: {e}")

    def test_download_channel(self):
        try:
            n = Notification( id=self.uid,
                title="Download Done",
                message="Your file finished downloading.",
                channel_name="Download Notifications",
                channel_id="downloads_notifications"
            )
            n.send()
        except Exception as e:
            self.fail(f"Download channel failed: {e}")

    def test_channel_generate_id(self):
        try:
            n = Notification( id=self.uid,
                title="Generated Channel",
                message="Channel creation test",
                channel_name="Custom Channel"
            )
            n.send()
        except Exception as e:
            self.fail(f"Channel generating ID failed: {e}")

    def test_custom_id(self):
        try:
            n = Notification( id=self.uid,title="Custom ID", message="Click to trigger handler", name="change_app_page")
            n.send()
        except Exception as e:
            self.fail(f"Custom ID failed: {e}")

    def test_callback(self):
        try:
            n = Notification( id=self.uid,title="With Callback", message="Tap to run callback", callback=lambda: print("Callback invoked"))
            n.send()
        except Exception as e:
            self.fail(f"Callback failed: {e}")

    def test_custom_channel_name(self):
        try:
            n = Notification( id=self.uid,title="Custom Channel", message="Testing custom name", channel_name="MyChannelName")
            n.send()
        except Exception as e:
            self.fail(f"Custom channel name failed: {e}")

    def test_cancel_all(self):
        try:
            Notification.cancelAll()
        except Exception as e:
            self.fail(f"Cancel all failed: {e}")

    def test_create_channel_lifespan(self):
        try:
            n = Notification( id=self.uid,title="Check ID Lifespan", message="Testing channel id reuse")
            cid = "test_channel_id"
            n.createChannel(id=cid, name="Test Channel", description="Lifespan check")
            n.send()
        except Exception as e:
            self.fail(f"Create channel lifespan failed: {e}")

    def test_persistent(self):
        try:
            n = Notification( id=self.uid,title="Persistent", message="This notification should persist")
            n.send(persistent=True)
        except Exception as e:
            self.fail(f"Persistent notification failed: {e}")

    # def test_get_active_notifications(self):
    #     try:
    #         Notification( id=self.uid,).get_active_notifications()
    #     except Exception as e:
    #         self.fail(f"Get active notifications failed: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
