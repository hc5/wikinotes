# encoding: utf-8
import markdown
from markdown import etree
import re
import hashlib
import os
import sys
import traceback
import codecs
import base64

cache_dir = "wiki/cache/mathjax/"

class MJCPreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		processed_lines=""
		return lines
	
class MJCPostprocessor(markdown.postprocessors.Postprocessor):
	""" Replace placeholders with html entities. """
	def cacherepl(self,m):
		

		return "BLEEEEP"
	def run(self, text):
		"""
		
		what a shit piece of code
		
		parsed = ""
		buf = ""
		ptr = 0
		m = re.compile("(\$\$)([^\$]+)(\$\$)|(\$)([^\$]+)(\$)",re.MULTILINE)
		while(ptr<len(text)-5):
			cur_str = text[ptr:ptr+5]
			if cur_str == "<pre ":
				print "pre found"
				new_loc = text.index("</pre",ptr+5)
				parsed += text[ptr:new_loc]
				ptr = new_loc-1
				parsed +=m.sub(self.cacherepl,buf)
				buf = ""
			if cur_str == "<code":
				print "code found"
				new_loc = text.index("</code",ptr+5)
				parsed += text[ptr:new_loc]
				ptr = new_loc-1
				parsed +=m.sub(self.cacherepl,buf)
				buf = ""
			else:
				buf+=text[ptr]
			ptr+=1
		
		print "####\n"+parsed+"####\n"
		"""
		o = re.compile("<span([^/]*)/>",re.MULTILINE)
		modified = o.sub("<span\\1></span>",text)
		return modified

class MJCPattern(markdown.inlinepatterns.Pattern):
	config = {}
	def __init__(self):
		markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')
		
	def load(self, exp):
		parsed = ""
		s=""
		try:
			os.makedirs(cache_dir)
		except OSError, e:
			pass
		try:
			#return None
			cache_file = cache_dir+exp
			
			cache = codecs.open(cache_file,encoding='utf-8',mode='r+')
			parsed = "".join(cache.readlines())
			#parsed = base64.b64decode(parsed)
			o = re.compile("<img([^>]*)>",re.MULTILINE)
			modified = o.sub("<img\\1/>",parsed)
			cache.close()
			el = None
			if modified:
				s = unicode(modified)
				el = etree.fromstring(s)
			else:
				s =unicode(parsed)
				el = etree.fromstring(s)
			return el
		except:
			#print s
			#traceback.print_exc(file=sys.stdout)
			return None
	
	def handleMatch(self, m):
		h = hashlib.sha256()
		
		h.update(m.group(2)+m.group(3)+m.group(2))
		exp_hash = h.hexdigest()
		cache = self.load(exp_hash)
		if(cache):
			return cache
		else:
			print "Not using cache"
			return markdown.AtomicString(m.group(2) + m.group(3) + m.group(2))
		
		
		
	
	
class MJCExtension(markdown.Extension):
	def __init__(self, configs):
		self.config = { }

		for key, value in configs:
			self.setConfig(key, value)


	def extendMarkdown(self, md, md_globals):
		mjcext = MJCPreprocessor(md)
		mjcpattern = MJCPattern()
		mjcpattern.config = self.config
		md.preprocessors.add("mjc", mjcext, "_end")
		md.inlinePatterns.add("mjc",MJCPattern(),"<escape")
		md.postprocessors.add("mjc",MJCPostprocessor(),"_end")
	
def makeExtension(configs={}):
	return MJCExtension(configs=configs)
