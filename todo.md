# TODO

In Version 1.57 make it this way

Instance
- . add_progress_bar(value,max)
- . set_progress_bar(value)
- .add_big_pcture()
- .add_large_icon()
- .add_line()
- .big_text_style()
Wayy Better

From Version 2.0 Maybe Remove style attribute


Small icon: required; set using setSmallIcon().
App name: provided by the system.
Time stamp: provided by the system, but you can override it using setWhen() or hide it using setShowWhen(false).
Large icon: optional; usually used only for contact photos. Don't use it for your app icon. Set using setLargeIcon().
Title: optional; set using setContentTitle().
Text: optional; set using setContentText().

importance attr
The possible importance levels and the associated notification behaviors are the following:

    Urgent: makes a sound and appears as a heads-up notification.

    High: makes a sound.

    Medium: makes no sound.

    Low: makes no sound and doesn't appear in the status bar.


createNotificationChannel(name='Default channel',id='default_channel',importance='high',description='')
 // Create the NotificationChannel.
    val name = getString(R.string.channel_name)
    val descriptionText = getString(R.string.channel_description)
    val importance = NotificationManager.IMPORTANCE_DEFAULT
    val mChannel = NotificationChannel(CHANNEL_ID, name, importance)
    mChannel.description = descriptionText
    // Register the channel with the system. You can't change the importance
    // or other notification behaviors after this.
    val notificationManager = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.createNotificationChannel(mChannel)

val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
val id: String = "my_channel_01"
notificationManager.deleteNotificationChannel(id)




Read notification channel settings

Users can modify the settings for notification channels, including behaviors such as vibration and alert sound. If you want to know the settings a user applies to your notification channels, follow these steps:

    Get the NotificationChannel object by calling getNotificationChannel() or getNotificationChannels().

    Query specific channel settings such as getVibrationPattern(), getSound(), and getImportance().

If you detect a channel setting that you believe inhibits the intended behavior for your app, you can suggest that the user change it and provide an action to open the channel settings, as shown in the next section.




Open the notification channel settings

After you create a notification channel, you can't change the notification channel's visual and auditory behaviors programmatically. Only the user can change the channel behaviors from the system settings. To provide your users easy access to these notification settings, add an item in your app's settings UI that opens these system settings.

You can open the system settings for notification channels with an Intent that uses the ACTION_CHANNEL_NOTIFICATION_SETTINGS action.

For example, the following sample code shows how you can redirect a user to the settings for a notification channel:
Kotlin
Java

val intent = Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS).apply {
    putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
    putExtra(Settings.EXTRA_CHANNEL_ID, myNotificationChannel.getId())
}
startActivity(intent)

Notice that the intent requires two extras that specify your app's package name (also known as the application ID) and the channel to edit.




The notification priority, set by setPriority(). The priority determines how intrusive the notification is on Android 7.1 and earlier. For Android 8.0 and later, instead set the channel importance as shown in the next section.

For adding buttons
.addAction(