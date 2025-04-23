export const installation_code_buildozer = `# Add pyjnius so ensure it's packaged with the build
requirements = python3, kivy, pyjnius, android-notify

# Add permission for notifications
android.permissions = POST_NOTIFICATIONS

# Required dependencies (write exactly as shown, no quotation marks)
android.gradle_dependencies = androidx.core:core:1.6.0, androidx.core:core-ktx:1.15.0
android.enable_androidx = True
android.api = 35`
export const installation_code_pip = `pip install android-notify`
export const code = `from android_notify import Notification

# Create a simple notification
notification = Notification(
    title="Hello From Python",
    message="This is a basic notification."
)
notification.send()`;