"""Unit tests for plain (non-dispatching) media controllers (desktop-only).

A controller that is not a Kivy ``EventDispatcher`` cannot drive the media
notification through ``state``/``on_seek`` bindings. These tests pin the
fallback: binding is skipped, and ``MediaNotification.syncPlaybackState()`` (and
the MediaSessionListener transport callbacks) keep the notification in sync.
"""

import unittest
from unittest import mock

import android_notify.media as music
from android_notify.media import (
    MediaNotification,
    MediaSessionListener,
    _controller_dispatches_events,
)
from android_notify.media.music.helper import SoundLoader


class FakePlainController:
    """Minimal IMediaController implementation without any Kivy events."""

    def __init__(self, length=0.0, state="stop"):
        self.source = "/tmp/track.ogg"
        self._length = length
        self.state = state
        self._pos = 0.0

    @property
    def length(self):
        return self._length

    def play(self):
        self.state = "play"

    def pause(self):
        self.state = "pause"

    def seek(self, pos):
        self._pos = pos

    def get_pos(self):
        return self._pos


class FakeEventController(FakePlainController):
    """Controller that looks like a Kivy EventDispatcher (bind/dispatch/events).

    Mirrors the real ``EventDispatcher``: ``events()`` lists only the declared
    ``__events__`` (the ``on_*`` names), while property names such as ``state``
    are reported by ``properties()``.
    """

    def __init__(self, *args, events=("on_seek", "on_load"), has_state=True, **kwargs):
        super().__init__(*args, **kwargs)
        self._events = list(events)
        self._has_state = has_state
        self.bind_calls = []
        self.unbind_calls = []

    def bind(self, **kwargs):
        self.bind_calls.append(kwargs)

    def unbind(self, **kwargs):
        self.unbind_calls.append(kwargs)

    def dispatch(self, *args, **kwargs):
        pass

    def events(self):
        return list(self._events)

    def properties(self):
        return {"state": None} if self._has_state else {}


class TestControllerDispatchDetection(unittest.TestCase):

    def test_plain_controller_does_not_dispatch(self):
        self.assertFalse(_controller_dispatches_events(FakePlainController()))

    def test_event_controller_dispatches(self):
        self.assertTrue(_controller_dispatches_events(FakeEventController()))

    def test_state_property_detected_even_though_events_lists_only_on_star(self):
        # Regression: real Kivy events() never contains "state" (a property), so
        # detection must read properties() for it or every controller looks plain.
        controller = FakeEventController(events=("on_seek", "on_load"), has_state=True)
        self.assertNotIn("state", controller.events())
        self.assertTrue(_controller_dispatches_events(controller))

    def test_event_controller_missing_state_does_not_dispatch(self):
        controller = FakeEventController(has_state=False)
        self.assertFalse(_controller_dispatches_events(controller))


class TestSetMediaController(unittest.TestCase):

    def setUp(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def tearDown(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def test_plain_controller_binds_nothing(self):
        controller = FakeEventController(events=("on_load",))
        notification = MediaNotification(controller)
        self.assertIs(notification._bound_instance, controller)
        self.assertEqual(controller.bind_calls, [])

    def test_event_controller_is_bound(self):
        controller = FakeEventController()
        MediaNotification(controller)
        self.assertEqual(len(controller.bind_calls), 1)
        bound_events = set(controller.bind_calls[0])
        self.assertEqual(bound_events, {"state", "on_load", "on_seek"})


class TestSyncPlaybackState(unittest.TestCase):

    def setUp(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def tearDown(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def test_no_controller_is_a_noop(self):
        controller = FakePlainController(length=5.0)
        notification = MediaNotification(controller)
        notification.mediaController = None
        self.assertIsNone(notification.syncPlaybackState())

    def test_builds_when_ready_but_not_built(self):
        controller = FakePlainController(length=12.0, state="play")
        notification = MediaNotification(controller)
        notification.already_built = False
        notification._build_if_media_session_setup_is_done = mock.Mock()

        notification.syncPlaybackState()

        notification._build_if_media_session_setup_is_done.assert_called_once()

    def test_does_not_build_when_not_ready(self):
        controller = FakePlainController(length=0.0, state="stop")
        notification = MediaNotification(controller)
        notification.already_built = False
        notification._build_if_media_session_setup_is_done = mock.Mock()

        notification.syncPlaybackState()

        notification._build_if_media_session_setup_is_done.assert_not_called()

    def test_flips_icon_with_current_state(self):
        controller = FakePlainController(length=12.0, state="play")
        notification = MediaNotification(controller)
        notification.already_built = True
        notification._parse_state = mock.Mock()

        notification.syncPlaybackState()

        notification._parse_state.assert_called_once()
        self.assertEqual(notification._parse_state.call_args[0][1], "play")


class TestListenerSyncsPlainControllers(unittest.TestCase):

    def setUp(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def tearDown(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def _listener(self):
        listener = MediaSessionListener()
        listener.play_music = lambda: None
        listener.pause_music = lambda: None
        return listener

    def test_play_triggers_sync_for_plain_controller(self):
        controller = FakePlainController(length=5.0, state="stop")
        notification = MediaNotification(controller)
        notification.syncPlaybackState = mock.Mock()

        self._listener().onPlay()

        notification.syncPlaybackState.assert_called_once()

    def test_pause_triggers_sync_for_plain_controller(self):
        controller = FakePlainController(length=5.0, state="play")
        notification = MediaNotification(controller)
        notification.syncPlaybackState = mock.Mock()

        self._listener().onPause()

        notification.syncPlaybackState.assert_called_once()

    def test_event_controller_is_not_synced_twice(self):
        controller = FakeEventController(length=5.0, state="stop")
        notification = MediaNotification(controller)
        notification.syncPlaybackState = mock.Mock()

        self._listener().onPlay()

        notification.syncPlaybackState.assert_not_called()


class _FakePlayer:
    """Minimal MediaPlayer stand-in for the completion guard tests."""

    def __init__(self):
        self.seek_calls = []
        self.start_calls = 0

    def seekTo(self, milliseconds):
        self.seek_calls.append(milliseconds)

    def start(self):
        self.start_calls += 1


class TestCompletionLoopRestartGuard(unittest.TestCase):
    """Regression: a completing player must not be touched after an on_complete
    listener swaps it for the next track.

    SoundLoader is a singleton, so an auto-advance handler loads the next track
    from inside the on_complete dispatch, replacing ``_player``. The old
    unconditional ``seek(0)`` + ``start()`` then ran against the fresh,
    not-yet-prepared player; with no OnErrorListener Android routed that error
    back into onCompletion, producing an endless COMPLETE -> load loop.
    """

    def setUp(self):
        SoundLoader._instance = None

    def tearDown(self):
        SoundLoader._instance = None

    def test_restart_skipped_when_listener_swaps_player(self):
        instance = SoundLoader()
        completed = _FakePlayer()
        next_track = _FakePlayer()
        instance._player = completed
        instance._player_ready = True
        instance.loop = True

        def on_complete(*_):
            instance._player = next_track

        instance.dispatch = on_complete
        instance.on_player_complete()

        self.assertEqual(next_track.start_calls, 0)
        self.assertEqual(next_track.seek_calls, [])
        self.assertEqual(completed.start_calls, 0)
        self.assertEqual(completed.seek_calls, [])

    def test_restart_happens_when_player_is_unchanged(self):
        instance = SoundLoader()
        completed = _FakePlayer()
        instance._player = completed
        instance._player_ready = True
        instance.loop = True

        instance.dispatch = lambda *_: None
        instance.on_player_complete()

        self.assertEqual(completed.start_calls, 1)
        self.assertEqual(completed.seek_calls, [0])

    def test_no_restart_when_loop_disabled(self):
        instance = SoundLoader()
        completed = _FakePlayer()
        instance._player = completed
        instance._player_ready = True
        instance.loop = False

        instance.dispatch = lambda *_: None
        instance.on_player_complete()

        self.assertEqual(completed.start_calls, 0)


class _RecordingBuilder:
    """NotificationCompat.Builder stand-in that records title/message/icons."""

    def __init__(self):
        self.title = None
        self.message = None
        self.large_icons = []

    def setContentTitle(self, value):
        self.title = str(value)

    def setContentText(self, value):
        self.message = str(value)

    def setLargeIcon(self, bitmap):
        self.large_icons.append(bitmap)

    def build(self):
        return self


class _RecordingSession:
    def __init__(self):
        self.metadata = None

    def setMetadata(self, metadata):
        self.metadata = metadata


class _RecordingMetadataBuilder:
    def __init__(self):
        self.values = {}

    def putString(self, key, value):
        self.values[key] = str(value)
        return self

    def putLong(self, key, value):
        self.values[key] = value
        return self

    def build(self):
        return self.values


class TestNowPlayingUpdates(unittest.TestCase):
    """setTitle/setArtist/setNowPlaying/refresh must update a live notification.

    Regression: a plain (non-dispatching) controller never triggers a rebuild
    via on_load, so the setters themselves have to push the new track into the
    already-built notification instead of only storing fields.
    """

    def setUp(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None
        self.controller = FakePlainController(length=12.0, state="play")
        self.notification = MediaNotification(self.controller)
        self.notification.builder = _RecordingBuilder()
        self.notification.session = _RecordingSession()
        self.notification.already_built = True
        self.manager = mock.Mock()
        self._patchers = [
            mock.patch.object(music, "get_notification_manager", return_value=self.manager),
            mock.patch.object(music, "set_title"),
            mock.patch.object(music, "set_message"),
            mock.patch.object(music, "MediaMetadataBuilder", _RecordingMetadataBuilder),
        ]
        for patcher in self._patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def test_set_title_updates_live_notification(self):
        self.notification.setTitle("New title")

        music.set_title.assert_called_once()
        self.assertEqual(music.set_title.call_args.kwargs["title"], "New title")
        self.assertEqual(
            self.notification.session.metadata[music.MediaMetadata.METADATA_KEY_TITLE],
            "New title",
        )
        self.manager.notify.assert_called_once()

    def test_set_now_playing_applies_both_fields_in_one_refresh(self):
        self.notification.setNowPlaying("T", "A")

        self.assertEqual(music.set_title.call_args.kwargs["title"], "T")
        self.assertEqual(music.set_message.call_args.kwargs["message"], "A")
        metadata = self.notification.session.metadata
        self.assertEqual(metadata[music.MediaMetadata.METADATA_KEY_TITLE], "T")
        self.assertEqual(metadata[music.MediaMetadata.METADATA_KEY_ARTIST], "A")
        self.manager.notify.assert_called_once()

    def test_set_now_playing_before_first_build_is_quiet(self):
        self.notification.already_built = False

        self.notification.setNowPlaying("T", "A")

        self.assertEqual(self.notification._title, "T")
        self.assertEqual(self.notification._artist, "A")
        music.set_title.assert_not_called()
        self.manager.notify.assert_not_called()

    def test_refresh_reapplies_now_playing(self):
        self.notification._title = "T"
        self.notification._artist = "A"

        self.notification.refresh()

        self.assertEqual(music.set_title.call_args.kwargs["title"], "T")
        self.assertEqual(music.set_message.call_args.kwargs["message"], "A")
        self.manager.notify.assert_called_once()

    def test_set_now_playing_tolerates_unknown_length(self):
        # Regression: setNowPlaying runs right after load(), before the player
        # reports its duration - a None length must not crash the track change.
        self.controller._length = None

        self.notification.setNowPlaying("T", "A")

        metadata = self.notification.session.metadata
        self.assertEqual(metadata[music.MediaMetadata.METADATA_KEY_DURATION], 0)
        self.manager.notify.assert_called_once()

    def test_refresh_does_not_propagate_errors(self):
        # A refresh is best-effort: it must never raise into the caller's
        # transport handler / Kivy dispatch.
        self.notification._apply_now_playing = mock.Mock(side_effect=TypeError("boom"))

        self.notification.refresh()  # must not raise


class TestSoundLoaderLength(unittest.TestCase):
    """``SoundLoader.length`` must be numeric before the player is ready.

    Kivy's own ``Sound._get_length()`` returns 0 (never None) when there is no
    player, so callers can safely do arithmetic with ``length`` at any time.
    """

    def setUp(self):
        SoundLoader._instance = None

    def tearDown(self):
        SoundLoader._instance = None

    def test_length_is_zero_before_player_ready(self):
        instance = SoundLoader()
        instance._player = None
        instance._player_ready = False

        self.assertEqual(instance._get_length(), 0.0)
        self.assertEqual(instance.length, 0.0)


class TestMediaControllerLength(unittest.TestCase):
    """``IMediaController.length`` must query the underlying getter exactly once.

    ``hasattr(obj, "length")`` already invokes the property getter, so reading
    ``obj.length`` again doubled the work (and any side effects/logging).
    """

    def test_getter_is_read_once_per_access(self):
        calls = []

        class Controller:
            source = "/tmp/track.ogg"

            @property
            def length(self):
                calls.append(1)
                return 5.0

        adapter = music.IMediaController(Controller())

        self.assertEqual(adapter.length, 5.0)
        self.assertEqual(len(calls), 1)

    def test_missing_length_is_zero(self):
        class Controller:
            source = "/tmp/track.ogg"

        self.assertEqual(music.IMediaController(Controller()).length, 0)


class TestLargeIconCache(unittest.TestCase):
    """Album art is decoded per source, and a track without art must replace
    the previous cover instead of leaving it on the shared builder."""

    def setUp(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None
        self.retriever_calls = []
        retriever_calls = self.retriever_calls

        class CountingRetriever:
            def __init__(self):
                retriever_calls.append(1)

            def setDataSource(self, *args, **kwargs):
                pass

            def getEmbeddedPicture(self):
                return None

        patcher = mock.patch.object(music, "MediaMetadataRetriever", CountingRetriever)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.default_icon = object()
        fallback = mock.patch.object(
            music, "get_default_large_icon", return_value=self.default_icon)
        fallback.start()
        self.addCleanup(fallback.stop)

        self.controller = FakePlainController(length=12.0)
        self.notification = MediaNotification(self.controller)
        self.notification.builder = _RecordingBuilder()

    def tearDown(self):
        music.MediaNotification._instance = None
        music._active_music_notification = None

    def test_same_source_decodes_once(self):
        self.notification.setLargeIcon(music_path="/tmp/track.ogg")
        self.notification.setLargeIcon(music_path="/tmp/track.ogg")

        self.assertEqual(len(self.retriever_calls), 1)

    def test_new_source_decodes_again(self):
        self.notification.setLargeIcon(music_path="/tmp/track.ogg")
        self.notification.setLargeIcon(music_path="/tmp/other.ogg")

        self.assertEqual(len(self.retriever_calls), 2)

    def test_new_track_without_art_replaces_the_previous_cover(self):
        # Regression: the same Notification.Builder is reused for every track,
        # so doing nothing when a track has no picture kept the previous cover.
        art = object()

        class ArtRetriever:
            def setDataSource(self, *args, **kwargs):
                pass

            def getEmbeddedPicture(self):
                return b"\xff\xd8\xff"

        class FakeBitmapFactory:
            @staticmethod
            def decodeByteArray(data, offset, length):
                return art

        with mock.patch.object(music, "MediaMetadataRetriever", ArtRetriever), \
                mock.patch.object(music, "BitmapFactory", FakeBitmapFactory):
            self.notification.setLargeIcon(music_path="/tmp/with_art.ogg")

        self.notification.setLargeIcon(music_path="/tmp/artless.ogg")

        self.assertEqual(self.notification.builder.large_icons,
                         [art, self.default_icon])

    def test_broken_img_path_falls_back_to_the_default_icon(self):
        with mock.patch.object(
                music, "get_img_absolute_path", return_value="/tmp/missing.png"
        ), mock.patch.object(music, "get_bitmap_from_path", return_value=False):
            self.notification.setLargeIcon(img_path="assets/missing.png")

        self.assertEqual(self.notification.builder.large_icons, [self.default_icon])


if __name__ == "__main__":
    unittest.main()
