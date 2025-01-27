# Un-released - V1.51
this version hasn't been released because: 
- working on adding user-specified online images quietly to notification without pop-up.
- 🙃 plus electricity problem is hindering development
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
No need to bind listener in your app, This will now be done automatically, If you want to listen to notification clicks in your app You unbind using `NotificationHandler.unbindNotifyListener` 
