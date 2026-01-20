"""
Deprecated: v1.59
Use - (setLargeIcon, setBigPicture, setBigText and setLines) on Notification instance Instead
---
Contains Safe way to call Styles
"""

class NotificationStyles:
    """ Safely Adding Styles"""
        
    # v1.59+
    # Deprecated
    # setBigText == Notification(...,big_picture_path="...",style=NotificationStyles.BIG_TEXT)
    # setLargeIcon == Notification(...,large_icon_path="...",style=NotificationStyles.LARGE_ICON)
    # setBigPicture == Notification(...,body="...",style=NotificationStyles.BIG_PICTURE)
    # setLines == Notification(...,lines_txt="...",style=NotificationStyles.INBOX)
    # Set progress_current_value and progress_max_value for progress style

    # Use .refresh to apply any new changes after .send
    
    DEFAULT = "simple"
    PROGRESS = "progress"
    INBOX = "inbox"
    BIG_TEXT = "big_text"
    LARGE_ICON = "large_icon"
    BIG_PICTURE = "big_picture"
    BOTH_IMGS = "both_imgs"

    # MESSAGING = "messaging" # TODO
    # CUSTOM = "custom" # TODO v1.60
