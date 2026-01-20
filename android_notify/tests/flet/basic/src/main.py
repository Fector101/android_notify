import flet as ft
import os,traceback

try:
    from core import send_notification
except Exception as e:
    print("Not on android")
    print("Error importing android_notify: {}".format(e))

md1 = """ """
i=0

def main(page: ft.Page): 
    page.scroll = ft.ScrollMode.ADAPTIVE
    mdObj=ft.Markdown(
            md1,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: page.launch_url(e.data),
        )
    def handle_click(style):
        if style == "big_text":
            send_notification(
                title="Big Text Example",
                message="This uses the BigTextStyle!",
                style="big_text",
                big_text="This is an expanded notification showing how much text can fit here."
            )
        elif style == "big_picture":
            send_notification(
                title="Big Picture Example",
                message="This uses the BigPictureStyle!",
                big_picture_path="assets/splash_android.png"
            )
        elif style == "large_icon":
            send_notification(
                title="Large Icon Example",
                message="This uses a Large Icon!",
                large_icon_path="assets/icon.png"
            )
        elif style == "both_imgs":
            send_notification(
                title="Both 'Large Icon' and 'Big Picture' Example",
                message="This uses a Both Imgs!",
                big_picture_path="assets/splash_android.png",
                large_icon_path="assets/icon.png"
            )
        elif style == "inbox":
            send_notification(
                title="Inbox Example",
                message="This uses the InboxStyle!",
                lines="Line 1\nLine 2\nLine 3"
            )
        else:
            send_notification(
                title="Simple Notification",
                message="This is a normal notification!"
            )

        page.snack_bar = ft.SnackBar(ft.Text(f"Sent: {style or 'default'}"))
        page.snack_bar.open = True
        page.update()

    def console(a):
        global md1,i
        i+=1
        print('Testing print visibility: ',i,'\n')
        try:
            with open(os.getenv("FLET_APP_CONSOLE"), "r") as f:
                md1 = f.read()
                mdObj.value=md1
        except Exception as e:
            mdObj.value=f"{e}, hello readddd me i'm Error"
        finally:
            mdObj.update()


    def send_basic(e):
        send_notification(title='Hello World',message='From android_notify',custom_app_icon_path=f'assets/icon.png')

    def request_permission(e):
        try:
            from core import asks_permission_if_needed
            asks_permission_if_needed()
        except Exception as e:
            print( f"pyjnius android_ import error: {traceback.format_exc()}"            )

    page.add(
        ft.OutlinedButton(
            "Request Permission if Needed",
            on_click=request_permission,
        ), ft.OutlinedButton(
            "Refresh Prints",
            on_click=console,
        )
    )
    page.add(
        ft.Text("🧪 Android Notify Test", size=25, weight=ft.FontWeight.BOLD),
        ft.Text("Click a button below to test the corresponding style.\n", size=16),

        ft.ElevatedButton("🔔 Simple Notification", on_click=lambda e: handle_click(None)),
        ft.ElevatedButton("🖼️ Big Picture Style", on_click=lambda e: handle_click("big_picture")),
        ft.ElevatedButton("🧩 Large Icon Style", on_click=lambda e: handle_click("large_icon")),
        ft.ElevatedButton("# Both imgs", on_click=lambda e: handle_click("both_imgs")),
        ft.ElevatedButton("📝 Big Text Style", on_click=lambda e: handle_click("big_text")),
        ft.ElevatedButton("📋 Inbox Style", on_click=lambda e: handle_click("inbox")),
    )
    btn = ft.ElevatedButton("Click me!", on_click=send_basic)
    page.add(btn)
    page.add(mdObj)
ft.app(main)

