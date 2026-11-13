import logging
import os, sys, importlib, traceback, unittest
import flet as ft

from contextlib import redirect_stdout
from android_notify import Notification, NotificationHandler

from android_notify.config import on_android_platform, __version__
from android_notify.core import get_app_root_path, asks_permission_if_needed
from android_notify.internal.logger import android_print, logger

logger.setLevel(logging.DEBUG)


def main(page: ft.Page):
    page.title = f"Android Notify {__version__}"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.window.width = 400
    page.window.height = 720

    # ---------------------------------------------------------------------------
    # Paths
    # ---------------------------------------------------------------------------
    try:
        logs_path = (
            os.path.join(get_app_root_path(), "test_logs.txt")
            if on_android_platform()
            else os.path.join(os.getcwd(), "src", "test_logs.txt")
        )
    except Exception:
        logs_path = "/sdcard/test_logs.txt"

    # ---------------------------------------------------------------------------
    # Shared UI pieces
    # ---------------------------------------------------------------------------
    snack = ft.SnackBar(ft.Text(""), duration=2000)

    def flash(msg: str, color="green"):
        snack.content = ft.Text(msg, color="white")
        snack.bgcolor = color
        snack.open = True
        snack.update()

    def badge_row():
        has = NotificationHandler.has_permission()
        return ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE if has else ft.Icons.CANCEL,
                        color="green" if has else "red", size=16),
                ft.Text("Notification permission granted" if has else "Notification permission denied",
                        size=12, color="green" if has else "red"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    # ---------------------------------------------------------------------------
    # Home page
    # ---------------------------------------------------------------------------
    def home_view() -> list:
        def on_ask(_):
            try:
                asks_permission_if_needed()
                flash("Permission prompt sent")
            except Exception as e:
                flash(str(e), "red")

        def on_basic(_):
            try:
                Notification(title=f"{__version__} Hello World", message="From android_notify").send()
                flash("Notification sent")
            except Exception as e:
                flash(str(e), "red")

        def on_cancel(_):
            try:
                Notification.cancelAll()
                flash("All notifications cancelled")
            except Exception as e:
                flash(str(e), "red")

        return [
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[ft.Colors.BLUE_700, ft.Colors.BLUE_500],
                ),
                padding=ft.padding.Padding.all(24),
                border_radius=ft.border_radius.BorderRadius.only(bottom_left=20, bottom_right=20),
                content=ft.Column(
                    [
                        ft.Text("Android Notify", size=26, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Text(f"v{__version__}", size=14, color="white70"),
                        ft.Container(height=8),
                        badge_row(),
                    ],
                    spacing=4,
                ),
            ),
            ft.Container(
                padding=ft.padding.Padding.symmetric(horizontal=16),
                content=ft.Column(
                    [
                        _section_header("Quick Actions"),
                        _action_card(
                            "Send Notification",
                            "Basic title + message notification",
                            ft.Icons.NOTIFICATIONS_ACTIVE,
                            on_basic,
                        ),
                        _action_card(
                            "Request Permission",
                            "Prompt for POST_NOTIFICATIONS access",
                            ft.Icons.SHIELD,
                            on_ask,
                        ),
                        _action_card(
                            "Cancel All",
                            "Clear all notifications from tray",
                            ft.Icons.DELETE_SWEEP,
                            on_cancel,
                        ),
                    ],
                    spacing=8,
                ),
            ),
        ]

    # ---------------------------------------------------------------------------
    # Styles page
    # ---------------------------------------------------------------------------
    def styles_view() -> list:
        def _send(fn, label):
            try:
                fn()
                flash(f"{label} sent")
            except Exception as e:
                flash(str(e), "red")

        def s_simple(_):
            _send(
                lambda: Notification(title="Simple", message="Basic notification").send(),
                "Simple",
            )

        def s_progress(_):
            import time as _t
            def _do():
                n = Notification(title="Downloading...", message="0%", progress_current_value=0, progress_max_value=100)
                n.send()
                for i in range(0, 101, 20):
                    _t.sleep(1)
                    n.updateProgressBar(i, f"{i}%")
                n.removeProgressBar(title="Done", message="Download complete")
            _send(_do, "Progress")

        def s_big_text(_):
            def _do():
                n = Notification(title="Big Text", message="Tap to expand")
                n.setBigText("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                             "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                             "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.")
                n.send()
            _send(_do, "Big Text")

        def s_big_picture(_):
            def _do():
                n = Notification(title="Big Picture", message="Image notification")
                n.setBigPicture("assets/icon.png")
                n.send()
            _send(_do, "Big Picture")

        def s_large_icon(_):
            def _do():
                n = Notification(title="Large Icon", message="Has a large icon")
                n.setLargeIcon("assets/icon.png")
                n.send()
            _send(_do, "Large Icon")

        def s_inbox(_):
            n = Notification(title="Inbox", message="Multi-line inbox style")
            n.setLines(["First item", "Second item", "Third item", "Fourth item"])
            _send(lambda: n.send(), "Inbox")

        def s_buttons(_):
            n = Notification(title="With Buttons", message="Tap a button below")
            n.addButton(text="Like", on_release=lambda: print("Liked"))
            n.addButton(text="Share", on_release=lambda: print("Shared"))
            _send(lambda: n.send(), "Buttons")

        def s_persistent(_):
            _send(
                lambda: Notification(title="Persistent", message="Won't be cleared").send(persistent=True),
                "Persistent",
            )

        def s_update(_):
            import time as _t
            def _do():
                n = Notification(title="Original Title", message="Original Message")
                n.send()
                _t.sleep(2)
                n.updateTitle("Updated Title")
                n.updateMessage("Updated Message")
            _send(_do, "Update")

        def s_custom_color(_):
            _send(
                lambda: Notification(
                    title="Colored Title", message="Colored message body",
                    title_color="#FF5722", message_color="#4CAF50",
                ).send(),
                "Custom Color",
            )

        items = [
            ("Simple", "Basic title + message", ft.Icons.NOTIFICATIONS, s_simple),
            ("Progress", "Live progress bar updates", ft.Icons.DOWNLOAD, s_progress),
            ("Big Text", "Expandable long text", ft.Icons.ARTICLE, s_big_text),
            ("Big Picture", "Large image preview", ft.Icons.IMAGE, s_big_picture),
            ("Large Icon", "Right-side icon image", ft.Icons.INSERT_PHOTO, s_large_icon),
            ("Inbox", "Multi-line list style", ft.Icons.INBOX, s_inbox),
            ("Buttons", "Action buttons below", ft.Icons.SMART_BUTTON, s_buttons),
            ("Persistent", 'Survives "users" clear-all', ft.Icons.LOCK, s_persistent),
            ("Update Title/Msg", "Modify after sending", ft.Icons.EDIT, s_update),
            ("Custom Colors", "Colored title and body", ft.Icons.PALETTE, s_custom_color),
        ]

        return [_section_header("Notification Styles")] + \
            [_action_card(name, desc, icon, fn) for name, desc, icon, fn in items]

    # ---------------------------------------------------------------------------
    # Channels page
    # ---------------------------------------------------------------------------
    def channels_view() -> list:
        channel_name_field = ft.TextField(label="Channel Name", value="Test Channel", dense=True)
        channel_id_field = ft.TextField(label="Channel ID", value="test_channel", dense=True)
        result_text = ft.Text("", size=13, color="grey", selectable=True)

        def on_create(_):
            try:
                n = Notification(
                    title="Channel Test", message="Sent via custom channel",
                    channel_name=channel_name_field.value or "Test Channel",
                    channel_id=channel_id_field.value or "test_channel",
                )
                n.send()
                result_text.value = f"Created & sent on '{channel_name_field.value}'"
                result_text.color = "green"
                flash("Channel notification sent")
            except Exception as e:
                result_text.value = str(e)
                result_text.color = "red"
            result_text.update()

        def on_check(_):
            try:
                cid = channel_id_field.value or "test_channel"
                exists = Notification.channelExists(cid)
                result_text.value = f"Channel '{cid}': {'exists' if exists else 'NOT found'}"
                result_text.color = "green" if exists else "orange"
            except Exception as e:
                result_text.value = str(e)
                result_text.color = "red"
            result_text.update()

        def on_list(_):
            try:
                channels = Notification.getChannels()
                if channels:
                    lines = [f"- {c}" for c in channels]
                    result_text.value = f"Channels:\n" + "\n".join(lines)
                else:
                    result_text.value = "No channels found"
                result_text.color = "grey"
            except Exception as e:
                result_text.value = str(e)
                result_text.color = "red"
            result_text.update()

        return [
            _section_header("Notification Channels"),
            ft.Container(
                padding=16,
                margin=ft.margin.Margin.symmetric(horizontal=16),
                border=ft.border.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                content=ft.Column(
                    [
                        channel_name_field,
                        channel_id_field,
                        ft.Row(
                            [
                                ft.ElevatedButton("Send via Channel", on_click=on_create, icon=ft.Icons.SEND),
                                ft.OutlinedButton("Check Exists", on_click=on_check, icon=ft.Icons.HELP_OUTLINE),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.TextButton("List All Channels", on_click=on_list, icon=ft.Icons.LIST),
                        result_text,
                    ],
                    spacing=10,
                ),
            ),
        ]

    # ---------------------------------------------------------------------------
    # Tests page
    # ---------------------------------------------------------------------------
    def tests_view() -> list:
        test_log = ft.Markdown(
            "",
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            expand=True,
        )
        status_text = ft.Text("Ready", size=13, color="grey")
        progress = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

        def run_all(_):
            status_text.value = "Running tests..."
            progress.visible = True
            status_text.update()
            progress.update()

            try:
                base_path = (
                    get_app_root_path()
                    if on_android_platform()
                    else os.path.join(os.getcwd(), "src")
                )
            except Exception:
                base_path = os.path.dirname(__file__)

            try:
                with open(logs_path, "w") as logf, redirect_stdout(logf):
                    suite = unittest.TestSuite()
                    test_loader = unittest.TestLoader()
                    loaded = False

                    for dirpath, _, filenames in os.walk(base_path):
                        py = sorted(f for f in filenames if f.startswith("test_") and f.endswith(".py"))
                        pyc = sorted(f for f in filenames if f.startswith("test_") and f.endswith(".pyc"))

                        if not py and not pyc:
                            continue

                        if py:
                            try:
                                suite.addTests(test_loader.discover(start_dir=dirpath, pattern="test_*.py"))
                                loaded = True
                            except Exception as e:
                                android_print(f"discover .py failed: {e}")

                        if not loaded and pyc:
                            for name in pyc:
                                pyc_path = os.path.join(dirpath, name)
                                mod_name = name[:-4]
                                try:
                                    src_loader = importlib.machinery.SourcelessFileLoader(mod_name, pyc_path)
                                    spec = importlib.util.spec_from_loader(mod_name, src_loader, origin=pyc_path)
                                    mod = importlib.util.module_from_spec(spec)
                                    src_loader.exec_module(mod)
                                    suite.addTests(test_loader.loadTestsFromModule(mod))
                                    loaded = True
                                except Exception as e:
                                    android_print(f"import {mod_name} failed: {e}")

                    count = suite.countTestCases()
                    android_print(f"Discovered tests: {count}")

                    if count == 0:
                        status_text.value = "No tests found"
                        progress.visible = False
                        status_text.update()
                        progress.update()
                        return

                    runner = unittest.TextTestRunner(stream=logf, verbosity=2)
                    runner.run(suite)

                if os.path.exists(logs_path):
                    with open(logs_path, "r") as f:
                        test_log.value = f.read()
            except Exception as e:
                test_log.value = f"```\n{traceback.format_exc()}\n```"

            test_log.update()
            status_text.value = "Done"
            progress.visible = False
            status_text.update()
            progress.update()

        return [
            _section_header("Test Suite"),
            ft.Container(
                padding=16,
                margin=ft.margin.Margin.symmetric(horizontal=16),
                border=ft.border.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.ElevatedButton("Run All Tests", on_click=run_all, icon=ft.Icons.PLAY_ARROW),
                                progress,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        status_text,
                    ],
                    spacing=10,
                ),
            ),
            ft.Container(
                margin=ft.margin.Margin.symmetric(horizontal=16),
                padding=12,
                border=ft.border.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                expand=True,
                content=ft.Column([test_log], scroll=ft.ScrollMode.AUTO),
            ),
        ]

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------
    def _section_header(title: str) -> ft.Control:
        return ft.Container(
            padding=ft.padding.Padding.only(left=4, top=12, bottom=4),
            content=ft.Text(title, size=13, weight=ft.FontWeight.W_600, color="grey"),
        )

    def _action_card(title: str, subtitle: str, icon: ft.IconData, on_click) -> ft.Control:
        return ft.Container(
            margin=ft.margin.Margin.symmetric(horizontal=16),
            border=ft.border.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=12,
            content=ft.ListTile(
                leading=ft.Icon(icon, color=ft.Colors.BLUE_600),
                title=ft.Text(title, size=15, weight=ft.FontWeight.W_500),
                subtitle=ft.Text(subtitle, size=12, color="grey"),
                on_click=on_click,
                content_padding=ft.padding.Padding.symmetric(horizontal=16, vertical=4),
            ),
        )

    # ---------------------------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------------------------
    pages = {
        0: home_view,
        1: styles_view,
        2: channels_view,
        3: tests_view,
    }
    body = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=8,
        expand=True,
    )

    nav = ft.NavigationBar(
        selected_index=0,
        height=64,
        label_behavior=ft.NavigationBarLabelBehavior.ALWAYS_SHOW,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS, label="Styles"),
            ft.NavigationBarDestination(icon=ft.Icons.DEVICES, label="Channels"),
            ft.NavigationBarDestination(icon=ft.Icons.SCIENCE, label="Tests"),
        ],
        on_change=lambda e: switch_tab(e.control.selected_index),
    )

    def switch_tab(idx):
        body.controls = pages[idx]()
        if body.page:
            body.update()

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                [body, nav],
                spacing=0,
                expand=True,
                scroll=None,
            ),
        ),
    )
    page.overlay.append(snack)
    switch_tab(0)


if __name__ == "__main__":
    ft.run(main)