"""Contains Safe way to call Styles"""

class NotificationStyles:
    """ Safely Adding Styles"""
    DEFAULT = "simple"

    PROGRESS = "progress"
    INBOX = "inbox"
    
    # v1.59+
    # Deprecated
    # setBigText == Notification(...,big_picture_path="...",style=NotificationStyles.BIG_TEXT)
    # setLargeIcon == Notification(...,large_icon_path="...",style=NotificationStyles.LARGE_ICON)
    # setBigPicture == Notification(...,body="...",style=NotificationStyles.BIG_PICTURE)
    # Use .refresh to apply any new changes after .send
    BIG_TEXT = "big_text"
    LARGE_ICON = "large_icon"
    BIG_PICTURE = "big_picture"
    BOTH_IMGS = "both_imgs"

    # MESSAGING = "messaging" # TODO
    # CUSTOM = "custom" # TODO
