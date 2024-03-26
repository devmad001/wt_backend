import os
import sys
import codecs
import json
import re
from datetime import datetime

from dateutil import parser



LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Jan  2, 2024  Opening balance option + enhanced date parsing

"""
    TEXT DATE RANGE TO DATE OBJECTS
    - may need to extend or use LLM on no match
"""

def str2date(the_string):
    ## Cascade of date formats
    #[ ] recall elsewhere you fall back to LLM
    date_obj=''
    if the_string:
        try: date_obj = datetime.strptime(the_string, "%Y-%m-%d").date()
        except:
            try: date_obj = datetime.strptime(the_string, "%B %d, %Y").date()
            except:
                try: date_obj = parser.parse(start_str).date()
                except:
                    logging.warning("[error] could not parse date: "+str(the_string))
                    pass
    return date_obj

def statement_range_to_objects(statement_period,statement_date,verbose=False):

    start_date_obj=None
    end_date_obj=None
    
    statement_period=statement_period.strip()
    
    ## ASSUME ALWAYS START OF THE MONTH??
    ## TRY via single statement_date

    if verbose:
        print ("[debug] statement_period: "+str(statement_period))
        
    if not statement_period:
        return start_date_obj, end_date_obj

    ## i)   2022-01-01 to 2022-01-31
    ## ii) 'July 31, 2021 through August 31, 2021'}

    #i)
    if ' to ' in statement_period:
        # Split the string into start and end dates
        start_str, end_str = map(str.strip, statement_period.split(" to "))
        
        # Convert strings to date objects
        try: start_date_obj = datetime.strptime(start_str, "%Y-%m-%d").date()
        except:
            try: start_date_obj = parser.parse(start_str).date()
            except:pass

        try: end_date_obj = datetime.strptime(end_str, "%Y-%m-%d").date()
        except:
            try: end_date_obj = parser.parse(end_str).date()
            except: pass

    #ii) tbd
    elif ' through ' in statement_period:
        # Split the string into start and end dates
        start_str, end_str = map(str.strip, statement_period.split(" through "))
        # Convert strings to date objects

        try: start_date_obj = datetime.strptime(start_str, "%B %d, %Y").date()
        except:
            try: start_date_obj = parser.parse(start_str).date()
            except: pass

        try: end_date_obj = datetime.strptime(end_str, "%B %d, %Y").date()
        except:
            try: end_date_obj = parser.parse(end_str).date()
            except: pass

    elif ' - ' in statement_period:
        # Split the string into start and end dates
        start_str, end_str = map(str.strip, statement_period.split(" - "))
        # Convert strings to date objects

        try: start_date_obj = datetime.strptime(start_str, "%B %d, %Y").date()
        except:
            try: start_date_obj = parser.parse(start_str).date()
            except: pass
        try: end_date_obj = datetime.strptime(end_str, "%B %d, %Y").date()
        except:
            try: end_date_obj = parser.parse(end_str).date()
            except: pass
        
    else:
        logging.warning("[unknown statement date delimiter]: "+str(statement_period))

        ## Auto guess at delimiter or just grab first date or ?
        try:
            start_date_obj = parser.parse(statement_period).date()
            end_date_obj=None
        except:
            pass

    
    if not start_date_obj:
        logging.warning("[warning] could not parse start date (extend or use LLM): "+str(statement_period))
    
    return start_date_obj, end_date_obj



def dev_local_samples():
    sample1='2020-05-01 to 2020-05-29'
    start_date_obj,end_date_obj=statement_range_to_objects(sample1,None)
    print ("GOT: START: "+str(start_date_obj))

    return


if __name__=='__main__':
    branches=['dev_local_samples']

    for b in branches:
        globals()[b]()




"""

"""
