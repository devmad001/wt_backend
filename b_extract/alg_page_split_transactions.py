import os
import sys
import codecs
import json
import re
import ast
import random
import datetime

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_storage.ystorage.ystorage_handler import Storage_Helper
from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Sep 10, 2023  Init

"""
ADD CACHE FOR FUNCTIONAL TEST

"""


#** event gpt-4 won't split.
#1.  auto splitter (for transaction?)
#2   page splitter auto (for helping)

def alg_get_freq_of_cols_ORG(page,line_end='\n',separator=' '):
    ss={}
    ss['liners']=re.split(line_end,page)
    ss['count_liners']=len(ss['liners'])
    
    ## Count cols per liner
    lstats={}
    lstats['count_spaces']={}
    for liner in ss['liners']:
        lcount=liner.count(separator)
        lstats['count_spaces'][lcount]=lstats['count_spaces'].get(lcount,0)+1
        
    ## Most common space count
    most_common_space_count=sorted(lstats['count_spaces'].items(), key=lambda x: x[1], reverse=True)[0][0]
    frequency_of_most_common=sorted(lstats['count_spaces'].items(), key=lambda x: x[1], reverse=True)[0][1]
    frequency_of_most_common=frequency_of_most_common/ss['count_liners']

    #ie/ 86%
    print ("Most common space count: "+str(most_common_space_count)+" frequency: "+str(frequency_of_most_common)+" rows: "+str(ss['count_liners']))
    return most_common_space_count,frequency_of_most_common,ss['count_liners'],line_end,separator

def alg_get_freq_of_cols(page, line_end='\n', separator=' '):
    ss = {}
    ss['liners'] = re.split(line_end, page)
    ss['count_liners'] = len(ss['liners'])
    
    # Count cols per liner
    lstats = {}
    lstats['count_spaces'] = {}
    lstats['freq_num'] = {}
    lstats['freq_letter'] = {}
    
    for liner in ss['liners']:
        lcount = liner.count(separator)
        lstats['count_spaces'][lcount] = lstats['count_spaces'].get(lcount, 0) + 1
        
        # Calculate the frequency of numbers and letters
        count_num = len(re.findall(r'\d', liner))
        count_letter = len(re.findall(r'[a-zA-Z]', liner))
        
        if lcount not in lstats['freq_num']:
            lstats['freq_num'][lcount] = []
            lstats['freq_letter'][lcount] = []
        
        lstats['freq_num'][lcount].append(count_num / len(liner) if len(liner) != 0 else 0)
        lstats['freq_letter'][lcount].append(count_letter / len(liner) if len(liner) != 0 else 0)
        
    # Aggregate the frequencies
    aggregated_freq = {k: (sum(lstats['freq_num'][k]) / len(lstats['freq_num'][k]),
                         sum(lstats['freq_letter'][k]) / len(lstats['freq_letter'][k]))
                       for k in lstats['freq_num']}
    
    # Most common space count
    most_common_space_count = max(lstats['count_spaces'], key=lstats['count_spaces'].get)
    frequency_of_most_common = lstats['count_spaces'][most_common_space_count] / ss['count_liners']
    
    # Display results
    print("Most common space count:", most_common_space_count, "frequency:", frequency_of_most_common, "rows:", ss['count_liners'])
    print("Aggregated frequencies of numbers and letters per space count:", aggregated_freq)
    
    return most_common_space_count, frequency_of_most_common, ss['count_liners'], line_end, separator, aggregated_freq


def auto_parse_page(tt):
    continue=if_needed #but, gpt-4 with A-E mapping and verbose request should fix
    ## Look for general ways to reduce data scope
    
    print ("[] start in middle of page and walk up until find header")
    print ("[] optional get normal what data looks like ie/ numbers, chars etc")

    pagelets=[]
    
    most_common_space_count,frequency_of_most_common,row_count,line_end,separator,freqs=alg_get_freq_of_cols(tt)
    #ie/ 86%
    
    ## Candidate to auto divide?
    if frequency_of_most_common>0.70 and row_count>15:
        print ("[info] candidate to auto split page!  Assume column count: "+str(frequency_of_most_common))
        
        ## LOGIC:  duplicate headers?, assume split in half?!
        liners=re.split(line_end,tt)
        
        page_liners=[]
        target_split=round(row_count/2)
        
        ## Header:  assume various lengths until evens out to data
        assumed_header=[]
        for liner in liners:
            lcounts=liner.count(separator)
            
            freq_num=freqs[lcounts]
            print ("NUM: "+str(freq_num)+" at: "+str(liner))

            ## Does liner look like data or header?
            is_data=False
            if liner.count(separator)==most_common_space_count:
                is_data=True
            
            if len(page_liners)<target_split:
                ## Keep first page
                page_liners.append(liner)
            else:
                ## Grab first page on first swap
                if len(pagelets)==0:
                    pagelets=[separator.join(page_liners)]
                    
                    ## Start page 2
                    page_liners=[]
                page_liners.append(liner)

    
    return


def dev1():
    tt="""
    SCHOOLKIDZ.COM LLC   !   Account # 0046 1527 6199   !   December 1, 2021 to December 31, 2021
Page 10 of 32Checks - continued
Date Check # Bank reference Amount Date Check # Bank reference Amount
continued on the next page12/06 93504* 813005792018788 -241.35 12/03 94123* 813005592861225 -4,338.04
12/09 93570* 813007152116509 -1,954.00 12/13 94124 813001192382566 -133.52
12/13 93572* 813008592725056 -4.03 12/06 94127* 813005792803846 -471.80
12/06 93580* 813005892441297 -887.15 12/01 94129* 813005392249642 -468.17
12/21 93619* 813005692174518 -14.23 12/02 94136* 813005492593273 -1,440.00
12/03 93655* 813009492373980 -651.24 12/10 94139* 813008292737706 -349.45
12/10 93679* 813004492342028 -649.35 12/02 94143* 813009292700599 -2,432.00
12/10 93694* 813008292911822 -1,612.52 12/06 94147* 813007292156556 -145.00
12/14 93699* 813008692569455 -3,139.01 12/07 94148 813005992906807 -692.00
12/08 93702* 813008092335035 -398.65 12/06 94149 813009792234502 -3,400.00
12/08 93726* 813008252052758 -433.82 12/06 94150 813005792803845 -3,741.34
12/02 93738* 813009392664029 -859.22 12/07 94151 813005992880744 -1,982.40
12/03 93743* 813005692025428 -2,480.22 12/06 94152 813009792409418 -6,372.75
12/06 93752* 813005792067124 -48.06 12/08 94153 813004192376105 -3,151.80
12/31 93756* 813004792383396 -149.72 12/15 94154 813004992206939 -531.74
12/23 93807* 813009792110009 -1,588.16 12/22 94155 813008152799852 -93,275.00
12/06 93827* 813005792433275 -763.17 12/06 94156 813007192788812 -887.01
12/06 93851* 813005792018780 -129.16 12/17 94157 813009192040774 -299.79
12/21 93855* 813005692039541 -412.30 12/13 94159* 813004692737159 -3,156.11
12/01 93860* 813008452027302 -12.90 12/15 94160 813008792771174 -3,999.00
12/10 93892* 813004492153661 -204.74 12/28 94161 813004392172142 -8,010.00
12/08 93894* 813008092917941 -379.54 12/13 94162 813004592914976 -803.72
12/07 93899* 813009892822222 -288.00 12/14 94163 813003492166623 -417.52
12/07 93900 813009892822223 -188.31 12/20 94164 813005392351833 -62.85
12/02 93902* 813005492385901 -933.49 12/14 94165 813001392673750 -1,364.22
12/30 93929* 813004692189340 -154.27 12/20 94166 813006192337396 -2,514.72
12/15 93930 813004992691012 -305.40 12/20 94167 813009392522674 -7,987.68
12/06 93931 813005792433274 -557.45 12/23 94168 813006592758928 -1,348.69
12/09 93938* 813004392099240 -145.96 12/21 94169 813009492567129 -846.26
12/22 93998* 813009692415687 -66.61 12/21 94172* 813009492049955 -871.15
12/10 94081* 813008292737704 -879.52 12/24 94173 813009892472460 -85.00
12/31 94088* 813008692484431 -20.21 12/20 94174 813005492242123 -1,686.26
12/09 94090* 813008192896760 -36.29 12/28 94175 813004392718489 -9,440.50
12/16 94091 813008992560907 -27.12 12/23 94177* 813006592564031 -93.43
12/09 94093* 813004392275417 -226.57 12/21 94178 813009392908398 -3,222.00
12/14 94096* 813008692431221 -250.64 12/22 94179 813009692297453 -29.06
12/13 94098* 813004692262567 -36.80 12/24 94180 813006692331547 -344.61
12/10 94116* 813008292737705 -1,128.00 12/23 94181 813006592926813 -29.44
    """
    pagelets=auto_parse_page(tt)

    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""