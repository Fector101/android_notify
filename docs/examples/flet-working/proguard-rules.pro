-keep class com.flet.serious_python_android.** { *; }
-keepnames class * { *; }

# Keep any AndroidX Core class with 'Notification' in its name
-keep class androidx.core.**Notification** { *; }
-keep class androidx.core.**Notification**$* { *; }

# Used to request access to Notification
-keep class androidx.core.app.ActivityCompat { *; }