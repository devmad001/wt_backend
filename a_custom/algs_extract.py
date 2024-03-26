import os
import sys
import codecs
import json
import re
import ast
from collections import OrderedDict

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_llm.llm_interfaces import LazyLoadLLM
from dateutil.parser import parse

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep  8, 2023  Init

"""
ALGS FOR EXTRACTION
"""


def llm_resolve_date(dt):
    LLM=LazyLoadLLM.get_instance()
    print ("[info] using LLM to resolve date: "+str(dt))
    prompt="""You are a date conversion tool and return the response in valid json.
        Output should look like: {'date':'2018-09-21'} in yyyy--mm-dd format.
        Please convert the following date (if there are two dates return the first): """+str(dt)

    response=LLM.prompt(prompt)
    try:
        dt=alg_json2dict(response).get('date','')
    except Exception as e:
        print ("[warning] on llm_resolve_date: "+str(e))
        dt=''
    return dt

def alg_resolve_to_date(statement_period):
    ## Resolve date to normal format -- use LLM if needed
    ## INPUTS:
    #'2018-09-21 to 2018-10-21' 
    # #'July 31, 2021 through August 31, 2021' 
    ## OUTPUTS:
    #: 2018-09-21
    dt=''
    if statement_period:
        statement_period=str(statement_period).strip()
        statement_date=re.sub(r' to .*','',statement_period)
        statement_date=re.sub(r' through .*','',statement_period)
        try:
            dt = parse(statement_date)
            dt=str(dt.strftime('%Y-%m-%d'))
        except:
            dt=llm_resolve_date(statement_date)
    return dt


## Common attempt
def alg_json2dict(given,depth=0):
    ## NOTES:
    #i)  Auto repair ie/ if fails first and has alpha at start
    # Given str return dict
    #1)  json
    #2)  eval
    #3)  swap ' for "
    dd={}

    if not isinstance(given,dict) and depth<=1:
        try:
            dd=json.loads(given)
        except:
            try:
                dd = ast.literal_eval(given)
            except:
                pass

            if not dd or not isinstance(dd,dict):
                ##Try swapping ' for "" but not if it's escaped or buried
                given = re.sub(r"(?<!\\)\'", '"', given)

                ##Try removing characters at start (ie...look for [ and { )
                given=re.sub(r'^.*?([\[\{\`])', r'\1', given,flags=re.DOTALL).strip()

                dd=alg_json2dict(given,depth=depth+1)

    elif isinstance(given,dict):
        dd=given
    else:
        dd={}
    return dd

if __name__=='__main__':
    branches=['do_extract']
    for b in branches:
        globals()[b]()


"""
"""
