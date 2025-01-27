# On released - V1.51
[new-feature](online images new feature)
(fixes) 
(change)
## Runtime protection
Removed `FileNotFoundError` from package, if file is not found it'll be simply logged out to console with all files in app directory.
## 🥳 Online images [new feature]
You can finally use online images in your notifications
### Requirements :
1. In your buildozer file add `requirements=INTERNET`
2. All Online images to be added should be inputted with their full URL, that is should start with `https://` or `http://`
### Online Images Con
1. Online Images might take up to half a second to be added to notification depending on Internet speed
## Fixes
1. Big text style: `Notification` takes a new argument called `subject` this will be shown before the user clicks drop down btn to view large text `message`.
2. Types: most of `Notification` arguments are strings and return strings except `['progress_max_value','progress_current_value','callback','logs']`

### NotificationHandler [change]
No need to bind listener in your app, This will now be done automatically, You can unbind by using `NotificationHandler.unbindNotifyListener` 
