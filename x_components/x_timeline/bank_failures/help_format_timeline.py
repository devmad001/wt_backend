import os
import sys
import random
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Oct 15, 2023  Init



def help_add_colors(timeline_data,name_key,amount_key,date_key):
    ## Format timeline:
    #- main node view
    #- popup window view
    #- color of nodes
    #- position (debit/credit)
    
    ## Timeline data
    
    #[1] debit/credit colors or color by type
    
    ## Given jsonl, name_key, amount_key, date_key
    
    ## Color by name key
    
    ## Get list of unique names
    unique_names=[]
    for dd in timeline_data:
        if dd.get(name_key,'') not in unique_names and name_key:
            unique_names.append(dd.get(name_key,''))
    if unique_names==['']: unique_names=[] #patch
            
    ## Assign color to names
    #https://www.canva.com/colors/color-wheel/
    colors={}
    colors['orangeish']='#f3a45e'
    colors['blueish']='#677cc0' # purple: '#8e95d8'
    colors['greyish']='#d2d2d2' #same levels as above but no color
    colors['greenish']='#5ca36d'
    
    ascolors={}
    ## Name placement
    
    ## orange withdrawl
    for name in unique_names:
        for reg in ['debit','withdrawl','payment','asset']:
            if re.search(reg,name,flags=re.I):
                if not name in ascolors and 'orangeish' in colors:
                    ascolors[name]=colors.pop('orangeish')
    ## blue deposit    
    for name in unique_names:
        for reg in ['deposit','credit','liability']:
            if re.search(reg,name,flags=re.I):
                if not name in ascolors and 'blueish' in colors:
                    ascolors[name]=colors.pop('blueish')
                    
    ## Random assign (only 3 unique or others?)
    for name in unique_names:
        if name not in ascolors:
            # If there are remaining colors, choose randomly, otherwise default to grey
            chosen_color = random.choice(list(colors.keys())) if colors else 'greyish'
            ascolors[name] = colors.pop(chosen_color, '#d2d2d2')
            
    print ("Unique names: "+str(unique_names))
    print ("[debug] colors assigned: "+str(ascolors))
    if timeline_data: print ("[debug] full "+str(timeline_data[0]))

    for record in timeline_data:
        if record.get(name_key,'') in ascolors:
            record['color']=ascolors[record.get(name_key,'')]

    return timeline_data

def dev1():
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""

"""
