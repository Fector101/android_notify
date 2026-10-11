"""
On-screen, level-colored log view for Kivy apps.

A tiny ``ScrollView`` that renders log lines with a color per level, plus a
``logging.Handler`` that forwards records into it. Records emitted before a
view is attached are buffered, so import-time logs (media-session setup, etc.)
are not lost.

Usage::

    handler = install_kivy_log_handler()
    ...
    root.add_widget(LogPanel(handler=handler))

``install_kivy_log_handler`` must run before importing modules whose import-time
logs you want to capture. ``LogPanel`` can also create a handler on its own for
a quick one-liner, but then it only captures logs emitted after it is built.

Importing this module pulls in Kivy, so it is intentionally *not* re-exported
from ``android_notify/__init__.py``.
"""

import logging
import threading

from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.utils import escape_markup

# Level -> hex color. Loosely mirrors internal.logger.KivyColorFormatter.
LEVEL_COLORS = {
    "DEBUG": "#7FB3FF",
    "INFO": "#4CC38A",
    "WARNING": "#E3B341",
    "ERROR": "#F0736A",
    "CRITICAL": "#D25DD2",
}
DEFAULT_LEVEL_COLOR = "#DDDDDD"
NAME_COLOR = "#8A8A8A"

MAX_BUFFER_LINES = 1000
MAX_VIEW_LINES = 500


def _format_line(record):
    """Render one record as Kivy markup: colored level, dim name, plain message."""
    color = LEVEL_COLORS.get(record.levelname, DEFAULT_LEVEL_COLOR)
    level = escape_markup(record.levelname.ljust(7))
    name = escape_markup(f"[{record.name}]")
    message = escape_markup(record.getMessage())
    return (
        f"[color={color}]{level}[/color] "
        f"[color={NAME_COLOR}]{name}[/color] {message}"
    )


class LogView(ScrollView):
    """Auto-scrolling panel that renders pre-colored markup log lines."""

    def __init__(self, **kwargs):
        kwargs.setdefault("bar_width", dp(4))
        super().__init__(**kwargs)
        self._lines = []
        self._label = Label(
            text="",
            markup=True,
            size_hint_y=None,
            size_hint_x=1,
            halign="left",
            valign="top",
            color=(0.9, 0.92, 0.95, 1),
            font_size=sp(13)
        )
        self._label.bind(
            width=lambda *_: setattr(self._label, "text_size", (self._label.width, None)),
            texture_size=self._sync_label_height,
        )
        self.add_widget(self._label)

    def _sync_label_height(self, *args):
        # Kivy's DampedScrollEffect divides by the content height while
        # overscrolling; an empty label would be 0 and crash. Keep it >= 1 so
        # small/empty content stays draggable (a short log is swiped up by the
        # content being smaller than the viewport).
        self._label.height = max(self._label.texture_size[1], 1)

    def set_lines(self, lines):
        self._lines = list(lines)[-MAX_VIEW_LINES:]
        self._render()

    def append(self, markup_line):
        self._lines.append(markup_line)
        if len(self._lines) > MAX_VIEW_LINES:
            self._lines = self._lines[-MAX_VIEW_LINES:]
        self._render()

    def _render(self):
        self._label.text = "\n\n".join(self._lines)
        self.scroll_y = 0  # newest line at the bottom

    def clear(self):
        self._lines = []
        self._label.text = ""


class KivyLogHandler(logging.Handler):
    """Forward log records into a :class:`LogView`, safely from any thread.

    Lines are buffered until :meth:`attach` is called, so records emitted before
    the UI exists are shown once the view is ready.
    """

    def __init__(self, level=logging.DEBUG):
        super().__init__(level)
        self._lock = threading.Lock()
        self._buffer = []
        self._view = None

    def attach(self, log_view):
        
        with self._lock:
            buffered = list(self._buffer)
            self._view = log_view
        log_view.set_lines(buffered)

    def clear(self):
        with self._lock:
            self._buffer.clear()

    def emit(self, record):
        try:
            line = _format_line(record)
        except Exception:
            return
        with self._lock:
            self._buffer.append(line)
            if len(self._buffer) > MAX_BUFFER_LINES:
                del self._buffer[:-MAX_BUFFER_LINES]
        view = self._view
        if view is not None:
            Clock.schedule_once(lambda _dt: view.append(line))


def install_kivy_log_handler(level=logging.DEBUG, loggers=("", "android_notify")):
    """Attach a :class:`KivyLogHandler` to the given loggers and return it.

    ``""`` is the root logger, which catches Kivy (Window/GL/AudioSDL3) and most
    third-party loggers. ``"android_notify"`` needs its own handler because it
    sets ``propagate=False``.

    The named loggers are set to ``level`` so debug records reach the handler.
    The ``kivy`` logger is deliberately left untouched (its Kivy-configured
    ``INFO`` level avoids flooding the terminal with Kivy debug output).
    """
    handler = KivyLogHandler(level)
    for name in loggers:
        target = logging.getLogger(name)
        target.addHandler(handler)
        target.setLevel(level)
    return handler


class LogPanel(BoxLayout):
    """Drop-in log panel: title, level selector, Clear button and a LogView.

    :param handler: a handler from :func:`install_kivy_log_handler`. When
        ``None`` one is created for you, but a pre-installed handler is needed
        to capture logs emitted before the panel is built.
    :param level: initial level shown/selected in the level spinner.
    :param title: text shown at the left of the header.
    """

    LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")

    def __init__(self, handler=None, level="DEBUG", title="Logs", **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing", dp(4))
        super().__init__(**kwargs)
        self.handler = handler if handler is not None else install_kivy_log_handler()

        header = BoxLayout(size_hint_y=None, height=dp(28), spacing=dp(6))
        header.add_widget(Label(text=title, halign="left", valign="middle"))

        self.level_spinner = Spinner(
            text=level,
            values=self.LEVELS,
            size_hint_x=None,
            width=dp(110),
        )
        self.level_spinner.bind(text=self._on_level_selected)
        header.add_widget(self.level_spinner)

        self.clear_btn = Button(text="Clear", size_hint_x=None, width=dp(80))
        self.clear_btn.bind(on_release=lambda *_: self.clear())
        header.add_widget(self.clear_btn)
        self.add_widget(header)

        self.log_view = LogView(size_hint_y=1)
        self.add_widget(self.log_view)

        self.handler.setLevel(getattr(logging, level, logging.DEBUG))
        # Flush anything buffered before the panel existed.
        self.handler.attach(self.log_view)

    def _on_level_selected(self, _spinner, level_name):
        self.handler.setLevel(getattr(logging, level_name, logging.DEBUG))

    def clear(self):
        self.log_view.clear()
        self.handler.clear()
