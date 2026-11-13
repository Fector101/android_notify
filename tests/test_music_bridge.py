"""Unit tests for the fixed-package music bridge references (desktop-only).

These pin the strings pyjnius uses on Android to locate the bridge class
``org.android_notify.music.MediaSessionCallback`` and its nested listener
interface. If they drift from the pre-compiled Maven bridge artifact
(``io.github.fector101:android-notify-music-bridge``), the media buttons on the
notification silently stop working.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


class TestMusicBridgeIdentifiers(unittest.TestCase):

    def test_fixed_bridge_identifiers(self):
        import android_notify.media as music

        self.assertEqual(music.MUSIC_BRIDGE_PACKAGE, "org.android_notify.music")
        self.assertEqual(music.JAVA_FILE_NAME, "MediaSessionCallback")
        self.assertEqual(
            music.bridge_interface_class,
            "org/android_notify/music/MediaSessionCallback$MediaSessionListener",
        )
        self.assertEqual(
            music.MEDIA_BUTTON_RECEIVER_NAME,
            "MediaSessionCallback$MediaButtonReceiver",
        )

    def test_desktop_facade_still_loads(self):
        from android_notify.internal.facade import MediaSessionCallback

        callback = MediaSessionCallback(listener=None)
        self.assertIsNotNone(callback)

    def test_legacy_file_content_uses_fixed_package(self):
        from android_notify.media.music.helper import JAVA_CALLBACK_FILE_CONTENT

        self.assertIn("package org.android_notify.music;", JAVA_CALLBACK_FILE_CONTENT)
        self.assertNotIn("com.example.android_notify", JAVA_CALLBACK_FILE_CONTENT)
        self.assertIn("MediaSessionCallback", JAVA_CALLBACK_FILE_CONTENT)

    def test_action_buttons_use_bridge_solid_icons(self):
        import android_notify.media as music

        music.MediaNotification._instance = None
        notification = music.MediaNotification(SimpleNamespace(state="play"), on_next=True, on_previous=True)
        notification.builder = SimpleNamespace(mActions=[])
        notification.builder.addAction = notification.builder.mActions.append
        notification._MediaNotification__create_media_button_intent = lambda key_code: key_code

        class CapturingAction:
            def __init__(self, icon, _title, _intent):
                self.icon = icon

            def build(self):
                return self

        with mock.patch.object(music, "ActionBuilder", CapturingAction):
            notification._format_buttons()
            self.assertEqual(
                [action.icon for action in notification.builder.mActions],
                [
                    music.MediaActionDrawable.an_media_previous,
                    music.MediaActionDrawable.an_media_pause,
                    music.MediaActionDrawable.an_media_next,
                ],
            )

            notification.mediaController.instance.state = "pause"
            notification._format_buttons()
            self.assertEqual(
                [action.icon for action in notification.builder.mActions],
                [
                    music.MediaActionDrawable.an_media_previous,
                    music.MediaActionDrawable.an_media_play,
                    music.MediaActionDrawable.an_media_next,
                ],
            )

    def test_action_buttons_fall_back_without_bridge_icons(self):
        import android_notify.media as music

        music.MediaNotification._instance = None
        notification = music.MediaNotification(SimpleNamespace(state="play"))
        notification.builder = SimpleNamespace(mActions=[])
        notification.builder.addAction = notification.builder.mActions.append
        notification._MediaNotification__create_media_button_intent = lambda key_code: key_code

        class CapturingAction:
            def __init__(self, icon, _title, _intent):
                self.icon = icon

            def build(self):
                return self

        with (
            mock.patch.object(music, "MediaActionDrawable", None),
            mock.patch.object(music, "ActionBuilder", CapturingAction),
        ):
            notification._format_buttons()
        self.assertEqual(
            [action.icon for action in notification.builder.mActions],
            [music.R_drawable.ic_media_pause],
        )


class TestMediaButtonReceiverRouting(unittest.TestCase):

    def setUp(self):
        import android_notify.media as music

        self.music = music
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def tearDown(self):
        self.music.MediaNotification._instance = None
        self.music._active_music_notification = None

    def test_action_pending_intent_targets_bridge_receiver(self):
        music = self.music
        receiver = object()
        context = object()

        class Controller:
            source = "/tmp/test.ogg"
            length = 1.0
            state = "play"

            def play(self):
                pass

            def pause(self):
                pass

            def seek(self, _position):
                pass

            def get_pos(self):
                return 0.0

        class Intent:
            ACTION_MEDIA_BUTTON = "android.intent.action.MEDIA_BUTTON"
            EXTRA_KEY_EVENT = "android.intent.extra.KEY_EVENT"

            def __init__(self, actual_context, actual_receiver):
                self.component = (actual_context, actual_receiver)
                self.extras = {}
                self.action = None

            def setAction(self, action):
                self.action = action

            def putExtra(self, key, value):
                self.extras[key] = value

        class KeyEvent:
            ACTION_DOWN = 0
            KEYCODE_MEDIA_NEXT = 87

            def __init__(self, action, key_code):
                self.action = action
                self.key_code = key_code

        class PendingIntent:
            FLAG_UPDATE_CURRENT = 1
            FLAG_IMMUTABLE = 2
            call = None

            @classmethod
            def getBroadcast(cls, *args):
                cls.call = args
                return args

        notification = music.MediaNotification(Controller())
        notification.context = context
        with (
            mock.patch.object(music, "MediaButtonReceiver", receiver),
            mock.patch.object(music, "Intent", Intent),
            mock.patch.object(music, "KeyEvent", KeyEvent),
            mock.patch.object(music, "PendingIntent", PendingIntent),
            mock.patch.object(music, "BuildVersion", type("BuildVersion", (), {"SDK_INT": 31})),
            mock.patch.object(music, "cast", lambda _type, value: value),
        ):
            result = notification._MediaNotification__create_media_button_intent(
                KeyEvent.KEYCODE_MEDIA_NEXT
            )

        self.assertEqual(result, PendingIntent.call)
        actual_context, request_code, intent, flags = PendingIntent.call
        self.assertIs(actual_context, context)
        self.assertEqual(request_code, KeyEvent.KEYCODE_MEDIA_NEXT)
        self.assertEqual(intent.component, (context, receiver))
        self.assertEqual(intent.action, Intent.ACTION_MEDIA_BUTTON)
        self.assertEqual(
            intent.extras[Intent.EXTRA_KEY_EVENT].key_code,
            KeyEvent.KEYCODE_MEDIA_NEXT,
        )
        self.assertEqual(flags, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)

    def test_receiver_is_declared_in_aar_manifest(self):
        root = Path(__file__).resolve().parents[1]
        manifest = (
            root
            / "bridges"
            / "android"
            / "android-notify-music-bridge"
            / "src"
            / "main"
            / "AndroidManifest.xml"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "org.android_notify.music.MediaSessionCallback$MediaButtonReceiver",
            manifest,
        )
        self.assertIn('android:exported="false"', manifest)

    def test_bridge_declares_solid_vector_action_icons(self):
        root = Path(__file__).resolve().parents[1]
        resources = root / "bridges" / "android" / "android-notify-music-bridge" / "src" / "main" / "res" / "drawable"

        for icon in ("play", "pause", "previous", "next"):
            with self.subTest(icon=icon):
                content = (resources / f"an_media_{icon}.xml").read_text(encoding="utf-8")
                self.assertIn('android:fillColor="#FFFFFFFF"', content)
                self.assertIn("android:pathData=", content)
                self.assertNotIn("android:stroke", content)


if __name__ == "__main__":
    unittest.main()