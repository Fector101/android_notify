"""Android-Notify Tester"""


from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.metrics import sp
from kivy.clock import Clock

import time

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton

from android_notify import Notification,NotificationStyles,notificationHandler
Notification.logs = 1
Builder.load_string("""
<MDTextButton>:
    adaptive_width:True
    MDButtonText:
        id:text_id
        text: root.text
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
""")

class MDTextButton(MDButton):
    text = StringProperty('Fizz')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_height = "Custom"
        self.theme_width = "Custom"

class CustomInput(MDBoxLayout):
    text=StringProperty('')
    placeholder=StringProperty('')
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.adaptive_height=True
        self.spacing=13
        self.orientation='vertical'
        self.add_widget(MDLabel(text=self.text,adaptive_width=1,pos_hint={'center_x': .5,'center_y': .5}))
        self.input_widget=MDTextField(text=self.placeholder,pos_hint={'center_x': .5,'center_y': .5}, size_hint=[.8, None], height=sp(60))
        self.add_widget(self.input_widget)

from jnius import autoclass

class Laner(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "White"
         
    def build(self):
        self.title = 'AN-Tester'
        self.screen = MDScreen()
        self.layout =  MDBoxLayout(
            adaptive_height=True,
            orientation='vertical',
            spacing=sp(30),
            pos_hint={'center_y': .5}
        )
        # self.layout.md_bg_color=[1,1,0,1]
        self.ids = {}
        input_ids=["style","title", "message", "bigimgpath", "largeiconpath"]
        titles=["Style:","Title:", "Message:", "Big Img path:", "Large Icon path:"]
        placeholders=["simple","My Title", "Some Message", "assets/icons/might/applications-python.png", "assets/icons/py.png"]

        for i in range(len(titles)):
            widget=CustomInput(text=titles[i],placeholder=placeholders[i])
            self.ids[input_ids[i]]=widget.input_widget
            self.layout.add_widget(widget)

        self.text_input=MDTextButton(text='Send',size=[sp(100),sp(30)],on_release=self.use_android_notify,pos_hint={'center_x': .5})
        self.layout.add_widget(self.text_input)
        self.screen.add_widget(self.layout)
        return self.screen
    def on_start(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        notificationHandler(context)
    def on_resume(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity

        intent = context.getIntent()
        action = intent.getAction()
        print("Action:", action)
        print("getExtra1 --> ", context.getIntent().getExtra("button_id"))
        extras = intent.getExtras()
        if extras:
            print("getExtras Cyper--> ", extras.getInt("key_int"))
            print("getStringExtra -->", extras.getString("button_id"))
            # print("getStringExtra -->", extras.getString("button_id")) # might be useful
        notificationHandler(context)

    def use_android_notify(self,widget):

        style=self.ids['style'].text
        title=self.ids['title'].text
        message=self.ids['message'].text
        big_img_path=self.ids['bigimgpath'].text
        large_icon_path=self.ids['largeiconpath'].text
        # print('title: ',title, ',meassage: ',message,',style: ',style)
        try:
            match style:
                case "simple":
                    # 1. Simple notification
                    notification = Notification(
                        title=title,
                        message=message
                    )
                    notification.send()
            
                case "progress":
                    # 2. Progress-Bar notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="progress",
                        progress_max_value=100,
                        progress_current_value=0
                    )
                    notification.send()
                    Clock.schedule_once(lambda dt: notification.updateProgressBar(30, "30% downloaded"), 6)
                    Clock.schedule_once(lambda dt: notification.removeProgressBar(message=message), 6)
                case "big_picture":
                    # 3. Big Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="big_picture",
                        big_picture_path=big_img_path
                    )
                    notification.send()
                case "inbox":
                    # 4. Send a notification with inbox style
                    notification = Notification(
                        title=title,
                        message=message,
                        style='inbox'
                    )
                    notification.send()
                case "large_icon":
                    # 5. Large Icon Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="large_icon",
                        large_icon_path=large_icon_path
                    )
                    notification.send()
                case "big_text":
                    # 7. Big text notification (Will Display as simple text if Device dosen't support)
                    notification = Notification(
                        title=title,
                        message=message,
                        style="big_text"
                    )
                    notification.send()
                case "btns":
                    # 6. Notification with Buttons
                    notification = Notification(title=title, message=message)
                    def playVideo():
                        print('Playing Video')

                    def turnOffNoti():
                        print('Please Turn OFf Noti')

                    def watchLater():
                        print('Add to Watch Later')

                    notification.addButton(text="Play",on_release=playVideo)
                    notification.addButton(text="Turn Off",on_release=turnOffNoti)
                    notification.addButton(text="Watch Later",on_release=watchLater)
                    notification.send()
                case "btnsi":
                    # 6. Notification with Buttons
                    notification = Notification(
                        title=title,
                        message=message,
                        style="large_icon",
                        large_icon_path=large_icon_path
                    )
                    def playVideo():
                        print('Playing Video')

                    def turnOffNoti():
                        print('Please Turn OFf Noti')

                    def watchLater():
                        print('Add to Watch Later')

                    notification.addButton(text="Play",on_release=playVideo)
                    notification.addButton(text="Turn Off",on_release=turnOffNoti)
                    notification.addButton(text="Watch Later",on_release=watchLater)
                    notification.send()
                case "1":
                    Notification(
                        title="New Photo",
                        message="Check out this image",
                        style=NotificationStyles.BIG_PICTURE,
                        big_picture_path=big_img_path
                    ).send()
                case "both_imgs":
                    # 5. Large Icon Image notification
                    notification = Notification(
                        title=title,
                        message=message,
                        style="both_imgs",
                        large_icon_path=large_icon_path,
                        big_picture_path=big_img_path
                    )
                    notification.send()
        except Exception as e:
            print(e, "Package Error 100")

if __name__ == '__main__':
    Laner().run()
