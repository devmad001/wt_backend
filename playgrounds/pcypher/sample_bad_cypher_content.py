import os
import sys
import codecs
import json
import re
import datetime
import uuid


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"

sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")
sys.path.insert(0,LOCAL_PATH+"../..")

from w_storage.gstorage.gneo4j import Neo

from get_logger import setup_logging
logging=setup_logging()


        
#0v1# JC Jan 30, 2024  Setup


"""
    PLAYGROUND FOR DEVELOPER & CYPHER GRAPH DATABASE


"""



# HOGAN CHECKS:
"""
gneo4j.py exception: {code: Neo.ClientError.Statement.SyntaxError} {message: Invalid input ''': expected whitespace, '.', node labels, '[', '^', '*', '/', '%', '+', '-', "=~", IN, STARTS, ENDS, CONTAINS, IS, '=', '~', "<>", "!=", '<', '>', "<=", ">=", AND, XOR, OR, ',' or '}' (line 1, column 1026 (offset: 1025))
"""


def a2lg_final_attempt_clean_description(cypher):
    # Regex to match the transaction_description assuming it ends with ',
    pattern = re.compile(r"transaction_description: '(.*?)', ", re.DOTALL)
    
    # Search for the pattern in the given Cypher query
    match = pattern.search(cypher)
    
    if match:
        transaction_description = match.group(1)
    
        # Replace two single quotes with one to handle escaped quotes within the string
        transaction_description = transaction_description.replace("''", "'")
    
        # Clean the transaction_description by removing non-regular characters but keep single quotes
        cleaned_description = re.sub(r"[^a-zA-Z0-9 .,;:!?'-]", '', transaction_description)
    
        # Replace the original transaction_description in the Cypher query with the cleaned version
        # Ensure the cleaned description is properly formatted with single quotes for Cypher
        cleaned_description_for_cypher = cleaned_description.replace("'", "''")  # Escape single quotes for Cypher
        modified_cypher = cypher.replace(match.group(0), f"transaction_description: '{cleaned_description_for_cypher}', ")
        
        return modified_cypher
    else:
        print("Transaction description not found or doesn't follow the expected pattern.")
        return cypher  # Return the original cypher if no transaction_description is found or pattern doesn't match

def alg_final_attempt_clean_description(cypher_query):
    # Regex to match the transaction_description assuming it ends with ',
    pattern = re.compile(r"(transaction_description: ')(.*?)(',)", re.DOTALL)
    
    # Function to clean the transaction_description
    def clean_description(match):
        transaction_description = match.group(2)  # Extract the actual description text
        transaction_description = transaction_description.replace("''", "'")  # Handle escaped quotes
        cleaned_description = re.sub(r"[^a-zA-Z0-9 .,;:!?-\|\\\/]", ' ', transaction_description)  # Clean the description
        return match.group(1) + cleaned_description + match.group(3)  # Reconstruct the match with cleaned description
    
    # Replace the transaction_description in the cypher_query with the cleaned version
    modified_cypher = re.sub(pattern, clean_description, cypher_query)
    
    return modified_cypher


def step_through_odd_cypher():
    stmt="""
MERGE (transaction1:Transaction {id: 'c225a439afa3f51991989f936e0b055f818fdcf8b1e1da93b5c798717fadbd4a'}) ON CREATE SET transaction1 += {transaction_description: 'RONY YOSEF Please Post to Account ASHFORDPARKCONDOMINIUM | nk O | PO Box 7238 | ——— RONY YOSEF | RONY YOSEF | 1 MEWS ALY | POUGHKEEPSIE, NY 12603-3409 Sloux Falls SD 57117-7236 | PAY Two Hundred Forty Four and 00/ 8 00 Dollars | TO THE #CSP01000B950CT3# 62€290567 | ORDER OF ASHFORD PARK CON BDOMINIUM ASSOCIA | 435 BUCKLAND RD | SOUTH WINDSOR CT  06074-3720 Securiy | Features | Details on | v 83K Payadle Through | KEYBANK, NA | ONLINE BARKING BILL PAY 6103 23778231 | 419 | June 2, 2018 | [ 1 S $§ ******a*n244.00 % | VOID 90 DAYS AFTER {SSUE | L ||l|| ||||| |H|| il |l||l i ||||| Hili I|||| [11] Memo | ‘ 237?83 120 4L 32070L0O 3509935850000 | >211170348< 20180614 -~ ~ , | L 4 ‘s / £E U! , O a2 2 2 | § By 4 °m] : | I | ] =1 N | : ks " "\' VR ¥ ig : | £ 14y / 3 F| ¢ A3z ) Oc ol s | - e  P Tl = | S S A e “ol R T | < PROE AND REAPPERR- z=Qf = | : sapeAN . '' i | Posting Date 2018 Jun 14 | Bank # 1615 | Research Seq # 6088352474 | Account # 350993518504 | Dollar Amount  $244.00 | Check/Serial Store # 23778231 | Tran Code 0 | RTABA 41207040 | DB/CR 2', transaction_amount: 244.0, transaction_date: '2018-06-02', section: '', account_number: '350993518504', account_id: '65caaffb9b6ff316a779f525-350993518504', id: 'c225a439afa3f51991989f936e0b055f818fdcf8b1e1da93b5c798717fadbd4a', case_id: '65caaffb9b6ff316a779f525', statement_id: '65caaffb9b6ff316a779f525-2018-06-14-350993518504-M&T Victim Records__Operating 2018__CR__2018 06__061418-$4,392.00.pdf', filename: 'M&T Victim Records__Operating 2018__CR__2018 06__061418-$4,392.00.pdf', filename_page_num: 16, label: 'Transaction'} ON MATCH SET transaction1 += {transaction_description: 'RONY YOSEF Please Post to Account ASHFORDPARKCONDOMINIUM | nk O | PO Box 7238 | ——— RONY YOSEF | RONY YOSEF | 1 MEWS ALY | POUGHKEEPSIE, NY 12603-3409 Sloux Falls SD 57117-7236 | PAY Two Hundred Forty Four and 00/ 8 00 Dollars | TO THE #CSP01000B950CT3# 62€290567 | ORDER OF ASHFORD PARK CON BDOMINIUM ASSOCIA | 435 BUCKLAND RD | SOUTH WINDSOR CT  06074-3720 Securiy | Features | Details on | v 83K Payadle Through | KEYBANK, NA | ONLINE BARKING BILL PAY 6103 23778231 | 419 | June 2, 2018 | [ 1 S $§ ******a*n244.00 % | VOID 90 DAYS AFTER {SSUE | L ||l|| ||||| |H|| il |l||l i ||||| Hili I|||| [11] Memo | ‘ 237?83 120 4L 32070L0O 3509935850000 | >211170348< 20180614 -~ ~ , | L 4 ‘s / £E U! , O a2 2 2 | § By 4 °m] : | I | ] =1 N | : ks " "\' VR ¥ ig : | £ 14y / 3 F| ¢ A3z ) Oc ol s | - e  P Tl = | S S A e “ol R T | < PROE AND REAPPERR- z=Qf = | : sapeAN . '' i | Posting Date 2018 Jun 14 | Bank # 1615 | Research Seq # 6088352474 | Account # 350993518504 | Dollar Amount  $244.00 | Check/Serial Store # 23778231 | Tran Code 0 | RTABA 41207040 | DB/CR 2', transaction_amount: 244.0, transaction_date: '2018-06-02', section: '', account_number: '350993518504', account_id: '65caaffb9b6ff316a779f525-350993518504', id: 'c225a439afa3f51991989f936e0b055f818fdcf8b1e1da93b5c798717fadbd4a', case_id: '65caaffb9b6ff316a779f525', statement_id: '65caaffb9b6ff316a779f525-2018-06-14-350993518504-M&T Victim Records__Operating 2018__CR__2018 06__061418-$4,392.00.pdf', filename: 'M&T Victim Records__Operating 2018__CR__2018 06__061418-$4,392.00.pdf', filename_page_num: 16, label: 'Transaction'}
"""

    ## PATCH 1
    # Regular expression to match \' where there are no word characters (\w) on either side
    # Uses negative lookbehind (?<!\w) and negative lookahead (?!\w)
#    pattern = re.compile(r'(?<![^\W_])\\\'(?![^\W_])')
    # Replace matching occurrences with an empty string
#    stmt = pattern.sub('', stmt)
#    stmt=re.sub(r"\\'",' ',stmt)


#    pattern = re.compile(r'(?<! )\\\'')  # Negative lookbehind to check there's no space before "\'"
#    # Replace occurrences with a space before "\'"
#    stmt=pattern.sub(r" \\'", stmt)
    stmt=alg_final_attempt_clean_description(stmt)

    cypher_query=stmt
    
    # Define the offset where the error occurred
    error_offset = 908
    
    # Print a portion of the query string around the error_offset for inspection
    context_range = 50  # Adjust as needed to show more or less context
    start = max(0, error_offset - context_range)
    end = min(len(cypher_query), error_offset + context_range)
    
    # Print the substring around the error offset
    print(cypher_query[start:end])
    
    # Specifically highlight the character at the error offset
    print("Error at position:", cypher_query[error_offset])



    print ("FO: "+str(stmt))
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
#    stmt2=alg_final_attempt_clean_description(stmt)
#    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    
    return
    

def ultra_normalize():
    trans = {
    "transaction_description": "Connectic PAY 10 [HY | erofwncf w{''--@@ HELEN E. SANBORN 51-7719/2119 | PH. 860-429-9061 | 32-8 POMPEY RD | ASHFORD, CT 06278 | Astdod. fonde Condo Adete | Aoun and ''%m | ut State Employees Credit Union Inc. | Hartford, CT 06106 1 | 3 w%wbeu Ig MEMO 31 | Ellq??lu'':I''?l DDqu EBE?SDOII'' I.EBE 425/ 23 ''[1_23",
    "transaction_amount": 244.0,
    "transaction_date": "2018-05-31",
    "section": "",
    "account_number": "92827500",
    "account_id": "65caaffb9b6ff316a779f525-92827500",
    "id": "9c28a13c4693aef234141e3a9423c85fd4ca54b4f693873ab3f182cd1b8daa6f",
    "case_id": "65caaffb9b6ff316a779f525",
    "statement_id": "65caaffb9b6ff316a779f525-2018-05-31-92827500-M&T Victim Records__Operating 2018__CR__2018 05__053118-$488.00.pdf",
    "filename": "M&T Victim Records__Operating 2018__CR__2018 05__053118-$488.00.pdf",
    "filename_page_num": 3,
    "label": "Transaction"
    }
    return

if __name__=='__main__':
    branches=['step_through_odd_cypher']
    for b in branches:
        globals()[b]()



"""
"""