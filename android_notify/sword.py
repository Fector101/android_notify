"""This Module Contain Class for creating Notification With Java"""
import difflib
import traceback
import os
import threading
import re
from .styles import NotificationStyles
from .base import BaseNotification
DEV=0
ON_ANDROID = False

try:
    # Android Imports
    from jnius import autoclass,cast  # Needs Java to be installed pylint: disable=W0611, C0114
    from android import activity # pylint: disable=import-error
    from android.config import ACTIVITY_CLASS_NAME # pylint: disable=import-error
    from android.runnable import run_on_ui_thread # pylint: disable=import-error

    # Get the required Java classes
    Bundle = autoclass('android.os.Bundle')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    String = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    context = PythonActivity.mActivity # Get the app's context
    BitmapFactory = autoclass('android.graphics.BitmapFactory')
    BuildVersion = autoclass('android.os.Build$VERSION')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    IconCompat = autoclass('androidx.core.graphics.drawable.IconCompat')
    ON_ANDROID = True
except Exception as e:# pylint: disable=W0718
    MESSAGE='This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.' # pylint: disable=C0301
    # from .types_idea import *
    # print(MESSAGE) Already Printing in core.py

    # This is so no crashes when developing on PC
    def run_on_ui_thread(func):
        """Fallback for Developing on PC"""
        def wrapper(*args, **kwargs):
            # print("Simulating run on UI thread")
            return func(*args, **kwargs)
        return wrapper

if ON_ANDROID:
    try:
        from android.permissions import request_permissions, Permission,check_permission # pylint: disable=E0401
        from android.storage import app_storage_path  # pylint: disable=E0401

        NotificationManagerCompat = autoclass('androidx.core.app.NotificationManagerCompat')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')

        # Notification Design
        NotificationCompatBuilder = autoclass('androidx.core.app.NotificationCompat$Builder') # pylint: disable=C0301
        NotificationCompatBigTextStyle = autoclass('androidx.core.app.NotificationCompat$BigTextStyle') # pylint: disable=C0301
        NotificationCompatBigPictureStyle = autoclass('androidx.core.app.NotificationCompat$BigPictureStyle') # pylint: disable=C0301
        NotificationCompatInboxStyle = autoclass('androidx.core.app.NotificationCompat$InboxStyle')
    except Exception as e:# pylint: disable=W0718
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
    :param progress_current_value: interger To set progress bar current value.
    :param progress_max_value: interger To set Max range for progress bar.
    :param body: large text For `big_Text` style, while `message` acts as sub-title.
    ---
    (Advance Options)
    :param callback: Function for notification Click.
    :param channel_name: - str Defaults to "Default Channel"
    :param channel_id: - str Defaults to "default_channel"
    ---
    (Options during Dev On PC)
    :param logs: - Bool Defaults to True
    """
    notification_ids=[0]
    button_ids=[0]
    btns_box={}
    main_functions={}

    # During Development (When running on PC)
    BaseNotification.logs=not ON_ANDROID
    def __init__(self,**kwargs): #pylint: disable=W0231 #@dataclass already does work
        super().__init__(**kwargs)

        self.__id = self.__getUniqueID()
        self.__update_timer = None  # To Track progressbar last update (According to Android Docs Don't update bar to often, I also faced so issues when doing that)
        self.__formatChannel(kwargs)
        if not ON_ANDROID:
            return
        # TODO make send method wait for __asks_permission_if_needed method
        self.__asks_permission_if_needed()
        self.notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)
        self.__builder=NotificationCompatBuilder(context, self.channel_id)# pylint: disable=E0606
    def showInfiniteProgressBar(self):
        """Displays an (Infinite) progress Bar in Notification, that continues loading indefinitely.
        Can be Removed By `removeProgressBar` Method
        """
        self.__builder.setProgress(0,0, True)
        self.__dispatchNotification()
        
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
            self.__dispatchNotification()

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
            self.__dispatchNotification()

    def updateProgressBar(self,current_value:int,message:str='',title:str='',buffer=0.5):
        """Updates progress bar current value
        
        Args:
            current_value (int): the value from progressbar current progress
            message (str): defaults to last message
            title (str): defaults to last title
            buffer (float, optional): Avoid Updating progressbar value too frequently Defaults to 0.5secs
        NOTE: There is a 0.5sec delay for value change, if updating title,msg with progressbar frequenlty pass them in too to avoid update issues
        """
        # replacing new value for when timer is called
        self.progress_current_value = current_value

        if self.__update_timer:
            if self.logs:
                print('Progressbar update too soon Doing bounce 0.5sec')
            return

        def delayed_update():
            if self.__update_timer is None:
            # Ensure we are not executing an old timer
                return
            if self.logs:
                print(f'Progress Bar Update value: {self.progress_current_value}')

            if not ON_ANDROID:
                return
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)
            if message:
                self.updateMessage(message)
            if title:
                self.updateTitle(title)
            self.__dispatchNotification()
            self.__update_timer = None


        # Start a new timer that runs after 0.5 seconds
        self.__update_timer = threading.Timer(0.5, delayed_update)
        self.__update_timer.start()

    def removeProgressBar(self,message='',show_on_update=True, title:str='') -> bool:
        """Removes Progress Bar from Notification

        Args:
            message (str, optional): notification message. Defaults to 'last message'.
            show_on_update (bool, optional): To show notification brifely when progressbar removed. Defaults to True.
            title (str, optional): notification title. Defaults to 'last title'.
        """
        if self.__update_timer:
            self.__update_timer.cancel()
            self.__update_timer = None
        
        if self.logs:
            msg = message or self.message
            title_=title or self.title
            print(f'removed progress bar with message: {msg} and title: {title_}')

        if not ON_ANDROID:
            return False

        self.__builder.setOnlyAlertOnce(not show_on_update)
        if message:
            self.updateMessage(message)
        if title:
            self.updateTitle(title)
        self.__builder.setProgress(0, 0, False)
        self.__dispatchNotification()
        return True

    def send(self,silent:bool=False,persistent=False,close_on_click=True):
        """Sends notification
        
        Args:
            silent (bool): True if you don't want to show briefly on screen
            persistent (bool): True To not remove Notification When User hits clears All notifications button
            close_on_click (bool): True if you want Notification to be removed when clicked
        """
        self.silent=self.silent or silent
        if ON_ANDROID:
            self.__startNotificationBuild(persistent,close_on_click)
            self.__dispatchNotification()
        if self.logs:
            string_to_display=''
            print("\n Sent Notification!!!")
            for name,value in vars(self).items():
                if value and name in ["title", "message", "style", "body", "large_icon_path", "big_picture_path", "progress_current_value", "progress_max_value", "channel_name"]:
                    if name == "progress_max_value":
                        if self.style == NotificationStyles.PROGRESS:
                            string_to_display += f'\n {name}: {value}'
                    else:
                        string_to_display += f'\n {name}: {value}'

            string_to_display +="\n (Won't Print Logs When Complied,except if selected `Notification.logs=True`)"
            print(string_to_display)
            if DEV:
                print(f'channel_name: {self.channel_name}, Channel ID: {self.channel_id}, id: {self.__id}')
            print('Can\'t Send Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.\n' if DEV else '\n') # pylint: disable=C0301

    def addButton(self, text:str,on_release):
        """For adding action buttons

        Args:
            text (str): Text For Button
        """
        if self.logs:
            print('Added Button: ', text)

        if not ON_ANDROID:
            return

        btn_id= self.__getIDForButton()
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
            self.__dispatchNotification()
        if self.logs:
            print('Removed Notication Buttons')

    @run_on_ui_thread
    def addNotificationStyle(self,style:str,already_sent=False):
        """Adds Style to Notification
            Version 1.51.2+ Exposes method to Users (Note): Always try to Call On UI Thread

        Args:
            style (str): required style
            already_sent (bool,False): If notification was already sent
        """

        if not ON_ANDROID:
            # TODO for logs when not on android and style related to imgs etraxct app path from buildozer.spec and print
            return False

        if style == NotificationStyles.BIG_TEXT:
            big_text_style = NotificationCompatBigTextStyle() # pylint: disable=E0606
            big_text_style.bigText(str(self.body))
            self.__builder.setStyle(big_text_style)

        elif style == NotificationStyles.INBOX:
            inbox_style = NotificationCompatInboxStyle() # pylint: disable=E0606
            for line in self.message.split("\n"):
                inbox_style.addLine(str(line))
            self.__builder.setStyle(inbox_style)

        elif (style == NotificationStyles.LARGE_ICON and self.large_icon_path) or (style == NotificationStyles.BIG_PICTURE and self.big_picture_path):
            img = self.large_icon_path if style == NotificationStyles.LARGE_ICON else self.big_picture_path
            self.__buildImg(img, style)

        elif style == NotificationStyles.BOTH_IMGS and (self.big_picture_path or self.large_icon_path):
            if self.big_picture_path:
                self.__buildImg(self.big_picture_path, NotificationStyles.BIG_PICTURE)
            if self.large_icon_path:
                self.__buildImg(self.large_icon_path, NotificationStyles.LARGE_ICON)

        elif style == NotificationStyles.PROGRESS:
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)

        if already_sent:
            self.__dispatchNotification()

        return True
        # elif style == 'custom':
        #     self.__builder = self.__doCustomStyle()

    def __dispatchNotification(self):
        self.notification_manager.notify(self.__id, self.__builder.build())
    def __startNotificationBuild(self,persistent,close_on_click):
        self.__createBasicNotification(persistent,close_on_click)
        if self.style not in ['simple','']:
            self.addNotificationStyle(self.style)

    def __createBasicNotification(self,persistent,close_on_click):
        # Notification Channel (Required for Android 8.0+)
        # print("THis is cchannel is ",self.channel_id) #"
        if BuildVersion.SDK_INT >= 26 and self.notification_manager.getNotificationChannel(self.channel_id) is None:
            importance=NotificationManagerCompat.IMPORTANCE_DEFAULT if self.silent else NotificationManagerCompat.IMPORTANCE_HIGH # pylint: disable=possibly-used-before-assignment
            # importance = 3 or 4
            channel = NotificationChannel(
                self.channel_id,
                self.channel_name,
                importance
            )
            self.notification_manager.createNotificationChannel(channel)

        # Build the notification
        # str() This is to prevent Error When user does Notification.title='blah' instead of Notification(title='blah'
        # TODO fix this by creating a on_Title method in other versions
        self.__builder.setContentTitle(str(self.title))
        self.__builder.setContentText(str(self.message))
        self.__insertAppIcon()
        self.__builder.setDefaults(NotificationCompat.DEFAULT_ALL) # pylint: disable=E0606
        self.__builder.setPriority(NotificationCompat.PRIORITY_DEFAULT if self.silent else NotificationCompat.PRIORITY_HIGH)
        self.__builder.setOnlyAlertOnce(True)
        self.__builder.setOngoing(persistent)
        self.__builder.setAutoCancel(close_on_click)
        self.__addIntentToOpenApp()

    # def __doCustomStyle(self):
    #     # TODO Will implement when needed
    #     return self.__builder
    def __insertAppIcon(self):
        if self.app_icon not in ['','Defaults to package app icon']:
            self.__setIconFromBitmap(self.app_icon)
        else:
            self.__builder.setSmallIcon(context.getApplicationInfo().icon)

    def __buildImg(self, user_img,img_style):
        if user_img.startswith('http://') or user_img.startswith('https://'):
            def callback(bitmap):
                self.__applyNotificationImage(bitmap,img_style)
            thread = threading.Thread(
                                        target=self.__getBitmapFromURL,
                                        args=[user_img,callback]
                                    )
            thread.start()
        else:
            bitmap = self.__getImgFromPath(user_img)
            if bitmap:
                self.__applyNotificationImage(bitmap,img_style)

    def __setIconFromBitmap(self,img_path):
        """Path can be link or relative path"""
        if img_path.startswith('http://') or img_path.startswith('https://'):
            def callback(bitmap):
                icon = IconCompat.createWithBitmap(bitmap)
                self.__builder.setSmallIcon(icon)
            threading.Thread(
                                        target=self.__getBitmapFromURL,
                                        args=[img_path,callback]
                                    ).start()
        else:
            bitmap = self.__getImgFromPath(img_path)
            if bitmap:
                icon = IconCompat.createWithBitmap(bitmap)
                self.__builder.setSmallIcon(icon)
            else:
                if self.logs:
                    print('Failed getting img for custom notification icon defaulting to app icon')
                self.__builder.setSmallIcon(context.getApplicationInfo().icon)

    def __getImgFromPath(self, relative_path):
        app_folder=os.path.join(app_storage_path(),'app') # pylint: disable=possibly-used-before-assignment
        output_path = os.path.join(app_folder, relative_path)
        if not os.path.exists(output_path):
            print(f"\nImage not found at path: {output_path}, (Local images gotten from App Path)")
            print("These are the existing files in your app Folder:")
            print('['+', '.join(os.listdir(app_folder)) + ']')
            return None
        # TODO test with a badly written Image and catch error
        Uri = autoclass('android.net.Uri')
        uri = Uri.parse(f"file://{output_path}")
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))

    def __getBitmapFromURL(self,url,callback):
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
                print('Error No Bitmap ------------')
        except Exception as e:
            # TODO get all types of JAVA Error
            print('Error Type ',e)
            print('Failed to get Bitmap from URL ',traceback.format_exc())

    @run_on_ui_thread
    def __applyNotificationImage(self,bitmap,img_style):
        if self.logs:
            print('appying notification image-------')
        try:
            if img_style == NotificationStyles.BIG_PICTURE:
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap) # pylint: disable=E0606
                self.__builder.setStyle(big_picture_style)
            elif img_style == NotificationStyles.LARGE_ICON:
                self.__builder.setLargeIcon(bitmap)
            self.__dispatchNotification()
            if self.logs:
                print('Done adding image to notification-------')
        except Exception as e:
            img = self.large_icon_path if img_style == NotificationStyles.LARGE_ICON else self.big_picture_path
            print(f'Failed adding Image of style: {img_style} || From path: {img}, Exception {e}')
            print('could stop get Img from URL ',traceback.format_exc())

    def __getUniqueID(self):
        notification_id = self.notification_ids[-1] + 1
        self.notification_ids.append(notification_id)
        return notification_id

    def __asks_permission_if_needed(self):
        """
        Ask for permission to send notifications if needed.
        """
        def on_permissions_result(permissions, grant): # pylint: disable=unused-argument
            if self.logs:
                print("Permission Grant State: ",grant)

        permissions=[Permission.POST_NOTIFICATIONS] # pylint: disable=E0606
        if not all(check_permission(p) for p in permissions):
            request_permissions(permissions,on_permissions_result) # pylint: disable=E0606

    def __addIntentToOpenApp(self):
        intent = Intent(context, PythonActivity)
        action = str(self.identifer) or f"ACTION_{self.__id}"
        intent.setAction(action)
        self.__addDataToIntent(intent)
        self.main_functions[action]=self.callback
        intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)

        pending_intent = PendingIntent.getActivity(
                            context, 0,
                            intent, PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT
                        )
        self.__builder.setContentIntent(pending_intent)
        
    def __addDataToIntent(self,intent):
        """Persit Some data to notification object for later use"""
        bundle = Bundle()
        bundle.putString("title",  self.title or 'Title Placeholder')
        bundle.putInt("notify_id", self.__id)
        intent.putExtras(bundle)

    def __getIDForButton(self):
        btn_id = self.button_ids[-1] + 1
        self.button_ids.append(btn_id)
        return btn_id

    def __formatChannel(self, inputted_kwargs):
        if 'channel_name' in inputted_kwargs:
            cleaned_name = inputted_kwargs['channel_name'].strip()
            self.channel_name = cleaned_name[:40] if cleaned_name else 'Default Channel'

        if 'channel_id' in inputted_kwargs:
            cleaned_id = inputted_kwargs['channel_id'].strip()
            self.channel_id = self.__generate_channel_id(cleaned_id) if cleaned_id else 'default_channel'
        elif 'channel_name' in inputted_kwargs:  
            # Generate channel_id from channel_name if only channel_name is provided
            generated_id = self.__generate_channel_id(inputted_kwargs['channel_name'])
            self.channel_id = generated_id

    def __generate_channel_id(self,channel_name: str) -> str:
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

class NotificationHandler:
    """For Notification Operations """
    __identifer = None
    __bound = False

    @classmethod
    def getIdentifer(cls):
        """Returns identifer for Clicked Notification."""
        if not cls.is_on_android():
            return "Not on Android"

        saved_intent = cls.__identifer
        if not saved_intent or (isinstance(saved_intent, str) and saved_intent.startswith("android.intent")):
            # All other notifications are not None after First notification opens app
            # NOTE these notifications are also from Last time app was opened and they Still Give Value after first one opens App
            # TODO Find a way to get intent when App if Swiped From recents
            __PythonActivity = autoclass(ACTIVITY_CLASS_NAME)
            __mactivity = __PythonActivity.mActivity
            __context = cast('android.content.Context', __mactivity)
            __Intent = autoclass('android.content.Intent')
            __intent = __Intent(__context, __PythonActivity)
            action = __intent.getAction()
            print('Start up Intent ----', action)
            print('start Up Title --->',__intent.getStringExtra("title"))

        return saved_intent

    @classmethod
    def __notificationHandler(cls,intent):
        """Calls Function Attached to notification on click.
            Don't Call this function manual, it's Already Attach to Notification.
        
        Returns:
            str: The Identiter of Nofication that was clicked.
        """
        if not cls.is_on_android():
            return "Not on Android"
        buttons_object=Notification.btns_box
        notifty_functions=Notification.main_functions
        if DEV:
            print("notifty_functions ",notifty_functions)
            print("buttons_object", buttons_object)
        action = None
        try:
            action = intent.getAction()
            cls.__identifer = action

            print("The Action --> ",action)
            if action == "android.intent.action.MAIN": # Not Open From Notification
                return 'Not notification'

            print(intent.getStringExtra("title"))
            try:
                if action in notifty_functions and notifty_functions[action]:
                    notifty_functions[action]()
                elif action in buttons_object:
                    buttons_object[action]()
            except Exception as e: # pylint: disable=broad-exception-caught
                print('Failed to run function: ', traceback.format_exc())
                print("Error Type ",e)
        except Exception as e: # pylint: disable=broad-exception-caught
            print('Notify Hanlder Failed ',e)
        return action

    @classmethod
    def bindNotifyListener(cls):
        """This Creates a Listener for All Notification Clicks and Functions"""
        if not cls.is_on_android():
            return "Not on Android"
        #TODO keep trying BroadcastReceiver
        if cls.__bound:
            print("bounding done already ")
            return True
        try:
            activity.bind(on_new_intent=cls.__notificationHandler)
            cls.__bound = True
            return True
        except Exception as e: # pylint: disable=broad-exception-caught
            print('Failed to bin notitfications listener',e)
            return False
    @classmethod
    def unbindNotifyListener(cls):
        """Removes Listener for Notifications Click"""
        if not cls.is_on_android():
            return "Not on Android"

        #Beta TODO use BroadcastReceiver
        try:
            activity.unbind(on_new_intent=cls.__notificationHandler)
            return True
        except Exception as e: # pylint: disable=broad-exception-caught
            print("Failed to unbind notifications listener: ",e)
            return False

    @staticmethod
    def is_on_android():
        """Utility to check if the app is running on Android."""
        return ON_ANDROID

NotificationHandler.bindNotifyListener()
