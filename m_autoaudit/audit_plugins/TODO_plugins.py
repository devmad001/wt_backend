import os
import sys
import json
import re
import time


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


#0v1# JC  Mar 15, 2023  Setup



"""
    AUDIT PLUGINS   IDEAS

"""




def todo_plugin_check_transaction_text_exists():

    # *recall, with incremental models you have a soft check rerun ability so even if loosely flags not a big deal
    

    #> hallucinated on creation of RECORD?
    #   -> should all records be back-checked against specific text?
    #> Estimated record counts not match (like before)
    
    # Plugin flagging may depend if knowledge used a weak model!
    # if weak model used do light checks:
    # 123 Main St?  123 Main St, Anytown, US 90212

    # Problem pages (in the past regex)
    # This Page Intentionally Left Blank  <-- caused problem 3.5 so combo again and auto bump!
    

    """
        gpt 3.5 hallucinates and creates two nodes
        - maybe part of thinking its' a chat continuation??
        - LOGIC:  check at least 1 transaction should match first word of desc + section
        - SUGGESTION:  if gpt 3.5 -> 4 if not found!
        

         CHASE © 
        This Page Intentionally Left Blank 
        SB1500217-F1 February 01, 2023 through February 28, 2023 
        Account Number:  000000910227575 
        Page 2 of 2 37
        
        [page2t] trying model: default at attempt #1 (try_cache: True)
        [info] Loaded cached llm response
        [debug] word count: 140
        [debug] [B] started llm query [gpt-3.5-turbo]: 2024-03-15 12:55:50.212393 timeout: 203
        [debug] LLM runtime: 2.929912567138672 seconds
        [debug validate transactions] transaction stats: {'count_transactions': 2, 'count_amounts': 2}
        [intermediary found count]: 2
        [ ] beware assume transactions could be signed but sign may be incorrect or dropped!
        [llm_page2t] TRANSACTIONS FOUND ON PAGE FINAL:
        {
            "all_transactions": [
                {
                    "transaction_description": "ATM WITHDRAWAL 123 Main St New York NY 10001",
                    "transaction_amount": 60.0,
                    "transaction_date": "2023-02-15",
                    "section": "ATM & DEBIT CARD WITHDRAWLS"
                },
                {
                    "transaction_description": "GROCERY STORE PURCHASE 456 Elm St Los Angeles CA 90001",
                    "transaction_amount": 30.5,
                    "transaction_date": "2023-02-20",
                    "section": "ELECTRONIC PURCHASES"
                }
            ]
        }
        [found 2 transactions]
        [debug gneo4j] 2 nodes were created.

    """


    return




if __name__=='__main__':
    branches=[]
    for b in branches:
        globals()[b]()



"""

"""








