import flet as ft
import os,traceback


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
    def console(a):
        global md1
        try:
            with open(os.getenv("FLET_APP_CONSOLE"), "r") as f:
                md1 = f.read()
                mdObj.value=md1
        except Exception as e:
            print(e,"hello readddd it's me")
            mdObj.value=f"{e}, hello readddd it's me"
        finally:
            mdObj.update()

    def send_basic(e):
        
        try:
            from core import send_notification
            send_notification(title='Hello World',message='From android_notify',custom_app_icon_path=f'assets/icon.png')
        except Exception as e:
            print("Error importing android_notify: {}".format(e))
    
    def log_stuff(e):
        global i
        i+=1
        print('Testing print visiblity: ',i,'\n')
        console(None)

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
        ), ft.OutlinedButton(
            "Testing print visiblity",
            on_click=log_stuff,
        )
    )
    btn = ft.ElevatedButton("Click me!", on_click=send_basic)
    page.add(btn)
    page.add(mdObj)

ft.app(main)
