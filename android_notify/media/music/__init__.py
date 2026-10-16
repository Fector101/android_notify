"""Music playback helpers.

Convenience re-exports so users can write
``from android_notify.media.music import SoundLoader`` instead of reaching
into ``...music.helper``. ``MediaNotification`` itself lives one level up in
``android_notify.media``.
"""
from android_notify.media.music.helper import (
    JAVA_CALLBACK_FILE_CONTENT,
    MediaPermissionHandler,
    SoundLoader,
)
