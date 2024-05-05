import os
import sys
import time
import codecs
import json
import re

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from pypher import __, Pypher
from w_storage.gstorage.gneo4j import Neo

from a_agent.RUN_sim_wt import call_normal_full_run
from a_agent.sim_wt import wt_main_pipeline
from a_agent.sim_wt import get_job_state

from a_query.queryset1 import query_statements
from a_query.queryset1 import query_transaction
from a_query.queryset1 import query_transactions
from a_query.queryset1 import delete_transaction_node

from a_query.admin_query import admin_remove_case_from_kb

from get_logger import setup_logging
logging=setup_logging()


#0v1# JC  Sep 27, 2023  Init



def run_page_challenges():
    ##              CHALLENGE                 IDEA
    
    print (">> BOA & CHASE PRIORITIES!")

    challenges=[]
    challenges+=[('missing transactions','')]
    challenges+=[('no check numbers','use kb logic function to extract')]
    challenges+=[("Check images section is duplicate entries which could be interpreted as transactions..ensure they aren't",'use kb logic function to extract','Thought i dealt with but check')]
    
    ### SEPT 29
    #> chase example
    #> [ ] review/watch multiple pdf extraction methods + transaction id definition
    jon=[]
    jon+=['Do boa processing full run for BOA case_id=case_schoolkids Schoolkidsz December 2021 statement']
    jon=['do chase sample 1']
    jon=['check chase entities']
    jon=['chase checks and debits'] #Checks paid
    jon=['chase checks and debits2']
    jon=['chase checks and debits3']

    jon=['chase balances as amounts'] # oct 27
    
    if 'chase balances as amounts' in jon:
        #** found via visualization
        case_id='chase_2_barcenas'
        #PROBLEM:  Thinks balance is transaction amount
        #AREA:  llm_page2t
        #PAGE?  14  (found via OCR'd Chase Statements 2.pdf)

        options={}
        #ok        call_normal_full_run(case_id=case_id,b=['normal sample run'])

        options['only_pages']=[14]
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
        print ("[main_pipeline meta]: "+str(meta))

        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
        a=kk
        
    elif 'Do boa processing full run for BOA case_id=case_schoolkids Schoolkidsz December 2021 statement' in jon:
        case_id='case_schoolkids'
        #ok        call_normal_full_run(case_id=case_id,b=['normal sample run'])

        options={}
        options['only_pages']=[3] #case_schoolkids passed!
        options['only_pages']=[4] # 14 ok
        options['only_pages']=[10] # 76 checks?!
        options['only_pages']=[11] # end of checks, service feeds and balances
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
        
        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))


        print ("[ ] reminder:  qa_schema + call_kbai etc for formalizing all additions to data model")

    elif 'do chase sample 1' in jon:
        case_id='case_chase_dev_1'
        options={}
        #ok        call_normal_full_run(case_id=case_id,b=['normal sample run'])

        #options['only_pages']=[27]  #really first page
        # 47:: +/- transactions to appear properly!
        options['only_pages']=[47]  # [ ]   transaction where most are out (neg) but Transfer From Sav is positive!!
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))

    elif 'check chase entities' in jon:
        case_id='case_chase_dev_1'
        options={}
        #ok        call_normal_full_run(case_id=case_id,b=['normal sample run'])

        # 47:: +/- transactions to appear properly!
        options['only_pages']=[47]  # [ ]   transaction where most are out (neg) but Transfer From Sav is positive!!
#        manual_skip_caps=['start_KBAI_processing_pipeline']
        manual_skip_caps=['start_main_processing_pipeline']
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
    
    elif 'chase checks and debits' in jon:
        """
           3 cols mixed with 1 col & 350+ numbers
           Checks paid split!
        """
        case_id='case_o1_case_single'
        options={}
        #ok        call_normal_full_run(case_id=case_id,b=['normal sample run'])

        #options['only_pages']=[27]  #really first page
        # 47:: +/- transactions to appear properly!
        options['only_pages']=[2]  # [ ]   transaction where most are out (neg) but Transfer From Sav is positive!!
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))

    elif 'chase checks and debits2' in jon:
        """
        """
        case_id='case_o2_case_single'
        options={}

        options['only_pages']=[2] #< [x] 1 hidden transaction found with gpt-4 once compare against expected?!
        options['only_pages']=[1]

        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
        
    elif 'chase checks and debits3' in jon:
        """
        """
        
        print ("** 113 withdrawls or so across $28M -- good for detailed look")
        print ("continuum chase 1278")
        print ("OUTPOUT EXPECT>>> [challenge meta] transactions touched: 136")
        case_id='case_o3_case_single'
        #KEEP# admin_remove_case_from_kb(case_id=case_id)

        options={}

        options['only_pages']=[3] # 18
        options['only_pages']=[1] #[x] ok **THIS is standard 5 - Oct 5
        options['only_pages']=[2] # 20 expected. 20 found great!
        options['only_pages']=[]

        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
        


    else:
        stopp=unknown_challenge
    
    return

def run_kbai_challenges():
    ## Focus on kbai tasks:
    #- transaction method | type
    #- Entities
    #-
    jon=['chase checks and debits3']

    if False:
        
        pass

    elif 'chase checks and debits3' in jon:
        print ("** 113 withdrawls or so across $28M -- good for detailed look")
        print ("continuum chase 1278")
        case_id='case_o3_case_single'
        options={}

        options['only_pages']=[2] # 20 expected. 20 found great!
        options['only_pages']=[3] # 18
        options['only_pages']=[1] #[x] ok
        options['only_pages']=[]

        manual_skip_caps=['start_main_processing_pipeline']
        meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

        print ("[main_pipeline meta]: "+str(meta))
        print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
        

    return


def challenges_queries():
    b=['case to statements']
    b=['statement filename to transaction']
    
    if 'case to statements' in b:
        case_id='case_chase_dev_1'
        print ("Case to statement ids (for easy kb query)")
        
        for statement_id in query_statements(case_id=case_id):
            print ("statement id> "+str(statement_id))
            
            ## Now internally transactions!
            for transaction in query_transactions(statement_id=statement_id):
                print ("transaction> "+str(transaction))
                        
            break
        
    if 'statement filename to transaction' in b:
        ## of course filenames is NOT unique
        filename='Chase statements 1.pdf'
        filename='Schoolkidz-December-2021-statement.pdf'
        for transaction in query_transactions(filename=filename):
            print ("transaction> "+str(transaction))

    return


def challenge_narrow_audit():
    ## of course filenames is NOT unique
#    filename='Chase statements 1.pdf'
    filename='Schoolkidz-December-2021-statement.pdf'
    filename='Chase Statements 2.pdf'
    for transaction in query_transactions(filename=filename):
        if transaction['transaction_amount'] and not transaction['transaction_description']:
#        if str(transaction.get('filename_page_num',''))=='3':
#            print ("transaction> "+str(transaction))
            print ("transaction> "+str(transaction))
#OK carefull#            delete_transaction_node(transaction_id=transaction['id'])

    return

def local_admin_remove_case_from_kb(case_id=''):
    print ("REMOVING CASE FROM ADMIN: "+str(case_id))
    admin_remove_case_from_kb(case_id=case_id)
    return

def run_single_full_challenge():
    ## Above flexible but one function
    #options['only_pages']=[1] #[x] ok **THIS is standard 5 - Oct 5
    #options['only_pages']=[]
    options={}
    
    print (">>. RUN_sim_wt for full run")
    
    start_time=time.time()

    case_id='MarnerHoldings1' #14 pages 1 ok. [x] jon did one on local machine.
    case_id='pjplumbingA'  #?? did i start on server?
    case_id='rambouillettA'   # corrupt pdfs?
    case_id='rambouillettB'   # corrupt pdfs? -- retry should auto ocr!

    case_id='Marner'
    case_id='ColinTestCase'

    ###
    case_id='chase_2_barcenas' #700 pages
#    options['only_pages']=[632] #<-- no year in date
#fixed    case_id='chase_2_barcenas_nodate'
    case_id='chase_3_66_b' #"66 pages
    
    case_id='chase_3_66_b3'
    case_id='chase_3_66_b4'
    
#BEWARE    local_admin_remove_case_from_kb(case_id=case_id)

#    options['only_pages']=[2]

    

    case_id='chase_3_66_5ktransfer' #[x] ok
    

    case_id='chase_3_66_big'

    case_id='chase_4_a'

#ok#    case_id='chase_4_a_33'  #[ ] sample of unknown source 'Deposit' [ ] add as test??

#    case_id='chase_4_a' #[nov 7 rerun] 

    #options['only_pages']=[24] #chase_4_a should be non cause just summary
#    options['only_pages']=[6]

#ok via Irs sample.    case_id='chase_4_a_6'

    ## Nov 6
    #C:\scripts-23\watchtower\wcodebase\w_ui\file_manager\storage\chase_5_a

    case_id='chase_5_a'

    ## Nov 10 jon rerun
    case_id='chase_3_66_5ktransfer'

    case_id="MarnerHoldings"
    case_id="MarnerHoldingsJune" #page 1 of June
    case_id="MarnerHoldingsJune2" #page 1 of June

    case_id="MarnerHoldingsA" #Nov 23 run full again.
    case_id="MarnerHoldingsB"
    
    ###############################
    # DEC 7 Hello
    ###############################
    case_id="case_test_loc"
    ###############################
    # DEC 12 Hello
    ###############################
    case_id="6578e48c20668da6f77cd052"
    
    ## DEC 16 hello.  this frozen on remote so run local with verbose multithread
    case_id='6579bf870c64027a3b9f2cfe' #<-- seems to have finished??
    case_id='colin_dec_21_a'
    
    ## dec 17 sub page 69 of colin.  not seeing dot in ocr
    case_id='colin_69_no_dot_no_ocr'

    case_id='6580cfc69a57063d991de1aa'
    options['force_ocr']=False   #Will not go False because have global forced 
    #Global where??


    ## dec 18
    case_id='colin_dec_21_direct'

    ## DEC 19
    case_id='colin_wells_1_odd_page'

    ## dec 18 B
    case_id='colin_dec_21_direct_multi'

    ## dec 19
    case_id='colin_dec_21_direct_multi10'
    case_id='colin_dec_21_direct_multi12'
    case_id='colin_dec_21_direct_multi8'
    
    ## dec 20
    case_id='colin_wells_1_odd_page'

    case_id='colin_dec_1nonpage'
    case_id='colin_dec_2statements' #Looks good but got some bad from non page.

    case_id='65858e0c198ceb69d5058fc3' # 2 page wells fargo on server manual run


    ## BOA:  2/15 paused
    case_id='6587008b36850ea066e5843c' # BOA raw account summary should now be removed

    ## DEMO
    case_id='659839266c33e2599cce540d'
    case_id='65987c726c33e2599cce5eba'
    
    case_id='65987c726c33e2599cce5eba'
    

    ## Colin case with no titles?

    #
    #    -rw-rw-r-- 1 ubuntu ubuntu    105336 Jan 10 18:31 exe1_659ee02b6c33e2599cce68e2_2024_01_10_18_25.log
    #-rw-rw-r-- 1 ubuntu ubuntu    177695 Jan 10 18:37 exe1_659ee02b6c33e2599cce68e4_2024_01_10_18_24.log
    #-rw-rw-r-- 1 ubuntu ubuntu    113309 Jan 10 18:29 exe1_659ee02b6c33e2599cce68e6_2024_01_10_18_22.log

    case_id='659ee02b6c33e2599cce68e6' #Repetitive?? done 207??
    case_id='659ee02b6c33e2599cce68e4' # ran in 323 it seems
    case_id='659ee02b6c33e2599cce68e2'
    case_id='659f1c966c33e2599cce6d1c'

    case_id='6596f679c8fca0cb7b70e1fb' #Colin requires ocr   (ran but oops deleted some nodes)
    case_id='65a057c36c33e2599cce71d7'

    case_id='659457fca348734715059312' #wire transfer stopped or bad type class.

    case_id='65a7c36225abd0e6773a659e'  #Bank State Group
 
    case_id='65a7ce0bac045a667c77c7b5' #nohup_group12

    case_id='65a7ec01ac045a667c77c92b' #Pjp

    case_id='65c64ee590657f5b87e92666'
    case_id='65ccf25e9b6ff316a77a15bf' #M business
    case_id='65cd01899b6ff316a77a1988'
    case_id='65caaffb9b6ff316a779f525' #ashford_park_1'
    case_id='65cd01cd9b6ff316a77a19db' # check fraud?

    case_id='65caaffb9b6ff316a779f525' #ashford_park_1' Hogan LARGE NO DEL


    case_id='65cd06669b6ff316a77a1d21'  #TD redacted also long.

    case_id='65cd06669b6ff316a77a1d21_TDlean' #<-- requires OCR!


    case_id='65ca5aed9b6ff316a779e928_local' #Bad pdf?
    
    case_id='65ca5aed9b6ff316a779e928'   #Reprocess for pdf viewer (jon)

    case_id='6596f679c8fca0cb7b70e1fb' # New age redo kept timing out never worked

    case_id='65cbb7ac9b6ff316a779fac0' #Colin case 1-50 as deposit and weirds. [x] good
    case_id='65d65ae49be7358de5d1fb89' #James case. has dup node (2 statements ok. also, refined hallucination likely.)

    case_id='65960931c8fca0cb7b70e024' #123.45 case evan dad [ ] has bad check debit/credit

    case_id='65d11a8c04aa75114767637a_silent_1page' # azure ocr test
    case_id='65d11a8c04aa75114767637a' # Silent pipe entire with azure (no force gpt4 but 3.5 misses single column outputs)

    case_id='6596f679c8fca0cb7b70e1fb' #Evan main New Age demo but local possible to run?

    case_id='65960931c8fca0cb7b70e024' # still has bad check debit but not on single retest. redo mar 19

    case_id='65f9a28a7a047045e56b4df1' #Affinity...just don't do ocr
    case_id='65fa72717a047045e56b54bb'  #Test case odd debit on reversal
    

    case_id='affinity2pageoddyear'
    case_id='65f5d2d87a047045e56b3da0' #Chase Statements 2 but still on server so want clean view better dates
    
    ## Rerun old colin FirstCitizenBank case with 300 dpi and new setup (mar vs oct)
    case_id='ColinFCB1'

    ## JON TO RUN
    case_id='660446437a047045e56b7970'  #Short ok and viewable Done first 5pm 27th..
    
    case_id='65ca54869b6ff316a779e6d5' #many COLIN!

    case_id='660467cb7a047045e56b81e9'
    case_id='6603074b7a047045e56b730a'
    case_id='6604682d7a047045e56b823d'
    case_id='660445557a047045e56b7847'
    case_id='65caaffb9b6ff316a779f525'
    case_id='65cd01899b6ff316a77a1988'
    case_id='6602ebdb7a047045e56b71e0'
    case_id='66046a277a047045e56b82a4'
    case_id='66046d277a047045e56b82eb'
    case_id='66047d2b7a047045e56b8374'

    case_id='660446e97a047045e56b79c9' #optimza 2/4  started
    case_id='6604467c7a047045e56b7989' # 6604467c7a047045e56b7989 --> {'name': 'Sample bank statement__Chase - Test 3'
    case_id='660445ab7a047045e56b78c5' # 660445ab7a047045e56b78c5 --> {'name': 'Test 1',  started

    case_id='660446437a047045e56b7970' # DOD
    case_id='660445557a047045e56b7847' # Manual req



    options['force_ocr']=False

    local_admin_remove_case_from_kb(case_id=case_id)

    
    get_job_state(case_id=case_id) #WILL ALSO SYNC
    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=['start_KBAI_processing_pipeline'])
    print ("[challenge meta] transactions touched: "+str(meta.get('count_transactions','')))
    
    manual_skip_caps=['start_main_processing_pipeline']
    meta=wt_main_pipeline(case_id=case_id,options=options,manual_skip_caps=manual_skip_caps)

    print ("[main_kb meta]: "+str(meta))
        
    print ("RUNTIME FOR: "+str(case_id)+" "+str(time.time()-start_time))

    return


def make_sub_pdf():
    from w_pdf.pdf_extractor import alg_extract_pages_from_pdf
    pages=[12]


    print ("NEW base_storage_rel_dir")
    filename='________________rage/chase_3_66_5ktransfer/Chase Statements 4.pdf'
    out_filename='____________rage/chase_3_66_5ktransfer/Chase Statements 4 33.pdf'


    pages=[6]
    filename='___________________ger/storage/chase_4_a/Chase Statements 4.pdf'
    out_filename='______________i/file_manager/storage/chase_4_a/Chase Statements 4 6.pdf'
    
    filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/colin_dec_21_direct/well_fargo_all.pdf'
    out_filename='C:/scripts-23/watchtower/CASE_FILES_STORAGE/storage/colin_dec_21_direct/well_fargo_1_10.pdf'
    pages=[1,2,3,4,5,6,7,8,9,10]
    alg_extract_pages_from_pdf(filename,out_filename,keep_pages=pages)
    print ("WROTE: "+str(out_filename))

    return

if __name__=='__main__':
    branches=['challenges_queries']

    branches=['run_kbai_challenges']



    branches=['challenge_narrow_audit']
    branches=['run_page_challenges']

    branches=['make_sub_pdf']
    branches=['run_single_full_challenge']

    for b in branches:
        globals()[b]()




"""
Use JPM unique idenfiier on transaction?
 "receiver_id": "951) 2242099 Jpm696293969",


//  sample BOA withdrawls
            "section": "Withdrawals and other debits",			
WIRE TYPE:WIRE OUT DATE:211201 TIME:1724 ET\nTRN:2021120100554721 SERVICE REF:527479\nBNF:PAYCHEX, INC ID:512068399 BNF\nBK:JPMORGAN CHAS E BANK, N. ID:0002 PMT\nDET:21C1F14252DW2T361607-81 06 NewNet903712010554721			
AMERIFLEX LLC    DES:PPDFUNDING\nID:00000003841974  INDN:NewNet Secure\nTransact  CO ID:1223639401 PPD902535029125818			


// BOA lots of wire transfers
A lot of weird transactions					
	see:		file:///C:/scripts-23/watchtower/Watchtower%20Solutions%20AI/Bank%20Statements%20-%20for%20Beta%20Testing/Dec%2031%202021%20NST%20BOA%20Bank%20Statement.pdf		






"""


"""
Beginning Balance $346.25
200.00
200.00
500.00
5,562.50Web site:
Service Center:
Deaf and Hard of Hearing: 1-800-242-7383
Para Espanol: 1-877-312-4273
International Calls:
1-713-262-1679BERNADETTE S SHENOUDA
13834 HUNTERVALE DR
CORONA CA 92880 -3799
Chase Total Checking
Deposits and Additions 6,462.50
Checks Paid -500.00
ATM & Debit Card Withdrawals  -187.59
Electronic Withdrawals -1,270.46
Fees -12.00
5703  ^ 08/11 $500.00
If you see a check description in the Transaction Detail section, it means your check has already been converted for
electronic payment. Because of this, we're not able to return the check to you or show you an image on Chase.com.
^ An image of this check may be available for you to view on Chase.com.
07/17 ATM Cash Deposit        07/17 6060 Hamner Ave Mira Loma CA Card 5316 546.25
07/17 Card Purchase With Pin  07/15 Costco Whse #0432 Corona CA Card 5316 - 187.59 358.66
07/18 Deposit       900440779 558.66
07/19 Hmf              Hmfusa.Com                 PPD ID: 9200704262 - 203.62 355.04
07/28 Online Transfer From Chk ...2232 Transaction#: 6401153349 855.04
07/28 Waste Management Internet   043000092096276 Web ID: 9049038216 - 78.93 776.11
07/31 Att              Payment    191468004Myw9G  Web ID: 9864031005 - 322.87 453.24
08/07 Online Transfer From Chk ...5068 Transaction#: 6422347624 6,015.74
08/08 So Cal Edison CO Bill Paymt 139271126       Web ID: 4951240335 - 52.75 5,962.99
08/09 Discover         E-Payment  2341            Web ID: 2510020270 - 281.00 5,681.99
08/09 Citi Card Online Payment    112402544516699 Web ID: Citictp - 139.55 5,542.44CHECKING SUMMARY


"""
