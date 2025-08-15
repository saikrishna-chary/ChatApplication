# chat/templatetags/custom_filters.py

import os
from django import template

register = template.Library()

@register.filter
def basename(value):
    """Returns the base name of a file path."""
    return os.path.basename(value)
