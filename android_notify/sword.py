"""This Module Contain Class for creating Notification With Java"""
import difflib
import traceback
import os
import threading
import re
from .styles import NotificationStyles

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
    ON_ANDROID = True
except Exception as e:# pylint: disable=W0718
    MESSAGE='This Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" to see design patterns and more info.' # pylint: disable=C0301
    print(MESSAGE if DEV else '')

    # This is so no crashes when developing on PC
    def run_on_ui_thread(func):
        """Fallback for Developing on PC"""
        def wrapper(*args, **kwargs):
            print("Simulating run on UI thread")
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
        print(e if DEV else '','Import Fector101')
        # print(e if DEV else '')
        print("""
        Dependency Error: Add the following in buildozer.spec:
        * android.gradle_dependencies = androidx.core:core-ktx:1.15.0, androidx.core:core:1.6.0
        * android.enable_androidx = True
        * android.permissions = POST_NOTIFICATIONS
        """)

class Notification:
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
    :param subject: Preview text For `big_Text` style `message`.
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
    style_values=[
                  '','simple',
                  'progress','big_text',
                  'inbox', 'big_picture',
                  'large_icon','both_imgs',
                  'custom'
                ] # TODO make pattern for non-android Notifications
    defaults={
        'title':'Default Title',
        'message':'Default Message',
        'style':'simple',
        'big_picture_path':'',
        'large_icon_path':'',
        'progress_max_value': 0,
        'progress_current_value': 0,
        'subject':'',
        'channel_name':'Default Channel',
        'channel_id':'default_channel',
        'logs':True,
        "identifer": '',
        'callback': None
    }
    # TODO specify types in a better way instead of using
    # if key not in non_string_keys: value = str(value) to fix
    #non_string_keys=['progress_max_value','progress_current_value','callback','logs']
    # TODO using default values to check types
    # During Development (When running on PC)
    logs=not ON_ANDROID
    def __init__(self,**kwargs):
        self.__validateArgs(kwargs)
        # Basic options
        self.title=''
        self.message=''
        self.style=''
        self.large_icon_path=''
        self.big_picture_path=''
        self.progress_current_value=0
        self.progress_max_value=0
        self.subject= ''

        # For Nofitication Functions
        self.identifer=''
        self.callback = None

        # Advance Options
        self.channel_name='Default Channel'
        self.channel_id='default_channel'
        self.silent=False

        # During Dev on PC
        self.logs=self.logs

        # Private (Don't Touch)
        self.__id = self.__getUniqueID()
        self.__setArgs(kwargs)

        if not ON_ANDROID:
            return
        # TODO make send method wait for __asks_permission_if_needed method
        self.__asks_permission_if_needed()
        self.notification_manager = context.getSystemService(context.NOTIFICATION_SERVICE)
        self.__builder=NotificationCompatBuilder(context, self.channel_id)# pylint: disable=E0606

    def updateTitle(self,new_title):
        """Changes Old Title

        Args:
            new_title (str): New Notification Title
        """
        self.title=new_title
        if ON_ANDROID:
            self.__builder.setContentTitle(new_title)

    def updateMessage(self,new_message):
        """Changes Old Message

        Args:
            new_message (str): New Notification Message
        """
        self.message=new_message
        if ON_ANDROID:
            self.__builder.setContentText(new_message)
            return True
        return 'Updated'
    def updateProgressBar(self,current_value,message:str=''):
        """current_value is the value to set progressbar, message defaults to last message"""

        if self.logs:
            print(f'Progress Bar Update value: {current_value}')

        if not ON_ANDROID:
            return

        self.__builder.setProgress(self.progress_max_value, current_value, False)
        if message:
            self.__builder.setContentText(String(message))
        self.notification_manager.notify(self.__id, self.__builder.build())

    def removeProgressBar(self,message=''):
        """message defaults to last message"""

        if self.logs:
            print('removed')

        if not ON_ANDROID:
            return True

        if message:
            self.__builder.setContentText(String(message))
            return True
        self.__builder.setProgress(0, 0, False)
        self.notification_manager.notify(self.__id, self.__builder.build())

    def send(self,silent:bool=False):
        """Sends notification
        
        Args:
            silent (bool): True if you don't want to show briefly on screen
        """
        self.silent=self.silent or silent
        if ON_ANDROID:
            self.__startNotificationBuild()
            self.notification_manager.notify(self.__id, self.__builder.build())
        elif self.logs:
            string_to_display=''
            print("\n Sent Notification!!!")
            for name,value in vars(self).items():
                if value and name in ["title", "message", "style", "subject", "large_icon_path", "big_picture_path", "progress_current_value", "progress_max_value", "channel_name"]:
                    string_to_display += f'\n {name}: {value}'
            string_to_display +="\n (Won't Print Logs When Complied,except if selected `Notification.logs=True`)"
            print(string_to_display)
            if DEV:
                print(f'channel_name: {self.channel_name}, Channel ID: {self.channel_id}, id: {self.__id}')
            print('Can\'t Send Package Only Runs on Android !!! ---> Check "https://github.com/Fector101/android_notify/" for Documentation.\n' if DEV else '\n') # pylint: disable=C0301

    def __validateArgs(self,inputted_kwargs):

        def checkInReference(inputted_keywords,accepteable_inputs,input_type):
            def singularForm(plural_form):
                return plural_form[:-1]
            invalid_args= set(inputted_keywords) - set(accepteable_inputs)
            if invalid_args:
                suggestions=[]
                for arg in invalid_args:
                    closest_match = difflib.get_close_matches(arg,accepteable_inputs,n=2,cutoff=0.6)
                    if closest_match:
                        suggestions.append(f"* '{arg}' Invalid -> Did you mean '{closest_match[0]}'? ") # pylint: disable=C0301
                    else:
                        suggestions.append(f"* {arg} is not a valid {singularForm(input_type)}.")
                suggestion_text='\n'.join(suggestions)
                hint_msg=singularForm(input_type) if len(invalid_args) < 2 else input_type

                raise ValueError(f"Invalid {hint_msg} provided: \n\t{suggestion_text}\n\t* list of valid {input_type}: [{', '.join(accepteable_inputs)}]")

        allowed_keywords=self.defaults.keys()
        inputted_keywords_=inputted_kwargs.keys()
        checkInReference(inputted_keywords_,allowed_keywords,'arguments')

        # Validate style values
        if 'style' in inputted_keywords_ and inputted_kwargs['style'] not in self.style_values:
            checkInReference([inputted_kwargs['style']],self.style_values,'values')

    def __setArgs(self,options_dict:dict):
        non_string_keys=['progress_max_value','progress_current_value','callback','logs']

        for key,value in options_dict.items():
            if key not in non_string_keys: # Fixing Types
                value = str(value)
            if key == 'channel_name' and value.strip():
                setattr(self,key, value[:40])
            elif key == 'channel_id' and value.strip(): # If user input's a channel id (i format properly)
                setattr(self,key, self.__generate_channel_id(value))
            else:
                setattr(self,key, value if value else self.defaults[key])

        if "channel_id" not in options_dict and 'channel_name' in options_dict: # if User doesn't input channel id but inputs channel_name
            setattr(self,'channel_id', self.__generate_channel_id(options_dict['channel_name']))

    def __startNotificationBuild(self):
        self.__createBasicNotification()
        if self.style not in ['simple','']:
            self.__addNotificationStyle()

    def __createBasicNotification(self):
        # Notification Channel (Required for Android 8.0+)
        # print("THis is cchannel is ",self.channel_id) #"BLAH"
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
        if self.style == NotificationStyles.BIG_TEXT:
            self.__builder.setContentText(str(self.subject))
        else:
            self.__builder.setContentText(str(self.message))
        self.__builder.setSmallIcon(context.getApplicationInfo().icon)
        self.__builder.setDefaults(NotificationCompat.DEFAULT_ALL) # pylint: disable=E0606
        self.__builder.setPriority(NotificationCompat.PRIORITY_DEFAULT if self.silent else NotificationCompat.PRIORITY_HIGH)
        self.__builder.setOnlyAlertOnce(True)
        self.__addIntentToOpenApp()

    def __addNotificationStyle(self):
        if self.style == NotificationStyles.BIG_TEXT:
            big_text_style = NotificationCompatBigTextStyle() # pylint: disable=E0606
            big_text_style.bigText(self.message)
            self.__builder.setStyle(big_text_style)

        elif self.style == NotificationStyles.INBOX:
            inbox_style = NotificationCompatInboxStyle() # pylint: disable=E0606
            for line in self.message.split("\n"):
                inbox_style.addLine(line)
            self.__builder.setStyle(inbox_style)

        elif self.style == NotificationStyles.BIG_PICTURE and self.big_picture_path:
            self.__buildImg(self.big_picture_path, self.style)

        elif self.style == NotificationStyles.LARGE_ICON and self.large_icon_path:
            self.__buildImg(self.large_icon_path, self.style)

        elif self.style == NotificationStyles.BOTH_IMGS and (self.big_picture_path or self.large_icon_path):
            if self.big_picture_path:
                self.__buildImg(self.big_picture_path, NotificationStyles.BIG_PICTURE)
            if self.large_icon_path:
                self.__buildImg(self.large_icon_path, NotificationStyles.LARGE_ICON)

        elif self.style == 'progress':
            self.__builder.setContentTitle(String(self.title))
            self.__builder.setContentText(String(self.message))
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)

        # elif self.style == 'custom':
        #     self.__builder = self.__doCustomStyle()

    # def __doCustomStyle(self):
    #     # TODO Will implement when needed
    #     return self.__builder

    def __buildImg(self, user_img,img_style):
        if user_img.startswith('http://') or user_img.startswith('https://'):
            thread = threading.Thread(
                                        target=self.__getImgFromURL,
                                        args=(user_img,img_style,)
                                    )
            thread.start()
        else:
            if NotificationStyles.BIG_PICTURE:
                bitmap = self.__getImgFromPath(user_img)
                if bitmap:
                    big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap) # pylint: disable=E0606
                    self.__builder.setStyle(big_picture_style)
            elif NotificationStyles.LARGE_ICON:
                bitmap = self.__getImgFromPath(user_img)
                if bitmap:
                    self.__builder.setLargeIcon(bitmap)

    def __getImgFromPath(self, relative_path):
        app_folder=os.path.join(app_storage_path(),'app') # pylint: disable=possibly-used-before-assignment
        output_path = os.path.join(app_folder, relative_path)
        if not os.path.exists(output_path):
            print(f"\nImage not found at path: {output_path}, (Local images gotten from App Path)")
            print("These are the existing files in your app Folder:")
            print('['+', '.join(os.listdir(app_folder)) + ']')
            return None
        Uri = autoclass('android.net.Uri')
        uri = Uri.parse(f"file://{output_path}")
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(uri))

    def __getImgFromURL(self,url,img_style):
        print("getting image from URL---")
        try:
            URL = autoclass('java.net.URL')
            url = URL(url)
            connection = url.openConnection()
            connection.connect()
            input_stream = connection.getInputStream()
            bitmap = BitmapFactory.decodeStream(input_stream)
            input_stream.close()
            self.__applyNotificationImage(bitmap,img_style)
        except Exception as e:
            # TODO get type of JAVA Error
            print('Error Type ',e)
            print('Failed to get Img from URL ',traceback.format_exc())

    @run_on_ui_thread
    def __applyNotificationImage(self,bitmap,img_style):
        print('appying notification image thread ', bitmap)
        try:
            if img_style == NotificationStyles.BIG_PICTURE:
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(bitmap) # pylint: disable=E0606
                self.__builder.setStyle(big_picture_style)
            elif img_style == NotificationStyles.LARGE_ICON:
                self.__builder.setLargeIcon(bitmap)
            self.notification_manager.notify(self.__id, self.__builder.build())
            print('added notification image done-------')
        except Exception as e:
            print('I could stop ',e)
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
        self.__builder.setAutoCancel(True)

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
