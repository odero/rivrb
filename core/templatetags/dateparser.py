from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone

from dateutil import parser

register = template.Library()


@register.filter
@stringfilter
def parse(value):
    datetime = parser.parse(value)
    # return timezone.localtime(datetime)
    return datetime
