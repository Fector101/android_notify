"""
Android Texts related logic
"""

from android_notify.config import on_android_platform
from android_notify.internal.java_classes import String, NotificationCompatBigTextStyle, NotificationCompatInboxStyle


def set_big_text(builder, body, title="", summary=""):
    """Sets a big text for when drop down button is pressed

    :param builder: Builder instance
    :param body: The big text that will be displayed
    :param title: The big text title
    :param summary: The big text summary
    """
    if not on_android_platform():
        return False

    big_text_style = NotificationCompatBigTextStyle()

    if title:
        big_text_style.setBigContentTitle(String(title))
    if summary:
        big_text_style.setSummaryText(String(summary))

    big_text_style.bigText(String(body))
    builder.setStyle(big_text_style)
    logger.info('Done setting big text')

    return True


def set_sub_text(builder, sub_text):
    """
    :param builder: Builder instance.
    :param sub_text: The text that will be displayed.
    """
    if on_android_platform():
        builder.setSubText(String(sub_text))
    logger.info(f'new notification sub text: {sub_text}')


def set_title(builder, title, using_layout=False):
    """Sets notification Title

    :param builder: Builder instance:
    :param title: New Notification Title
    :param using_layout: Whether to use layout or not
    """

    if not on_android_platform():
        return None

    if using_layout:
        pass
        # self.__apply_basic_custom_style()
    else:
        builder.setContentTitle(String(title))

    logger.info(f'new notification title: {title}')
    return None


def set_message(builder, message, using_layout=False):
    """Sets notification message

    :param builder: Builder instance:
    :param message: New Notification message
    :param using_layout: Whether to use layout or not
    """

    if not on_android_platform():
        return None

    if using_layout:
        pass
        # self.__apply_basic_custom_style()
    else:
        builder.setContentText(String(message))

    logger.info(f'new notification message: {message}')
    return None


def set_lines(builder, lines):
    """Sets notification line
    :param builder: Builder instance
    :param lines: List of strings
    """
    if not on_android_platform() or not lines:
        return None

    inbox_style = NotificationCompatInboxStyle()
    for line in lines:
        inbox_style.addLine(str(line))

    builder.setStyle(inbox_style)
    logger.info(f'Added Lines: {lines}')
    return None



from android_notify.internal.java_classes import Color, RemoteViews, NotificationCompatDecoratedCustomViewStyle
from android_notify.internal.logger import logger
from android_notify.config import get_python_activity_context


def setLayoutText(layout, text_id, text, color):
    # checked if self.title_color available before entering method
    if text_id and text:
        layout.setTextViewText(text_id, text)
        if color:
            layout.setTextColor(text_id, Color.parseColor(color))


def set_custom_colors(builder, title, message, title_color, message_color):
    # Load layout
    context = get_python_activity_context()
    resources = context.getResources()
    package_name = context.getPackageName()

    # ids
    small_layout_id = resources.getIdentifier("an_colored_basic_small", "layout", package_name)
    large_layout_id = resources.getIdentifier("an_colored_basic_large", "layout", package_name)
    title_id = resources.getIdentifier("title", "id", package_name)
    message_id = resources.getIdentifier("message", "id", package_name)

    # Layout
    notificationLayout = RemoteViews(package_name, small_layout_id)
    notificationLayoutExpanded = RemoteViews(package_name, large_layout_id)
    if small_layout_id == 0: # "== 0" for reference will be zero when not found
        logger.warning(f'XML for Colored text Not Found small_layout_id: {small_layout_id}, large_layout_id:  {large_layout_id}')

    # Notification Content
    setLayoutText(
        layout=notificationLayout, text_id=title_id,
        text=title, color=title_color
    )
    setLayoutText(
        layout=notificationLayoutExpanded, text_id=title_id,
        text=title, color=title_color
    )
    setLayoutText(
        layout=notificationLayoutExpanded, text_id=message_id,
        text=message, color=message_color
    )
    # self.__setLayoutText(
    #     layout=notificationLayout, id=message_id,
    #     text=self.message, color=self.message_color
    # )
    builder.setStyle(NotificationCompatDecoratedCustomViewStyle())
    builder.setCustomContentView(notificationLayout)
    builder.setCustomBigContentView(notificationLayoutExpanded)

# Have to reconstruct layout, i.e. refill args title's and msg's
# def set_custom_layout_title(builder, text,color=None):
#     """Sets custom title
#     :param builder: Builder instance:
#     :param text: Title text
#     :param color: title Color"""
#
#     if not on_android_platform():
#         return None
#     setLayoutText
#     return None