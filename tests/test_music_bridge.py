"""Unit tests for the fixed-package music bridge references (desktop-only).

These pin the strings pyjnius uses on Android to locate the bridge class
``org.android_notify.music.MediaSessionCallback`` and its nested listener
interface. If they drift from the pre-compiled Maven bridge artifact
(``io.github.fector101:android-notify-music-bridge``), the media buttons on the
notification silently stop working.
"""

import unittest


class TestMusicBridgeIdentifiers(unittest.TestCase):

    def test_fixed_bridge_identifiers(self):
        import android_notify.media.music as music

        self.assertEqual(music.MUSIC_BRIDGE_PACKAGE, "org.android_notify.music")
        self.assertEqual(music.JAVA_FILE_NAME, "MediaSessionCallback")
        self.assertEqual(
            music.bridge_interface_class,
            "org/android_notify/music/MediaSessionCallback$MediaSessionListener",
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


if __name__ == "__main__":
    unittest.main()