"""Unit tests for plain (non-dispatching) media controllers (desktop-only).

A controller that is not a Kivy ``EventDispatcher`` cannot drive the media
notification through ``state``/``on_seek`` bindings. These tests pin the
fallback: binding is skipped, and ``MediaNotification.syncPlaybackState()`` (and
the MediaSessionListener transport callbacks) keep the notification in sync.
"""

import unittest
from unittest import mock

import android_notify.media.music as music
from android_notify.media.music import (
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


if __name__ == "__main__":
    unittest.main()
