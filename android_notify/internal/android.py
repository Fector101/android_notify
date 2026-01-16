"""
Android related logic
"""
import time

from .logger import logger
from ..config import get_notification_manager, on_android_platform, from_service_file, on_flet_app, \
    get_python_activity_context
from .permissions import has_notification_permission
from .java_classes import autoclass, BuildVersion, Uri, NotificationCompat, NotificationManagerCompat, \
    NotificationManager, Context
from .an_types import Importance


def cancel_all_notifications():
    """
    Removes all app Notifications from tray
    """
    if on_android_platform():
        get_notification_manager().cancelAll()
    logger.info('Removed All Notifications.')


def cancel_notifications(notification_id):
    """
    Removes a Notification from tray
    :param notification_id: gotten form `Notification` id
    """
    if on_android_platform():
        get_notification_manager().cancel(notification_id)
    logger.info('Removed Notification.')


def dispatch_notification(notification_id, builder, passed_check=False):
    if from_service_file():  # android has_notification_permission has some internal error when checking from service
        try:
            get_notification_manager().notify(notification_id, builder.build())
        except Exception as error_sending_notification_from_service:
            logger.exception(error_sending_notification_from_service)
    elif on_flet_app() or passed_check or has_notification_permission():
        try:
            get_notification_manager().notify(notification_id, builder.build())
        except Exception as notify_error:
            logger.exception(notify_error)
    else:
        logger.warning('Permission not granted to send notifications')


def set_when(builder, secs_ago):
    """
    Sets the notification's timestamp to a specified number of seconds in the past.

    :param builder: Builder instance
    :param secs_ago : int or float
        The number of seconds ago the notification should appear to have been posted.
        For example, `60` means "1 minute ago", `3600` means "1 hour ago".

    """

    if not on_android_platform():
        return None

    ms = int((time.time() - secs_ago) * 1000)
    builder.setWhen(ms)
    builder.setShowWhen(True)

    logger.info(f"When set to {secs_ago} ago.")
    return None


def show_infinite_progressbar(builder):
    """
    Shows the infinite progressbar
    :param builder: Builder instance
    """

    if on_android_platform():
        builder.setProgress(0, 0, True)

    logger.info('Showing infinite progressbar.')


def remove_buttons(builder):
    """
    Removes all buttons
    """
    if on_android_platform():
        builder.mActions.clear()

    logger.info('Removed Notification Buttons.')


def get_sound_uri(res_sound_name):
    if not on_android_platform() or not res_sound_name:
        return None
    context = get_python_activity_context()
    package_name = context.getPackageName()
    return Uri.parse(f"android.resource://{package_name}/raw/{res_sound_name}")


def set_sound(builder, res_sound_name):
    """
    Sets sound for devices less than android 8 (For 8+ use createChannel)
    :param builder: builder instance
    :param res_sound_name: audio file name (without .wav or .mp3) locate in res/raw/
    """

    if not on_android_platform():
        return None

    if res_sound_name and BuildVersion.SDK_INT < 26:
        try:
            builder.setSound(get_sound_uri(res_sound_name))
            return True
        except Exception as failed_adding_sound_for_devices_below_android8:
            logger.exception(failed_adding_sound_for_devices_below_android8)
    return None


def get_android_importance(importance: Importance):
    """
    Returns Android Importance Values
    :param importance: ['urgent','high','medium','low','none']
    :return: Android equivalent int or empty str
    """
    if not on_android_platform():
        return None
    value = ''
    if importance == 'urgent':
        value = NotificationCompat.PRIORITY_HIGH if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_HIGH
    elif importance == 'high':
        value = NotificationCompat.PRIORITY_DEFAULT if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_DEFAULT
    elif importance == 'medium':
        value = NotificationCompat.PRIORITY_LOW if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_LOW
    elif importance == 'low':
        value = NotificationCompat.PRIORITY_MIN if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_MIN
    elif importance == 'none':
        value = '' if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_NONE

    return value
    # side-note 'medium' = NotificationCompat.PRIORITY_LOW and 'low' = NotificationCompat.PRIORITY_MIN # weird but from docs


def do_not_disturb_on():
    if not on_android_platform():
        return None
    try:
        nm = get_python_activity_context().getSystemService(Context.NOTIFICATION_SERVICE)
        mode = nm.getCurrentInterruptionFilter()
        return mode != NotificationManager.INTERRUPTION_FILTER_ALL
    except Exception as error_getting_do_not_disturb_state:
        logger.exception(error_getting_do_not_disturb_state)


def force_vibrate(repeat=False):
    if not on_android_platform():
        return None

    context = get_python_activity_context()
    vibrator = context.getSystemService(Context.VIBRATOR_SERVICE)

    if vibrator is None or not vibrator.hasVibrator():
        logger.warning("No vibrator available")
        return None

    if do_not_disturb_on():
        logger.warning("Do not disturb is on")

    AudioAttributes = autoclass('android.media.AudioAttributes')
    AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
    pattern = [0, 500]  # vibrate pattern for once trying to replicate regular notification vibration.

    if BuildVersion.SDK_INT >= 26:
        VibrationEffect = autoclass('android.os.VibrationEffect')
        effect = VibrationEffect.createWaveform(pattern, -1 if not repeat else 0)
        attributes = AudioAttributesBuilder().setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).setUsage(
            AudioAttributes.USAGE_ALARM).build()
        vibrator.vibrate(effect, attributes)
        return None
    else:
        vibrator.vibrate(pattern, -1 if not repeat else 0)
        return None
