# android_notify/tests/basic_notification_actions.py

from android_notify import NotificationHandler
from android_notify.internal.permissions import ask_notification_permission
from android_notify.core import asks_permission_if_needed


def ask_permission_no_callback():
    NotificationHandler.asks_permission()


def ask_permission_with_callback():
    def some_callback(answer):
        print(f"Hey Dude, Notification Request result {answer}.")
    NotificationHandler.asks_permission(some_callback)


def ask_permission_simple_regular():
    asks_permission_if_needed()


def ask_permission_simple_legacy():
    asks_permission_if_needed(legacy=True)


def ask_permission_from_source():
    def some_callback(answer):
        print(f"Hey, Notification Request Request1: {answer}")
    ask_notification_permission(callback=some_callback)


NOTIFICATION_PERMISSION_TESTS = {
    "permission (no callback)": ask_permission_no_callback,
    "permission (with callback)": ask_permission_with_callback,
    "permission (simple)": ask_permission_simple_regular,
    "permission (legacy)": ask_permission_simple_legacy,
    "permission (from source)": ask_permission_from_source,
}
