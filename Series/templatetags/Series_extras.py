from django import template
import datetime
from django.utils import timezone

register = template.Library()

@register.filter
def addstr(arg1, arg2):
    """
    string concatenation

    "toto"|addstr:"patate"
    """
    return str(arg1) + str(arg2)


@register.filter
def older_than(date, delta):
    """
    returns true or false depending on the delta between the date and now.    
    """
    if date is None:
        # if the date is None consider that it is not older than anything
        return False
    if isinstance(date, datetime.datetime):
        # if the date is a datetime
        time_delta = timezone.now() - date
    else:
        # if it is only a date
        time_delta = datetime.date.today() - date

    if time_delta < eval("datetime.timedelta(%s)" % delta):
        return False
    else:
        return True


@register.tag(name='captureas')
def do_captureas(parser, token):
    """
    Capture content to re-use throughout a template.

    {% captureas series_function %}
        {{ 'openTab(event, "'|addstr:season.number|addstr:'")' }}
    {% endcaptureas %}

    """
    try:
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("'captureas' node requires a variable name")
    nodelist = parser.parse(('endcaptureas', ))
    parser.delete_first_token()
    return CaptureasNode(nodelist, args)


class CaptureasNode(template.Node):

    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = output
        return ''