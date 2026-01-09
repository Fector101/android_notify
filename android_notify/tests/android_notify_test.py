"""
Comprehensive test suite for Android-Notify Tester (Laner.use_android_notify)
Covers all notification styles, callbacks, and behaviors.
"""
import unittest
import time

from android_notify import Notification, NotificationStyles, NotificationHandler, send_notification
from android_notify.widgets.texts import set_title, set_message

secs2 = 2
secs3 = 3
secs5 = 5
class TestAndroidNotifyFull(unittest.TestCase):

    def setUp(self):
        max_int = 2_147_483_647
        self.uid = int(time.time() * 1000) % max_int

    def tearDown(self):
        time.sleep(secs3)

    # -------------------------
    # ACTIVE TESTS (ALPHABETICAL)
    # -------------------------

    def test_big_picture(self):
        try:
            n = Notification(id=self.uid, title="Big Picture", message="Testing big picture")
            n.setBigPicture("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Big picture failed: {e}")

    def test_big_text(self):
        try:
            n = Notification(id=self.uid, title="Big Text", message="Testing big text")
            n.setBigText("Lorem Ipsum is dummy text for testing BigTextStyle display.")
            n.send()
        except Exception as e:
            self.fail(f"Big text failed: {e}")

    def test_both_imgs(self):
        try:
            n = Notification(id=self.uid, title="Both Images", message="Testing both large & big picture")
            n.setLargeIcon("assets/icons/icon.png")
            n.setBigPicture("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Both imgs failed: {e}")

    def test_buttons(self):
        try:
            n = Notification(id=self.uid, title="With Buttons", message="Testing action buttons")
            n.addButton(text="NB Play", on_release=lambda: print("Playing"))
            n.addButton(text="NB Pause", on_release=lambda: print("Paused"))
            n.addButton(text="NB Stop", on_release=lambda: print("Stopped"))
            n.send()
        except Exception as e:
            self.fail(f"Buttons failed: {e}")

    def test_buttons_broadcast(self):
        try:
            n = Notification(id=self.uid, title="With Buttons", message="Testing action buttons")
            n.addButton(text="Play", receiver_name="CarouselReceiver", action="ACTION_UNKNOWN")
            n.addButton(text="Pause", receiver_name="CarouselReceiver", action="ACTION_SKIP")
            n.addButton(text="pk.skip", receiver_name="CarouselReceiver", action="org.wally.waller.ACTION_SKIP")
            n.send()
        except Exception as e:
            self.fail(f"Buttons failed: {e}")

    def test_callback(self):
        try:
            n = Notification(
                id=self.uid,
                title="With Callback",
                message="Tap to run callback",
                callback=lambda: print("Callback invoked")
            )
            n.send()
        except Exception as e:
            self.fail(f"Callback failed: {e}")

    def test_cancel(self):
        try:
            n = Notification(id=self.uid, title="Testing cancel() in 3secs", message="Cancel")
            n.send()
            time.sleep(3)
            n.cancel()
        except Exception as e:
            self.fail(f"Cancel failed: {e}")

    def test_cancel_all(self):
        try:
            Notification.cancelAll()
        except Exception as e:
            self.fail(f"Cancel all failed: {e}")

    def test_cancel_with_id(self):
        try:
            n = Notification(id=self.uid, title="Testing cancel with id in 3secs", message="Cancel")
            n.send()
            time.sleep(secs3)
            n.cancel(_id=n.id)
        except Exception as e:
            self.fail(f"Cancel with id failed: {e}")

    def test_channel_exists(self):
        try:
            ans = Notification.channelExists("default_channel")
            print(f"default_channel exist state: {ans}")
        except Exception as e:
            self.fail(f"Channel exists failed: {e}")

    def test_channel_generate_id(self):
        try:
            n = Notification(
                id=self.uid,
                title="Generated Channel",
                message="Channel creation test",
                channel_name="Custom Channel"
            )
            n.send()
        except Exception as e:
            self.fail(f"Channel generating ID failed: {e}")

    def test_close_on_click(self):
        try:
            n = Notification(id=self.uid, title="Test close_on_click False", message="Testing close_on_click")
            n.send(close_on_click=False)
        except Exception as e:
            self.fail(f"Test close_on_click failed: {e}")

    def test_close_on_click_and_persistent(self):
        try:
            n = Notification(
                id=self.uid,
                title="Test close_on_click False and persistent",
                message="close_on_click False and persistent"
            )
            n.send(persistent=True, close_on_click=False)
        except Exception as e:
            self.fail(f"Test close_on_click False and persistent failed: {e}")

    def test_create_channel(self):
        try:
            Notification.createChannel(
                id="frm_tests",
                name="Frm Tests",
                description="Made From Tests"
            )
        except Exception as e:
            self.fail(f"Create channel failed: {e}")

    def test_create_channel_with_only_id_and_name(self):
        try:
            Notification.createChannel(
                id="test_create_channel_with_only_id_and_name",
                name="Create from tests with only id and name"
            )
        except Exception as e:
            self.fail(f"Create channel with only id and name failed: {e}")

    def test_creating_and_using_channel(self):
        try:
            n = Notification(
                id=self.uid,
                title="Download Done",
                message="Your file finished downloading.",
                channel_name="Download Notifications",
                channel_id="downloads_notifications"
            )
            n.send()
        except Exception as e:
            self.fail(f"Download channel failed: {e}")

    def test_custom_channel_name(self):
        try:
            Notification.deleteChannel('default_channel')
            # This clears all Notifications Like Cancel All
        except Exception as e:
            self.fail(f"Test deleteChannel failed: {e}")

    def test_custom_icon(self):
        try:
            n = Notification( id=self.uid,title="Custom Icon", message="Testing custom app icon")
            n.setSmallIcon("assets/icons/bell.png")
            n.send()
        except Exception as e:
            self.fail(f"Custom icon failed: {e}")

    def test_custom_icon1(self):
        try:
            n = Notification( id=self.uid,title="Custom Icon1", message="Testing custom app icon")
            n.setSmallIcon("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Custom icon1 failed: {e}")


    def test_custom_name(self):
        try:
            n = Notification(
                id=self.uid,
                title='Click to see "name"',
                message="Click to trigger handler",
                name="change_app_page"
            )
            n.send()
        except Exception as e:
            self.fail(f"Test name failed: {e}")

    def test_do_channels_exist(self):
        try:
            channels = Notification.doChannelsExist(
                ['default_channel', "frm_tests", "stuffs"]
            )
            print(f"Channel that don't exist: {channels}")
        except Exception as e:
            self.fail(f"Do channels exist failed: {e}")

    def test_inbox(self):
        try:
            n = Notification(id=self.uid, title="Inbox", message="Inbox notification")
            n.setLines(["Line 1", "Line 2", "Line 3"])
            n.send()
        except Exception as e:
            self.fail(f"Inbox notification failed: {e}")

    def test_inbox_add_line(self):
        try:
            n = Notification(
                id=self.uid,
                title="Testing addLine()",
                message="Drop down to view Lines."
            )
            n.addLine("First line")
            n.addLine("Second line")
            n.addLine("Third line")
            n.send()
        except Exception as e:
            self.fail(f"Inbox addLine failed: {e}")

    def test_large_icon(self):
        try:
            n = Notification(id=self.uid, title="Large Icon", message="Testing large icon")
            n.setLargeIcon("assets/icons/icon.png")
            n.send()
        except Exception as e:
            self.fail(f"Large icon failed: {e}")

    def test_name_getting(self):
        try:
            Notification(
                title="Change Page",
                message="Click to change App page.",
                name='change_app_page'
            ).send()

            Notification(
                title="Change Color",
                message="Click to change App Color",
                name='change_app_color'
            ).send()
        except Exception as e:
            self.fail("Failed added names",e)

    def test_persistent(self):
        try:
            n = Notification(id=self.uid, title="Test persistent", message="Testing persistent")
            n.send(persistent=True)
        except Exception as e:
            self.fail(f"Test persistent failed: {e}")

    def test_progress(self):
        try:
            n = Notification(
                id=self.uid,
                title="Downloading...",
                message="0% downloaded",
                progress_current_value=0,
                progress_max_value=100
            )
            n.send()
            for i in range(0, 101, 10):
                time.sleep(secs2)
                n.updateProgressBar(i, f"{i}% done", title="test download progress bar")
            n.removeProgressBar(message="Done", title="Download Complete")
        except Exception as e:
            self.fail(f"Progress notification failed: {e}")

    def test_refresh(self):
        try:
            n = Notification(id=self.uid, title="Testing refresh() in 3secs", message="Refresh")
            set_title(n.builder, "New Title from refresh")
            set_message(n.builder, "New Title from refresh")
            time.sleep(secs3)
            n.refresh()
        except Exception as e:
            self.fail(f"Refresh failed: {e}")

    def test_set_color(self):
        try:
            n = Notification(title="Test for colored Icon", message="colored Icon")
            n.setColor('red')
            n.send()
        except Exception as e:
            self.fail(f"Colored Icon failed: {e}")

    def test_set_priority(self):
        try:
            n = Notification(id=self.uid, title="Test setPriority", message="Testing setPriority")
            n.setPriority("high")
            n.send()
        except Exception as e:
            self.fail(f"setPriority icon failed: {e}")

    def test_set_sound(self):
        try:
            time.sleep(secs5)
            Notification.createChannel(
                id="weird_sound_tester",
                name="Weird Sound Tester",
                description="A test channel used to verify custom notification sounds.",
                res_sound_name="sneeze"
            )
            n = Notification(
                title="Custom Sound Notification",
                message="This tests playback of a custom sound (sneeze.wav)",
                channel_id="weird_sound_tester"
            )
            n.setSound("sneeze")
            n.send()
        except Exception as e:
            self.fail(f"Custom Sound notification failed: {e}")

    def test_set_sub_text(self):
        try:
            n = Notification(id=self.uid, title="setSubText test", message="Testing setSubText")
            n.setSubText("101 secs left")
            n.send()
        except Exception as e:
            self.fail(f"setSubText failed: {e}")

    def test_set_when(self):
        try:
            n = Notification(title="Test for colored Icon", message="colored Icon")
            n.setWhen(60 * 60)
            n.send()
        except Exception as e:
            self.fail(f"setWhen failed: {e}")

    def test_show_infinite_progressbar(self):
        try:
            n = Notification(title="Test for showInfiniteProgressBar", message="showInfiniteProgressBar")
            n.showInfiniteProgressBar()
            n.send()
        except Exception as e:
            self.fail(f"showInfiniteProgressBar failed: {e}")

    def test_sub_text(self):
        try:
            n = Notification(id=self.uid, title="setSubText test", message="Testing setSubText")
            n.setSubText("101 secs left")
            n.send()
        except Exception as e:
            self.fail(f"setSubText failed: {e}")

    def test_title_message_update(self):
        try:
            n = Notification(id=self.uid, title="Old Title", message="Old Message")
            n.send()
            time.sleep(secs2)
            n.updateTitle("New Title1")
            n.updateMessage("New Message2")
        except Exception as e:
            self.fail(f"Update title/message failed: {e}")

    def test_update_message(self):
        try:
            n = Notification(title="Test for updateMessage", message="updateMessage")
            n.updateMessage("New Message")
            n.send()
        except Exception as e:
            self.fail(f"updateMessage failed: {e}")

    def test_update_title(self):
        try:
            n = Notification(title="Test for updateTitle", message="updateTitle")
            n.updateTitle("New Title")
            n.send()
        except Exception as e:
            self.fail(f"updateTitle failed: {e}")




if __name__ == "__main__":
    unittest.main(verbosity=2)
