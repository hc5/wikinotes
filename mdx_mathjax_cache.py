# encoding: utf-8
import markdown
from markdown import etree
import re
import hashlib
import os
import sys
import traceback
import codecs

cache_dir = "wiki/cache/mathjax/"
engine = ""
to_cache = {}
class MJCPreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		processed_lines=""
		return lines
	
class MJCPostprocessor(markdown.postprocessors.Postprocessor):
	
	def run(self, text):
		modified = text
		for cache in to_cache:
			modified = modified.replace(cache,to_cache[cache])
		modified = "\n".join([modified,cache_script])
		return modified

class MJCPattern(markdown.inlinepatterns.Pattern):
	config = {}
	def __init__(self):
		markdown.inlinepatterns.Pattern.__init__(self, r'(?<!\\)(\$\$?)(.+?)\2')
		
	def load(self, exp,type):
		parsed = ""
		s=""
		final_dir = cache_dir+type+"/WebKit/"
		try:
			os.makedirs(final_dir)
		except OSError, e:
			pass
		try:
			cache_file = final_dir+exp
			#cache = open(cache_file,mode="r+")
			cache = codecs.open(cache_file,encoding='utf-8',mode='r+')
			parsed = "".join(cache.readlines())
			return parsed
		except:
			print 'error while trying to read cache'
			traceback.print_exc(file=sys.stdout)
			return None
		
		
	
	def handleMatch(self, m):
		h = hashlib.sha256()
		h.update(m.group(3))
		exp_hash = h.hexdigest()
		type = ''
		if m.group(2)=='$$':
			type = 'block'
		if m.group(2)=='$':
			type = 'inline'
		cache = self.load(exp_hash,type)
		if(cache):
			to_cache[exp_hash] = cache
			return markdown.AtomicString(exp_hash)
		else:
			print "not using cache"
			return markdown.AtomicString(m.group(2) + m.group(3) + m.group(2))
	
	
class MJCExtension(markdown.Extension):
	def __init__(self, configs):
		self.config = {'user_agent':"WebKit"}
		for key in configs:
			self.setConfig(key, configs[key])


	def extendMarkdown(self, md, md_globals):
		mjcext = MJCPreprocessor(md)
		user_agent = self.config['user_agent']
		engines = ["WebKit","Firefox","Trident","Presto"]
		print user_agent
		for e in engines:
			if e in user_agent:
				engine = e
		print engine
		md.preprocessors.add("mjc", mjcext, "_end")
		md.inlinePatterns.add("mjc",MJCPattern(),"<escape")
		md.postprocessors.add("mjc",MJCPostprocessor(),"_end")
	
def makeExtension(configs={}):
	return MJCExtension(configs=configs)




cache_script = """
<style>
.MathJax_Display {
    display: block;
    margin: 1em 0;
    position: relative;
    text-align: center;
    width: 100%;
}
.MathJax .merror {
    border: 1px solid;
    color: black;
    font-family: serif;
    font-size: 80%;
    padding: 1px 3px;
    text-align: left;
}
.MathJax_Preview {
    color: #888888;
}
#MathJax_Tooltip {
    background-color: infobackground;
    border: 1px solid black;
    box-shadow: 2px 2px 5px #AAAAAA;
    color: infotext;
    display: none;
    height: auto;
    left: 0;
    padding: 3px 4px;
    position: absolute;
    top: 0;
    width: auto;
}
.MathJax {
    border: 0 none;
    direction: ltr;
    display: inline;
    float: none;
    font-family: serif;
    font-size: 100%;
    font-size-adjust: none;
    font-style: normal;
    font-weight: normal;
    letter-spacing: normal;
    line-height: normal;
    margin: 0;
    padding: 0;
    text-align: left;
    text-indent: 0;
    text-transform: none;
    white-space: nowrap;
    word-spacing: normal;
    word-wrap: normal;
}
.MathJax img, .MathJax nobr, .MathJax a {
    border: 0 none;
    line-height: normal;
    margin: 0;
    max-height: none;
    max-width: none;
    padding: 0;
    text-decoration: none;
    vertical-align: 0;
}
img.MathJax_strut {
    border: 0 none !important;
    margin: 0 !important;
    padding: 0 !important;
    vertical-align: 0 !important;
}
.MathJax span {
    border: 0 none;
    display: inline;
    line-height: normal;
    margin: 0;
    padding: 0;
    position: static;
    text-decoration: none;
    vertical-align: 0;
}
.MathJax nobr {
    white-space: nowrap;
}
.MathJax img {
    display: inline !important;
}
.MathJax_Processing {
    height: 0;
    overflow: hidden;
    position: fixed;
    visibility: hidden;
    width: 0;
}
.MathJax .MathJax_HitBox {
    cursor: text;
}
#MathJax_Tooltip * {
    background: none repeat scroll 0 0 transparent;
    filter: none;
}
@font-face {
    font-family: "MathJax_Main";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Main-Regular.otf");
}
@font-face {
    font-family: "MathJax_Main";
    font-weight: bold;
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Main-Bold.otf");
}
@font-face {
    font-family: "MathJax_Main";
    font-style: italic;
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Main-Italic.otf");
}
@font-face {
    font-family: "MathJax_Math";
    font-style: italic;
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Math-Italic.otf");
}
@font-face {
    font-family: "MathJax_Caligraphic";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Caligraphic-Regular.otf");
}
@font-face {
    font-family: "MathJax_Size1";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Size1-Regular.otf");
}
@font-face {
    font-family: "MathJax_Size2";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Size2-Regular.otf");
}
@font-face {
    font-family: "MathJax_Size3";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Size3-Regular.otf");
}
@font-face {
    font-family: "MathJax_Size4";
    src: url("http://cdn.mathjax.org/mathjax/latest/fonts/HTML-CSS/TeX/otf/MathJax_Size4-Regular.otf");
}
#MathJax_getScales {
    font-family: MathJax_Main,MathJax_Size1,MathJax_AMS;
}
.MathJax .math span {
    font-family: MathJax_Main,MathJax_Size1,MathJax_AMS;
}

</style>
<script type="text/javascript">
 	function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
	MathJax.Hub.Register.MessageHook("New Math",function (message) {
		var script = $(MathJax.Hub.getJaxFor(message[1]).SourceElement());
		if(script.attr("type") == "math/mml"){//can't cache
			return;
		}
		var type = "";
		var raw = script.html();
		var layoutEngine = "";
		engines = ["WebKit","Firefox","Trident","Presto"]
		for(var i = 0;i<engines.length;i++){
			if(navigator.userAgent.indexOf(engines[i])>-1)
				layoutEngine = engines[i]
		}
		var parsed = script.prev().clone();
		var html = parsed.wrap("<div>").parent().html();
		if (html.substring(0,"<div".length)=="<div"){
			type = "block";
		}
		if (html.substring(0,"<span".length)=="<span"){
			type = "inline";
		}
		
		var csrf_token = getCookie('csrftoken');
		$.post("/mathjax_cache",{
		'exp':raw,
		'parsed':html,
		'layout_engine':layoutEngine,
		'type':type,
		'csrfmiddlewaretoken':csrf_token
		},
		function(data){
		}
		);
  });
	</script>
"""