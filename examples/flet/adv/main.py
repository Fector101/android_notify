import os,traceback,io,sys,unittest
import flet as ft
from contextlib import redirect_stdout
from android_notify.core import get_app_root_path,asks_permission_if_needed

md1=''
i=0
def main(page: ft.Page):
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.add(ft.Text("1111111111 Android Notify Test Results", size=24, weight=ft.FontWeight.BOLD))
    logs_path=os.path.join(get_app_root_path(),'last.txt')
    mdObj = ft.Markdown(
        md1,
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        on_tap_link=lambda e: page.launch_url(e.data),
    )
    page.add(mdObj)
    def console(a):
        global md1,i
        i+=1
        print('Testing print visibility: ',i,'\n')
        try:
            if os.getenv("FLET_APP_CONSOLE"):
                with open(os.getenv("FLET_APP_CONSOLE"), "r") as f:
                    md1 = f.read()
                    mdObj.value = md1

            with open(logs_path, 'r') as logf:
                mdObj.value = logf.read() + md1
        except Exception as err:
            mdObj.value = f"Error reading log: {err}"
        finally:
            mdObj.update()


    def send_basic(e):
        """Send a notification to verify android_notify works"""
        try:
            from android_notify import Notification
            Notification(title="Hello World", message="From android_notify").send()
        except Exception as err:
            mdObj.value = f"Notification error: {err}"
            mdObj.update()
    def asks_permission_if_needed_(e):
        asks_permission_if_needed()


    def ensure_tests_folder():
        try:
            base_path = get_app_root_path()
        except Exception:
            base_path = os.path.dirname(__file__)

        tests_path = os.path.join(base_path, "tests")
        os.makedirs(tests_path, exist_ok=True)
        init_file = os.path.join(tests_path, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, "w").close()

        page.add(ft.Text(f"{tests_path}", size=24, weight=ft.FontWeight.BOLD))
        return tests_path

    page.add(ft.Text("2222222222 Android Notify Test Results", size=24, weight=ft.FontWeight.BOLD))

    def run_tests(e=None):
        """Run tests and log results to /sdcard/flet_app_console.txt"""
        tests_path = ensure_tests_folder()

        try:
            with open(logs_path, "w") as logf, redirect_stdout(logf):
                loader = unittest.TestLoader()
                suite = loader.discover(start_dir=tests_path, pattern="test_*.py")
                print("Discovered tests:",suite.countTestCases())
                if suite.countTestCases() ==0:
                    print("No tests found")


                runner = unittest.TextTestRunner(stream=logf, verbosity=2)
                runner.run(suite)

            mdObj.value = f"Tests complete. Log saved to:\n`{logs_path}`"
        except Exception as err:
            mdObj.value = f"Test error:\n{traceback.format_exc()}"
        mdObj.update()
    def has_per(e=None):
        from android_notify import NotificationHandler
        print('permmm:',NotificationHandler.has_permission())
    page.add(
        ft.OutlinedButton("🔔 Send Basic Notification", on_click=send_basic),
        ft.OutlinedButton("🔁 Refresh Prints", on_click=console),
        ft.OutlinedButton("🧪 Run Tests", on_click=run_tests),
        ft.OutlinedButton("🧪permmm", on_click=has_per),
        ft.OutlinedButton("🧪asks_permission_if_needed", on_click=asks_permission_if_needed_),
    )

ft.app(main)
