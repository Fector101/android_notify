"""This Module Contain Class for creating Notification With Java"""
import traceback
import os,re
import threading


from .an_types import Importance
from .an_utils import can_accept_arguments
from .styles import NotificationStyles
from .base import BaseNotification
DEV=0
ON_ANDROID = False

# noinspection PyBroadException
try:
    # Android Imports
    from jnius import autoclass,cast
    from android import activity
    from android.config import ACTIVITY_CLASS_NAME
    from android.runnable import run_on_ui_thread

    try:
        from android import config
        ns = config.JAVA_NAMESPACE
        # print('This is Java name space:',ns)
    except (ImportError,AttributeError):
        ns='org.kivy.android'

    # Get the required Java classes needs to on android to import
    Bundle = autoclass('android.os.Bundle')
    PythonActivity = autoclass(ns+'.PythonActivity')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    context = PythonActivity.mActivity
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    VersionCodes = autoclass('android.os.Build$VERSION_CODES')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')
    ON_ANDROID = True
except Exception as e:
    if hasattr(e,'name') and e.name != 'android':
        print('Exception: ',e)
        print(traceback.format_exc())

    MESSAGE='This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.'
    # from .types_idea import *
    # print(MESSAGE) Already Printing in core.py

    # This is so no crashes when developing on PC
    from .an_utils import run_on_ui_thread

if ON_ANDROID:
    try:
        from android.permissions import request_permissions, Permission,check_permission
        from android.storage import app_storage_path

        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')

        # Notification Design
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder')
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle')
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle')
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
        # NotificationCompatDecoratedCustomViewStyle = autoclass('androidx.core.app.NotificationCompat$DecoratedCustomViewStyle')
    except Exception as e:
        print(e)
        print("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS
        """)

class Notification(BaseNotification):
    """
    Send a notification on Android.

    :param title: Title of the notification.
    :param message: Message body.
    :param style: Style of the notification 
    ('simple', 'progress', 'big_text', 'inbox', 'big_picture', 'large_icon', 'both_imgs').
    both_imgs == using lager icon and big picture
    :param big_picture_path: Relative Path to the image resource.
    :param large_icon_path: Relative Path to the image resource.
    :param progress_current_value: integer To set progress bar current value.
    :param progress_max_value: integer To set Max range for progress bar.
    :param body: large text For `big_Text` style, while `message` acts as subtitle.
    :param lines_txt: text separated by newLine symbol For `inbox` style `use addLine method instead`
    ---
    (Advance Options)
    :param id: Pass in Old 'id' to use old instance
    :param callback: Function for notification Click.
    :param channel_name: - str Defaults to "Default Channel"
    :param channel_id: - str Defaults to "default_channel"
    ---
    (Options during Dev On PC)
    :param logs: - Bool Defaults to True
    """

    notification_ids = [0]
    button_ids=[0]
    btns_box={}
    main_functions={}

    # During Development (When running on PC)
    BaseNotification.logs=not ON_ANDROID
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

        self.__format_channel(self.channel_name, self.channel_id)
        if not ON_ANDROID:
            return

        NotificationHandler.asks_permission()
        notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
        self.notification_manager = cast(NotificationManager, notification_service)
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
            cls.__return_notification_manger().cancelAll()
        if cls.logs:
            print('Removed All Notifications.')

    @classmethod
    def createChannel(cls, id, name:str, description='',importance:Importance='urgent'):
        """
        Creates a user visible toggle button for specific notifications, Required For Android 8.0+
        :param id: Used to send other notifications later through same channel.
        :param name: user-visible channel name.
        :param description: user-visible detail about channel (Not required defaults to empty str).
        :param importance: ['urgent', 'high', 'medium', 'low', 'none'] defaults to 'urgent' i.e. makes a sound and shows briefly
        :return: boolean if channel created
        """

        if not ON_ANDROID:
            return False

        notification_manager=cls.__return_notification_manger()
        android_importance_value = cls.__get_android_importance(importance)

        if BuildVersion.SDK_INT >= 26 and notification_manager.getNotificationChannel(id) is None:
            channel = NotificationChannel(id, name, android_importance_value)
            if description:
                channel.setDescription(description)
            notification_manager.createNotificationChannel(channel)
            return True
        return False

    @classmethod
    def deleteChannel(cls, channel_id):
        """Delete a Channel Matching channel_id"""
        if not ON_ANDROID:
            return None

        cls.__return_notification_manger().deleteNotificationChannel(channel_id)

    @classmethod
    def deleteAllChannel(cls):
        """Deletes all notification channel
        :returns amount deleted
        """

        amount = 0
        if not ON_ANDROID:
            return amount

        notification_manager = cls.__return_notification_manger()
        channels = cls.getChannels()
        for index in range(channels.size()):
            amount += 1
            channel = channels.get(index)
            channel_id = channel.getId()
            notification_manager.deleteNotificationChannel(channel_id)
        return amount

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
            self.__insert_app_icon(path)
        elif self.logs:
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
            # When on android there are other logs
            print('Done setting big text')

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
            self.__builder.setContentText(String(self.message))
            self.refresh()

    def updateProgressBar(self,current_value:int,message:str='',title:str='',cooldown=0.5):
        """Updates progress bar current value

        Args:
            current_value (int): the value from progressbar current progress
            message (str): defaults to last message
            title (str): defaults to last title
            cooldown (float, optional): Little Time to Wait before change actually reflects, to avoid android Ignoring Change, Defaults to 0.5secs

        NOTE: There is a 0.5sec delay for value change, if updating title,msg with progressbar frequently pass them in too to avoid update issues
        """

        # replacing new values for when timer is called
        self.progress_current_value = current_value
        self.__progress_bar_msg = message
        self.__progress_bar_title = title

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

    def removeProgressBar(self,message='',show_on_update=True, title:str='',cooldown=0.5):
        """Removes Progress Bar from Notification

        Args:
            message (str, optional): notification message. Defaults to 'last message'.
            show_on_update (bool, optional): To show notification briefly when progressbar removed. Defaults to True.
            title (str, optional): notification title. Defaults to 'last title'.
            cooldown (float, optional): Little Time to Wait before change actually reflects, to avoid android Ignoring Change, Defaults to 0.5secs

        In-Built Delay of 0.5sec According to Android Docs Don't Update Progressbar too Frequently
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
            android_importance_value = self.__get_android_importance(importance)
            if not isinstance(android_importance_value, str):  # Can be an empty str if importance='none'
                self.__builder.setPriority(android_importance_value)

    def send(self,silent:bool=False,persistent=False,close_on_click=True):
        """Sends notification

        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """
        self.silent= silent or self.silent
        if ON_ANDROID:
            self.__start_notification_build(persistent, close_on_click)
            self.__dispatch_notification()

        if self.logs:
            string_to_display=''
            print("\n Sent Notification!!!")
            for name,value in vars(self).items():
                if value and name in ["title", "message", "style", "body", "large_icon_path", "big_picture_path", "progress_current_value", "progress_max_value", "channel_name",'body','name']:
                    if name == "progress_max_value":
                        if self.style == NotificationStyles.PROGRESS:
                            string_to_display += f'\n {name}: {value}'
                    elif name == "body":
                        if self.style == NotificationStyles.BIG_TEXT:
                            string_to_display += f'\n {name}: {value}'
                    else:
                        string_to_display += f'\n {name}: {value}'

            string_to_display +="\n (Won't Print Logs When Complied,except if selected `Notification.logs=True`)"
            print(string_to_display)
            if DEV:
                print(f'channel_name: {self.channel_name}, Channel ID: {self.channel_id}, __id: {self.__id}')

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

        if style == NotificationStyles.BIG_TEXT:
            self.setBigText(self.body)

        elif style == NotificationStyles.INBOX and self.lines_txt:
            lines = self.lines_txt.split("\n")
            self.setLines(lines)

        elif (style == NotificationStyles.LARGE_ICON and self.large_icon_path) or (style == NotificationStyles.BIG_PICTURE and self.big_picture_path):
            img = self.large_icon_path if style == NotificationStyles.LARGE_ICON else self.big_picture_path
            self.__build_img(img, style)

        elif style == NotificationStyles.BOTH_IMGS and (self.big_picture_path or self.large_icon_path):
            if self.big_picture_path:
                self.setBigPicture(self.big_picture_path)
            if self.large_icon_path:
                self.setLargeIcon(self.large_icon_path)

        elif style == NotificationStyles.PROGRESS:
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)

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

    def __dispatch_notification(self):
        if NotificationHandler.has_permission():
            self.notification_manager.notify(self.__id, self.__builder.build())
        else:
            print('Permission not granted to send notifications')
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
        if BuildVersion.SDK_INT >= 26 and self.notification_manager.getNotificationChannel(self.channel_id) is None:
            self.createChannel(self.channel_id, self.channel_name)
        elif not self.__using_set_priority_method:
            self.setPriority('medium' if self.silent else 'urgent')
        # Build the notification
        # str() This is to prevent Error When user does Notification.title='blah' instead of Notification(title='blah'
        # TODO fix this by creating a on_title method in other versions
        self.__builder.setContentTitle(str(self.title))
        self.__builder.setContentText(str(self.message))
        self.__insert_app_icon()
        self.__builder.setDefaults(NotificationCompat.DEFAULT_ALL)
        self.__builder.setOnlyAlertOnce(True)
        self.__builder.setOngoing(persistent)
        self.__builder.setAutoCancel(close_on_click)
        self.__add_intent_to_open_app()
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
            self.__builder.setSmallIcon(context.getApplicationInfo().icon)

    def __build_img(self, user_img, img_style):
        if user_img.startswith('http://') or user_img.startswith('https://'):
            def callback(bitmap_):
                self.__apply_notification_image(bitmap_,img_style)
            thread = threading.Thread(
                                        target=self.__get_bitmap_from_url,
                                        args=[user_img,callback]
                                    )
            thread.start()
        else:
            bitmap = self.__get_img_from_path(user_img)
            if bitmap:
                self.__apply_notification_image(bitmap, img_style)

    def __set_icon_from_bitmap(self, img_path):
        """Path can be a link or relative path"""
        if img_path.startswith('http://') or img_path.startswith('https://'):
            def callback(bitmap_):
                if bitmap_:
                    icon_ = IconCompat.createWithBitmap(bitmap_)
                    self.__builder.setSmallIcon(icon_)
                else:
                    if self.logs:
                        print('Using Default Icon as fallback......')
                    self.__builder.setSmallIcon(context.getApplicationInfo().icon)
            threading.Thread(
                target=self.__get_bitmap_from_url,
                args=[img_path,callback]
                ).start()
        else:
            bitmap = self.__get_img_from_path(img_path)
            if bitmap:
                icon = IconCompat.createWithBitmap(bitmap)
                self.__builder.setSmallIcon(icon)
            else:
                if self.logs:
                    app_folder=os.path.join(app_storage_path(),'app')
                    img_absolute_path = os.path.join(app_folder, img_path)
                    print(f'Failed getting img for custom notification icon defaulting to app icon\n absolute path {img_absolute_path}')
                self.__builder.setSmallIcon(context.getApplicationInfo().icon)

    @staticmethod
    def __get_img_from_path(relative_path):
        app_folder=os.path.join(app_storage_path(),'app')
        output_path = os.path.join(app_folder, relative_path)
        if not os.path.exists(output_path):
            print(f"\nImage not found at path: {app_folder}, (Local images gotten from App Path)")
            try:
                print("- These are the existing files in your app Folder:")
                print('['+', '.join(os.listdir(app_folder)) + ']')
            except Exception as could_not_get_files_in_path_error:
                print('Exception: ', could_not_get_files_in_path_error)
                print("Couldn't get Files in App Folder")
            return None
        # TODO test with a badly written Image and catch error
        Uri = autoclass('android.net.Uri')
        uri = Uri.parse(f"file://{output_path}")
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))

    def __get_bitmap_from_url(self, url, callback):
        """Gets Bitmap from url

        Args:
            url (str): img url
            callback (function): method to be called after thread done -passes in bitmap data as argument
        """
        if self.logs:
            print("getting Bitmap from URL---")
        try:
            URL = autoclass('java.net.URL')
            url = URL(url)
            connection = url.openConnection()
            connection.connect()
            input_stream = connection.getInputStream()
            bitmap = BitmapFactory.decodeStream(input_stream)
            input_stream.close()
            if bitmap:
                callback(bitmap)
            else:
                print('Error No Bitmap for small icon ------------')
        except Exception as extracting_bitmap_frm_URL_error:
            callback(None)
            # TODO get all types of JAVA Error that can fail here
            print('Error Type ',extracting_bitmap_frm_URL_error)
            print('Failed to get Bitmap from URL ',traceback.format_exc())

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
        self.__add_data_to_intent(intent)
        self.main_functions[action]=self.callback
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)

        pending_intent = PendingIntent.getActivity(
                            context, 0,
                            intent, PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT
                        )
        self.__builder.setContentIntent(pending_intent)
        
    def __add_data_to_intent(self, intent):
        """Persist Some data to notification object for later use"""
        bundle = Bundle()
        bundle.putString("title",  self.title or 'Title Placeholder')
        # bundle.putInt("notify_id", self.__id)
        bundle.putInt("notify_id", 101)
        intent.putExtras(bundle)

    def __get_id_for_button(self):
        btn_id = self.button_ids[-1] + 1
        self.button_ids.append(btn_id)
        return btn_id

    def __format_channel(self, channel_name:str='Default Channel',channel_id:str='default_channel'):
        """
        Formats and sets self.channel_name and self.channel_id to formatted version
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
                generated_id = self.__generate_channel_id(channel_name)
                self.channel_id = generated_id

    @staticmethod
    def __generate_channel_id(channel_name: str) -> str:
        """
        Generate a readable and consistent channel ID from a channel name.
        
        Args:
            channel_name (str): The name of the notification channel.
        
        Returns:
            str: A sanitized channel ID.
        """
        # Normalize the channel name
        channel_id = channel_name.strip().lower()
        # Replace spaces and special characters with underscores
        channel_id = re.sub(r'[^a-z0-9]+', '_', channel_id)
        # Remove leading/trailing underscores
        channel_id = channel_id.strip('_')
        return channel_id[:50]

    def __get_unique_id(self):
        notification_id = self.notification_ids[-1] + 1
        self.notification_ids.append(notification_id)
        return notification_id

    @staticmethod
    def __return_notification_manger():
        notification_service = context.getSystemService(context.NOTIFICATION_SERVICE)
        return cast(NotificationManager, notification_service)

    @classmethod
    def getChannels(cls):
        """Return all existing channels"""
        if not ON_ANDROID:
            return []

        return cls.__return_notification_manger().getNotificationChannels()

    @staticmethod
    def __get_android_importance(importance:Importance):
        """
        Returns Android Importance Values
        :param importance: ['urgent','high','medium','low','none']
        :return: Android equivalent int or empty str
        """
        value=''
        if importance == 'urgent':
            value = NotificationCompat.PRIORITY_HIGH if BuildVersion.SDK_INT <= 25 else  NotificationManagerCompat.IMPORTANCE_HIGH
        elif importance == 'high':
            value = NotificationCompat.PRIORITY_DEFAULT if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_DEFAULT
        elif importance == 'medium':
            value = NotificationCompat.PRIORITY_LOW  if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_LOW
        elif importance == 'low':
            value = NotificationCompat.PRIORITY_MIN if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_MIN
        elif importance == 'none':
            value = '' if BuildVersion.SDK_INT <= 25 else NotificationManagerCompat.IMPORTANCE_NONE

        return value
        # side-note 'medium' = NotificationCompat.PRIORITY_LOW and 'low' = NotificationCompat.PRIORITY_MIN # weird but from docs
    # TODO method to create channel groups


class NotificationHandler:
    """For Notification Operations """
    __name = None
    __bound = False
    __requesting_permission=False
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
        if not cls.is_on_android():
            return "Not on Android"
        #TODO keep trying BroadcastReceiver
        if cls.__bound:
            print("binding done already ")
            return True
        try:
            activity.bind(on_new_intent=cls.__notification_handler)
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
        try:
            activity.unbind(on_new_intent=cls.__notification_handler)
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
            cls.__requesting_permission = True
            request_permissions([Permission.POST_NOTIFICATIONS],on_permissions_result)
        else:
            cls.__requesting_permission = False
            if callback:
                if can_accept_arguments(callback,True):
                    callback(True)
                else:
                    callback()


NotificationHandler.bindNotifyListener()
