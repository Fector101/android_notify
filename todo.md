warning:
remove fallback icon for Flet and pydroid on android 14 below they don't enforce monochrome small icons 

fit: 
Intent listener for service now right pythactivity is getting returned 

1.60 
- Version code name: sounds, colours, services.
 
note to be in home page: 
- sounds
- colours
- vibrations
- services
- groups

- custom sounds, text and icon colours, service compatibility, notification groups, vibratand 10 Custom notifications

- 🟢 colours
- 🟡 service compatibility
- ⚫ notification groups
- ⚫ custom sounds
- 1/10 Custom notifications



# resources
### for vibration
https://stackoverflow.com/a/17066803/19961621

### important for implementing BroadcastReceiver probably v1.61 (so not to delay v1.60[stable] longer)
https://github.com/Guhan-SenSam/Android-Notification-in-Python

# Pseudos

## Vibration pseudo
### for default

```java
import android.os.Vibrator
Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);

// Vibrate for 400 milliseconds
v.vibrate(400);
```

### my implementation
```python
send(..., vibrate=400)
```

### Advanced stuff

```java
long[] pattern = {0, 100, 1000};

// Start without a delay
// Each element then alternates between vibrate, sleep, vibrate, sleep...
long[] pattern = {0, 100, 1000, 300, 200, 100, 500, 200, 100};

// The '0' here means to repeat indefinitely
// '0' is actually the index at which the pattern keeps repeating from (the start)
// To repeat the pattern from any other point, you could increase the index, e.g. '1'
// The '-1' here means to vibrate once, as '-1' is out of bounds in the pattern array.
v.vibrate(pattern, 0)
```

### my implementation

```python
# users will use `vibration_pattern` to change pattern when using `send`
Notification.vibration_pattern=[start,vibrate,sleep]
Notification.vibrate(ms=500,indefinite=False,pattern=[0,100,1000], start=0)
```


---
# to remove 
unused code
1. Remove `run_on_ui_thread` decorator where not necessary like these methods`addNotificationStyle`,`__apply_notification_image`.
But leave it in `asks_permission` where UI Thread is necessary


# important

when user denies twice Pop-up request no longer shows

```java
import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.provider.Settings;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.appcompat.app.AlertDialog;

// ... inside your Activity ...

public void checkNotificationPermissionStatus() {
    if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
        // Permission is denied
        if (ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.POST_NOTIFICATIONS)) {
            // User denied once, but not permanently.
            // You can still show a custom rationale UI and request permission again.
            showPermissionRationaleDialog();
        } else {
            // User permanently denied ("Don't ask again" was selected/implied by two denials).
            // The system popup will no longer show. Guide them to app settings.
            showSettingsDialog();
        }
    } else {
        // Permission is granted.
        // Proceed with your notification logic.
    }
}

private void showPermissionRationaleDialog() {
    // Show a custom dialog explaining why the app needs notifications
    new AlertDialog.Builder(this)
        .setTitle("Permission Needed")
        .setMessage("This app needs notification access to provide timely updates. Please grant permission.")
        .setPositiveButton("Grant", (dialog, which) -> {
            // Request the permission again
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.POST_NOTIFICATIONS}, NOTIFICATION_PERMISSION_REQUEST_CODE);
        })
        .setNegativeButton("Cancel", null)
        .show();
}

private void showSettingsDialog() {
    // Inform the user that they must enable permissions manually in settings
    new AlertDialog.Builder(this)
        .setTitle("Permission Required")
        .setMessage("Notifications are permanently disabled. Please enable them manually in the app settings.")
        .setPositiveButton("Go to Settings", (dialog, which) -> {
            Intent intent = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
            Uri uri = Uri.fromParts("package", getPackageName(), null);
            intent.setData(uri);
            startActivity(intent); // Directs user to app settings
        })
        .setNegativeButton("Cancel", null)
        .show();
}

// Don't forget to handle the onRequestPermissionsResult callback
@Override
public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults);
    if (requestCode == NOTIFICATION_PERMISSION_REQUEST_CODE) {
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            // Permission granted, proceed
        } else {
            // Permission denied, the checkNotificationPermissionStatus() method can be called here again
            // to determine the state and show the appropriate UI (rationale or settings dialog).
        }
    }
}
```