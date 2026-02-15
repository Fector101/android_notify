export const installation_code_buildozer = `# Add pyjnius so ensure it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependency (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core-ktx:1.15.0
android.enable_androidx = True
android.api = 35`
export const installation_code_buildozer_without_androidx = `requirements = python3, kivy, pyjnius, android-notify==1.60.10.dev0
 android.permissions = POST_NOTIFICATIONS
`
export const installation_code_flet = `[tool.flet.android]
dependencies = [
  "pyjnius","android-notify==1.60.10.dev0"
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true`
export const installation_code_pip = `pip install android-notify`
export const code = `from android_notify import Notification, NotificationHandler

# Create a simple notification
def send_notification(ans):
    Notification(
        title="Hello From Python",
        message="This is a basic notification."
    ).send()

NotificationHandler.asks_permission(send_notification)
`;