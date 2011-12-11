
import markdown
from markdown import etree
import re

class ILEPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        processed_lines = ""
        line_buf = [{
                     'text':[],
                     'start':0,
                     'end':1
                     }]
        level_counters = [0,0,0,0]
        block_level_counters = [0,0,0,0]
        template = "<pre style='display:none' id='%s' name='%s'>%s</pre>"
        link_template = "<a href='javascript:void(0)' style='float: right;position:relative;top:-20px' class='editButton' id='%s' onclick='return editBlock(this)'>[edit]</a>"
        cur_level = 0
        line_number = 0
        for line in lines:
            if line == "[TOC]":
                processed_lines+=(line)+"\n"
                continue
            
            match = re.match(r"(#+) (.+)",line)
            link_holder = None
            #it's a header line
            if match:
                cur_level =  len(match.group(1))
                #the beginning of a block inside header, add an edit link
                link_id = "editlink-%d-%d" %(cur_level,level_counters[cur_level])
                link =  link_template % (link_id)
                level_counters[cur_level]+=1
                link_holder = self.markdown.htmlStash.store(link,safe=True)
                
                while cur_level< len(line_buf)+1:
                    if len(line_buf[-1]['text'])>0:
                        cur_block_level = len(line_buf)
                        cur_block = line_buf.pop()
                        block_id = "edittext-%d-%d"%(cur_block_level,
                                            block_level_counters[cur_block_level]
                                                                      
                                            )
                        line_range = "%d-%d" %(cur_block['start'],cur_block['end'])
                        code = template % (block_id,line_range
                                            , "\n".join(cur_block['text']))
                        block_level_counters[cur_block_level]+=1
                        placeholder = self.markdown.htmlStash.store(code,safe=True)
                        processed_lines+=placeholder+"\n"
                while len(line_buf) < cur_level:
                    line_buf.append({
                                     'text':[],
                     'start':line_number,
                     'end':line_number
                                     })
            #it's normal text
            
            else:
                #the beginning of a normal textblock, add an edit link
                if len(line_buf)==1 and len(line_buf[0]['text'])==0:
                    link_id = "editlink-%d-%d" %(1,level_counters[0])
                    link = link_template % (link_id)
                    link_holder = self.markdown.htmlStash.store(link,safe=True)
                    level_counters[1]+=1
            for level in line_buf:
                level['text'].append(line)
                level['end']+=1
            
            processed_lines+=(line)+"\n"
            if link_holder:
                processed_lines+=link_holder+"\n"
            
            line_number+=1
        while(len(line_buf)>0):
            if len(line_buf[-1])>0:
                cur_block_level = len(line_buf)
                cur_block = line_buf.pop()
                block_id = "edittext-%d-%d"%(cur_block_level,
                                    block_level_counters[cur_block_level]
                                                              
                                    )
                line_range = "%d-%d" %(cur_block['start'],cur_block['end'])
                code = template % (block_id,line_range
                                    , "\n".join(cur_block['text']))
                block_level_counters[cur_block_level]+=1
                placeholder = self.markdown.htmlStash.store(code,safe=True)
                processed_lines+=placeholder+"\n"
        return processed_lines.split("\n")
        
class ILEExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = { "slugify" : [self.slugify,
                            "Function to generate anchors based on header text-"
                            "Defaults to a built in slugify function."]
                        }

        for key, value in configs:
            self.setConfig(key, value)

    # This is exactly the same as Django's slugify
    def slugify(self, value):
        """ Slugify a string, to make it URL friendly. """
        import unicodedata
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
        value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
        return re.sub('[-\s]+','-',value)

    def extendMarkdown(self, md, md_globals):
        ileext = ILEPreprocessor(md)
        ileext.config = self.config
        md.preprocessors.add("ile", ileext, "_begin")
    
def makeExtension(configs={}):
    return ILEExtension(configs=configs)
