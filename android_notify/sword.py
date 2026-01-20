"""This Module Contain Class for creating Notification With Java"""
import time, threading, traceback
from typing import Any, Callable

from .base import BaseNotification
from .styles import NotificationStyles
from .internal.helper import generate_channel_id
from .config import from_service_file, get_notification_manager, on_flet_app, get_package_name, run_on_ui_thread, \
    get_python_activity_context, on_android_platform
from .internal.android import cancel_all_notifications, cancel_notifications, dispatch_notification, \
    set_when, show_infinite_progressbar, remove_buttons, set_sound, get_android_importance, force_vibrate

# Types
from .internal.an_types import Importance
# Permissions
from .internal.permissions import has_notification_permission, ask_notification_permission
# Channels
from .internal.channels import does_channel_exist, do_channels_exist, create_channel, delete_channel, \
    delete_all_channels, get_channels
# Intents
from .internal.intents import add_intent_to_open_app, get_default_pending_intent_for_btn, \
    get_broadcast_pending_intent_for_btn, get_name_used_to_open_app, get_data_object_added_to_intent
# All Needed Java Classes
from .internal.java_classes import autoclass, cast, String, BuildVersion, NotificationCompat, NotificationCompatBuilder, \
    NotificationCompatBigPictureStyle
# Logger
from .internal.logger import logger

from .widgets.images import set_default_small_icon, get_bitmap_from_path, get_bitmap_from_url, \
    set_small_icon_with_bitmap, get_img_absolute_path, find_and_set_default_icon, set_small_icon_color
from .widgets.texts import set_big_text, set_sub_text, set_title, set_message, set_lines, set_custom_colors



class Notification(BaseNotification):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    ---
    (Style Options)
    :param style: Style of the notification ('simple', 'progress', 'big_text', 'inbox', 'big_picture', 'large_icon', 'both_imgs'). both_imgs == using lager icon and big picture
    :param big_picture_path: Relative Path to the image resource.
    :param large_icon_path: Relative Path to the image resource.
    :param progress_current_value: Integer To set progress bar current value.
    :param progress_max_value: Integer To set Max range for progress bar.
    :param body: Large text For `big_Text` style, while `message` acts as subtitle.
    :param lines_txt: text separated by newLine symbol For `inbox` style `use addLine method instead`
    ---
    (Advance Options)
    :param sub_text: str for additional information next to title
    :param id: Pass in Old 'id' to use old instance
    :param callback: Function for notification Click.
    :param channel_name: - str Defaults to "Default Channel"
    :param channel_id: - str Defaults to "default_channel"
    ---
    (Options during Dev On PC)
    :param logs: - Bool Defaults to True
    ---
    (Custom Style Options)
    :param title_color: title color str (to be safe use hex code)
    :param message_color: message color str (to be safe use hex code)

    """

    notification_ids = [0]
    btns_box = {}
    main_functions = {}
    passed_check = False

    # During Development (When running on PC)
    BaseNotification.logs = not on_android_platform()

    def __init__(self, **kwargs):  # @dataclass already does work
        super().__init__(**kwargs)

        self.__called_set_data = None
        self.data_object = None
        self.__id = self.id or self.__get_unique_id()  # Different use from self.name all notifications require `integers` id's not `strings`
        self.id = self.__id  # To use same Notification in different instances

        # To Track progressbar last update (According to Android Docs Don't update bar to often, I also faced so issues when doing that)
        self.__update_timer = None
        self.__progress_bar_msg = ''
        self.__progress_bar_title = ''
        self.__cooldown = 0

        self.__generic_parameters_filled = False
        self.__using_set_priority_method = False

        # For components
        self.__lines = []
        self.__has_small_icon = False  # important notification can't send without
        self.__using_custom = self.message_color or self.title_color
        self.__format_channel(self.channel_name, self.channel_id)
        self.builder = None  # available through getter `self.builder`
        self.__no_of_buttons = 0
        self.notification_manager = None

        if not on_android_platform():
            return

        if not from_service_file() and not NotificationHandler.has_permission():
            NotificationHandler.asks_permission()

        self.notification_manager = get_notification_manager()
        context = get_python_activity_context()
        self.builder = NotificationCompatBuilder(context, self.channel_id)

    def setData(self, data_object:dict):
        """
        Set Optional data for notification
        :param data_object:
        :return:
        """
        self.__called_set_data = True
        self.data_object = data_object
        action_name = str(self.name or self.__id)
        add_intent_to_open_app(builder=self.builder, action_name=action_name, notification_title=str(self.title),
                               notification_id=self.__id, data_object=self.data_object)


    def addLine(self, text: str):
        self.__lines.append(text)

    def cancel(self, _id=0):
        """
        Removes a Notification instance from tray
        :param _id: not required uses Notification instance id as default
        """
        cancel_notifications(_id or self.__id)

    @classmethod
    def cancelAll(cls):
        """
        Removes all app Notifications from tray
        """
        cancel_all_notifications()

    @classmethod
    def channelExists(cls, channel_id):
        """
        Checks if a notification channel exists
        """
        return does_channel_exist(channel_id=channel_id)

    @classmethod
    def createChannel(cls, id, name: str, description='', importance: Importance = 'urgent', res_sound_name=None, vibrate=False):
        """
        Creates a user visible toggle button for specific notifications, Required For Android 8.0+
        :param id: Used to send other notifications later through same channel.
        :param name: user-visible channel name.
        :param description: user-visible detail about channel (Not required defaults to empty str).
        :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
        :param res_sound_name: audio file name (without .wav or .mp3) locate in res/raw/
        :param vibrate: if channel notifications should vibrate or not
        :return: boolean if channel created
        """
        return create_channel(id__=id, name=name, description=description, importance=importance, res_sound_name=res_sound_name, vibrate=vibrate)

    @classmethod
    def deleteChannel(cls, channel_id):
        """Delete a Channel Matching channel_id"""
        return delete_channel(channel_id)

    @classmethod
    def deleteAllChannel(cls):
        """Deletes all notification channel
        :returns amount deleted
        """
        return delete_all_channels()

    @classmethod
    def doChannelsExist(cls, ids):
        """Uses list of IDs to check if channel exists
        returns list of channels that don't exist
        """
        return do_channels_exist(ids)

    def refresh(self):
        """TO apply new components on notification"""
        if self.__generic_parameters_filled:
            # Don't dispatch before filling required values `self.__create_basic_notification`, Shouldn't dispatch till .send() is called
            self.__applyNewLinesIfAny()
            dispatch_notification(notification_id=self.__id, builder=self.builder, passed_check=self.passed_check)

    def setBigPicture(self, path):
        """
        set a Big Picture at the bottom
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if on_android_platform():
            self.__build_img(path, NotificationStyles.BIG_PICTURE)
        logger.info('Done setting big picture.')

    def setSmallIcon(self, path):
        """
        sets small icon to the top left
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if on_android_platform():
            self.app_icon = path
            self.__insert_app_icon(path)
        logger.info('Done setting small icon.')

    def setLargeIcon(self, path):
        """
        sets Large icon to the right
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if on_android_platform():
            self.__build_img(path, NotificationStyles.LARGE_ICON)
        logger.info('Done setting large icon.')

    def setBigText(self, body, title="", summary=""):
        """Sets a big text for when drop down button is pressed

        :param body: The big text that will be displayed
        :param title: The big text title
        :param summary: The big text summary
        """
        set_big_text(builder=self.builder, body=str(body), title=str(title), summary=str(summary))

    def setSubText(self, text):
        """
        In android version 7+ text displays in header next to title,
        While in lesser versions displays in third line of text, where progress-bar occupies
        :param text: str for subtext

        """
        self.sub_text = str(text)
        set_sub_text(builder=self.builder, sub_text=str(text))

    def setColor(self, color: str):
        """
        Sets Notification accent color, visible change in SmallIcon color
        :param color:  str - red,pink,... (to be safe use hex code)
        """
        set_small_icon_color(builder=self.builder, color=color)

    def setWhen(self, secs_ago):
        """
        Sets the notification's timestamp to a specified number of seconds in the past.

        :param secs_ago: int or float
            The number of seconds ago the notification should appear to have been posted.
            For example, `60` means "1 minute ago", `3600` means "1 hour ago".

        """

        set_when(builder=self.builder, secs_ago=secs_ago)

    def showInfiniteProgressBar(self):
        """Displays an (Infinite) progress Bar in Notification, that continues loading indefinitely.
        Can be Removed By `removeProgressBar` Method
        """
        show_infinite_progressbar(self.builder)
        self.refresh()

    def updateTitle(self, new_title):
        """Changes Old Title

        Args:
            new_title (str): New Notification Title
        """
        self.title = str(new_title)
        if self.isUsingCustom():
            self.__apply_basic_custom_style()
        else:
            set_title(builder=self.builder, title=self.title, using_layout=self.isUsingCustom())
        self.refresh()

    def updateMessage(self, new_message):
        """Changes Old Message

        Args:
            new_message (str): New Notification Message
        """
        self.message = str(new_message)
        if self.isUsingCustom():
            self.__apply_basic_custom_style()
        else:
            set_message(builder=self.builder, message=self.message, using_layout=self.isUsingCustom())
        self.refresh()

    def updateProgressBar(self, current_value: int, message: str = '', title: str = '', cooldown=0.5,
                          _callback: Callable = None):
        """Updates progress bar current value

        Args:
            current_value (int): the value from progressbar current progress
            message (str): defaults to last message
            title (str): defaults to last title
            cooldown (float, optional): Little Time to Wait before change actually reflects, to avoid android Ignoring Change, Defaults to 0.5secs
            _callback (object): function for when change actual happens

        NOTE: There is a 0.5 sec delay for value change, if updating title,msg with progressbar frequently pass them in too to avoid update issues
        """

        # replacing new values for when timer is called
        self.progress_current_value = current_value
        self.__progress_bar_msg = message or self.message
        self.__progress_bar_title = title or self.title

        if self.__update_timer and self.__update_timer.is_alive():
            return

        def delayed_update():
            if self.__update_timer is None:  # Ensure we are not executing an old timer
                logger.warning('ProgressBar update skipped: bar has been removed.')
                return

            logger.info(f'Progress Bar Update value: {self.progress_current_value}.')

            if _callback:
                try:
                    _callback()
                except Exception as passed_in_callback_error:
                    logger.exception(passed_in_callback_error)
                    traceback.print_exc()

            if not on_android_platform():
                self.__update_timer = None
                return

            self.builder.setProgress(self.progress_max_value, self.progress_current_value, False)

            if self.__progress_bar_msg:
                self.updateMessage(self.__progress_bar_msg)
            if self.__progress_bar_title:
                self.updateTitle(self.__progress_bar_title)

            self.refresh()
            self.__update_timer = None

        # Start a new timer that runs after 0.5 seconds
        # self.__timer_start_time = time.time() # for logs
        self.__cooldown = cooldown
        self.__update_timer = threading.Timer(cooldown, delayed_update)
        self.__update_timer.start()

    def removeProgressBar(self, message='', show_on_update=True, title: str = '', cooldown=0.5,
                          _callback: Callable = None):
        """Removes Progress Bar from Notification

        Args:
            message (str, optional): notification message. Defaults to 'last message'.
            show_on_update (bool, optional): To show notification briefly when progressbar removed. Defaults to True.
            title (str, optional): notification title. Defaults to 'last title'.
            cooldown (float, optional): Little Time to Wait before change actually reflects, to avoid android Ignoring Change, Defaults to 0.5secs
            _callback (object): function for when change actual happens

        In-Built Delay of 0.5 sec According to Android Docs Don't Update Progressbar too Frequently
        """

        # To Cancel any queued timer from `updateProgressBar` method and to avoid race effect incase it somehow gets called while in this method
        # Avoiding Running `updateProgressBar.delayed_update` at all
        # so didn't just set `self.__progress_bar_title` and `self.progress_current_value` to 0
        if self.__update_timer:
            self.__update_timer.cancel()
            self.__update_timer = None

        def delayed_update():
            if self.logs:
                msg = message or self.message
                title_ = title or self.title
                logger.info(f'removed progress bar with message: {msg} and title: {title_}.')

            if _callback:
                try:
                    _callback()
                except Exception as passed_in_callback_error:
                    logger.exception(passed_in_callback_error)
                    traceback.print_exc()

            if not on_android_platform():
                return

            if message:
                self.updateMessage(message)
            if title:
                self.updateTitle(title)
            self.builder.setOnlyAlertOnce(not show_on_update)
            self.builder.setProgress(0, 0, False)
            self.refresh()

        # In case `self.updateProgressBar delayed_update` is called right before this method, so android doesn't bounce update
        threading.Timer(cooldown, delayed_update).start()

    def setPriority(self, importance: Importance):
        """
        For devices less than android 8
        :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
        :return:
        """
        self.__using_set_priority_method = True
        if on_android_platform():
            android_importance_value = get_android_importance(importance)
            if not isinstance(android_importance_value, str):  # Can be an empty str if importance='none'
                self.builder.setPriority(android_importance_value)

    def send(self, silent: bool = False, persistent=False, close_on_click=True):
        """Sends notification

        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """
        self.silent = silent or self.silent
        if on_android_platform():
            self.start_building(persistent, close_on_click)
            dispatch_notification(notification_id=self.__id, builder=self.builder, passed_check=self.passed_check)

        self.__send_logs()

    def send_(self, silent: bool = False, persistent=False, close_on_click=True):
        """Sends notification without checking for additional notification permission

        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """
        self.passed_check = True
        self.send(silent, persistent, close_on_click)

    def setVibrate(self, pattern=None):
        """
        Set the vibration pattern for the notification (Android API < 26 only).

        On devices running Android versions prior to 8.0 (Oreo),
        vibration is configured directly on the notification builder.
        This method is ignored on API 26+ where NotificationChannel
        controls vibration behavior.

        Args:
            pattern (list[int] | None, optional):
                A vibration pattern in milliseconds formatted as:
                [delay, vibrate, pause, vibrate, ...].

                If not provided, the default pattern
                [0, 500] is used.

        Example:
            >>> self.setVibrate()
            >>> self.setVibrate([0, 500, 200, 500])
        """
        if on_android_platform() and BuildVersion < 26:
            pattern = pattern or [0, 500]
            self.builder.setVibrate(pattern)
        if not on_android_platform() or BuildVersion < 26:
            logger.info(f"Vibration pattern set to {pattern}")

    @staticmethod
    def fVibrate():
        """
        Some Android devices have a setting to only vibrate on silent, If Vibration is a MUST called this.
        :return:
        """
        force_vibrate()

    def __send_logs(self):
        if not self.logs:
            return
        string_to_display = ''
        print("\n Sent Notification!!!")
        displayed_args = [
            "title", "message",
            "style", "body", "large_icon_path", "big_picture_path",
            "progress_max_value",
            'name', "channel_name",
        ]
        is_progress_not_default = isinstance(self.progress_current_value, int) or (
                isinstance(self.progress_current_value, float) and self.progress_current_value != 0.0)
        for name, value in vars(self).items():
            if value and name in displayed_args:
                if name == "progress_max_value":
                    if is_progress_not_default:
                        string_to_display += f'\n progress_current_value: {self.progress_current_value}, {name}: {value}'
                elif name == "channel_name":
                    string_to_display += f'\n {name}: {value}, channel_id: {self.channel_id}'
                else:
                    string_to_display += f'\n {name}: {value}'

        string_to_display += "\n (Won't Print Logs When Complied,except if selected `Notification.logs=True`)"
        print(string_to_display)

    def addButton(self, text: str, on_release=None, receiver_name=None, action=None):
        """For adding action buttons

        :param text: Text For Button
        :param on_release: function to be called when button is clicked
        :param receiver_name:  receiver class name
        :param action: action for receiver
        """

        self.__no_of_buttons += 1
        if not on_android_platform():
            return

        action = action or f"{text}_{self.id}"  # tagging with id so it can found notification handle object

        # for bundle data
        title = self.title or 'Title Placeholder'
        btn_no = self.__no_of_buttons

        pending_action_intent = None
        receiver_class_name = None
        if receiver_name:
            try:
                receiver_class_name = f"{get_package_name()}.{receiver_name}"
                receiverClass = autoclass(receiver_class_name)
                pending_action_intent = get_broadcast_pending_intent_for_btn(receiver_class=receiverClass,
                                                                             action=action, title=title, btn_no=btn_no, data_object=self.data_object)
            except Exception as error_getting_broadcast_receiver:
                logger.exception(error_getting_broadcast_receiver)

        if receiver_name and not pending_action_intent:
            logger.warning(f"Didn't find: {receiver_class_name}, Warning defaulting to getActivity for Button")

        if not receiver_name and not pending_action_intent:
            pending_action_intent = get_default_pending_intent_for_btn(action=action, title=title, btn_no=btn_no, data_object=self.data_object)

        context = get_python_activity_context()
        action_text = cast('java.lang.CharSequence', String(text))
        self.builder.addAction(int(context.getApplicationInfo().icon), action_text, pending_action_intent)
        self.builder.setContentIntent(pending_action_intent)  # Set content intent for notification tap

        self.btns_box[action] = on_release
        # action_intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)

        logger.info(f'Added Button: {text}. \nButton action: {action}.')

    def removeButtons(self):
        """Removes all notification buttons
        """
        remove_buttons(self.builder)
        self.refresh()

    @run_on_ui_thread
    def addNotificationStyle(self, style: str, already_sent=False):
        """Adds Style to Notification

        NOTE: This method has Deprecated Use - (setLargeIcon, setBigPicture, setBigText and setLines) Instead

        --------
        Args:
            style (str): required style
            already_sent (bool,False): If notification was already sent
        """

        if not on_android_platform():
            # TODO for logs when not on android and style related to imgs extract app path from buildozer.spec and log
            return False

        if self.body:
            self.setBigText(self.body)

        elif self.lines_txt:
            lines = self.lines_txt.split("\n")
            self.setLines(lines)

        elif self.big_picture_path or self.large_icon_path:
            if self.big_picture_path:
                self.setBigPicture(self.big_picture_path)
            if self.large_icon_path:
                self.setLargeIcon(self.large_icon_path)

        elif self.progress_max_value or self.progress_current_value:
            self.builder.setProgress(self.progress_max_value, self.progress_current_value or 0.1, False)

        if already_sent:
            self.refresh()

        return True

    def setLines(self, lines: list):
        """Pass in a list of strings to be used for lines"""
        set_lines(builder=self.builder, lines=lines)

    def setSound(self, res_sound_name):
        """
        Sets sound for devices less than android 8 (For 8+ use createChannel)
        :param res_sound_name: audio file name (without .wav or .mp3) locate in res/raw/
        """

        return set_sound(self.builder, res_sound_name)

    def start_building(self, persistent=False, close_on_click=True, silent: bool = False):
        # Main use is for foreground service, bypassing .notify in .send method to let service.startForeground(...) send it
        self.silent = silent or self.silent
        if not on_android_platform():
            return NotificationCompatBuilder  # this is just a facade
        self.__create_basic_notification(persistent, close_on_click)
        if self.style not in ['simple', '']:
            self.addNotificationStyle(self.style)
        self.__applyNewLinesIfAny()

        return self.builder

    def __applyNewLinesIfAny(self):
        if self.__lines:
            set_lines(builder=self.builder, lines=self.__lines)
            self.__lines = []  # for refresh method to known when new lines added

    def __create_basic_notification(self, persistent, close_on_click):
        if not self.channelExists(self.channel_id):
            self.createChannel(id=self.channel_id, name=self.channel_name)
        elif not self.__using_set_priority_method:
            self.setPriority('medium' if self.silent else 'urgent')

        # Build the notification
        if self.isUsingCustom():
            self.__apply_basic_custom_style()
        else:
            self.builder.setContentTitle(str(self.title))
            self.builder.setContentText(str(self.message))
        self.__insert_app_icon()
        self.builder.setDefaults(NotificationCompat.DEFAULT_ALL)
        self.builder.setOnlyAlertOnce(True)
        self.builder.setOngoing(persistent)
        self.builder.setAutoCancel(close_on_click)

        try:
            action_name = str(self.name or self.__id)
            if not self.__called_set_data:
                add_intent_to_open_app(builder=self.builder, action_name=action_name, notification_title=str(self.title),
                                   notification_id=self.__id, data_object=self.data_object)
            self.main_functions[action_name] = self.callback
        except Exception as failed_to_add_intent_to_open_app:
            logger.exception(failed_to_add_intent_to_open_app)

        self.__generic_parameters_filled = True

    def __insert_app_icon(self, path=''):
        if BuildVersion.SDK_INT >= 23 and (path or self.app_icon not in ['', 'Defaults to package app icon']):
            # Bitmap Insert as Icon Not available below Android 6
            logger.info('Getting custom icon...')
            self.__set_icon_from_bitmap(path or self.app_icon)
        else:
            find_and_set_default_icon(self.builder)
            self.__has_small_icon = True

    def __build_img(self, user_img, img_style):
        if user_img.startswith('https://'):
            def apply_image_with_bitmap_from_url(bitmap_from_url):
                self.__apply_notification_image(bitmap_from_url, img_style)

            thread = threading.Thread(
                target=get_bitmap_from_url,
                args=[user_img, apply_image_with_bitmap_from_url]
            )
            thread.start()
        else:
            image_absolute_path = get_img_absolute_path(user_img)
            bitmap = get_bitmap_from_path(image_absolute_path)
            if bitmap:
                self.__apply_notification_image(bitmap, img_style)

    def __set_icon_from_bitmap(self, img_path):
        """Path can be a link or relative path"""

        if img_path.startswith('https://'):
            def set_icon_with_bitmap_from_url(bitmap_from_url):
                if bitmap_from_url:
                    set_small_icon_with_bitmap(bitmap=bitmap_from_url, builder=self.builder)
                else:
                    logger.warning('No bitmap from url for small icon, Using Default Icon as fallback...')
                    set_default_small_icon(self.builder)
                self.__has_small_icon = True

            threading.Thread(
                target=get_bitmap_from_url,
                args=[img_path, set_icon_with_bitmap_from_url]
            ).start()
        else:
            image_absolute_path = get_img_absolute_path(img_path)
            bitmap_from_path = get_bitmap_from_path(image_absolute_path)
            if bitmap_from_path:
                set_small_icon_with_bitmap(bitmap=bitmap_from_path, builder=self.builder)
                self.__has_small_icon = True
            else:
                logger.warning(
                    f'Failed getting bitmap for custom icon, Using Default...\n Tried absolute path: {image_absolute_path}')
                set_default_small_icon(self.builder)
            self.__has_small_icon = True
        # self.__has_small_icon = True # Can not set here because of threading when getting bitmap for url

    @run_on_ui_thread
    def __apply_notification_image(self, bitmap, img_style):
        try:
            if img_style == NotificationStyles.BIG_PICTURE and bitmap:
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
                self.builder.setStyle(big_picture_style)
            elif img_style == NotificationStyles.LARGE_ICON and bitmap:
                self.builder.setLargeIcon(bitmap)
            # LargeIcon requires smallIcon to be already set
            # 'setLarge, setBigPic' tries to dispatch before filling required values `self.__create_basic_notification`
            self.refresh()
            logger.info('Done adding image to notification.')
        except Exception as notification_image_error:
            img = self.large_icon_path if img_style == NotificationStyles.LARGE_ICON else self.big_picture_path
            logger.exception(
                f'Failed adding Image of style: {img_style} || From path: {img}, Exception: {notification_image_error}')

    def __format_channel(self, channel_name: str = 'Default Channel', channel_id: str = 'default_channel'):
        """
        Formats and sets self.channel_name and self.channel_id to a formatted version
        :param channel_name:
        :param channel_id:
        :return:
        """
        # Shorten channel name # android docs as at most 40 chars
        if channel_name != 'Default Channel':
            cleaned_name = channel_name.strip()
            self.channel_name = cleaned_name[:40] if cleaned_name else 'Default Channel'

            # If no channel_id then generating channel_id from passed in channel_name
            if channel_id == 'default_channel':
                generated_id = generate_channel_id(channel_name)
                self.channel_id = generated_id

    def __get_unique_id(self):
        if from_service_file():
            return int(time.time() * 1000) % 2_147_483_647

        notification_id = self.notification_ids[-1] + 1
        self.notification_ids.append(notification_id)
        return notification_id

    @classmethod
    def getChannels(cls) -> list[Any] | Any:
        """Return all existing channels"""
        return get_channels()

    def __apply_basic_custom_style(self):

        if not self.__generic_parameters_filled:
            current_time_mills = int(time.time() * 1000)
            self.builder.setWhen(current_time_mills)
            self.builder.setShowWhen(True)

        set_custom_colors(builder=self.builder, title=self.title, message=self.message, title_color=self.title_color,
                          message_color=self.message_color)

    def isUsingCustom(self):
        self.__using_custom = self.title_color or self.message_color
        return bool(self.__using_custom)
    # TODO method to create channel groups


class NotificationHandler:
    """For Notification Operations """
    __name = None
    __bound = False
    __requesting_permission = False
    android_activity = None
    data_object = {} # For getting added data on notification

    if on_android_platform() and not on_flet_app():
        # noinspection PyPackageRequirements
        from android import activity  # type: ignore
        android_activity = activity

    @classmethod
    def get_name(cls, on_start=False):
        """Returns name or id str for Clicked Notification."""
        if not on_android_platform():
            return "Not on Android"

        saved_intent = cls.__name
        cls.__name = None  # so value won't be set when opening app not from notification
        # drint('saved_intent ',saved_intent)
        # if not saved_intent or (isinstance(saved_intent, str) and saved_intent.startswith("android.intent")):
        # Below action is always None
        # __PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
        # __mActivity = __PythonActivity.mActivity
        # __context = cast('android.content.Context', __mActivity)
        # __Intent = autoclass('android.content.Intent')
        # __intent = __Intent(__context, __PythonActivity)
        # action = __intent.getAction()
        # drint('Start up Intent ----', action)
        # drint('start Up Title --->',__intent.getStringExtra("title"))

        if on_start:    # Using `on_start` arg because no way to know if opening from `Recents` only `Home Screen`
        # if not saved_intent and cls.opened_from_notification:
            # When Launching app(on_start) `cls.opened_from_notification` will be true so `get_name_used_to_open_app` can check for `extras`
            # When Opening App from main screen `__notification_handler` receives real Intent action value if `android.intent.action.MAIN` it sets to cls.opened_from_notification false
            # TODO Launching From Recents
            saved_intent = get_name_used_to_open_app()
            cls.data_object = get_data_object_added_to_intent()

        logger.debug(f"name used to open app: {saved_intent}")

        return saved_intent

    @classmethod
    def __notification_handler(cls, intent):
        """Calls Function Attached to notification on click.
            Don't Call this function manual, it's Already Attach to Notification.

        Sets self.__name #action of Notification that was clicked from Notification.name or Notification.id
        """
        if not on_android_platform():
            return None

        buttons_object = Notification.btns_box
        notify_functions = Notification.main_functions

        try:
            action = intent.getAction()
            name = intent.getStringExtra("notification_name") # btns also have this.
            cls.__name = name

            logger.debug(f"Intent Data - notification_name: {name}, Action: {action}")
            if not name:  # Not Open From Notification
                logger.debug(f"Intent not from notification")
                cls.__name = None
                return None
            cls.data_object = get_data_object_added_to_intent(intent)

            try:
                if name in notify_functions:
                    notification_callback = notify_functions[name]
                    if notification_callback:
                        notification_callback()
                    else:
                        logger.warning(f"Clicked Notification Callback Function Not Found.")
                elif name in buttons_object:
                    button_function = buttons_object[name]
                    if button_function:
                        button_function()
                    else:
                        logger.warning(f"Clicked Notification button function not found.")
            except Exception as notification_handler_function_error:
                logger.exception(f"Error Handling Notification Function: {notification_handler_function_error}")
        except Exception as extracting_notification_props_error:
            logger.exception(f'Error getting Notify Name For Handler: {extracting_notification_props_error}')

    @classmethod
    def bindNotifyListener(cls):
        """This Creates a Listener for All Notification Clicks and Functions"""
        if not on_android_platform():
            return None

        if on_flet_app():
            logger.warning("On Flet App, Didn't Binding Notification Listener")
            return None

        if from_service_file():
            # In Service File error 'NoneType' object has no attribute 'registerNewIntentListener'
            logger.warning("In service file, Didn't Binding Notification Listener")
            return None

        # TODO use BroadcastReceiver For Whole notification Click Not Just Buttons
        if cls.__bound:
            logger.warning("binding done already.")
            return True
        try:
            cls.android_activity.bind(on_new_intent=cls.__notification_handler)
            cls.__bound = True
            return True
        except Exception as binding_listener_error:
            logger.exception(f'Failed to bind notifications listener: {binding_listener_error}')
            return False

    @classmethod
    def unbindNotifyListener(cls):
        """Removes Listener for Notifications Click"""
        if not on_android_platform() or on_flet_app() or from_service_file():
            return False

        try:
            cls.android_activity.unbind(on_new_intent=cls.__notification_handler)
            return True
        except Exception as unbinding_listener_error:
            logger.exception(f"Failed to unbind notifications listener: {unbinding_listener_error}")
            return False

    @staticmethod
    def has_permission():
        """
        Checks if device has permission to send notifications
        returns True if device has permission
        """
        return has_notification_permission()

    @classmethod
    @run_on_ui_thread
    def asks_permission(cls, callback=None):
        """
        Ask for permission to send notifications if needed.
        Passes True to callback if access granted
        """

        if cls.__requesting_permission:
            logger.warning("still requesting permission ")
            return None

        def requesting_state(state):
            cls.__requesting_permission = state

        ask_notification_permission(callback=callback, set_requesting_state=requesting_state)
        return None


if on_android_platform():
    try:
        NotificationHandler.bindNotifyListener()
    except Exception as notification_listener_bind_error:
        logger.exception(notification_listener_bind_error)
