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
