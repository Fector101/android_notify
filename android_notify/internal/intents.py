"""
For Intent related blocks
"""
import traceback

from .java_classes import Bundle, Intent, PendingIntent
from android_notify.config import get_python_activity, get_python_activity_context, get_package_name
from android_notify.internal.logger import logger
from android_notify.internal.helper import JAVA_INT_RANGE


def set_action(action_intent, action, title, key_int, data_object):
    action_intent.setAction(action)
    action_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
    bundle = Bundle()
    insert_data_object(data_object=data_object, bundle=bundle)
    bundle.putString("notification_name", action) # Used to check if from notification
    bundle.putString("notification_button_title", title)
    bundle.putInt("notification_button_id", key_int)
    action_intent.putExtras(bundle)


def get_button_request_code(notification_id, btn_no):
    """Request code for a button's `PendingIntent`, unique per notification.

    A PendingIntent is identified by (package, request code, `Intent.filterEquals()`);.
    `btn_no` is a per notification button counter, so it is 1 for the first button of *every* notification: two notifications
    using the same action would share one PendingIntent, and `FLAG_UPDATE_CURRENT` would
    overwrite the other notification's extras (data_object, notification_button_title...).
    Folding the notification id in keeps them apart.
    """
    return (notification_id * 1000 + btn_no) % JAVA_INT_RANGE


def get_default_pending_intent_for_btn(action, title, btn_no, data_object, notification_id):
    context = get_python_activity_context()
    PythonActivity = get_python_activity()
    action_intent = Intent(context, PythonActivity)
    set_action(action_intent=action_intent, action=action, title=title, key_int=btn_no, data_object=data_object)
    pending_action_intent = PendingIntent.getActivity(
        context, get_button_request_code(notification_id, btn_no), action_intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    return pending_action_intent

def get_broadcast_pending_intent_for_btn(receiver_class, action, title, btn_no, data_object, notification_id):
    context = get_python_activity_context()
    action_intent = Intent(context, receiver_class)
    set_action(action_intent=action_intent, action=action, title=title, key_int=btn_no, data_object=data_object)
    pending_action_intent = PendingIntent.getBroadcast(
        context, get_button_request_code(notification_id, btn_no), action_intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    return pending_action_intent


def get_dynamic_broadcast_pending_intent(action, title, btn_no, data_object, notification_id):
    """Pending intent for a button that must reach a runtime registered receiver.

    `get_broadcast_pending_intent_for_btn` builds an explicit intent
    (`Intent(context, receiver_class)`), which only a receiver declared in the manifest can
    receive. Receivers registered at runtime (`android.broadcast.BroadcastReceiver`) are
    matched by intent filter only, so the button has to send an implicit broadcast.
    `setPackage()` scopes it to this app, which Android 14+ requires for implicit broadcasts
    delivered to a `RECEIVER_NOT_EXPORTED` receiver.

    Pass `notification_id` so the request code (and therefore the PendingIntent identity) is
    unique per notification, see `get_button_request_code`.
    """
    context = get_python_activity_context()
    action_intent = Intent(action)
    action_intent.setPackage(get_package_name())
    set_action(action_intent=action_intent, action=action, title=title, key_int=btn_no, data_object=data_object)
    pending_action_intent = PendingIntent.getBroadcast(
        context, get_button_request_code(notification_id, btn_no), action_intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    return pending_action_intent


def insert_data_object(data_object, bundle):
    if not data_object:
        return None
    try:
        for key, value in data_object.items():
            bundle.putString(str(key), str(value))
    except Exception as error_adding_data_object:
        logger.exception(error_adding_data_object)


def add_data_to_intent(intent, title, notification_id, action_name, data_object):
    """Persist Some data to notification object for later use"""
    bundle = Bundle()
    insert_data_object(data_object, bundle)
    bundle.putString("notification_title", title or 'Title Placeholder')
    bundle.putInt("notification_id", notification_id)
    bundle.putString("notification_name", action_name)
    intent.putExtras(bundle)


def add_intent_to_open_app(builder, action_name, notification_title, notification_id, data_object,_ignore_data=False):
    context = get_python_activity_context()
    PythonActivity = get_python_activity()
    intent = get_intent_for_launching_app() or Intent(context, PythonActivity)
    intent.setFlags(
        Intent.FLAG_ACTIVITY_CLEAR_TOP |  # Makes Sure tapping notification always brings the existing instance of app forward.
        Intent.FLAG_ACTIVITY_SINGLE_TOP |  # If the activity is already at the top, reuse it instead of creating a new instance.
        Intent.FLAG_ACTIVITY_NEW_TASK
        # Required when starting an Activity from a Service; ignored when starting from another Activity.
    )
    # action = String(action_name)
    # intent.setAction(action)

    # intent.setAction(Intent.ACTION_MAIN)      # Marks this intent as the main entry point of the app, like launching from the home screen.
    # intent.addCategory(Intent.CATEGORY_LAUNCHER)  # Adds the launcher category so Android treats it as a launcher app intent and properly manages the task/back stack.
    if not _ignore_data:
        add_data_to_intent(intent, notification_title, notification_id, str(action_name), data_object)
    pending_intent = PendingIntent.getActivity(
        context, notification_id,
        intent, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
    )
    builder.setContentIntent(pending_intent)
    if not _ignore_data:
        logger.debug(
        f'data for opening app-  notification_title: {notification_title}, notification_id: {notification_id}, notification_name: {action_name}')


def get_intent_for_launching_app():
    try:
        context = get_python_activity_context()
        package_manager = context.getPackageManager()
        package_name = context.getPackageName()
        return package_manager.getLaunchIntentForPackage(package_name)
    except Exception as error_getting_default_intent_for_launching_app:
        logger.error(error_getting_default_intent_for_launching_app)
        traceback.print_exc()
        return None


def get_name_used_to_open_app():
    """
    Fail Safe for `App.on_start`
    :return:
    """
    name = None

    # ALL WORKED
    # try:
    #     PythonActivity = autoclass('org.kivy.android.PythonActivity')
    #     activity = PythonActivity.mActivity
    #     intent = activity.getIntent()
    #     try:
    #         extras = intent.getExtras()
    #         drint(extras, 11)
    #         if extras:
    #             for key in extras.keySet().toArray():
    #                 value = extras.get(key)
    #                 drint(key, value)
    #             drint('start Up Title --->', intent.getStringExtra("notification_title"))
    #     except Exception as error_in_loop:
    #         drint(error_in_loop)
    #
    #
    #     try:
    #         action = intent.getAction()
    #         drint('Start up Intent ----', action)
    #     except Exception as error_getting_action:
    #         drint("error_getting_action",error_getting_action)
    #
    #
    # except Exception as error_getting_notify_name:
    #     drint("Error getting name1:", error_getting_notify_name)

    # TODO action Doesn't change even not opened from notification
    try:
        context = get_python_activity_context()
        intent = context.getIntent()
        extras = intent.getExtras()
        if extras:
            name = extras.getString("notification_name")
            # logger.debug(f"on_start notification_name: {name}")
        if not name:
            action = name = intent.getAction()
            logger.warning(f"Did not find notification name no extras in intent, Using action value: {action}")

        # logger.debug(f"on_start action: {intent.getAction()}")
    except Exception as error_getting_notification_name:
        logger.exception(error_getting_notification_name)

    return name


def get_data_object_added_to_intent(intent=None):
    gotten_data_object = {}
    if not intent:
        try:
            context = get_python_activity_context()
            intent = context.getIntent()
        except Exception as error_getting_intent:
            logger.exception(error_getting_intent)
    try:
        extras = intent.getExtras()
        if extras:
            for key in extras.keySet().toArray():
                value = extras.get(key)
                gotten_data_object[key] = value
        else:
            pass
    except Exception as error_getting_optional_data_object:
        logger.exception(f"Error getting data_object {error_getting_optional_data_object}")

    return gotten_data_object
