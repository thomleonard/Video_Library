from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
	"""
	string concatenation

	"toto"|addstr:"patate"
	"""
	return str(arg1) + str(arg2)

@register.tag(name='captureas')
def do_captureas(parser, token):
	"""
	Capture content to re-use throughout a template.
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