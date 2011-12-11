
import markdown
from markdown import etree
import re

class ILEPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        processed_lines = ""
        #a block of src, start/end are the line numbers where it's located in the
        #source of the entire page, so we can merge together the changes
        line_buf = [{
                     'text':[],
                     'start':0,
                     'end':1
                     }]
        
        #used to give unique IDs to src blocks and edit links
        heading_level_counters = [0,0,0,0]
        block_level_counters = [0,0,0,0]
        #we wrap the src block around a pre tag so it doesn't get chewed up by MD or math
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
                
                #each level is a rank of headings
                # ## -> level 2, # -> level 1, no heading is equivalent to level 1
                cur_level =  len(match.group(1))
                
                # whenever we reach a heading, we add an edit link 
                # for all the src for that heading as well as its
                # subheadings
                
                #first number is the level of the heading, second is the counter of how
                #many headings there were of that same level. this way we will have no
                #conflicts in link id
                link_id = "editlink-%d-%d" %(cur_level,heading_level_counters[cur_level])
                link =  link_template % (link_id)
                heading_level_counters[cur_level]+=1
                
                #put the generated link html in the stash so it doesn't get chewed up by MD
                link_holder = self.markdown.htmlStash.store(link,safe=True)
                
                
                #if the current level of headings is lower or equal to the last level
                #it must mean the text under the previous heading has ended
                #e.g if the last heading was an h2, and this heading is an h1, that means
                #    the section of text under the h2 has ended and h1 is a start of a new section
                while cur_level< len(line_buf)+1:
                    cur_block = line_buf.pop()
                    if len(cur_block['text'])>0:
                        
                        cur_block_level = len(line_buf)
                        
                        
                        block_id = "edittext-%d-%d"%(cur_block_level,
                                            block_level_counters[cur_block_level]                                      
                                            )
                        
                        #add information about what lines the block of text spans in the original src
                        line_range = "%d-%d" %(cur_block['start'],cur_block['end'])
                        code = template % (block_id,line_range
                                            , "\n".join(cur_block['text']))
                        
                        #increase the counter for the block id generation, and store the block of text
                        #in the htmlstash so it doesn't get chewed up, and add the block of hidden src 
                        #onto the page
                        block_level_counters[cur_block_level]+=1
                        placeholder = self.markdown.htmlStash.store(code,safe=True)
                        processed_lines+=placeholder+"\n"
                        
                #if the current level of headings is higher, that means we're going from text under
                #h1 to text under h2 etc. we add another level onto our text stack to accomodate this
                #new level of headings
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
                    link_id = "editlink-%d-%d" %(1,heading_level_counters[0])
                    link = link_template % (link_id)
                    link_holder = self.markdown.htmlStash.store(link,safe=True)
                    heading_level_counters[1]+=1    
            #for every current level that we have, we must add text to it, because
            #the text of h1 contains the text of all the h2/h3 that are contained in it
            for level in line_buf:
                level['text'].append(line)
                level['end']+=1
            
            processed_lines+=(line)+"\n"
            
            #if we generated a link anywhere before, we add it onto the page
            if link_holder:
                processed_lines+=link_holder+"\n"
            
            line_number+=1
            
            
        #we reached the end of the page, but there are still text stored in our stack
        #we dump them all onto the page because they all ended
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
