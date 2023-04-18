"""
https://docs.djangoproject.com/en/3.2/howto/custom-template-tags/
"""
import datetime
from django import template

register = template.Library()

@register.filter(name="datetime_formatted")
def datetime_formatted(dt):
    """ Template filter: Convert datetime object to string format """
    return dt.strftime("%I:%M%p - %a %d %b %Y")  # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

@register.filter
def format_time(s):
    """ Template filter: Convert number of seconds to formatted time """
    hr = int(int(s) / 3600)
    min = int(int(s) / 60)
    sec = int(int(s) % 60)
    return f"{hr:02d}:{min:02d}:{sec:02d}"

