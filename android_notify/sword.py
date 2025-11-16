"""This Module Contain Class for creating Notification With Java"""
import os, time, threading, traceback
from typing import Any, Callable
from .config import cast, autoclass

from .an_types import Importance
from .an_utils import can_accept_arguments, get_python_activity_context, \
    get_android_importance, generate_channel_id, get_img_from_path, setLayoutText, \
    get_bitmap_from_url, add_data_to_intent, get_sound_uri, get_flet_fallback_icon_path, get_bitmap_from_path,get_package_path

from .config import from_service_file, get_python_activity,get_notification_manager,ON_ANDROID,on_flet_app
from .config import (Bundle, String, BuildVersion,
                     Intent,PendingIntent,
                     app_storage_path,
                     NotificationChannel,RemoteViews,
                     run_on_ui_thread,
                     )
from .config import (AndroidNotification, NotificationCompatBuilder,
                     NotificationCompatBigTextStyle,NotificationCompatBigPictureStyle,
                     NotificationCompatInboxStyle,
                     Color
                     )
from .styles import NotificationStyles
from .base import BaseNotification
DEV=0
PythonActivity = get_python_activity()
context = get_python_activity_context()

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
    button_ids=[0]
    btns_box={}
    main_functions={}
    passed_check=False

    # During Development (When running on PC)
    BaseNotification.logs = not ON_ANDROID
    def __init__(self,**kwargs): #@dataclass already does work
        super().__init__(**kwargs)

        self.__id = self.id or self.__get_unique_id() # Different use from self.name all notifications require `integers` id's not `strings`
        self.id = self.__id # To use same Notification in different instances

        # To Track progressbar last update (According to Android Docs Don't update bar to often, I also faced so issues when doing that)
        self.__update_timer = None
        self.__progress_bar_msg = ''
        self.__progress_bar_title = ''
        self.__cooldown = 0

        self.__built_parameter_filled=False
        self.__using_set_priority_method=False

        # For components
        self.__lines = []
        self.__has_small_icon = False #important notification can't send without
        self.__using_custom = self.message_color or self.title_color
        self.__format_channel(self.channel_name, self.channel_id)
        self.__builder = None # want to make builder always available for getter
        self.notification_manager = None
        
        if not ON_ANDROID:
            return

        if not from_service_file() and not NotificationHandler.has_permission():
            NotificationHandler.asks_permission()

        self.notification_manager = get_notification_manager()
        self.__builder = NotificationCompatBuilder(context, self.channel_id)

    def addLine(self,text:str):
        self.__lines.append(text)

    def cancel(self,_id=0):
        """
        Removes a Notification instance from tray
        :param _id: not required uses Notification instance id as default
        """
        if ON_ANDROID:
            self.notification_manager.cancel(_id or self.__id)
        if self.logs:
            print('Removed Notification.')

    @classmethod
    def cancelAll(cls):
        """
        Removes all app Notifications from tray
        """
        if ON_ANDROID:
            get_notification_manager().cancelAll()
        if cls.logs:
            print('Removed All Notifications.')

    @classmethod
    def channelExists(cls, channel_id):
        """
        Checks if a notification channel exists
        """
        if not ON_ANDROID:
            return False
        notification_manager= get_notification_manager()
        if BuildVersion.SDK_INT >= 26 and notification_manager.getNotificationChannel(channel_id):
            return True
        return False
        
    @classmethod
    def createChannel(cls, id, name:str, description='',importance:Importance='urgent',res_sound_name=None):
        """
        Creates a user visible toggle button for specific notifications, Required For Android 8.0+
        :param id: Used to send other notifications later through same channel.
        :param name: user-visible channel name.
        :param description: user-visible detail about channel (Not required defaults to empty str).
        :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
        :param res_sound_name: audio file file name (without .wav or .mp3) locate in res/raw/
        :return: boolean if channel created
        """

        if not ON_ANDROID:
            return False

        notification_manager= get_notification_manager()
        android_importance_value = get_android_importance(importance)
        sound_uri = get_sound_uri(res_sound_name)

        if not cls.channelExists(id):
            channel = NotificationChannel(id, name, android_importance_value)
            if description:
                channel.setDescription(description)
            if sound_uri:
                channel.setSound(sound_uri, None)
            notification_manager.createNotificationChannel(channel)
            return True
        return False

    @classmethod
    def deleteChannel(cls, channel_id):
        """Delete a Channel Matching channel_id"""
        if not ON_ANDROID:
            return None

        if cls.channelExists(channel_id):
            get_notification_manager().deleteNotificationChannel(channel_id)
            
    @classmethod
    def deleteAllChannel(cls):
        """Deletes all notification channel
        :returns amount deleted
        """

        amount = 0
        if not ON_ANDROID:
            return amount

        notification_manager = get_notification_manager()
        channels = cls.getChannels()
        for index in range(channels.size()):
            amount += 1
            channel = channels.get(index)
            channel_id = channel.getId()
            notification_manager.deleteNotificationChannel(channel_id)
        return amount
        
    @classmethod
    def doChannelsExist(cls,ids):
        """Uses list of IDs to check if channel exists
        returns list of channels that don't exist
        """
        if not ON_ANDROID:
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
        

    def refresh(self):
        """TO apply new components on notification"""
        if self.__built_parameter_filled:
            # Don't dispatch before filling required values `self.__create_basic_notification`
            # We generally shouldn't dispatch till user call .send()
            self.__applyNewLinesIfAny()
            self.__dispatch_notification()

    def setBigPicture(self,path):
        """
        set a Big Picture at the bottom
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if ON_ANDROID:
            self.__build_img(path, NotificationStyles.BIG_PICTURE)
        elif self.logs:
            # When on android there are other logs
            print('Done setting big picture')

    def setSmallIcon(self,path):
        """
        sets small icon to the top left
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if ON_ANDROID:
            self.app_icon=path
            self.__insert_app_icon(path)
        if self.logs:
            # When on android there are other logs
            print('Done setting small icon')

    def setLargeIcon(self,path):
        """
        sets Large icon to the right
        :param path: can be `Relative Path` or `URL`
        :return:
        """
        if ON_ANDROID:
            self.__build_img(path, NotificationStyles.LARGE_ICON)
        elif self.logs:
            #When on android there are other logs
            print('Done setting large icon')

    def setBigText(self,body):
        """Sets a big text for when drop down button is pressed

        :param body: The big text that will be displayed
        """
        if ON_ANDROID:
            big_text_style = NotificationCompatBigTextStyle()
            big_text_style.bigText(str(body))
            self.__builder.setStyle(big_text_style)
        elif self.logs:
            # When on android, there are other logs
            print('Done setting big text')

    def setSubText(self, text):
        """
        In android version 7+ text displays in header next to title,
        While in lesser versions displays in third line of text, where progress-bar occupies
        :param text: str for subtext

        """
        self.sub_text = str(text)
        if self.logs:
            print(f'new notification sub text: {self.sub_text}')
        if ON_ANDROID:
            self.__builder.setSubText(self.sub_text)

    def setColor(self,color:str):
        """
        Sets Notification accent color, visible change in SmallIcon color
        :param color:  str - red,pink,... (to be safe use hex code)
        """
        if self.logs:
            print(f'new notification icon color: {color}')
        if ON_ANDROID:
            self.__builder.setColor(Color.parseColor(color))

    def showInfiniteProgressBar(self):
        """Displays an (Infinite) progress Bar in Notification, that continues loading indefinitely.
        Can be Removed By `removeProgressBar` Method
        """
        if self.logs:
            print('Showing infinite progressbar')
        if ON_ANDROID:
            self.__builder.setProgress(0,0, True)
            self.refresh()

    def updateTitle(self,new_title):
        """Changes Old Title

        Args:
            new_title (str): New Notification Title
        """
        self.title=str(new_title)
        if self.logs:
            print(f'new notification title: {self.title}')
        if ON_ANDROID:
            if self.isUsingCustom():
                self.__apply_basic_custom_style()
            else:
                self.__builder.setContentTitle(String(self.title))
            self.refresh()

    def updateMessage(self,new_message):
        """Changes Old Message

        Args:
            new_message (str): New Notification Message
        """
        self.message=str(new_message)
        if self.logs:
            print(f'new notification message: {self.message}')
        if ON_ANDROID:
            if self.isUsingCustom():
                self.__apply_basic_custom_style()
            else:
                self.__builder.setContentText(String(self.message))
            self.refresh()

    def updateProgressBar(self, current_value:int, message:str='', title:str='', cooldown=0.5, _callback:Callable=None):
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
            # Make Logs too Dirty
            # if self.logs:
                # remaining = self.__cooldown - (time.time() - self.__timer_start_time)
                # print(f'Progressbar update too soon, waiting for cooldown ({max(0, remaining):.2f}s)')
            return

        def delayed_update():
            if self.__update_timer is None: # Ensure we are not executing an old timer
                if self.logs:
                    print('ProgressBar update skipped: bar has been removed.')
                return
            if self.logs:
                print(f'Progress Bar Update value: {self.progress_current_value}')

            if _callback:
                try:
                    _callback()
                except Exception as passed_in_callback_error:
                    print('Exception passed_in_callback_error:', passed_in_callback_error)
                    traceback.print_exc()

            if not ON_ANDROID:
                self.__update_timer = None
                return

            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)

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

    def removeProgressBar(self, message='', show_on_update=True, title:str='', cooldown=0.5, _callback:Callable=None):
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
            # Make Logs too Dirty
            # if self.logs:
            #     print('cancelled progressbar stream update because about to remove',self.progress_current_value)
            self.__update_timer.cancel()
            self.__update_timer = None

        def delayed_update():
            if self.logs:
                msg = message or self.message
                title_=title or self.title
                print(f'removed progress bar with message: {msg} and title: {title_}')

            if _callback:
                try:
                    _callback()
                except Exception as passed_in_callback_error:
                    print('Exception passed_in_callback_error:', passed_in_callback_error)
                    traceback.print_exc()

            if not ON_ANDROID:
                return

            if message:
                self.updateMessage(message)
            if title:
                self.updateTitle(title)
            self.__builder.setOnlyAlertOnce(not show_on_update)
            self.__builder.setProgress(0, 0, False)
            self.refresh()

        # Incase `self.updateProgressBar delayed_update` is called right before this method, so android doesn't bounce update
        threading.Timer(cooldown, delayed_update).start()

    def setPriority(self,importance:Importance):
        """
        For devices less than android 8
        :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
        :return:
        """
        self.__using_set_priority_method=True
        if ON_ANDROID:
            android_importance_value = get_android_importance(importance)
            if not isinstance(android_importance_value, str):  # Can be an empty str if importance='none'
                self.__builder.setPriority(android_importance_value)

    def send(self,silent:bool=False,persistent=False,close_on_click=True):
        """Sends notification

        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """
        self.silent = silent or self.silent
        if ON_ANDROID:
            self.__start_notification_build(persistent, close_on_click)
            self.__dispatch_notification()

        self.__send_logs()
    
    def send_(self,silent:bool=False,persistent=False,close_on_click=True):
        """Sends notification without checking for additional notification permission

        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """        
        self.passed_check = True
        self.send(silent,persistent,close_on_click)

    def __send_logs(self):
        if not self.logs:
            return
        string_to_display=''
        print("\n Sent Notification!!!")
        displayed_args = [
            "title", "message",
            "style", "body", "large_icon_path", "big_picture_path",
            "progress_max_value",
            'name', "channel_name",
            ]
        is_progress_not_default = isinstance(self.progress_current_value, int) or (isinstance(self.progress_current_value, float) and self.progress_current_value != 0.0)
        for name,value in vars(self).items():
            if value and name in displayed_args:
                if name == "progress_max_value":
                    if is_progress_not_default:
                        string_to_display += f'\n progress_current_value: {self.progress_current_value}, {name}: {value}'
                elif name == "channel_name":
                    string_to_display += f'\n {name}: {value}, channel_id: {self.channel_id}'
                else:
                    string_to_display += f'\n {name}: {value}'

        string_to_display +="\n (Won't Print Logs When Complied,except if selected `Notification.logs=True`)"
        print(string_to_display)
        
    def builder(self):
        return self.__builder
        
    def addButton(self, text:str,on_release):
        """For adding action buttons

        Args:
            text (str): Text For Button
            on_release: function to be called when button is clicked
        """
        if self.logs:
            print('Added Button: ', text)

        if not ON_ANDROID:
            return

        btn_id= self.__get_id_for_button()
        action = f"BTN_ACTION_{btn_id}"

        action_intent = Intent(context, PythonActivity)
        action_intent.setAction(action)
        action_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        bundle = Bundle()
        bundle.putString("title", self.title or 'Title Placeholder')
        bundle.putInt("key_int", 123)
        action_intent.putExtras(bundle)
        action_intent.putExtra("button_id", btn_id)

        self.btns_box[action] = on_release
        # action_intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP)

        if self.logs:
            print('Button id: ',btn_id)
        pending_action_intent = PendingIntent.getActivity(
            context,
            0,
            action_intent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        )
        # Convert text to CharSequence
        action_text = cast('java.lang.CharSequence', String(text))



        # Add action with proper types
        self.__builder.addAction(
            int(context.getApplicationInfo().icon),  # Cast icon to int
            action_text,                             # CharSequence text
            pending_action_intent                    # PendingIntent
        )
        # Set content intent for notification tap
        self.__builder.setContentIntent(pending_action_intent)

    def removeButtons(self):
        """Removes all notification buttons
        """
        if ON_ANDROID:
            self.__builder.mActions.clear()
            self.refresh()
        if self.logs:
            print('Removed Notification Buttons')

    @run_on_ui_thread
    def addNotificationStyle(self,style:str,already_sent=False):
        """Adds Style to Notification
            Version 1.51.2+ Exposes method to Users (Note): Always try to Call On UI Thread

        Args:
            style (str): required style
            already_sent (bool,False): If notification was already sent
        """

        if not ON_ANDROID:
            # TODO for logs when not on android and style related to imgs extract app path from buildozer.spec and print
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
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value or 0.1, False)

        if already_sent:
            self.refresh()

        return True

    def setLines(self, lines: list):
        """Pass in a list of strings to be used for lines"""
        if not lines:
            return
        if ON_ANDROID:
            inbox_style = NotificationCompatInboxStyle()
            for line in lines:
                inbox_style.addLine(str(line))
            self.__builder.setStyle(inbox_style)
            print('Set Lines: ', lines)

        if self.logs:
            print('Added Lines: ', lines)

    def setSound(self,res_sound_name):
        """
        Sets sound for devices less than android 8 (For 8+ use createChannel)
        :param res_sound_name: audio file file name (without .wav or .mp3) locate in res/raw/
        """
        
        if not ON_ANDROID:
            return
        
        if res_sound_name and BuildVersion.SDK_INT < 26:
            try:
                self.__builder.setSound(get_sound_uri(res_sound_name))
            except Exception as failed_adding_sound_device_below_android8:
                print("failed_adding_sound_device_below_android8:",failed_adding_sound_device_below_android8)
                traceback.print_exc()
                
    def __dispatch_notification(self):
        # self.passed_check is for self.send_() some devices don't return true when checking for permission when it's actually True in settingsAdd commentMore actions
        # And so users can do Notification.passed_check = True at top of their file and use regular .send()
        
        if from_service_file(): # android has_permission has some internal error when checking from service
            try:
                self.notification_manager.notify(self.__id, self.__builder.build())
            except Exception as sending_notification_from_service_error:
                print('error sending notification from service:',sending_notification_from_service_error)
        elif on_flet_app() or self.passed_check or NotificationHandler.has_permission():
            try:
                self.notification_manager.notify(self.__id, self.__builder.build())
            except Exception as notify_error:
                print('Exception:', notify_error)
                print('Failed to send traceback:', traceback.format_exc())
        else:
            print('Permission not granted to send notifications')
            # TODO find way to open app notification settings and not ask only through POP-UP
            # Not asking for permission too frequently, This makes dialog popup to stop showing
            # NotificationHandler.asks_permission()

    def __start_notification_build(self, persistent, close_on_click):
        self.__create_basic_notification(persistent, close_on_click)
        if self.style not in ['simple','']:
            self.addNotificationStyle(self.style)
        self.__applyNewLinesIfAny()

    def __applyNewLinesIfAny(self):
        if self.__lines:
            self.setLines(self.__lines)
            self.__lines=[] # for refresh method to known when new lines added

    def __create_basic_notification(self, persistent, close_on_click):
        if not self.channelExists(self.channel_id):
            self.createChannel(self.channel_id, self.channel_name)
        elif not self.__using_set_priority_method:
            self.setPriority('medium' if self.silent else 'urgent')

        # Build the notification
        if self.isUsingCustom():
            self.__apply_basic_custom_style()
        else:
            self.__builder.setContentTitle(str(self.title))
            self.__builder.setContentText(str(self.message))
        self.__insert_app_icon()
        self.__builder.setDefaults(AndroidNotification.DEFAULT_ALL)
        self.__builder.setOnlyAlertOnce(True)
        self.__builder.setOngoing(persistent)
        self.__builder.setAutoCancel(close_on_click)

        if not from_service_file():
            try:
                self.__add_intent_to_open_app()
            except Exception as failed_to_add_intent_to_open_app:
                #if self.logs:
                #TODO remove this check and print error logs always
                print('failed_to_add_intent_to_open_app Error: ',failed_to_add_intent_to_open_app)
                traceback.print_exc()

        self.__built_parameter_filled = True

    def __insert_app_icon(self,path=''):
        if BuildVersion.SDK_INT >= 23 and (path or self.app_icon not in ['','Defaults to package app icon']):
            # Bitmap Insert as Icon Not available below Android 6
            if self.logs:
                print('getting custom icon...')
            self.__set_icon_from_bitmap(path or self.app_icon)
        else:
            if self.logs:
                print('using default icon...')
            if on_flet_app():
                try:
                    fallback_icon_path = get_flet_fallback_icon_path()
                    bitmap = get_bitmap_from_path(fallback_icon_path)
                    if bitmap:
                        icon = IconCompat.createWithBitmap(bitmap)
                        self.__builder.setSmallIcon(icon)
                        self.__has_small_icon = True
                        return
                except Exception as error_using_fallback_appicon:
                    print("error_using_fallback_appicon :",error_using_fallback_appicon) 
                    traceback.print_exc()
            self.__has_small_icon = True
            self.__builder.setSmallIcon(context.getApplicationInfo().icon)

    def __build_img(self, user_img, img_style):
        if user_img.startswith('http://') or user_img.startswith('https://'):
            def callback(bitmap_):
                self.__apply_notification_image(bitmap_,img_style)
            thread = threading.Thread(
                                        target=get_bitmap_from_url,
                                        args=[user_img,callback,self.logs]
                                    )
            thread.start()
        else:
            bitmap = get_img_from_path(user_img)
            if bitmap:
                self.__apply_notification_image(bitmap, img_style)

    def __set_icon_from_bitmap(self, img_path):
        """Path can be a link or relative path"""
        try:
            Icon = autoclass('android.graphics.drawable.Icon')
        except Exception as autoclass_icon_error:
            print("Couldn't find class to set custom icon:",autoclass_icon_error)
            self.__builder.setSmallIcon(context.getApplicationInfo().icon)
            self.__has_small_icon = True
            return
        
        
        if img_path.startswith('http://') or img_path.startswith('https://'):
            def callback(bitmap_):
                if bitmap_:
                    icon_ = Icon.createWithBitmap(bitmap_)
                    self.__builder.setSmallIcon(icon_)
                    self.__has_small_icon = True
                else:
                    if self.logs:
                        print('Using Default Icon as fallback......')
                    self.__has_small_icon = True
                    self.__builder.setSmallIcon(context.getApplicationInfo().icon)
            threading.Thread(
                target=get_bitmap_from_url,
                args=[img_path,callback,self.logs]
                ).start()
        else:
            bitmap = get_img_from_path(img_path)
            if bitmap:
                icon = Icon.createWithBitmap(bitmap)
                self.__builder.setSmallIcon(icon)
            else:
                if self.logs:
                    app_folder=os.path.join(app_storage_path(),'app')
                    img_absolute_path = os.path.join(app_folder, img_path)
                    print(f'Failed getting img for custom notification icon defaulting to app icon\n absolute path {img_absolute_path}')
                self.__builder.setSmallIcon(context.getApplicationInfo().icon)
            self.__has_small_icon = True

    @run_on_ui_thread
    def __apply_notification_image(self, bitmap, img_style):
        try:
            if img_style == NotificationStyles.BIG_PICTURE and bitmap:
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap)
                self.__builder.setStyle(big_picture_style)
            elif img_style == NotificationStyles.LARGE_ICON and bitmap:
                self.__builder.setLargeIcon(bitmap)
            # LargeIcon requires smallIcon to be already set
            # 'setLarge, setBigPic' tries to dispatch before filling required values `self.__create_basic_notification`
            self.refresh()
            if self.logs:
                print('Done adding image to notification-------')
        except Exception as notification_image_error:
            img = self.large_icon_path if img_style == NotificationStyles.LARGE_ICON else self.big_picture_path
            print(f'Failed adding Image of style: {img_style} || From path: {img}, Exception {notification_image_error}')
            print('could not get Img traceback: ',traceback.format_exc())

    def __add_intent_to_open_app(self):
        intent = Intent(context, PythonActivity)
        action = str(self.name or self.__id)
        intent.setAction(action)
        add_data_to_intent(intent,self.title)
        self.main_functions[action]=self.callback
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)

        pending_intent = PendingIntent.getActivity(
                            context, 0,
                            intent, PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT
                        )
        self.__builder.setContentIntent(pending_intent)

    def __get_id_for_button(self):
        btn_id = self.button_ids[-1] + 1
        self.button_ids.append(btn_id)
        return btn_id

    def __format_channel(self, channel_name:str='Default Channel',channel_id:str='default_channel'):
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
            max_int = 2_147_483_647
            return int(time.time() * 1000) % max_int

        notification_id = self.notification_ids[-1] + 1
        self.notification_ids.append(notification_id)
        return notification_id

    @classmethod
    def getChannels(cls) -> list[Any] | Any:
        """Return all existing channels"""
        if not ON_ANDROID:
            return []

        return get_notification_manager().getNotificationChannels()

    def __apply_basic_custom_style(self):
        NotificationCompatDecoratedCustomViewStyle = autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')

        # Load layout
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

        if DEV:
            print('small: ',small_layout_id, 'notificationLayout: ',notificationLayout)

        # Notification Content
        setLayoutText(
                layout=notificationLayout, id=title_id,
                text=self.title, color=self.title_color
        )
        setLayoutText(
                layout=notificationLayoutExpanded, id=title_id,
                text=self.title, color=self.title_color
        )
        setLayoutText(
                layout=notificationLayoutExpanded, id=message_id,
                text=self.message, color=self.message_color
        )
        # self.__setLayoutText(
        #     layout=notificationLayout, id=message_id,
        #     text=self.message, color=self.message_color
        # )
        if not self.__built_parameter_filled:
            current_time_mills = int(time.time() * 1000)
            self.__builder.setWhen(current_time_mills)
            self.__builder.setShowWhen(True)
        self.__builder.setStyle(NotificationCompatDecoratedCustomViewStyle())
        self.__builder.setCustomContentView(notificationLayout)
        self.__builder.setCustomBigContentView(notificationLayoutExpanded)

    def isUsingCustom(self):
        self.__using_custom = self.title_color or self.message_color
        return bool(self.__using_custom)
    def tell(self):
        from .core import send_notification
        t=str(get_package_path())
        send_notification(title="bool get_package_path()", message=str(os.path.isdir(t) ) )
        send_notification(title="get_package_path()", message=str(get_package_path()))
        send_notification(title="files", message="eyes",big_text=get_files_recursive(t))

    # TODO method to create channel groups


class NotificationHandler:
    """For Notification Operations """
    __name = None
    __bound = False
    __requesting_permission=False
    android_activity=None
    if ON_ANDROID and not on_flet_app():
        from android import activity
        android_activity = activity
    @classmethod
    def get_name(cls):
        """Returns name or id str for Clicked Notification."""
        if not cls.is_on_android():
            return "Not on Android"

        saved_intent = cls.__name
        cls.__name = None # so value won't be set when opening app not from notification
        # print('saved_intent ',saved_intent)
        # if not saved_intent or (isinstance(saved_intent, str) and saved_intent.startswith("android.intent")):
            # All other notifications are not None after First notification opens app
            # NOTE these notifications are also from Last time app was opened and they Still Give Value after first one opens App
            # TODO Find a way to get intent when App if Swiped From recents
            # Below action is always None
            # __PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
            # __mactivity = __PythonActivity.mActivity
            # __context = cast('android.content.Context', __mactivity)
            # __Intent = autoclass('android.content.Intent')
            # __intent = __Intent(__context, __PythonActivity)
            # action = __intent.getAction()
            # print('Start up Intent ----', action)
            # print('start Up Title --->',__intent.getStringExtra("title"))

        return saved_intent

    @classmethod
    def __notification_handler(cls, intent):
        """Calls Function Attached to notification on click.
            Don't Call this function manual, it's Already Attach to Notification.

        Sets self.__name #action of Notification that was clicked from Notification.name or Notification.id
        """
        if not cls.is_on_android():
            return "Not on Android"
        buttons_object=Notification.btns_box
        notifty_functions=Notification.main_functions
        if DEV:
            print("notifty_functions ",notifty_functions)
            print("buttons_object", buttons_object)
        try:
            action = intent.getAction()
            cls.__name = action

            # print("The Action --> ",action)
            if action == "android.intent.action.MAIN": # Not Open From Notification
                cls.__name = None
                return 'Not notification'

            print(intent.getStringExtra("title"))
            try:
                if action in notifty_functions and notifty_functions[action]:
                    notifty_functions[action]()
                elif action in buttons_object:
                    buttons_object[action]()
            except Exception as notification_handler_function_error:
                print("Error Type ",notification_handler_function_error)
                print('Failed to run function: ', traceback.format_exc())
        except Exception as extracting_notification_props_error:
            print('Notify Handler Failed ',extracting_notification_props_error)

    @classmethod
    def bindNotifyListener(cls):
        """This Creates a Listener for All Notification Clicks and Functions"""
        if on_flet_app():
            return False

        if not cls.is_on_android():
            return "Not on Android"
        #TODO keep trying BroadcastReceiver
        if cls.__bound:
            print("binding done already ")
            return True
        try:
            cls.android_activity.bind(on_new_intent=cls.__notification_handler)
            cls.__bound = True
            return True
        except Exception as binding_listener_error:
            print('Failed to bin notifications listener',binding_listener_error)
            return False

    @classmethod
    def unbindNotifyListener(cls):
        """Removes Listener for Notifications Click"""
        if not cls.is_on_android():
            return "Not on Android"

        #Beta TODO use BroadcastReceiver
        if on_flet_app() or from_service_file():
            return False # error 'NoneType' object has no attribute 'registerNewIntentListener'
        try:
            cls.android_activity.unbind(on_new_intent=cls.__notification_handler)
            return True
        except Exception as unbinding_listener_error:
            print("Failed to unbind notifications listener: ",unbinding_listener_error)
            return False

    @staticmethod
    def is_on_android():
        """Utility to check if the app is running on Android."""
        return ON_ANDROID

    @staticmethod
    def has_permission():
        """
        Checks if device has permission to send notifications
        returns True if device has permission
        """
        if not ON_ANDROID:
            return True

        if on_flet_app():
            Manifest = autoclass('android.Manifest$permission')
            VERSION_CODES = autoclass('android.os.Build$VERSION_CODES')
            PackageManager = autoclass("android.content.pm.PackageManager")

            if BuildVersion.SDK_INT >= VERSION_CODES.TIRAMISU:
                permission = Manifest.POST_NOTIFICATIONS
                return PackageManager.PERMISSION_GRANTED == context.checkSelfPermission(permission)
            else:
                print("android_notify- On Low android version don't need permission")
                return True #doesn't need permission
        else:
            from android.permissions import Permission, check_permission
            return check_permission(Permission.POST_NOTIFICATIONS)

    @classmethod
    @run_on_ui_thread
    def asks_permission(cls,callback=None):
        """
        Ask for permission to send notifications if needed.
        Passes True to callback if access granted
        """
        if cls.__requesting_permission or not ON_ANDROID:
            return True

        def on_permissions_result(permissions, grants):
            try:
                if callback:
                    if can_accept_arguments(callback, True):
                        callback(grants[0])
                    else:
                        callback()
            except Exception as request_permission_error:
                print('Exception: ',request_permission_error)
                print('Permission response callback error: ',traceback.format_exc())
            finally:
                cls.__requesting_permission = False

        if not cls.has_permission():
            if on_flet_app():
                Manifest = autoclass('android.Manifest$permission')
                permission = Manifest.POST_NOTIFICATIONS
                context.requestPermissions([permission], 101)
                # TODO Callback when user answers request question
            else:
                from android.permissions import request_permissions, Permission
                cls.__requesting_permission = True
                request_permissions([Permission.POST_NOTIFICATIONS],on_permissions_result)
                return None
        else:
            cls.__requesting_permission = False
            if callback:
                if can_accept_arguments(callback,True):
                    callback(True)
                else:
                    callback()
            return None


if not on_flet_app() and from_service_file():
    print("didn't bind listener, In service file")
elif ON_ANDROID:
    try:
        NotificationHandler.bindNotifyListener()
    except Exception as bind_error:
        # error 'NoneType' object has no attribute 'registerNewIntentListener'
        print("notification listener bind error:",bind_error)
        traceback.print_exc()


import os, sys
from .core import send_notification
def get_package_path1():
    """
    Tries multiple methods to determine the package path on Android.
    Sends the result to a notification using send_notification().
    """
    path = None

    # --- Method 1: Using __file__ ---
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        send_notification(title="__file__ method", message=path)
    except Exception as e:
        send_notification(title="__file__ failed", message=str(e))

    # --- Method 2: Using sys.argv[0] ---
    try:
        argv0 = os.path.abspath(sys.argv[0])
        send_notification(title="sys.argv[0] method", message=argv0)
    except Exception as e:
        send_notification(title="sys.argv[0] failed", message=str(e))

    # --- Method 3: Searching sys.path for site-packages ---
    try:
        site_packages = [p for p in sys.path if 'site-packages' in p]
        if site_packages:
            msg = "\n".join(site_packages)
            send_notification(title="site-packages method", message=msg)
        else:
            send_notification(title="site-packages method", message="Not found")
    except Exception as e:
        send_notification(title="site-packages failed", message=str(e))

import os

def get_files_recursive(path):
    """
    Returns all files inside the directory and its subdirectories
    as a single newline-separated string.
    """
    if not os.path.isdir(path):
        return f"❌ Path does not exist or is not a directory: {path}"

    files_list = []

    for root, dirs, files in os.walk(path):
        for filename in files:
            files_list.append(os.path.join(root, filename))

    # join into one big string
    return "\n".join(files_list)
