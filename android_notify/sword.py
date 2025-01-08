"""This Module Contain Class for creating Notification With Java"""
import difflib
import random
import os
import re
from jnius import autoclass,cast  # pylint: disable=W0611, C0114

DEV=0
ON_ANDROID = False

try:
    # Get the required Java classes
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
    :param big_picture_path: Path to the image resource.
    :param large_icon_path: Path to the image resource.
    ---
    (Advance Options)
    :param channel_name: Defaults to "Default Channel"
    :param channel_id: Defaults to "default_channel"
    ---
    (Options during Dev On PC)
    :param logs: Defaults to True
    """
    notification_ids=[]
    button_ids=[]
    style_values=[
                  '','simple',
                  'progress','big_text',
                  'inbox', 'big_picture',
                  'large_icon','both_imgs',
                  'custom'
                ] # TODO make pattern for non-android Notifications
    defaults={
        'title':'Default Title',
        'message':'Default Message', # TODO Might change message para to list if style set to inbox
        'style':'simple',
        'big_picture_path':'',
        'large_icon_path':'',
        'progress_max_value': 0,
        'progress_current_value': 0,
        'channel_name':'Default Channel',
        'channel_id':'default_channel',
        'logs':True,
    }
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

    def updateProgressBar(self,current_value,message:str=''):
        """message defaults to last message"""
        if not ON_ANDROID:
            return
            
        if self.logs:
            print(f'Progress Bar Update value: {current_value}')
        self.__builder.setProgress(self.progress_max_value, current_value, False)
        if message:
            self.__builder.setContentText(String(message))
        self.notification_manager.notify(self.__id, self.__builder.build())

    def removeProgressBar(self,message=''):
        """message defaults to last message"""
        if message:
            self.__builder.setContentText(String(message))
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
            for name,value in vars(self).items():
                if value and name not in ['logs','_Notification__id']:
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
        for key,value in options_dict.items():
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
        # self.__builder = NotificationCompatBuilder(context, self.channel_id)# pylint: disable=E0606
        self.__builder.setContentTitle(self.title)
        self.__builder.setContentText(self.message)
        self.__builder.setSmallIcon(context.getApplicationInfo().icon)
        self.__builder.setDefaults(NotificationCompat.DEFAULT_ALL) # pylint: disable=E0606
        self.__builder.setPriority(NotificationCompat.PRIORITY_DEFAULT if self.silent else NotificationCompat.PRIORITY_HIGH)
        self.__addIntentToOpenApp()
    def __addNotificationStyle(self):
        # pylint: disable=trailing-whitespace
        
        large_icon_javapath=None
        if self.large_icon_path:
            try:
                large_icon_javapath = self.__get_image_uri(self.large_icon_path)
            except FileNotFoundError as e:
                print('Failed Adding Big Picture Bitmap: ',e)
        
        big_pic_javapath=None
        if self.big_picture_path:
            try:
                big_pic_javapath = self.__get_image_uri(self.big_picture_path)
            except FileNotFoundError as e:
                print('Failed Adding Lagre Icon Bitmap: ',e)
        
        
        if self.style == "big_text":
            big_text_style = NotificationCompatBigTextStyle() # pylint: disable=E0606
            big_text_style.bigText(self.message)
            self.__builder.setStyle(big_text_style)
            
        elif self.style == "inbox":
            inbox_style = NotificationCompatInboxStyle() # pylint: disable=E0606
            for line in self.message.split("\n"):
                inbox_style.addLine(line)
            self.__builder.setStyle(inbox_style)
            
        elif self.style == "big_picture" and big_pic_javapath:
            big_pic_bitmap = self.__getBitmap(big_pic_javapath)
            big_picture_style = NotificationCompatBigPictureStyle().bigPicture(big_pic_bitmap) # pylint: disable=E0606
            self.__builder.setStyle(big_picture_style)
        
        elif self.style == "large_icon" and large_icon_javapath:
            large_icon_bitmap = self.__getBitmap(large_icon_javapath)
            self.__builder.setLargeIcon(large_icon_bitmap)
        
        elif self.style == 'both_imgs' and (large_icon_javapath or big_pic_javapath):
            if big_pic_javapath:
                big_pic_bitmap = self.__getBitmap(big_pic_javapath)
                big_picture_style = NotificationCompatBigPictureStyle().bigPicture(big_pic_bitmap)
                self.__builder.setStyle(big_picture_style)
            elif large_icon_javapath:
                large_icon_bitmap = self.__getBitmap(large_icon_javapath)
                self.__builder.setLargeIcon(large_icon_bitmap)
        elif self.style == 'progress':
            self.__builder.setContentTitle(String(self.title))
            self.__builder.setContentText(String(self.message))
            self.__builder.setProgress(self.progress_max_value, self.progress_current_value, False)
        # elif self.style == 'custom':
        #     self.__builder = self.__doCustomStyle()

    # def __doCustomStyle(self):
    #     # TODO Will implement when needed
    #     return self.__builder

    def __getUniqueID(self):
        reasonable_amount_of_notifications=101
        notification_id = random.randint(1, reasonable_amount_of_notifications)
        while notification_id in self.notification_ids:
            notification_id = random.randint(1, reasonable_amount_of_notifications)
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

    def __get_image_uri(self,relative_path):
        """
        Get the absolute URI for an image in the assets folder.
        :param relative_path: The relative path to the image (e.g., 'assets/imgs/icon.png').
        :return: Absolute URI java Object (e.g., 'file:///path/to/file.png').
        """

        output_path = os.path.join(app_storage_path(),'app', relative_path) # pylint: disable=possibly-used-before-assignment
        # print(output_path)  # /data/user/0/(package.domain+package.name)/files/app/assets/imgs/icon.png | pylint: disable=:line-too-long

        if not os.path.exists(output_path):
            # TODO Use images From Any where even Web
            raise FileNotFoundError(f"Image not found at path: {output_path}, (Can Only Use Images in App Path)")
        Uri = autoclass('android.net.Uri')
        return Uri.parse(f"file://{output_path}")
    def __getBitmap(self,img_path):
        return BitmapFactory.decodeStream(context.getContentResolver().openInputStream(img_path))

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
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP)
        pending_intent = PendingIntent.getActivity(
                            context, 0,
                            intent, PendingIntent.FLAG_IMMUTABLE if BuildVersion.SDK_INT >= 31 else PendingIntent.FLAG_UPDATE_CURRENT
                        )
        self.__builder.setContentIntent(pending_intent)
        self.__builder.setAutoCancel(True)

    def __getIDForButton(self):
        reasonable_amount_of_notifications=101
        btn_id = random.randint(1, reasonable_amount_of_notifications)
        while btn_id in self.button_ids:
            btn_id = random.randint(1, reasonable_amount_of_notifications)
        self.button_ids.append(btn_id)
        return str(btn_id)

    def addButton(self, text:str,on_release):
        """For adding action buttons

        Args:
            text (str): Text For Button
        """
        if not ON_ANDROID:
            return

        if self.logs:
            print('Added Button: '+text)
        action_intent = Intent(context, PythonActivity)
        action_intent.setAction("ACTION "+ self.__getIDForButton())
        pending_action_intent = PendingIntent.getActivity(
            context,
            0,
            action_intent,
            PendingIntent.FLAG_IMMUTABLE
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
                # on_release()

# def buttonsListener():
#     """Handle notification button clicks"""
#     try:
#         intent = context.getIntent()
#         action = context.getAction()
#         print("The Action --> ",action)
#         intent.setAction("")
#         context.setIntent(intent)
#     except Exception as e:
#         print("Catching Intents Error ",e)

#     notify=Notification(titl='My Title',channel_name='Go')#,logs=False)
#     # notify.channel_name='Downloads'
#     notify.message="Blah"
#     notify.send()
#     notify.updateTitle('New Title')
#     notify.updateMessage('New Message')
#     notify.send(True)
# except Exception as e:
#     print(e)

# notify=Notification(title='My Title1')
# # notify.updateTitle('New Title1')
# notify.send()


# Notification.logs=False # Add in Readme
# notify=Notification(style='large_icon',title='My Title',channel_name='Some thing about a thing ')#,logs=False)
# # notify.channel_name='Downloads'
# notify.message="Blah"
# notify.send()
# notify.updateTitle('New Title')
# notify.updateMessage('New Message')
