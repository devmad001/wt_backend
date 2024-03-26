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


Storage=None
def init_Storage():
    global Storage
    Storage=Storage_Helper(storage_dir=LOCAL_PATH+"../w_datasets")
    Storage.init_db('functional_tests')
    return 


def store_gold_functional_test(record):
    return

def store_page2transactions(filename,page_number,page_text,transactions,record={}):
    global Storage
    if not Storage: init_Storage()

    id=filename+"-"+str(page_number)
    record['id']=id
    record['filename']=filename
    record['page_number']=page_number
    record['page_text']=page_text
    record['transactions']=transactions
    record['transactions_count']=len(transactions['all_transactions'])

    record['datetime']=str(datetime.datetime.now())


    print ("[info] saved gold transactions count: "+str(record['transactions_count']))
    print (str(record))
    record['jon_validated']=True
    Storage.db_put(id,'record',record,name='functional_tests')

    return


def dev1():
    return



page_samples=[]
page_samples+=['\n*start*deposits and additions\nDEPOSITS AND ADDITIONS\n  (continued)\nDATE\nDESCRIPTION\nAMOUNT\n08/26\nRemote Online Deposit              1\n200.00\n08/27\n08/26/2021 Reversal: Orig CO Name:American Express\n4,213.77\n08/31\nRemote Online Deposit              1\n500.00\nTotal Deposits and Additions\n$20,117.77\n*end*deposits and additions\n*start*atm debit withdrawal\nATM & DEBIT CARD WITHDRAWALS\n DATE\nDESCRIPTION\nAMOUNT\n08/02\nCard Purchase           08/01 Fitness Mania Riverside CA Card 7397\n$49.99\n08/03\nCard Purchase           08/02 Www.Paystubsnow.Com Www.Paystubsn TX Card 7413\n7.99\n08/09\nRecurring Card Purchase 08/07 Uber   Pass Help.Uber.Com CA Card 7397\n24.99\n08/18\nCard Purchase           08/17 Fedex 940635302952 Memphis TN Card 7413\n8.20\n08/19\nRecurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413\n24.99\n08/24\nATM Withdrawal          08/24 6400 Laurel Canyon B North Hollywo CA Card 7413\n700.00\n08/30\nRecurring Card Purchase 08/28 Dnh*Godaddy.Com Https://Www.G AZ Card 7413\n10.99\nTotal ATM & Debit Card Withdrawals\n$827.15\n*end*atm debit withdrawal\n*start*atm and debit card summary\nATM & DEBIT CARD SUMMARY\nHugo Arturo Flores Card 7397\nTotal ATM Withdrawals & Debits\n$0.00\nTotal Card Purchases\n$74.98\nTotal Card Deposits & Credits\n$0.00\nAnthony Joseph Guillen Card 7413\nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$52.17\nTotal Card Deposits & Credits\n$500.00\nATM & Debit Card Totals  \nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$127.15\n*end*atm and debit card summary\n*start*electronic withdrawal\nTotal Card Deposits & Credits\n$500.00\nELECTRONIC WITHDRAWALS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nZelle Payment To Anthony Bro Jpm665864367\n$3,000.00\n08/02\nZelle Payment To Jennifer Nell Jpm667436915\n10.00\n08/02\nZelle Payment To Jennifer Nell Jpm667437893\n200.00\n08/02\nZelle Payment To Jennifer Nell Jpm667438464\n10.00\n08/04\nZelle Payment To Lil Bro Alex Jpm669535918\n350.00\n08/04\nZelle Payment To Meher Jpm669604904\n60.00\n08/04 Orig CO Name:Citi Autopay           Orig ID:Citicardap Desc Date:210803 CO Entry\n105.53\nDescr:Payment   Sec:Tel    Trace#:091409685898393 Eed:210804   Ind ID:080502002630039\nInd Name:Hugo Flores Trn: 2165898393Tc\n08/05\nZelle Payment To Paris Sugi Dba 12323832406\n500.00\n08/06\nZelle Payment To Anthony Bro Jpm671584743\n300.00\n08/09\nZelle Payment To Lil Bro Alex Jpm674243402\n200.00\n08/12\nZelle Payment To Teisy Jpm677655611\n172.00\n08/13\nZelle Payment To Melissa Fw Jpm678129044\n1,000.00\n*end*']
page_samples+=['deposits and additions\n*start*atm debit withdrawal\nATM & DEBIT CARD WITHDRAWALS\n DATE\nDESCRIPTION\nAMOUNT\n08/02\nCard Purchase           08/01 Fitness Mania Riverside CA Card 7397\n$49.99\n08/03\nCard Purchase           08/02 Www.Paystubsnow.Com Www.Paystubsn TX Card 7413\n7.99\n08/09\nRecurring Card Purchase 08/07 Uber   Pass Help.Uber.Com CA Card 7397\n24.99\n08/18\nCard Purchase           08/17 Fedex 940635302952 Memphis TN Card 7413\n8.20\n08/19\nRecurring Card Purchase 08/19 Experian* Credit Repor 479-3436237 CA Card 7413\n24.99\n08/24\nATM Withdrawal          08/24 6400 Laurel Canyon B North Hollywo CA Card 7413\n700.00\n08/30\nRecurring Card Purchase 08/28 Dnh*Godaddy.Com Https://Www.G AZ Card 7413\n10.99\nTotal ATM & Debit Card Withdrawals\n$827.15\n*end*atm debit withdrawal\n*start*atm and debit card summary\nATM & DEBIT CARD SUMMARY\nHugo Arturo Flores Card 7397\nTotal ATM Withdrawals & Debits\n$0.00\nTotal Card Purchases\n$74.98\nTotal Card Deposits & Credits\n$0.00\nAnthony Joseph Guillen Card 7413\nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$52.17\nTotal Card Deposits & Credits\n$500.00\nATM & Debit Card Totals  \nTotal ATM Withdrawals & Debits\n$700.00\nTotal Card Purchases\n$127.15\n*end*atm and debit card summary\n*start*electronic withdrawal\nTotal Card Deposits & Credits\n$500.00\nELECTRONIC WITHDRAWALS\nDATE\nDESCRIPTION\nAMOUNT\n08/02\nZelle Payment To Anthony Bro Jpm665864367\n$3,000.00\n08/02\nZelle Payment To Jennifer Nell Jpm667436915\n10.00\n08/02\nZelle Payment To Jennifer Nell Jpm667437893\n200.00\n08/02\nZelle Payment To Jennifer Nell Jpm667438464\n10.00\n08/04\nZelle Payment To Lil Bro Alex Jpm669535918\n350.00\n08/04\nZelle Payment To Meher Jpm669604904\n60.00\n08/04 Orig CO Name:Citi Autopay           Orig ID:Citicardap Desc Date:210803 CO Entry\n105.53\nDescr:Payment   Sec:Tel    Trace#:091409685898393 Eed:210804   Ind ID:080502002630039\nInd Name:Hugo Flores Trn: 2165898393Tc\n08/05\nZelle Payment To Paris Sugi Dba 12323832406\n500.00\n08/06\nZelle Payment To Anthony Bro Jpm671584743\n300.00\n08/09\nZelle Payment To Lil Bro Alex Jpm674243402\n200.00\n08/12\nZelle Payment To Teisy Jpm677655611\n172.00\n08/13\nZelle Payment To Melissa Fw Jpm678129044\n1,000.00\n*end*']


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""