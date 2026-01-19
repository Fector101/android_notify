"""For autocomplete Storing Reference to Available Methods"""
from typing import Literal

Importance = Literal['urgent', 'high', 'medium', 'low', 'none']
"""
    :argument urgent - Makes a sound and appears as a heads-up notification.
    
    :argument high - Makes a sound.
    
    :argument urgent - Makes no sound.
    
    :argument urgent - Makes no sound and doesn't appear in the status bar.
    
    :argument urgent - Makes no sound and doesn't in the status bar or shade.
"""

