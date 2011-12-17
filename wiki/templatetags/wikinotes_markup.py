from django import template
from django.utils.html import escape
import markdown
import time
import settings
import cProfile
from wiki.utils.mathjax_cache import MathjaxCache
register = template.Library()

md = markdown.Markdown(
	extensions=['subscript','inline_edit','superscript', 'urlize', 'nl2br', 'def_list', 'tables', 'mathjax', 'toc', 'footnotes'], 
	safe_mode='escape', 
	output_format='html4'
	)


# NEEDS TESTS
@register.filter()
def wikinotes_markdown(value,useragent=None):
	#if cache:
	#	md.registerExtension(mdx_mathjax_cache.makeExtension({'user_agent':useragent}))
	# Must reset it to clear the footnotes and maybe other stuff too
	md.reset()
	start_time = time.time()
	# Replace \$ with \\$ so that markdown doesn't do anything else to (in conjunction with mathjax's processEscapes)
	converted =  md.convert(value.replace("\\$", "\\\\$"))
	
	elapsed =  time.time() - start_time
	
	print "markdown conversion finished in %f" % elapsed
	if useragent:
		start_time = time.time()
		converted = MathjaxCache().check_cache(converted,useragent)
		elapsed =  time.time() - start_time
		print "mathjax caching finished in %f" % elapsed
	return converted
