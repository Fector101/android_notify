"""
For Notification Channels related blocks
"""
from typing import Any

from android_notify.config import get_notification_manager, on_android_platform

from android_notify.internal.java_classes import BuildVersion, NotificationChannel
from android_notify.internal.an_types import Importance
from android_notify.internal.android import get_sound_uri, get_android_importance
from android_notify.internal.logger import logger

def does_channel_exist(channel_id):
    """
    Check if a channel exists
    :param channel_id:
    """
    if not on_android_platform():
        return None

    notification_manager = get_notification_manager()
    if BuildVersion.SDK_INT >= 26 and notification_manager.getNotificationChannel(channel_id):
        return True
    return False


def create_channel(id__, name: str, description='', importance: Importance = 'urgent', res_sound_name=None,vibrate=False):
    """
    Creates a user visible toggle button for specific notifications, Required For Android 8.0+
    :param id__: Used to send other notifications later through same channel.
    :param name: user-visible channel name.
    :param description: user-visible detail about channel (Not required defaults to empty str).
    :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
    :param res_sound_name: audio file name (without .wav or .mp3) locate in res/raw/
    :param vibrate: if channel notifications should vibrate or not
    :return: boolean if channel created
    """
    def info_log():
        logger.info(
            f"Created {name} channel, id: {id__}, description: {description}, res_sound_name: {res_sound_name},vibrate: {vibrate}")

    if not on_android_platform():
        info_log()
        return None

    notification_manager = get_notification_manager()
    android_importance_value = get_android_importance(importance)
    sound_uri = get_sound_uri(res_sound_name)

    if not does_channel_exist(id__):
        channel = NotificationChannel(id__, name, android_importance_value)
        if description:
            channel.setDescription(description)
        if sound_uri:
            channel.setSound(sound_uri, None)
        if vibrate:
            # channel.setVibrationPattern([0, 500, 200, 500]) # Using Phone's default pattern
            # Android 15 ignored long patterns, didn't vibrate when not in silent and
            # conflicting channel names got the same vibrate state even with different ids
            # IMPORTANCE_LOW didn't vibrate but didn't show heads-up
            channel.enableVibration(bool(vibrate))
        notification_manager.createNotificationChannel(channel)
        info_log()
        return True
    else:
        logger.debug(f"{id__} channel already exists")
    return False


def delete_channel(channel_id):
    """
    Deletes a channel matching the channel_id
    :param channel_id: notification channel id
    """

    if not on_android_platform():
        return None

    if does_channel_exist(channel_id):
        get_notification_manager().deleteNotificationChannel(channel_id)
        return True
    return False


def delete_all_channels():
    """Deletes all notification channel
    :returns amount deleted
    """

    amount = 0
    if not on_android_platform():
        return amount

    notification_manager = get_notification_manager()
    channels = get_channels()
    for index in range(channels.size()):
        amount += 1
        channel = channels.get(index)
        channel_id = channel.getId()
        notification_manager.deleteNotificationChannel(channel_id)
    return amount


def get_channels() -> list[Any] | Any:
    """Return all existing channels"""
    if not on_android_platform():
        return []

    return get_notification_manager().getNotificationChannels()


def do_channels_exist(ids):
    """Uses list of IDs to check if channel exists
    returns list of channels that don't exist
    """
    if not on_android_platform():
        return ids  # Assume none exist on non-Android environments
    missing_channels = []
    notification_manager = get_notification_manager()
    for channel_id in ids:
        exists = (
                BuildVersion.SDK_INT >= 26 and
                notification_manager.getNotificationChannel(channel_id)
        )
        if not exists:
            missing_channels.append(channel_id)
    return missing_channels