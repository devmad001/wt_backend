import time
import os
import sys
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"..")

from get_logger import setup_logging


from w_llm.llm_interfaces import OpenAILLM
from w_storage.gstorage.gneo4j import Neo

logging=setup_logging()


#0v1# JC  Sep  2, 2023  Init


"""
IMPORT ALGS AS REQUIRED

"""

## NOTES:
#1)  Possible to modify transactions prior to cypher creation (ie add case_id)?
#2)  Validation:  missing payments?
#3)  Load llm from cache

## MISC:

#- missing id:
#- but this is a bit of Fill strategy
# #   {"transaction_id": "", "transaction_description": "Zelle Payment To Anthony Bro Jpm679645738", "transaction_amount": "1,000.00", "transaction_date": "2021-08-16"},


pages=['JPMorgan Chase Bank, N.A.\nP O Box 182051\nColumbus, OH 43218 - 2051\nJuly 31, 2021 through August 31, 2021\nAccount Number:\n 000000651770569\nCUSTOMER SERVICE INFORMATION\nWeb site:\nChase.com\nService Center:\n1-800-242-7338\n00075355 DRE 703 141 24421 NNNNNNNNNNN T  1 000000000 64 0000\nDeaf and Hard of Hearing: 1-800-242-7383\nGTA AUTO, INC.\nPara Espanol:\n1-888-622-4273\n6829 LANKERSHIM BLVD STE 116\nInternational Calls:\n1-713-262-1679\nNORTH HOLLYWOOD CA 91605 \n2\n2\n0\n0\n0\n0\n0\n0\n0\n1\n0\n2\n0\n5\n5\n3\n5\n7\n0\n0\n*start*summary\nCHECKING SUMMARY\nChase Total Business Checking\nBeginning Balance\n$3,197.10\nINSTANCES\nAMOUNT\nDeposits and Additions\n24\n20,117.77\nATM & Debit Card Withdrawals\n7\n-827.15\nElectronic Withdrawals\n40\n-22,367.92\nFees\n1\n-34.00\nEnding Balance\n72\n$85.80\n*end*summary\n*start*deposits and additions\nDEPOSITS AND ADDITIONS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nATM Check Deposit       08/02 6400 Laurel Canyon Blv North Hollywo CA Card 7413\n$500.00\n08/02\nOrig CO Name:Western Union          Orig ID:9222993574 Desc Date:Jul 30 CO Entry\n130.00\nDescr:Refund    Sec:PPD    Trace#:021000020270401 Eed:210802   Ind ID:\nInd Name:Hugo Flores Trn: 2140270401Tc\n08/04\nZelle Payment From Meher Fazal Cofyrdcim9Lw\n700.00\n08/06\nZelle Payment From Kelly Sotelo Laguna Wfct0C47Hsvn\n300.00\n08/11\nRemote Online Deposit              1\n700.00\n08/11\nRemote Online Deposit              1\n600.00\n08/12\nRemote Online Deposit              1\n2,084.00\n08/13\nRemote Online Deposit              1\n1,500.00\n08/16\nRemote Online Deposit              1\n2,000.00\n08/16\nZelle Payment From Anthony Gullen Wfct0C6Bsdmk\n500.00\n08/18\nZelle Payment From Melissa Serrano Backz69Iscil\n150.00\n08/19\nZelle Payment From Melissa Serrano Bacr67Llv5Aw\n100.00\n08/20\nZelle Payment From Anthony Gullen Wfct0C7G8Gjr\n500.00\n08/23\nRemote Online Deposit              1\n1,000.00\n08/25\nZelle Payment From Melissa Serrano Bach2Bgh006M\n140.00\n08/26\nRemote Online Deposit              1\n1,000.00\n08/26\nRemote Online Deposit              1\n800.00\n08/26\nRemote Online Deposit              1\n800.00\n08/26\nRemote Online Deposit              1\n700.00\n08/26\nRemote Online Deposit              1\n500.00\n08/26\nRemote Online Deposit              1\n500.00\n*end*deposits and additions\nPage\nof\n 4\n 1 \n \n      \n                                                       \n \n \n \n \n   \n', 'July 31, 2021 through August 31, 2021\nAccount Number:\n 000000651770569\n*start*deposits and additions\nDEPOSITS AND ADDITIONS\n  (continued)\nDATE\nDESCRIPTION\nAMOUNT\n08/26\nRemote Online Deposit              1\n200.00\n08/27\n08/26/2021 Reversal: Orig CO Name:American Express\n4,213.77\n08/31\nRemote Online Deposit              1\n500.00\nTotal Deposits and Additions\n$20,117.77\n*end*deposits and additions\n*start*atm debit withdrawal\nATM & DEBIT CARD WITHDRAWALS\n DATE\nDESCRIPTION\nAMOUNT\n08/02\nCard Purchase           08/01 Fitness Mania Riverside CA Card 7397\n$49.99\n08/03\nCard Purchase           08/02 Www.Paystubsnow.Com Www.Paystubsn TX Card 7413\n7.99\n08/09\nRecurring Card Purchase 08/07 Uber   Pass Help.Uber.Com CA Card 7397\n24.99\n08/18\nCard Purchase           08/17 Fedex 940635302952 Memphis TN Card 7413\n8.20\n08/19\nRecurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413\n24.99\n08/24\nATM Withdrawal          08/24 6400 Laurel Canyon B North Hollywo CA Card 7413\n700.00\n08/30\nRecurring Card Purchase 08/28 Dnh*Godaddy.Com Https://Www.G AZ Card 7413\n10.99\nTotal ATM & Debit Card Withdrawals\n$827.15\n*end*atm debit withdrawal\n*start*atm and debit card summary\nATM & DEBIT CARD SUMMARY\nHugo Arturo Flores Card 7397\nTotal ATM Withdrawals & Debits\n$0.00\nTotal Card Purchases\n$74.98\nTotal Card Deposits & Credits\n$0.00\nAnthony Joseph Guillen Card 7413\nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$52.17\nTotal Card Deposits & Credits\n$500.00\nATM & Debit Card Totals  \nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$127.15\n*end*atm and debit card summary\n*start*electronic withdrawal\nTotal Card Deposits & Credits\n$500.00\nELECTRONIC WITHDRAWALS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nZelle Payment To Anthony Bro Jpm665864367\n$3,000.00\n08/02\nZelle Payment To Jennifer Nell Jpm667436915\n10.00\n08/02\nZelle Payment To Jennifer Nell Jpm667437893\n200.00\n08/02\nZelle Payment To Jennifer Nell Jpm667438464\n10.00\n08/04\nZelle Payment To Lil Bro Alex Jpm669535918\n350.00\n08/04\nZelle Payment To Meher Jpm669604904\n60.00\n08/04 Orig CO Name:Citi Autopay           Orig ID:Citicardap Desc Date:210803 CO Entry\n105.53\nDescr:Payment   Sec:Tel    Trace#:091409685898393 Eed:210804   Ind ID:080502002630039\nInd Name:Hugo Flores Trn: 2165898393Tc\n08/05\nZelle Payment To Paris Sugi Dba 12323832406\n500.00\n08/06\nZelle Payment To Anthony Bro Jpm671584743\n300.00\n08/09\nZelle Payment To Lil Bro Alex Jpm674243402\n200.00\n08/12\nZelle Payment To Teisy Jpm677655611\n172.00\n08/13\nZelle Payment To Melissa Fw Jpm678129044\n1,000.00\n*end*electronic withdrawal\nPage\nof\n 4\n 2 \n \n \n   \n', '2\n6\n0\n0\n0\n0\n0\n0\n0\n2\n0\n2\n0\n5\n5\n3\n5\n7\n0\n1\nJuly 31, 2021 through August 31, 2021\nAccount Number:\n 000000651770569\n*start*electronic withdrawal\nELECTRONIC WITHDRAWALS\n (continued)\nDATE\nDESCRIPTION\nAMOUNT\n08/16\nZelle Payment To Anthony Bro Jpm679645738\n1,000.00\n08/16\nZelle Payment To Melissa Fw Jpm679646274\n1,000.00\n08/16\nZelle Payment To Anthony Bro Jpm679646739\n500.00\n08/16\nZelle Payment To Liz Flores Jpm680556028\n420.00\n08/16\nZelle Payment To Lil Bro Alex Jpm680632971\n700.00\n08/16\nZelle Payment To Martin 12392431698\n20.00\n08/16\nZelle Payment To Jesus Fireup Jpm681483026\n400.00\n08/16\nZelle Payment To Jessica Jpm681450613\n100.00\n08/16 Orig CO Name:Applecard Gsbank       Orig ID:9999999999 Desc Date:081421 CO Entry\n200.00\nDescr:Payment   Sec:Web    Trace#:124085088814230 Eed:210816   Ind ID:12810547\nInd Name:Hugo Flores Trn: 2288814230Tc\n08/16\nZelle Payment To Lil Bro Alex Jpm682224864\n90.00\n08/17\nZelle Payment To Kevin Jpm683042972\n300.00\n08/18\nZelle Payment To Brayan Gta Auto Jpm683291589\n1,300.00\n08/18\nZelle Payment To (951) 2242099 Jpm683992094\n150.00\n08/18\nZelle Payment To Mariza Haircut 12410934415\n30.00\n08/19\nZelle Payment To Haig Jpm684249239\n102.00\n08/19\nZelle Payment To Mariza Haircut 12415184384\n120.00\n08/20\nZelle Payment To Melissa Fw Jpm686601797\n500.00\n08/25\nZelle Payment To Luzby Andrade 12454300327\n35.00\n08/25\nZelle Payment To Mariza Haircut 12454479493\n30.00\n08/26\nZelle Payment To Melissa Fw Jpm692978891\n140.00\n08/26\nZelle Payment To Haig Jpm693056458\n140.00\n08/26 Orig CO Name:Allstate Nbindco       Orig ID:1362999368 Desc Date:Aug 21 CO Entry\n287.62\nDescr:Ins Prem  Sec:PPD    Trace#:021000026074791 Eed:210826   Ind ID:\nInd Name:Flores Trn: 2386074791Tc\n08/26 Orig CO Name:American Express       Orig ID:2005032111 Desc Date:210826 CO Entry\n4,213.77\nDescr:ACH Pmt   Sec:PPD    Trace#:021000023191259 Eed:210826   Ind ID:\nInd Name:Hugo Flores Trn: 2383191259Tc\n08/30\nZelle Payment To (951) 2242099 Jpm696293969\n500.00\n08/30\nZelle Payment To Melissa Fw Jpm696526753\n2,000.00\n08/30\nZelle Payment To Malek Sadi 12480636458\n300.00\n08/30\nZelle Payment To Reader Heavy Duty Jpm699325459\n300.00\n08/30 Orig CO Name:Barclaycard US         Orig ID:2510407970 Desc Date:       CO Entry\n1,582.00\nDescr:Creditcardsec:Web    Trace#:026002572841962 Eed:210830   Ind ID:810676570\nInd Name:Genesis Flores Trn: 2422841962Tc\nTotal Electronic Withdrawals\n$22,367.92\n*end*electronic withdrawal\n*start*fees section\nFEES\nDATE\nDESCRIPTION\nAMOUNT\n08/30\nInsufficient Funds Fee For A $1,582.00 Item - Details: Orig CO Name:Barclaycard US\n$34.00  \nOrig ID:2510407970 Desc Date:       CO Entry Descr:Creditcardsec:Web\nTrace#:026002572841962 Eed:210830   Ind ID:810676570                    Ind Name:Genesis\nFlores Trn: 2422841962Tc\nTotal Fees\n$34.00\n*end*fees section\n*start*post fees message\nThe monthly service fee of $15.00 was waived this period because you maintained a minimum daily balance of $1,500.00\nor more.\n*end*post fees message\nPage\nof\n 4\n 3 \n \n \n   \n', 'July 31, 2021 through August 31, 2021\nAccount Number:\n 000000651770569\n*start*daily ending balance2\nDAILY ENDING BALANCE\nDATE\nAMOUNT\nDATE\nAMOUNT\nDATE\nAMOUNT\n08/02\n$557.11\n08/12\n3,220.60\n08/23\n1,005.41\n08/03\n549.12\n08/13\n3,720.60\n08/24\n305.41\n08/04\n733.59\n08/16\n1,790.60\n08/25\n380.41\n08/05\n233.59\n08/17\n1,490.60\n08/26\n99.02\n08/06\n233.59\n08/18\n152.40\n08/27\n4,312.79\n08/09\n8.60\n08/19\n5.41\n08/30\n-414.20\n08/11\n1,308.60\n08/20\n5.41\n08/31\n85.80\n*end*daily ending balance2\n*start*service charge summary3\nSERVICE CHARGE SUMMARY\nTRANSACTIONS FOR SERVICE FEE CALCULATION\nNUMBER OF TRANSACTIONS\nChecks Paid / Debits\n11\nDeposits / Credits\nDeposited Items\n0\n0\nTransaction Total\n11\nSERVICE FEE CALCULATION\nAMOUNT\nService Fee\n$15.00\nService Fee Credit\n-$15.00\nNet Service Fee\n$0.00\nExcessive Transaction Fees (Above 100)\n$0.00\nTotal Service Fees\n$0.00\n*end*service charge summary3\n*start*dre portrait disclosure message area\nIN CASE OF ERRORS OR QUESTIONS ABOUT YOUR ELECTRONIC FUNDS TRANSFERS: \naddress on the front of this statement (non-personal accounts contact Customer Service) immediately if you think your statement or receipt is \nincorrect or if you need more information about a transfer listed on the statement or receipt.  \nFor personal accounts only: We must hear from you no later than 60 days after we sent you the FIRST statement on which the problem or error \nappeared.  Be prepared to give us the following information:\nYour name and account number\nThe dollar amount of the suspected error\nA description of the error or transfer you are unsure of, why you believe it is an error, or why you need more information.\n Call us at 1-866-564-2262 or write us at the \n•\n•\n•\nWe will investigate your complaint and will correct any error promptly.  If we take more than 10 business days (or 20 business days for new \naccounts) to do this, we will credit your account for the amount you think is in error so that you will have use of the money during the time it takes \nus to complete our investigation .\nIN CASE OF ERRORS OR QUESTIONS ABOUT NON-ELECTRONIC TRANSACTIONS:\nincorrect or if you need more information about any non-electronic transactions (checks or deposits) on this statement.  If any such error appears, \nyou must notify the bank in writing no later than 30 days after the statement was made available to you.  For more complete details, see the \nAccount Rules and Regulations or other applicable account agreement that governs your account. Deposit products and services are offered by \nJPMorgan Chase Bank, N.A.  Member FDIC\n  Contact the bank immediately if your statement is \n*end*dre portrait disclosure message area\nJPMorgan Chase Bank, N.A. Member FDIC\nPage\nof\n 4\n 4 \n   \n  \n']

def call_all():
    print ("[ ] runtime on entire")

    b=['query_graph']
    b=['pdf2graph']

    case_name='case_1'
    filename=''
    page_id=''
    statement_id=''

    run_id='run-'+str(case_name)+"-"+str(filename)+"-"+str(page_id)+"-"+str(statement_id)
    print ("[ ] store run_id input parameters for full debug")
    run={}
    run['id']=run_id

    if 'pdf2graph' in b:
        transactions=dev_pages2transactions(verbose=True,run=run)
        cypher_response=transactions2cypher(transactions,run=run)
        cypher,meta=cypher_marKup(cypher_response,run=run)
        insert_into_graph(cypher,run=run)

        ## Store run id variable for future debug
        print ("[ ] store run_id for future debug")

    if 'query_graph' in b:
        query=llm_write_question_query()
        print ("="*30)
        print ("QUERY: "+str(query))
        responses=query_neo4j(query)

        print ("RESPONSES: "+str(responses))


    return

def extract_amount(blob):
    #i) any repeated values?
    # First try $, then 4,000.00 then 23.00
    #[ ] test cases?
    amount=''
    print ("[ ] todo extract amount from: "+str(blob))
    return amount

def validate_transactions(dd):
    #If no transaction_amount, do basic regex to extract
    #- assumes structure
    vdd={}
    vdd['all_transactions']=[]
    for d in dd['all_transactions']:
        if d.get('transaction_amount','')=='':
            d['transaction_amount']=extract_amount(d['transaction_description'])
        vdd['all_transactions']+=[d]
    return vdd

def get_next_page():
    global pages
    #ok# for page in [pages[1]]:
    for page in [pages[2]]:
        print(page)
        break
    return page

def dev_pages2transactions(verbose=True,run={}):

    page=get_next_page()
    run['page_text']=page

    prompts={}

    #{'transactions':[{'transaction_id': '', 'transaction_description': 'some description', 'transaction_amount': '123.45', 'transaction_date': '2021-01-01','transaction_source': 'some source', 'transaction_target': 'some target', 'transaction_method': 'some method', 'transaction_state': 'some state']}

    prompts['page2transactions1']="""
    Please retrieve details about the transactions from the following bank statement page.
    If you cannot find the information from this text then return "".  Do not make things up.
    Always return your response as a valid json. All the transactions should be included in a list:

    {"all_transactions":[{"transaction_id": "id or blank", "transaction_description": "some description", "transaction_amount": "123.45", "transaction_date": "2021-01-01"]}

    Bank Statement Page:
    =====================

    """

    ## SCHEMA -copy-
    """
       "Transaction": {
            "Properties": ["id", "description", "source", "target", "method",
                           "amount", "date", "state"],
            "TransactionType": [
                "deposit", "withdrawal", "transfer", "payment",
                "interest payment", "refund", "payment received", "fee",
                "charge", "reversal", "adjustment"
            ],
            "Method": [
                "check", "electronic", "cash", "card payment", "debit card",
                "credit card", "wire transfer", "ACH", "mobile"
            ]
        }
    """

    LLM=OpenAILLM()
    prompt=prompts['page2transactions1']+page

    run['page_prompt']=prompt

    if verbose:
        print ("[verbose] big ask llm to extract transactions char length: "+str(len(prompt)))
    response=LLM.prompt(prompt)

    print ("[llm extracted response]: "+str(response))
    run['page_response']=response
    run['page_llm_stats']=LLM.get_stats()  #model, lib, runtime, tokens

    dd=json.loads(response)

    ## Inner validation
    run['cautions']=run.get('cautions',[])+['[transaction2cypher] count of inserts: '+str(count_inserts)+" not equal to transactions: "+str(len(transactions['all_transactions']))]
    
    return dd

def transactions2cypher(transactions, run={}):
    #trans=json.loads(transtxt)

    case_name='case_1'
    prompt_insert="""
    Here is a list of bank statement transactions. Convert them to cypher statements ie/
    MERGE (z:Payer {name: "Zelle"})
    MERGE (r1:Recipient {name: "Lil Bro Alex"})
    CREATE (z)-[p1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09") 
}]->(r1)
    =====

    """


    LLM=OpenAILLM()
    prompt=prompt_insert+str(json.dumps(transactions))

    run['transaction_prompt']=prompt

    print ("[info] prompting for cypher creation (length: "+str(len(prompt))+")")
    cypher_response=LLM.prompt(prompt)

    run['transaction_response']=cypher_response

    print ("CYPHER CREATION RESPONSE: "+str(cypher_response))

    count_inserts=len(re.findall(r'TRANSFERRED_TO',cypher_response))

    print ("[transactions count]: "+str(len(transactions['all_transactions'])))
    print ("[inserts created]: "+str(count_inserts))

    run['meta_transactions_count']=len(transactions['all_transactions'])
    run['meta_inserts_count']=count_inserts
    run['cypher_llm_stats']=LLM.get_stats()  #model, lib, runtime, tokens

    if count_inserts!=len(transactions['all_transactions']):
        logging.dev("[warning] count of inserts: "+str(count_inserts)+" not equal to transactions: "+str(len(transactions['all_transactions']))+" at run_id: "+str(run_id))

        run['cautions']=run.get('cautions',[])+['[transaction2cypher] count of inserts: '+str(count_inserts)+" not equal to transactions: "+str(len(transactions['all_transactions']))]

    """
    Data indexes:
    - bank_statement_id
    - case_id
    - source_id
    - target_id
    - transaction_id
    """
    return cypher_response

def cypher_marKup(cypher,case_name='case_1',run={}):
    ## Clean up cypher and add more meta
    #> clean response header?

    meta={}

    lines=[]
    last_line_type=''
    found_first_statement=False  #Assume CREATE or MERGE

    for liner in cypher.split('\n'):
        new_liner=''
#D1        print (liner) 

        ## Ignore lines until first statement
        if not found_first_statement:
            if re.search(r'CREATE|MERGE',liner):
                found_first_statement=True
            else:
                print ("[cypher] skipping line: "+str(liner))
                continue

        ## [cypher mod] Change node def
        #- if node defined line                     (not relationship which can have MERGE too)
        if re.search(r'MERGE .*\{',liner) and not re.search(r'\(.\)-',liner):

            ## EXTRACT NODE DEFINITION DICT

            # Using a regex pattern to identify key-value pairs
            pattern = r'(?P<key>\w+): "(?P<value>[^"]+)"'

            matches = re.findall(pattern, liner)
            if matches:
                # Converting matches into a dictionary
                dd = {key: value for key, value in matches}

                #1/2) ADD id to node
                if not 'id' in dd:
                    if dd.get('name',''):
                        dd['id']=case_name+"_"+dd.get('name','')
                    else:
                        dd['id']=case_name+"_"+str(uuid.uuid4())  #Randomize or base on description
#D                print("D: " + str(dd))

                #2/2) ADD case_id to node
                dd['case_id']=case_name

                ## UPDATE NODE DEFINITION DICT

                cypher_no_quote_keys_str=', '.join([f'{key}:"{value}"' for key, value in dd.items()])

                new_liner=re.sub(r'\{.*','',liner)+"{"+cypher_no_quote_keys_str+"}"+")"
#                print ("NEW: "+str(new_liner))

            else:
                pass
                #print("No match found")

        ## LOGIC:  relationship insert use MERGE not CREATE
        IS_REL_LINE=False
        if re.search(r'\)-\[',liner):  # CREATE (p19)-[p20]
            IS_REL_LINE=True
            if re.search(r'^[\s]{0,5}CREATE',liner):
                new_liner=re.sub(r'CREATE','MERGE',liner)

        ## SWAP NEW LINE
        if new_liner:
            lines.append(new_liner)
        else:
            lines.append(liner)

        ## [cypher mod]  Add case_id to relationship
        #- option 1:  look for create.  optoin 2: after transaction_id
        if IS_REL_LINE:  # Relationship create/merge line
            #lines.append('SET p.case_id="'+case_name+'"')
            lines.append('    case_id: "'+case_name+'",')

        ## [cypher mod]  Enforce merge on relationship create

    for liner in lines:
        print ("[cypher]: "+str(liner))
        if re.search(r'CREATE',liner):
            print ("[warning] CREATE found in response: "+str(liner))
            meta['warnings']=['CREATE found in response: '+str(liner)]


    return response,meta

def insert_into_graph(stmt,run={}):
    print ("[info] connecting to neo4j")

    print ("[stmt]: "+str(stmt))
    print ("Running cypher insert statement...")

    print ("EXPLAIN cypher_statement won't actually run it")
    did_insert=False #tbd on validation

    if False:
        results,tx=Neo.run_stmt(stmt,tx='')  #Returns result object (odd)
        print ("RESULT: "+str(results))

    else:
        try:
            for dd in Neo.iter_stmt(stmt):   #response to dict
                print ("cypher insert response> "+str(dd))
        except Exception as e:
            if 'Failed to read from defunct connection' in str(e):
                logging.error("[error] could NOT insert cypher statement *connection issue?: "+str(e))
                print ("** connection may have been killed:  https://github.com/neo4j/neo4j-python-driver/issues/484")
            else:
                print ("[error] could NOT insert cypher statement: "+str(stmt))
                logging.dev("[error] could NOT insert cypher statement at run_id: "+str(run_id))

    print ("[info] done insert_into_graph")
    return

def query_neo4j(stmt=''):
    if not stmt:
        stmt="""MATCH (n) RETURN n"""
        stmt="""MATCH (n) WHERE n.case_id = "case_1" RETURN n;"""

        ## Auto from llm write:
        stmt="""
        MATCH (r:Recipient)-[p:TRANSFERRED_TO {case_id: 'case_1'}]->()
        RETURN sum(p.transaction_amount) AS total_transaction_amount
        """
        
        ## Jon adjusts: WORKS
        stmt="""
        MATCH (r)-[p:TRANSFERRED_TO {case_id: 'case_1'}]->()
        RETURN sum(p.transaction_amount) AS total_transaction_amount
        """

    if 'explain query' in []:
        print ("EXPLAIN cypher query: "+str(stmt))
        responses=[]
        for dd in Neo.iter_stmt("EXPLAIN "+stmt):   #response to dict
            if isinstance(dd,list) and len(dd)==1:
                dd=dd[0]
            responses+=[dd]
        print ("explain response> "+str(responses))

    print ("Running query statement: "+str(stmt))
    responses=[]
    for dd in Neo.iter_stmt(stmt):   #response to dict
        if isinstance(dd,list) and len(dd)==1:
            dd=dd[0]
        responses+=[dd]
        print ("one response> "+str(dd))

    """
    RESPONSE:
    --->> total_transaction_amount values: 11498.449999999999
        > 11498.449999999999
    """
    return responses

def llm_write_question_query():
    question="""What is the total transaction amount for case_id='case_1'?"""

    ## Assume:  remove LabelName demo
    #MERGE (r16:Recipient {name:"Meher", id:"case_1_Meher", case_id:"case_1"})
    prompt="""
    I have a neo4j database with the following nodes and relationships (sample):
    MERGE (r16: {name:"Meher", id:"case_1_Meher", case_id:"case_1"})
CREATE (z)-[p16:TRANSFERRED_TO {
    case_id: "case_1",
    transaction_id: "",
    transaction_description: "Zelle Payment To Meher Jpm669604904",
    transaction_amount: 60.00,
    transaction_date: date("2021-08-04")
}]->(r16)

    Write a cypher query to answer the following question:
    """+question

    print ("[neo4j write cypher for my question]: "+str(prompt))
    LLM=OpenAILLM()
    response=LLM.prompt(prompt)
    print ("[debug auto cypher] RESPONSE: "+str(response))
    #dd=json.loads(response)

    #RESPONSE:
    """To answer the question "What is the total transaction amount for case_id='case_1'?", you can use the following Cypher query:

    '''
    MATCH (r:Recipient)-[p:TRANSFERRED_TO {case_id: 'case_1'}]->()
    RETURN sum(p.transaction_amount) AS total_transaction_amount
    ```
    
    This query matches all the relationships with the TRANSFERRED_TO label and the specified case_id value, and then calculates the sum of their transaction_amount property. The total transaction amount is returned as the result.
    """

    ## CLEAN (get from quotes)
    cleaned=[]
    state_opened=False
    state_closed=False
    pattern=r'\`\`\`'
    for liner in response.split('\n'):
        if re.search(pattern,liner) and state_opened:
            state_closed=True
            break
        elif re.search(pattern,liner) and not state_opened:
            state_opened=True #don't capture first line
        elif state_opened:
            cleaned.append(liner)
        else:
            pass

    resp=''
    if cleaned and state_closed:
        cleaned='\n'.join(cleaned)
    else:
        cleaned=response
    return cleaned

def dev1():
    logging.dev("Log jon test")
    return

if __name__=='__main__':
    branches=['dev_sample_llm_queries']
    branches=['transactions2cypher']

    branches=['cypher_samples']
    branches=['insert_into_graph']
    branches=['llm_write_question_query']

    branches=['query_neo4j']
    branches=['dev1']
    branches=['call_all']

    for b in branches:
        globals()[b]()




"""

    Here is a list of bank statement transactions.  Convert them to cypher statements ie/
    MERGE (z:Payer {name: "Zelle"})
    MERGE (r1:Recipient {name: "Lil Bro Alex"})
    CREATE (z)-[p1:TRANSFERRED_TO { 
        transaction_id: "Jpm674243402", 
        transaction_description: "Zelle Payment To Lil Bro Alex Jpm674243402", 
        transaction_amount: 200.00, 
        transaction_date: date("2021-08-09") 
    }]->(r1)
    =====
    {"all_transactions": [
    {
      "transaction_id": "1",
      "transaction_description": "Remote Online Deposit",
      "transaction_amount": "200.00",
      "transaction_date": "2021-08-26"
    },
    {
      "transaction_id": "",
      "transaction_description": "08/26/2021 Reversal: Orig CO Name:American Express",
      "transaction_amount": "4,213.77",
      "transaction_date": "2021-08-27"
    },
    {
      "transaction_id": "1",
      "transaction_description": "Remote Online Deposit",
      "transaction_amount": "500.00",
      "transaction_date": "2021-08-31"
    }]


    

"""
