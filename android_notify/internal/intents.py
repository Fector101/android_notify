"""
For Intent related blocks
"""

from .java_classes import Bundle, Intent, PendingIntent, String
from android_notify.config import get_python_activity, get_python_activity_context
from android_notify.internal.logger import logger


def set_action(action_intent, action, title, key_int):
    action_intent.setAction(action)
    action_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
    bundle = Bundle()
    bundle.putString("title", title)
    bundle.putInt("key_int", key_int)
    action_intent.putExtras(bundle)
    action_intent.putExtra("button_id", action)


def get_default_pending_intent_for_btn(action, title, btn_no):
    context = get_python_activity_context()
    PythonActivity = get_python_activity()
    action_intent = Intent(context, PythonActivity)
    set_action(action_intent=action_intent, action=action, title=title, key_int=btn_no)
    pending_action_intent = PendingIntent.getActivity(
        context, btn_no, action_intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    return pending_action_intent

def get_broadcast_pending_intent_for_btn(receiver_class, action, title, btn_no):
    context = get_python_activity_context()
    action_intent = Intent(context, receiver_class)
    set_action(action_intent=action_intent, action=action, title=title, key_int=btn_no)
    pending_action_intent = PendingIntent.getBroadcast(
        context, btn_no, action_intent,
        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
    )
    return pending_action_intent


def add_data_to_intent(intent, title, notification_id):
    """Persist Some data to notification object for later use"""
    bundle = Bundle()
    bundle.putString("notification_title", title or 'Title Placeholder')
    bundle.putInt("notification_id", notification_id)
    intent.putExtras(bundle)


def add_intent_to_open_app(builder, action_name, notification_title, notification_id):
    context = get_python_activity_context()
    PythonActivity = get_python_activity()
    intent = Intent(context, PythonActivity)
    intent.setFlags(
        Intent.FLAG_ACTIVITY_CLEAR_TOP |  # Makes Sure tapping notification always brings the existing instance of app forward.
        Intent.FLAG_ACTIVITY_SINGLE_TOP |  # If the activity is already at the top, reuse it instead of creating a new instance.
        Intent.FLAG_ACTIVITY_NEW_TASK
        # Required when starting an Activity from a Service; ignored when starting from another Activity.
    )
    action = String(action_name)
    intent.setAction(action)
    bundle = Bundle()
    bundle.putString("title", notification_title)
    bundle.putInt("notification_id", notification_id)
    intent.putExtras(bundle)
    add_data_to_intent(intent, notification_title, notification_id)

    # intent.setAction(Intent.ACTION_MAIN)      # Marks this intent as the main entry point of the app, like launching from the home screen.
    # intent.addCategory(Intent.CATEGORY_LAUNCHER)  # Adds the launcher category so Android treats it as a launcher app intent and properly manages the task/back stack.

    pending_intent = PendingIntent.getActivity(
        context, notification_id,
        intent, PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
    )
    builder.setContentIntent(pending_intent)



def get_intent_used_to_open_app():
    action = None

    # ALL WORKED
    # try:
    #     PythonActivity = autoclass('org.kivy.android.PythonActivity')
    #     activity = PythonActivity.mActivity
    #     intent = activity.getIntent()
    #     try:
    #         extras = intent.getExtras()
    #         print(extras, 11)
    #         if extras:
    #             for key in extras.keySet().toArray():
    #                 value = extras.get(key)
    #                 print(key, value)
    #     except Exception as error_in_loop:
    #         print(error_in_loop)
    #
    #
    #     try:
    #         action = intent.getAction()
    #         print('Start up Intent ----', action)
    #     except Exception as error_getting_action:
    #         print("error_getting_action",error_getting_action)
    #
    #
    #     try:
    #         extras = intent.getExtras()
    #         if extras:
    #             value = extras.getString(String("title"))
    #             print('title', value)
    #     except Exception as error_in_last:
    #         print("error_getting_title",error_in_last)
    #         pass
    #
    #     print('start Up Title --->', intent.getStringExtra("title"))
    # except Exception as error_getting_notify_name:
    #     print("Error getting xxxxx name:", error_getting_notify_name)


    # TODO action Doesn't change even not opened from notification
    try:
        context = get_python_activity_context()
        intent = context.getIntent()
        action = intent.getAction()
    except Exception as error_getting_notification_name:
        logger.exception(error_getting_notification_name)

    return action