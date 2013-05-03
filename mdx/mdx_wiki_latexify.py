import re
import markdown
from markdown.util import etree
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import LatexFormatter
import hashlib
from urllib import urlretrieve
from os import makedirs
from os.path import isfile

doc_template = """
\documentclass{article}
\usepackage{enumerate}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{array}
\usepackage{framed}
\usepackage[T1]{fontenc}
\usepackage{listings}
\usepackage{color,colortbl}
\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}
\usepackage[urlcolor=linkcolour,bookmarks=true]{hyperref}
\usepackage{tabularx}
\usepackage[utf8]{inputenc}
\usepackage{titlesec}
\usepackage{graphicx}
\usepackage{calc}
\usepackage{fontspec}
\usepackage{fancyhdr}
\usepackage{setspace}

\setlength{\\parindent}{0in}
\setlength{\\parskip}{0.2in}
\setmonofont{Consolas}
\setmainfont[SizeFeatures={Size={12}}]{Adobe Garamond Pro}
\onehalfspacing
\\newfontfamily\\headingfont{TradeGothic LT Bold}
\usepackage[margin=0.8in]{geometry}

%% the colors of the wind

\definecolor{numbering}{HTML}{CCCCCC} % section numbering
\definecolor{th-none}{HTML}{42A7C5}
\definecolor{tbody-none}{HTML}{FFFFFF}
\definecolor{th-autumn}{HTML}{FAA937}
\definecolor{tbody-autumn}{HTML}{FCFFE5}
\definecolor{th-clear}{HTML}{FFFFFF}
\definecolor{tbody-clear}{HTML}{FFFFFF}
\definecolor{th-fresh}{HTML}{62BC62}
\definecolor{tbody-fresh}{HTML}{FFFFFF}
\definecolor{th-iris}{HTML}{9466c6}
\definecolor{tbody-iris}{HTML}{FAE6F6}
\definecolor{th-ribbon}{HTML}{c83025}
\definecolor{tbody-ribbon}{HTML}{FFFFFF}
\definecolor{th-lights}{HTML}{B9CFFE}
\definecolor{tbody-lights}{HTML}{F3F5FB}
\definecolor{white}{HTML}{FEFEFE} % FFFFFF turns the text black for some reason???
\definecolor{shadecolor}{HTML}{FAFAFA}
\definecolor{framecolor}{HTML}{999999}
\definecolor{highlight}{HTML}{E5FAFF}
\definecolor{linkcolour}{RGB}{49,150,180}
\definecolor{keyword}{HTML}{073642}
\definecolor{string}{HTML}{585545}
\definecolor{identifier}{HTML}{CA3349}
\definecolor{comment}{HTML}{006677}
\definecolor{linenos}{HTML}{D3D7CC} % line numbers in code blocks
\definecolor{dark}{HTML}{303030}
\definecolor{quotebar}{HTML}{DDDDDD}
\definecolor{numbers}{HTML}{FF6600} % number literals in code

%% Pretty section titles

\\titleformat{\\section}
{\\Huge\\bfseries\\raggedright\\headingfont}{}{0em}{}[{}]
\\titleformat{\\subsection}
{\\LARGE\\bfseries\\raggedright\\headingfont}{}{0em}{}[{}]
\\titleformat{\\subsubsection}
{\\Large\\bfseries\\raggedright\\headingfont}{}{0em}{}[{}]
\\titlespacing*{\\section} {0pt}{50pt}{10pt}
\\titlespacing*{\\subsection} {0pt}{40pt}{10pt}
\\titlespacing*{\\subsubsection} {0pt}{30pt}{10pt}
\\pagestyle{empty} 
\\setcounter{secnumdepth}{5}


%% Smart column sizing

\\renewcommand{\\arraystretch}{2.5}
\\newcolumntype{+}{>{\\global\\let\\currentrowstyle\\relax}}
\\newcolumntype{^}{>{\\currentrowstyle}}
\\newcommand{\\rowstyle}[1]{\\gdef\\currentrowstyle{#1}%
#1\\ignorespaces
}
\\newcolumntype{R}[1]{>{\\hfill}m{#1}}
\\newcolumntype{C}[1]{>{\\centering\\let\\newline\\\\\\arraybackslash\\hspace{0pt}}m{#1}}

%% Pretty quote bars

\\renewenvironment{leftbar}{%
  \\def\\FrameCommand{\\textcolor{quotebar}{\\vrule width 3pt} \\hspace{10pt}}%
  \\MakeFramed {\\advance\hsize-\\width \\FrameRestore}}%
{\\endMakeFramed}

%% smart image sizing

\\newlength{\\imgwidth}
\\newcommand\\scalegraphics[1]{%   
    \\settowidth{\\imgwidth}{\\includegraphics{#1}}%
    \\setlength{\\imgwidth}{\\minof{\\imgwidth}{\\textwidth}}%
    \\includegraphics[width=\\imgwidth]{#1}%
}



\\newfontfamily{\\thfont}[Color=white]{Helvetica LT Bold}

%% Less ugly code listings

\\lstset{
basicstyle=\\ttfamily,
inputencoding=utf8,
stringstyle=\\color{string},
commentstyle=\\color{comment}\\itshape,
identifierstyle=\\color{identifier}, 
keywordstyle=\\color{keyword}\\bfseries,
showlines=true,
showstringspaces=false,
numberstyle=\\color{linenos}\\bfseries,
numbers=left,
frame=tb,
backgroundcolor=\\color{shadecolor},
rulecolor=\\color{framecolor},
framesep=10pt,
framerule=0.7pt,
aboveskip=20pt,
belowskip=20pt,
breaklines=true
}
\\lstset{literate=%
    *{0}{{{\color{numbers}0}}}1
    {1}{{{\color{numbers}1}}}1
    {2}{{{\color{numbers}2}}}1
    {3}{{{\color{numbers}3}}}1
    {4}{{{\color{numbers}4}}}1
    {5}{{{\color{numbers}5}}}1
    {6}{{{\color{numbers}6}}}1
    {7}{{{\color{numbers}7}}}1
    {8}{{{\color{numbers}8}}}1
    {9}{{{\color{numbers}9}}}1
}

%% Additional languages for listing to match up to pygments, missing css, nginx

\\lstdefinelanguage{mips}%
{morekeywords=[1]{abs,abs.d,abs.ps,abs.s,add,add.d,add.ps,add.s,addi,addiu,addu,alnv.ps,and,%
  andi,b,bal,bc1f,bc1fl,bc1t,bc1tl,bc2f,bc2fl,bc2t,bc2tl,beq,beql,beqz,bge,bgeu,bgez,%
  bgezal,bgezall,bgezl,bgt,bgtu,bgtz,bgtzl,ble,bleu,blez,blezl,blt,bltu,bltz,bltzal,%
  bltzall,bltzl,bne,bnel,bnez,break,c.eq.d,c.eq.ps,c.eq.s,c.f.d,c.f.ps,c.f.s,c.le.d,%
  c.le.ps,c.le.s,c.lt.d,c.lt.ps,c.lt.s,c.nge.d,c.nge.ps,c.nge.s,c.ngl.d,c.ngl.ps,%
  c.ngl.s,c.ngle.d,c.ngle.ps,c.ngle.s,c.ngt.d,c.ngt.ps,c.ngt.s,c.ole.d,c.ole.ps,c.ole.s,%
  c.olt.d,c.olt.ps,c.olt.s,c.seq.d,c.seq.ps,c.seq.s,c.sf.d,c.sf.ps,c.sf.s,c.ueq.d,c.ueq.ps,%
  c.ueq.s,c.ule.d,c.ule.ps,c.ule.s,c.ult.d,c.ult.ps,c.ult.s,c.un.d,c.un.ps,c.un.s,cache,%
  ceil.l.d,ceil.l.s,ceil.w.d,ceil.w.s,cfc0,cfc1,cfc2,clo,clz,cop2,ctc0,ctc1,ctc2,cvt.d.l,%
  cvt.d.s,cvt.d.w,cvt.l.d,cvt.l.s,cvt.ps.s,cvt.s.d,cvt.s.l,cvt.s.pl,cvt.s.pu,cvt.s.w,%
  cvt.w.d,cvt.w.s,deret,di,div,div.d,div.s,divu,ehb,ei,eret,ext,floor.l.d,floor.l.s,floor.w.d,%
  floor.w.s,ins,j,jal,jalr,jalr.hb,jr,jr.hb,l.d,l.s,la,lb,lbu,ld,ldc1,ldc2,ldxc1,lh,lhu,li,li.d,%
  li.s,ll,lui,luxc1,lw,lwc1,lwc2,lwl,lwr,lwxc1,madd,madd.d,madd.ps,madd.s,maddu,mfc0,mfc1,%
  mfc1.d,mfc2,mfhc1,mfhc2,mfhi,mflo,mov.d,mov.ps,mov.s,move,movf,movf.d,movf.ps,movf.s,movn,%
  movn.d,movn.ps,movn.s,movt,movt.d,movt.ps,movt.s,movz,movz.d,movz.ps,movz.s,msub,msub.d,msub.ps,%
  msub.s,msubu,mtc0,mtc1,mtc1.d,mtc2,mthc1,mthc2,mthi,mtlo,mul,mul.d,mul.ps,mul.s,mulo,%
  mulou,mult,multu,neg,neg.d,neg.ps,neg.s,negu,nmadd.d,nmadd.ps,nmadd.s,nmsub.d,nmsub.ps,%
  nmsub.s,nop,nor,not,or,ori,pll.ps,plu.ps,pref,prefx,pul.ps,puu.ps,rdhwr,rdpgpr,recip.d,%
  recip.s,rem,remu,rfe,rol,ror,rotr,rotrv,round.l.d,round.l.s,round.w.d,round.w.s,rsqrt.d,%
  rsqrt.s,s.d,s.s,sb,sc,sd,sdbbp,sdc1,sdc2,sdxc1,seb,seh,seq,sge,sgeu,sgt,sgtu,sh,sle,sleu,%
  sll,sllv,slt,slti,sltiu,sltu,sne,sqrt.d,sqrt.s,sra,srav,srl,srlv,ssnop,sub,sub.d,sub.ps,%
  sub.s,subu,suxc1,sw,swc1,swc2,swl,swr,swxc1,sync,synci,syscall,teq,teqi,tge,tgei,tgeiu,tgeu,%
  tlbp,tlbr,tlbwi,tlbwr,tlt,tlti,tltiu,tltu,tne,tnei,trunc.l.d,trunc.l.s,trunc.w.d,trunc.w.s,ulh,%
  ulhu,ulw,ush,usw,wrpgpr,wsbh,xor,xori},%
morekeywords=[2]{.alias,.align,.ascii,.asciiz,.asm0,.bgnb,.byte,.comm,.data,.double,.end,.endb,%
  .endr,.ent,.err,.extern,.file,.float,.fmask,.frame,.globl,.half,.kdata,.ktext,.lab,.lcomm,%
  .livereg,.loc,.mask,.noalias,.option,.rdata,.repeat,.sdata,.set,.space,.struct,.text,%
  .verstamp,.vreg,.word},%
comment=[l]\\#%
}[keywords,comments,strings]

\\lstdefinelanguage{javascript}{
  keywords={typeof, new, true, false, catch, function, return, null, catch, switch, var, if, in, while, do, else, case, break},
  morekeywords={class, export, boolean, throw, implements, import, this},
  sensitive=false,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]"
}

\\lstdefinelanguage{sml}
{morekeywords={val,let,in,end,rec,fn,fun,list,int,bool,real,char,unit,string,signature,datatype,of,and,type,option,SOME,NONE,sig,structure,where,if,then,else},
sensitive=false,
morecomment=[s]{(*}{*)},
morestring=[b]"
}

\\lstdefinestyle{bash}{language=bash}
\\lstdefinestyle{c}{language=c}
\\lstdefinestyle{cpp}{language=c++}
\\lstdefinestyle{css}{language=html}
\\lstdefinestyle{gas}{language=mips}
\\lstdefinestyle{html}{language=html}
\\lstdefinestyle{html+php}{style=html, alsolanguage=php}
\\lstdefinestyle{java}{language=java}
\\lstdefinestyle{javascript}{language=javascript}
\\lstdefinestyle{makefile}{language=make, alsolanguage=bash}
\\lstdefinestyle{matlab}{language=matlab}
\\lstdefinestyle{nginx}{language=sql, alsolanguage=php}
\\lstdefinestyle{ocaml}{language=sml}
\\lstdefinestyle{sml}{language=sml}
\\lstdefinestyle{php}{language=php}
\\lstdefinestyle{python}{language=python}
\\lstdefinestyle{ruby}{language=ruby}
\\lstdefinestyle{sql}{language=sql}
\\lstdefinestyle{tex}{language=tex}
\\lstdefinestyle{perl}{language=perl}



"""

def unescape_html_entities(text):
	def repl(m):
		code = hex(int(m.group(1)))[2:].upper().zfill(4)
		return reserve_token("\\") + 'char"' + code
	text = text.encode("utf-8")
	out = text.replace('&amp;', reserve_token('&'))
	out = out.replace('&quot;', '"')

	# stupid pilcrows
	out = out.replace("&para;", "")

	c = re.compile("&#([0-9]+);")
	out = c.sub(repl, out)
	return out


# generate a token for a string, repeated application of this function to itself is guaranteed to give the same result
def reserve_token(s):
	m = hashlib.md5()
	m.update(s)
	return "[RESERVEDTOKEN%s]" % (m.hexdigest(),)


# reserve_token() is needed to make esc() and unescape_html_entities() idempotent
def esc(text, **kwargs):
	escape_dollar_sign = kwargs.get("escape_dollar_sign", False)
	if not text:
		return ""
	"""Escape latex reserved characters."""
	out = text
	if escape_dollar_sign:
		out = out.replace("$", reserve_token("$"))
	out = out.replace("\\", reserve_token("textbackslash"))
	out = out.replace(reserve_token("textbackslash") + "$", "\\$")
	out = out.replace("#", reserve_token("#"))
	out = out.replace("%", reserve_token("%"))
	out = out.replace("^", reserve_token("^"))
	out = out.replace("&", reserve_token("&"))
	out = out.replace("_", reserve_token("_"))
	out = out.replace("{" , reserve_token("{"))
	out = out.replace("}", reserve_token("}"))
	out = out.replace("~", "$\sim$")
	return out

def clear_reserve_tokens(text):
	out = text
	to_replace = {
				"\\":"\\",
				"textbackslash":"\\textbackslash{}",
				"#":"\#",
				"^":"\\textasciicircum{}",
				"%":"\%",
				"&":"\\&",
				"_":"\\_",
				"{":"\\{",
				"$":"\\$",
				"}":"\\}",
				"<":"<",
				">":">"
				}
	for key in to_replace:
		out = out.replace(reserve_token(key), to_replace[key])
	return out

class LatexifyExtension(markdown.Extension):
	def __init__ (self, configs):
		self.config = {}

	def extendMarkdown(self, md, md_globals):
		md.registerExtension(self)
		md.postprocessors.add("latexify", LatexifyPostprocessor(self), "_end")

class LatexifyPostprocessor(markdown.postprocessors.Postprocessor):
	domain = "http://beta.wikinotes.ca"
	temp_dir = "wiki/temp/"
	def __init__ (self, ext):
		self.ext = ext

	def run(self, text):


		doc = "<div>%s</div>" % (text,)
		doc = doc.replace("&para;", "")
		root = etree.XML(doc)
		latex = self.latexify_node(root)
		doc = """
%s
\\begin{document}

\\pagestyle{fancy}

\\renewcommand{\headrulewidth}{0pt}
\\cfoot{}
%s
\\end{document}
		""" % (doc_template,  latex)
		doc = unescape_html_entities(doc)
		encoded = doc.encode("utf-8")
		encoded = clear_reserve_tokens(encoded)
		return encoded

	# converts an xml node into a latex string representation of it
	def latexify_node(self, node, **kwargs):
		tagname = node.tag
		method = "parse_%s" % (tagname,)
		if node.get("id"):
			return "\\hypertarget{%s}{%s}" % (node.get("id"), getattr(self, method)(node, **kwargs))
		return getattr(self, method)(node, **kwargs)

	def parse_div(self, node, **kwargs):

		# disgard the table of contents
		if node.get("class") == "toc":
			return ""

		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return text


	def parse_pre(self, node, **kwargs):
		text = node.text or ""
		for child in node.getchildren():
			if child.tag == "code":
				kwargs["inline"] = False
				text += self.latexify_node(child, **kwargs)
			text += child.tail or ""
		text = "%s" % text
		return text

	def parse_td(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return text

	def parse_th(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return text

	def parse_table(self, node, **kwargs):
		theme = node.get("class") or "none"
		if theme not in ['clear', 'autumn', 'lights', 'ribbon', 'fresh', 'iris', 'column']: # lol
			theme = "none"
		head = node.getchildren()[0]
		body = node.getchildren()[1]
		align = []
		alignments = {"right-align":"R", "left-align":"m", "center-align":"C"}
		rows = []
		row = []
		max_cell_length = [0] * len(head.getchildren()[0].getchildren())
		for (i, col) in enumerate(head.getchildren()[0].getchildren()):
			content = self.latexify_node(col, **kwargs)
			row.append(content)
			if len(content) > max_cell_length[i]:
				max_cell_length[i] = len(content)
			align.append((alignments[col.get("class")] if col.get("class") else "m"))
		rows.append(" & ".join(row))
		for child in body.getchildren():
			row = []
			for (i, col) in enumerate(child.getchildren()):
				content = self.latexify_node(col, **kwargs)
				row.append(content)
				if len(content) > max_cell_length[i]:
					max_cell_length[i] = len(content)
			rows.append(" & ".join(row))

		table_width = 0.9 # we make the table 0.9 * \textwidth
		total_length = sum(max_cell_length)
		normalized_widths = [i * table_width / total_length for i in max_cell_length]

		column_desc = ["%s{%s\\textwidth}" % (c[0], c[1]) for c in zip(align, normalized_widths)]
		align_str = "|+%s|" % ("|^".join(column_desc),)
		data_str = """\\hline
\\rowcolor{th-%s} 
\\rowstyle{\\thfont}
%s\\\\\n\\hline
""" % (theme, ("\\\\\n\\hline\n\\rowcolor{tbody-%s}" % (theme,)).join(rows),)
		table = "\\mbox{ }\\\\\\begin{center}\\begin{tabular}{%s}\n\n%s\\end{tabular}\\end{center}" % (align_str, data_str)
		return table

	def parse_span(self, node, **kwargs):
		numbering = kwargs.get("numbering", False)
		text = ""

		# If it's a mathjax span, don't escape anything except percentage signs
		if node.text and node.text[0] == '$' and node.text[-1] == '$':
			text = node.text.replace("%", reserve_token("%"))
		else:
			text = esc(node.text)


		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail) or ""
		if numbering:
			text = "{\\texorpdfstring{\\color{numbering}{%s  }}{}}" % (text,)
		return text

	def parse_h2(self, node, **kwargs):
		return self.parse_header(node, 0)

	def parse_h3(self, node, **kwargs):
		return self.parse_header(node, 1)

	def parse_h4(self, node, **kwargs):
		return self.parse_header(node, 2)

	def parse_h5(self, node, **kwargs):
		return self.parse_header(node, 3)

	def parse_h6(self, node, **kwargs):
		return self.parse_header(node, 4)

	def parse_header(self, node, level, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			if child.tag == "span":
				kwargs['numbering'] = True
				text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		levels = ["\\section*{%s}", "\\subsection*{%s}", "\\subsubsection*{%s}", "\\paragraph*{%s}", "\\subparagraph*{%s}"]
		text = levels[level] % (text,)
		return text

	def parse_sub(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "$_{\\text{%s}}$" % (text,)

	def parse_sup(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "$^{\\text{%s}}$" % (text,)

	# need to download first
	def parse_img(self, node, **kwargs):
		src = node.get("src")
		if src[0] == "/":
			src = self.domain + href
		m = hashlib.md5()
		m.update(src)
		hash = m.hexdigest()
		outpath = self.temp_dir + hash + ".png"	# it turns out the extension doesn't matter, but is still required????
		try:
			makedirs(self.temp_dir)
		except OSError:
			pass
		if not isfile(outpath):
			urlretrieve(src, outpath)
		return "\\scalegraphics{%s}" % (outpath,)

	def parse_a(self, node, **kwargs):
		text = esc(node.text)
		href = node.get("href")
		if href[0] == "/":
			href = self.domain + href
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		if href[0] == "#":
			return '{\color{linkcolour} \\hyperlink{%s}{%s}}' % (esc(href[1:]), esc(text))
		return '{\color{linkcolour} \\href{%s}{%s}}' % (esc(href), esc(text))

	def parse_p(self, node, **kwargs):
		not_paragraph = kwargs.get("not_p", False)
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		if not_paragraph:
			return text
		return "\\par\n %s" % (text,)

	def parse_strong(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "{\\bf %s}" % (text,)

	def parse_em(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "{\\it %s}" % (text,)

	def parse_br(self, node, **kwargs):
		return "\\mbox{ }\\\\\n"

	def parse_ul(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\begin{itemize}%s\\end{itemize}" % (text,)

	def parse_li(self, node, **kwargs):
		text = esc(node.text)
		kwargs["not_p"] = True
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\item %s" % (text,)

	def parse_ol(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\begin{enumerate}[1.]%s\\end{enumerate}" % (text,)

	def parse_blockquote(self, node, **kwargs):
		text = esc(node.text)
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\begin{leftbar}\n%s\n\\end{leftbar}" % (text,)

	def parse_hr(self, node, **kwargs):
		return "\n\\noindent\\makebox[\\linewidth]{\\rule{\\textwidth}{0.6pt}}\\\\\n"


	def parse_dl(self, node, **kwargs):
		text = esc(node.text)
		kwargs["not_p"] = True
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\begin{description}\n%s\n\\end{description}" % (text,)

	def parse_dt(self, node, **kwargs):
		text = esc(node.text)
		kwargs["not_p"] = True
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "\\item[%s] \\hfill \\\\" % (text,)

	def parse_dd(self, node, **kwargs):
		text = esc(node.text)
		kwargs["not_p"] = True
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += esc(child.tail)
		return "%s \\\\" % (text,)

	def parse_code(self, node, **kwargs):
		inline = kwargs.get("inline", True)
		text = node.text if node.text else ""
		for child in node.getchildren():
			text += self.latexify_node(child, **kwargs)
			text += child.tail or ""

		if inline:
			text = "\colorbox{highlight}{\\texttt{%s}}" % (esc(text, escape_dollar_sign=True),)

		else:
			lines = text.splitlines()

			lang = None
			linenos = False
			if node.get("class"):
				lang = node.get("class")

			else:
				c = re.compile(r'''
					(?:(?:::+)|(?P<shebang>[#]!))	# Shebang or 2 or more colons.
					(?P<path>(?:/\w+)*[/ ])?		# Zero or 1 path
					(?P<lang>[\w+-]*)			   # The language
					''', re.VERBOSE)
				first = lines.pop(0)
				m = c.search(first)
				if m:
					# we have a match
					try:
						lang = m.group('lang').lower()
					except IndexError:
						lang = None
					#print "TEXT:\n-----------------\n%s\n----------------------\nlang: %s"%(text,lang)
					if m.group('path'):
						# path exists - restore first line
						lines.insert(0, first)
					if m.group('shebang'):
						# shebang exists - use line numbers
						linenos = True
				else:
					# No match
					lines.insert(0, first)
			text = "\n".join(lines)
			lang = "java"
			if lang:
				text = "\\begin{lstlisting}[style=%s]\n%s\\end{lstlisting}" % (lang, text)
			else:
				text = "\\begin{lstlisting}[identifierstyle=\\color{dark}]\n%s\\end{lstlisting}" % text

			# If the block of code is shorter than 25 lines, we force the entire block to be on
			# its own page because it looks bad split up
			if len(lines) < 25:
				text = "\\mbox{ }\\\\\n\\begin{minipage}{\\linewidth}%s\\end{minipage}\\\\\n" % text
		return text

def makeExtension(configs=[]):
	return LatexifyExtension(configs=configs)
