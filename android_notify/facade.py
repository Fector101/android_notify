"""Assists Notification Class with Args auto-complete: keeps sub class cleaner"""
from dataclasses import dataclass

@dataclass
class BaseNotification:
    """Encapsulator"""
    
    # Basic options
    title: str = ''
    message: str = ''
    style: str = 'simple'
    
    # Style specfic attributes
    big_picture_path: str = ''
    large_icon_path: str = ''
    progress_max_value: int = 100
    progress_current_value: int = 0
    body: str = ''
    
    # For Nofitication Functions
    identifer: str = ''
    callback: object = None
    
    # Advance Options
    channel_name: str = 'Default Channel'
    channel_id: str = 'default_channel'
    silent: bool = False
    app_icon: str = 'Defaults to package app icon'
