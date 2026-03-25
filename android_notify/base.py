"""Assists Notification Class with Args keeps subclass cleaner"""
from dataclasses import dataclass, fields
import difflib
from .styles import NotificationStyles
# For Dev when creating new attr use have to set type for validate_args to work

@dataclass
class BaseNotification:
    """Encapsulation"""

    # Basic options
    title: str = ''
    message: str = ''

    # Style-specific attributes
    progress_max_value: int = 0
    progress_current_value: float = 0.0 # Also Takes in Ints

    # Notification Functions
    name: str = ''
    callback: object = None

    # Advanced Options
    id: int = 0
    app_icon: str = 'Defaults to package app icon'

    # Channel related
    channel_name: str = 'Default Channel'
    """User visible channel name"""
    channel_id: str = 'default_channel'
    """Used to reference notification channel"""

    silent: bool = False

    # Custom Notification Attrs
    title_color: str = ''
    message_color: str = ''

    def __init__(self, **kwargs):
        """Custom init to handle validation before dataclass assigns values"""

        # Validate provided arguments
        self.validate_args(kwargs)

        # Assign validated values using the normal dataclass behavior
        for field_ in fields(self):
            field_name = field_.name
            setattr(self, field_name, kwargs.get(field_name, getattr(self, field_name)))

    def validate_args(self, inputted_kwargs):
        """Check for unexpected arguments and suggest corrections before Python validation"""
        default_fields =  {field.name : field.type for field in fields(self)} #{'title': <class 'str'>, 'message': <class 'str'>,...}
        allowed_fields_keys = set(default_fields.keys())

        # Identify invalid arguments
        invalid_args = set(inputted_kwargs) - allowed_fields_keys
        if invalid_args:
            suggestions = []
            for arg in invalid_args:
                closest_match = difflib.get_close_matches(arg, allowed_fields_keys, n=1, cutoff=0.6)
                if closest_match:
                    suggestions.append(f"* '{arg}' is invalid -> Did you mean '{closest_match[0]}'?")
                else:
                    suggestions.append(f"* '{arg}' is not a valid argument.")

            suggestion_text = '\n'.join(suggestions)
            raise ValueError(f"Invalid arguments provided:\n{suggestion_text}")

        # Validating types
        for each_arg in inputted_kwargs.keys():
            expected_type = default_fields[each_arg]
            actual_value = inputted_kwargs[each_arg]

            # Allow both int and float for progress_current_value
            if each_arg == "progress_current_value":
                if not isinstance(actual_value, (int, float)):
                    raise TypeError(f"Expected '{each_arg}' to be int or float, got {type(actual_value)} instead.")
            else:
                if not isinstance(actual_value, expected_type):
                    raise TypeError(f"Expected '{each_arg}' to be {expected_type}, got {type(actual_value)} instead.")
