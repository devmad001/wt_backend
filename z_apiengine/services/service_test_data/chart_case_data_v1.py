import os
import sys
import codecs
import json
import re
import pandas as pd

from fastapi import FastAPI

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

sys.path.insert(0,LOCAL_PATH+"../..")

from get_logger import setup_logging
logging=setup_logging()

        
#0v1# JC Nov 26, 2023  Setup


"""
    HARD CODE BARCHART DATA FOR FE DEV
    
    case_chart_data_v1

"""

def get_square_data_sample(case_id):
    if not case_id=='case_chart_data_v1': raise Exception('case_id must be case_chart_data_v1')
    #'data': added at router
    data=[{"Transaction Date":"2021-06-09","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify Orig Id:1800948598 Desc Date: Co Entry Descr: Transfer Sec:Ccd Trace#:091000011378480 Eed: 210609 Ind Id:St-Bbgotowsex1Go Ind Name:Marner Holdings Inc Trn: 1601378480Tc¢C","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"37466.58"},{"Transaction Date":"2021-06-11","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000019099895 Eed:210611 Ind |Id:St-D1F8S8A7C5Y2 Ind Name:Marner Holdings Inc Trn: 1629099895Tc¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"32122.98"},{"Transaction Date":"2021-06-14","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify Orig Id: 1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000010059214 Eed:210614 Ind |Id:St-R8A6V7T8Tors3 Ind Name:Marner Holdings Inc Trn: 1650059214Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"36964.36"},{"Transaction Date":"2021-06-29","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr.Transfer Sec:Ccd Trace#:091000013822777 Eed: 210629 Ind Id:St-G204J71.2D0Z4 Ind Name:Marner Holdings Inc Trn: 1803822777Tc¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"58326.34"},{"Transaction Date":"2021-06-10","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/10 Online Domestic Wire Transfer Via: Bbva Usa/122105744 A/C. Mach 1 Tempe Az 21,623.36 | 85282 Us Imad: 0610B1Qgc05C002353 Trn: 3085551161Es","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"21623.36"},{"Transaction Date":"2021-06-11","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/11 Online International Wire Transfer A/C. Foreign Cur Bus Acct Bk 1 Columbus Newark De 33,780.39 | 197132107 Us Org: 00000000539360823 Marner Holdings Inc | Ben:/Pt50003300000005824471805 Armindo Freitas Ref. Business | Expenses/Ocmt/Eur27041,20/Exch/0.8005/Cntr/25751373/ Trn: 5184500162Re","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"33780.39"},{"Transaction Date":"2021-06-15","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/15 Online International Wire Transfer A/C. Foreign Cur Bus Acct Bk 1 Columbus Newark De 17,171.19 | 197132107 Us Org: 00000000539360823 Marner Holdings Inc | Ben:/Pt5000330000000582447 1805 Armindo Freitas Ref. Business | Expenses/Ocmt/Eur13781,60/Exch/0.8026/Cntr/30267038/ Trn: 8294000166Re","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"17171.19"},{"Transaction Date":"2021-06-15","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/15 Online International Wire Transfer A/C. Foreign Cur Bus Acct Bk 1 Columbus Newark De 17,459.87 | 197132107 Us Org: 00000000539360823 Marner Holdings Inc | Ben:/Pt50003300000005824471805 Armindo Freitas Ref: Business | Expenses/Ocmt/Eur14013,29/Exch/0.8026/Cntr/28452871/ Trn: 8594500166Re","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"17459.87"},{"Transaction Date":"2021-06-15","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000019624546 Eed:210615 Ind |Id:St-T8C2E4G4C2D2 Ind Name:Marner Holdings Inc Trn: 1669624546Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"67710.30"},{"Transaction Date":"2021-06-16","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr.Transfer Sec:Ccd Trace#:091000013488826 Eed:210616 Ind |D:St-W3L7J4H1Pou2 Ind Name:Marner Holdings Inc Trn: 1673488826Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"31882.33"},{"Transaction Date":"2021-06-17","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr.Transfer Sec:Ccd Trace#:091000011101308 Eed:210617 Ind |D:St-R8Gop4S3Z25X9 Ind Name:Marner Holdings Inc Trn: 1681101308Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"26220.80"},{"Transaction Date":"2021-06-21","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr.Transfer Sec:Ccd Trace#:091000010900414 Eed:210621 Ind |D:St-L3R5P6B5Sm3C9 Ind Name:Marner Holdings Inc Trn: 1720900414Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"28510.09"},{"Transaction Date":"2021-06-02","Filename Page Num":1,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify | Orig 1D:1800948598 | Desc Date: Co Entry | Descr: Transfer Sec:Ccd Trace#:091000010766693 Eed:210602 Ind | D: St-Goj8Rom4X3D1 Ind Name:Marner Holdings Inc Trn: 1530766693T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"141608.20"},{"Transaction Date":"2021-06-04","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig I1D:1800948598 Desc Date: Co Entry Descr: Transfer Sec:Ccd Trace#:091000015370824 Eed: 210604 Ind Id:St-Q0Y8W1S8L0U9S Ind Name:Marner Holdings Inc Trn: 1555370824 T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"43773.31"},{"Transaction Date":"2021-06-18","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"Orig Co Name:Rp Shopity Orig Id: 1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000011513644 Eed:210618 Ind |D:St-Z5E7Z6 X0F2Q9 Ind Name:Marner Holdings Inc Trn: 1691513644 Tc","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"28107.12"},{"Transaction Date":"2021-06-01","Filename Page Num":1,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"","Transaction Description":"Orig Co Name:Rp Shopity | Orig 1D:1800948598 | Desc Date: Co Entry | Descr. Transfer Sec:Ccd Trace#:091000018254113 Eed:210601 Ind | D:St-G208N4V4Q1L0 Ind Name:Marner Holdings Inc Trn: 1528254113Tc¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"","Transaction Amount":"19066.24"},{"Transaction Date":"2021-06-03","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr:. Transfer Sec:Ccd Trace#:091000018291335 Eed: 210603 Ind Id:St-Z7M602Q7D8N6 Ind Name:Marner Holdings Inc Trn: 1548291335T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"42422.46"},{"Transaction Date":"2021-06-07","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000013223905 Eed: 210607 Ind |D:St-M4Y9L4U2Mol8 Ind Name:Marner Holdings Inc Trn: 1583223905T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"14355.77"},{"Transaction Date":"2021-06-08","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr: Transfer Sec:Ccd Trace#:091000010358840 Eed: 210608 Ind |D: St-J8Q2R874Q4K1 Ind Name:Marner Holdings Inc Trn: 1590358840T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"81027.18"},{"Transaction Date":"2021-06-10","Filename Page Num":2,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr: Transfer Sec:Ccd Trace#:091000010007002 Eed: 210610 Ind Id:St-H2K3T8Da4As5P5 Ind Name:Marner Holdings Inc Trn: 1610007002T¢C","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"32616.74"},{"Transaction Date":"2021-06-15","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Online Transfer From Chk ...5635 Transaction#: 11983779146","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"35000.00"},{"Transaction Date":"2021-06-18","Filename Page Num":3,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Online Transfer From Chk ...5635 Transaction#: 11999794568","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"50000.00"},{"Transaction Date":"2021-06-22","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000013423214 Eed:210622 Ind Id:St-1I9W2C4T807L7 Ind Name:Marner Holdings Inc Trn: 1733423214T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"71339.13"},{"Transaction Date":"2021-06-23","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000013542925 Eed: 210623 Ind Id: St-A5Q7 X2N8C4W9 Ind Name:Marner Holdings Inc Trn: 1743542925T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"28191.53"},{"Transaction Date":"2021-06-24","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000019698412 Eed: 210624 Ind Id:St-T1V3N8G5Z8A6 Ind Name:Marner Holdings Inc Trn: 1759698412T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"12709.71"},{"Transaction Date":"2021-06-25","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Online Transfer From Chk ...5635 Transaction#: 12043277798","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"100000.00"},{"Transaction Date":"2021-06-25","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000018280307 Eed: 210625 Ind Id:St-Wor3K5Y1G7G6 Ind Name:Marner Holdings Inc Trn: 1768280307 T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"27794.39"},{"Transaction Date":"2021-06-28","Filename Page Num":4,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Orig Co Name:Rp Shopify Orig 1D:1800948598 Desc Date: Co Entry Descr. Transfer Sec:Ccd Trace#:091000016600548 Eed: 210628 Ind Id:St-Dokse4Am5G8S0 Ind Name:Marner Holdings Inc Trn: 1796600548T¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"24067.82"},{"Transaction Date":"2021-06-30","Filename Page Num":5,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Deposit","Transaction Description":"Orig Co Name:Rp Shopify Orig Id: 1800948598 Desc Date: Co Entry Descr: Transfer Sec:Ccd Trace#:091000011121446 Eed:210630 Ind |D:St-Wse9Sz8W2E3Q9 Ind Name:Marner Holdings Inc Trn: 1811121446Tc¢","Section":"Deposits And Additions","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"21728.23"},{"Transaction Date":"2021-06-01","Filename Page Num":8,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"2021/05/31 Online Transfer To Chk ...5635 Transaction#: 11878630156 36,000.00","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"36000.00"},{"Transaction Date":"2021-06-03","Filename Page Num":9,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"Orig Co Name:Shopify Capital Orig Id:7811161726 Desc Date:210602 Co Entry 8,0565.56 Descr:Rhtluzyyk Sec:Ccd  Trace#:121140394703417 Eed:210603 Ind Id:4098770 Ind Name:Marner Holdings Inc Trn: 1544703417 Tc","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"80565.56"},{"Transaction Date":"2021-06-03","Filename Page Num":9,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/03 Online International Wire Transfer A/C: Foreign Cur Bus Acct Bk 1 Columbus Newark De 186,636.80 197132107 Us Org: 00000000539360823 Marner Holdings Inc Ben:/Pt50003300000005824471805 Armindo Freitas Ref. Business Expenses/Ocmt/Eur150000,00/Exch/0.8037/Cntr/20680213/ Trn: 6250500154Re","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"186636.80"},{"Transaction Date":"2021-06-07","Filename Page Num":9,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/07 Online Transfer To Chk ...5635 Transaction#: 11928352281","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Online_Payment","Transaction Amount":"25000.00"},{"Transaction Date":"2021-06-07","Filename Page Num":9,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"2021/06/07 Online Domestic Wire Transfer Via: Gts Southern Sf Mo/286573322 A/C: Watch Chest Llc Branson Mo 65616 Us Ref: Order 1000003713 Imad: 0607B1Qgc06C008111 Trn: 3409321158Es","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Wire_Transfer","Transaction Amount":"17500.00"},{"Transaction Date":"2021-06-08","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"Orig Co Name:Shopify Capital Orig Id:7811161726 Desc Date:210607 Co Entry 3,5636.16 | Descr:Rnhvdnzpk Sec:Ccd  Trace#:121140396796923 Eed:210608 Ind Id:4163198 | Ind Name:Marner Holdings Inc Trn: 1596796923T¢","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Online_Payment","Transaction Amount":"35636.16"},{"Transaction Date":"2021-06-10","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"Orig Co Name:Gusto Orig Id:9138864001 Desc Date:210610 Co Entry Descr:Net 15,493.06 | 647873Sec:Ccd  Trace#:021000020463178 Eed:210610 Ind Id:6Semjptg70O4 | Ind Name:Marner Holdings Inc","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Online_Payment","Transaction Amount":"15493.06"},{"Transaction Date":"2021-06-14","Filename Page Num":10,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"2021/06/14 Online Transfer To Chk ...5635 Transaction#: 11973738486","Section":"Electronic Withdrawals","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"25000.00"},{"Transaction Date":"2021-06-25","Filename Page Num":12,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Withdrawal","Transaction Description":"Online International Wire Transfer A/C: Foreign Cur Bus Acct Bk 1 Columbus Newark De | 197132107 Us Org: 00000000539360823 Marner Holdings Inc | Ben:/Pt50003300000005824471805 Armindo Freitas Ref: Nonebusiness | Expenses/Ocmt/Eur100000,00/Exch/0.8212/Cntr/31798590/Acc/None Trn: 9824200176Re","Section":"","Account Number":"000000539360823","Transaction Method":"Online_Payment","Transaction Amount":"121773.02"},{"Transaction Date":"2021-06-26","Filename Page Num":12,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Payment","Transaction Description":"Payment To Chase Card Ending In 3510","Section":"","Account Number":"000000539360823","Transaction Method":"Other","Transaction Amount":"10651.37"},{"Transaction Date":"2021-06-29","Filename Page Num":12,"Filename":"2021-06June-Statement-0823.Pdf","Transaction Type":"Transfer","Transaction Description":"Online Transfer To Chk ...5635 Transaction#: 12068612327","Section":"","Account Number":"000000539360823","Transaction Method":"Online_Payment","Transaction Amount":"16000.00"}]
    return data

def get_barchart_data_sample(case_id):
    if not case_id=='case_chart_data_v1': raise Exception('case_id must be case_chart_data_v1')
    #'data': added at router
    data={}
    data['records']=[{"stacks":"other","other":10651.37,"wire_transfer":0,"online_payment":0,"":0},{"stacks":"wire_transfer","other":0,"wire_transfer":17500.0,"online_payment":0,"":0},{"stacks":"online_payment","other":0,"wire_transfer":0,"online_payment":16000.0,"":0},{"stacks":"","other":0,"wire_transfer":0,"online_payment":0,"":0}]

    style={}
    style['x_axis_title']='Transaction Method'
    style['y_axis_title']='Transaction Amount'
    style['main_title']=''
    
    big_data={}
    big_data['data']=data
    big_data['style']=style
    return big_data

def get_butterfly_data_sample(case_id):
    if not case_id=='case_chart_data_v1': raise Exception('case_id must be case_chart_data_v1')
    #'data': added at router
    data={"butterfly_sorted":[{"name":"Beam-Premium","debit_total":111.72,"credit_total":0.0},{"name":"Card 7413","debit_total":579.42,"credit_total":0.0},{"name":"Afterpay US, Inc","debit_total":944.54,"credit_total":297.5},{"name":"Commerzbank Aktiengesellschaft Frankfurt Am Main Germany","debit_total":1730.4,"credit_total":0.0},{"name":"Wells Fargo Bank, N.A.","debit_total":3510.95,"credit_total":0.0},{"name":"Apintego","debit_total":3726.24,"credit_total":0.0},{"name":"Sav","debit_total":5270.75,"credit_total":0.0},{"name":"So Cal Edison","debit_total":13567.5,"credit_total":0.0},{"name":"United Healthcar","debit_total":19201.2,"credit_total":0.0},{"name":"Bbva USA","debit_total":21623.36,"credit_total":0.0},{"name":"Citibank West Fsb","debit_total":30000.0,"credit_total":0.0},{"name":"Great-West Trust","debit_total":73338.36,"credit_total":0.0},{"name":"Ssbtrustops","debit_total":100272.3,"credit_total":83994.11},{"name":"Shoppayinst Afrm","debit_total":118772.61,"credit_total":18871.17},{"name":"Skyview Capital","debit_total":145998.66,"credit_total":74549.76},{"name":"Guideline Retire","debit_total":176598.68,"credit_total":0.0},{"name":"Skyview Capital Group","debit_total":203735.19,"credit_total":0.0},{"name":"Coldhearted Studio","debit_total":219761.09,"credit_total":0.0},{"name":"Gusto","debit_total":316295.91,"credit_total":48219.78},{"name":"Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107 US","debit_total":371584.29,"credit_total":173443.98},{"name":"Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107","debit_total":545316.95,"credit_total":0.0},{"name":"Affirm, Inc","debit_total":578966.07,"credit_total":40220.01},{"name":"Foreign Exch Rt ADJ","debit_total":862628.25,"credit_total":11.44},{"name":"Card 6034","debit_total":1412322.03,"credit_total":0.0},{"name":"Rp Shopify","debit_total":18535022.65,"credit_total":0.0},{"name":"Shopify Capital","debit_total":31586070.46,"credit_total":30504632.48},{"name":"KIm Netherla 07415046","debit_total":0.0,"credit_total":0.64},{"name":"KIm Netherla 07415046 Gp Amstelveen","debit_total":0.0,"credit_total":0.64},{"name":"Osha4dless","debit_total":0.0,"credit_total":5.99},{"name":"858-2083835","debit_total":0.0,"credit_total":5.99},{"name":"Usps","debit_total":0.0,"credit_total":15.75},{"name":"Card 5929","debit_total":0.0,"credit_total":18.99},{"name":"Adobe.Ly/Enus","debit_total":0.0,"credit_total":20.99},{"name":"Costco Whse #0569 Commerce","debit_total":0.0,"credit_total":28.52},{"name":"Usps Change of Addres","debit_total":0.0,"credit_total":31.5},{"name":"Cafe Santiago Porto","debit_total":0.0,"credit_total":37.07},{"name":"Fedex 94mphis TN","debit_total":0.0,"credit_total":38.88},{"name":"Fitness Mania","debit_total":0.0,"credit_total":38.88},{"name":"Amzn Mkip US*2R26G7Y","debit_total":0.0,"credit_total":49.59},{"name":"Amzn Mkip US*2X2015J","debit_total":0.0,"credit_total":52.89},{"name":"Hitpsshopify.","debit_total":0.0,"credit_total":54.09},{"name":"Shopify* 112556669 Hitpsshopify.","debit_total":0.0,"credit_total":54.09},{"name":"Adobe *obe.Ly/Enus","debit_total":0.0,"credit_total":62.97},{"name":"Kim Netherla 07415046 Gp","debit_total":0.0,"credit_total":64.68},{"name":"Amstelveen","debit_total":0.0,"credit_total":64.68},{"name":"Kim Netherla 07415046 Gp Amstelveen","debit_total":0.0,"credit_total":64.68},{"name":"Shahnaz Akter","debit_total":0.0,"credit_total":67.91},{"name":"Shell Service Station Long Beach","debit_total":0.0,"credit_total":70.0},{"name":"Costco","debit_total":0.0,"credit_total":85.56},{"name":"Microsoft*Ultimate 1 M Msbill.Info WA","debit_total":0.0,"credit_total":89.94},{"name":"Msbill.Info","debit_total":0.0,"credit_total":89.94},{"name":"Microsoft","debit_total":0.0,"credit_total":89.94},{"name":"Hooters of Long Beach","debit_total":0.0,"credit_total":90.0},{"name":"2Staples Centr 14547301","debit_total":0.0,"credit_total":92.01},{"name":"2Staples","debit_total":0.0,"credit_total":92.01},{"name":"Shipstation","debit_total":0.0,"credit_total":99.0},{"name":"512-485-4282","debit_total":0.0,"credit_total":99.0},{"name":"Amzn Mktp","debit_total":0.0,"credit_total":103.89},{"name":"Autozone 3980","debit_total":0.0,"credit_total":107.16},{"name":"Rolling Tires & Wheel","debit_total":0.0,"credit_total":114.96},{"name":"Rolling Tires & Wheel Bell Gardens","debit_total":0.0,"credit_total":114.96},{"name":"Vaccarum","debit_total":0.0,"credit_total":123.76},{"name":"Wal-Mart #5045","debit_total":0.0,"credit_total":135.96},{"name":"Wal-Mart","debit_total":0.0,"credit_total":135.96},{"name":"Uber Trip","debit_total":0.0,"credit_total":143.02},{"name":"Apple.Com/Bill","debit_total":0.0,"credit_total":146.79},{"name":"The Guardian","debit_total":0.0,"credit_total":158.45},{"name":"Shell Service Station","debit_total":0.0,"credit_total":183.92},{"name":"Etsy.Com","debit_total":0.0,"credit_total":194.7},{"name":"The Home Depot #0654","debit_total":0.0,"credit_total":239.13},{"name":"Gaucho Grill","debit_total":0.0,"credit_total":250.0},{"name":"Staples","debit_total":0.0,"credit_total":251.28},{"name":"Staples 1367 Huntington PA","debit_total":0.0,"credit_total":251.28},{"name":"Staples 1367 Huntington PA CA","debit_total":0.0,"credit_total":251.28},{"name":"Fernish Hitpswww.Fern","debit_total":0.0,"credit_total":260.78},{"name":"Parque Silo Auto Porto","debit_total":0.0,"credit_total":276.48},{"name":"The Home Depot #6627","debit_total":0.0,"credit_total":288.95},{"name":"Porto","debit_total":0.0,"credit_total":310.25},{"name":"Adobe","debit_total":0.0,"credit_total":314.85},{"name":"Autozone","debit_total":0.0,"credit_total":321.48},{"name":"Tam's Super Burgers #2","debit_total":0.0,"credit_total":344.68},{"name":"Amzn Mkip US*2X0K70T","debit_total":0.0,"credit_total":386.91},{"name":"Doordash*Chick-Fil-A","debit_total":0.0,"credit_total":390.18},{"name":"888-202-3007","debit_total":0.0,"credit_total":428.33},{"name":"Four Season","debit_total":0.0,"credit_total":435.0},{"name":"Beverly Hills CA","debit_total":0.0,"credit_total":435.0},{"name":"The Home Depot #0608","debit_total":0.0,"credit_total":440.55},{"name":"Airbnb Hmcckb55Er9 Airbnb.Com CA","debit_total":0.0,"credit_total":465.9},{"name":"Guideline Inc","debit_total":395.0,"credit_total":474.0},{"name":"Rue Porter Afterpay","debit_total":476.0,"credit_total":476.0},{"name":"Google *Gsuite_Ruepo Cc@ Google.Com","debit_total":0.0,"credit_total":576.0},{"name":"Google *Gsuite_Ruepo Cc","debit_total":0.0,"credit_total":576.0},{"name":"Google *Gsuite_Ruepo","debit_total":0.0,"credit_total":576.0},{"name":"Hakan Bagci","debit_total":0.0,"credit_total":576.8},{"name":"Amzn Mkip US*2X1DR6M Amzn.Com/Bill WA","debit_total":0.0,"credit_total":579.42},{"name":"Portos Bakery","debit_total":0.0,"credit_total":617.5},{"name":"Spectrum","debit_total":0.0,"credit_total":668.91},{"name":"Fernish","debit_total":0.0,"credit_total":782.34},{"name":"R De Passos Manuel","debit_total":0.0,"credit_total":817.29},{"name":"Lzc* Legal Plan","debit_total":0.0,"credit_total":840.0},{"name":"Amzn Mktp US","debit_total":0.0,"credit_total":844.65},{"name":"Ca","debit_total":0.0,"credit_total":880.83},{"name":"Facebk Mk8635P3U2","debit_total":0.0,"credit_total":900.0},{"name":"650-5434800","debit_total":0.0,"credit_total":900.0},{"name":"Ssense.Com","debit_total":0.0,"credit_total":1077.48},{"name":"Ssense.Com Montreal Qc","debit_total":0.0,"credit_total":1077.48},{"name":"Uber","debit_total":0.0,"credit_total":1119.51},{"name":"Bookly - Kpmg","debit_total":0.0,"credit_total":1170.0},{"name":"Amzn.Com/Bill","debit_total":0.0,"credit_total":1324.05},{"name":"Cash","debit_total":0.0,"credit_total":1686.42},{"name":"Airbnb Hmcck55Er9","debit_total":0.0,"credit_total":1747.68},{"name":"Airbnb.Com","debit_total":0.0,"credit_total":1747.68},{"name":"Att*Bill Payment","debit_total":0.0,"credit_total":1941.36},{"name":"800-288-2020","debit_total":0.0,"credit_total":1941.36},{"name":"American Clothing Supp Los Angeles CA","debit_total":0.0,"credit_total":1956.0},{"name":"American Clothing Supp","debit_total":0.0,"credit_total":1956.0},{"name":"Petsuites","debit_total":0.0,"credit_total":1992.63},{"name":"Petsuites Spring","debit_total":0.0,"credit_total":1992.63},{"name":"Hiscox Inc","debit_total":0.0,"credit_total":2161.41},{"name":"Amzn.Com/Bill WA","debit_total":0.0,"credit_total":2196.0},{"name":"Paypal *Shop Nyt Ebay","debit_total":0.0,"credit_total":2409.54},{"name":"Paypal","debit_total":0.0,"credit_total":2550.0},{"name":"The Home Depot","debit_total":0.0,"credit_total":2628.13},{"name":"All IN One Suppliers","debit_total":0.0,"credit_total":2659.09},{"name":"Facebk 35Q346F3U2","debit_total":0.0,"credit_total":2700.0},{"name":"Gucci Store","debit_total":0.0,"credit_total":2760.38},{"name":"Gucci Store 21","debit_total":0.0,"credit_total":2760.38},{"name":"Doordash*Benihana","debit_total":0.0,"credit_total":3292.3},{"name":"Ferrari Financia","debit_total":0.0,"credit_total":4179.54},{"name":"Luxury Lea- 5086","debit_total":0.0,"credit_total":5101.6},{"name":"Amzn Mkip","debit_total":0.0,"credit_total":5256.09},{"name":"Sprint *Wireless","debit_total":0.0,"credit_total":6580.35},{"name":"Airbnb","debit_total":0.0,"credit_total":10291.4},{"name":"800-4633339 TN","debit_total":0.0,"credit_total":10346.91},{"name":"800-4633339","debit_total":0.0,"credit_total":11324.47},{"name":"Indeed","debit_total":0.0,"credit_total":12067.5},{"name":"Bcbs Health Hps","debit_total":8077.76,"credit_total":14136.08},{"name":"Chk...5635","debit_total":0.0,"credit_total":16000.0},{"name":"Hitpsshopify","debit_total":0.0,"credit_total":16918.32},{"name":"Shopify* 111567098 Hitpsshopify. IL","debit_total":0.0,"credit_total":16918.32},{"name":"0007Marner Holdings","debit_total":0.0,"credit_total":19201.2},{"name":"Kaner Vonap","debit_total":0.0,"credit_total":21100.0},{"name":"Transaction#: 1","debit_total":0.0,"credit_total":25000.0},{"name":"Facebk","debit_total":0.0,"credit_total":25200.0},{"name":"Shopify","debit_total":0.0,"credit_total":33890.73},{"name":"Watch Chest LLC","debit_total":0.0,"credit_total":35000.0},{"name":"Eddie Rojas","debit_total":0.0,"credit_total":40600.0},{"name":"Chubb-Sci","debit_total":26384.4,"credit_total":56538.0},{"name":"Mach 1","debit_total":0.0,"credit_total":64870.08},{"name":"Marner Holdings","debit_total":41541.15,"credit_total":83763.48},{"name":"Newnet Communication Techn","debit_total":0.0,"credit_total":91621.62},{"name":"Chk ...5635","debit_total":0.0,"credit_total":168000.0},{"name":"American Express","debit_total":91550.0,"credit_total":322025.0},{"name":"Chase Card","debit_total":0.0,"credit_total":345713.06},{"name":"Foreign Cur Bus Acct","debit_total":0.0,"credit_total":365319.06},{"name":"Allstate Nbindco","debit_total":0.0,"credit_total":501254.79},{"name":"Chk","debit_total":215400.0,"credit_total":619000.0},{"name":"Kaner Apelacio","debit_total":72080.0,"credit_total":621309.13},{"name":"Rue Porter","debit_total":110558.17,"credit_total":831456.84},{"name":"Armindo Freitas","debit_total":0.0,"credit_total":1183993.13},{"name":"Fedex","debit_total":0.0,"credit_total":5734757.36}]}

    style={}
    style['x_axis_title']='Debit/Credit Amounts'
    style['y_axis_title']='Entities'
    style['main_title']='Debit and Credit Amounts by Entity'
    style['time_period']='2022-02-1 - 2022-06-01'

    big_data={}
    big_data['data']=data
    big_data['style']=style
    return big_data

def get_waterfall_data_sample(case_id):
    if not case_id=='case_chart_data_v1': raise Exception('case_id must be case_chart_data_v1')
    #'data': added at router
    #** think too negative!
    big_data={}
    big_data['data']={"balance_by_date":{"2021-06-01":7349.72,"2021-06-02":-38646.21,"2021-06-03":-872170.96,"2021-06-04":-880058.81,"2021-06-07":-1060675.88,"2021-06-08":-1277785.64,"2021-06-09":-1286152.66,"2021-06-10":-1423949.72,"2021-06-11":-1660990.8,"2021-06-14":-1725711.64,"2021-06-15":-1835112.38,"2021-06-16":-1876612.23,"2021-06-17":-1927753.61,"2021-06-18":-1826971.04,"2021-06-21":-1790676.98,"2021-06-22":-1503657.06,"2021-06-23":-1434306.76,"2021-06-24":-1479683.8,"2021-06-25":-1998203.6,"2021-06-26":-2030157.71,"2021-06-28":-1970865.75,"2021-06-29":-1836231.43,"2021-06-30":-1745983.1},"waterfall_by_date":{"2021-06-01":{"debit":-132106.68,"credit":26105.21},"2021-06-02":{"debit":-194476.29,"credit":148480.36},"2021-06-03":{"debit":-883002.86,"credit":49478.11},"2021-06-04":{"debit":-53321.79,"credit":45433.94},"2021-06-07":{"debit":-197116.12,"credit":16499.05},"2021-06-08":{"debit":-300574.91,"credit":83465.15},"2021-06-09":{"debit":-46164.04,"credit":37797.02},"2021-06-10":{"debit":-172272.98,"credit":34475.92},"2021-06-11":{"debit":-270416.71,"credit":33375.63},"2021-06-14":{"debit":-139600.18,"credit":74879.34},"2021-06-15":{"debit":-216668.4,"credit":107267.66},"2021-06-16":{"debit":-75562.4,"credit":34062.55},"2021-06-17":{"debit":-78685.11,"credit":27543.73},"2021-06-18":{"debit":-28016.52,"credit":128799.09},"2021-06-21":{"debit":-13020.25,"credit":49314.31},"2021-06-22":{"debit":-3590.52,"credit":290610.44},"2021-06-23":{"debit":-43961.58,"credit":113311.88},"2021-06-24":{"debit":-98723.72,"credit":53346.68},"2021-06-25":{"debit":-775595.98,"credit":257076.18},"2021-06-26":{"debit":-31954.11,"credit":0},"2021-06-28":{"debit":-40517.52,"credit":99809.48},"2021-06-29":{"debit":-106712.42,"credit":241346.74},"2021-06-30":{"debit":-50590.69,"credit":140839.02}}}

    style={}
    style['x_axis_title']='Date'
    style['y_axis_title']='Amounts'
    style['main_title']='Balance over time'

    big_data['style']=style
    return big_data



if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
        


"""

http://127.0.0.1:8008/api/v1/case/case_chart_data_v1/square_data
http://127.0.0.1:8008/api/v1/case/case_chart_data_v1/barchart_data
http://127.0.0.1:8008/api/v1/case/case_chart_data_v1/butterfly_data
http://127.0.0.1:8008/api/v1/case/case_chart_data_v1/waterfall_data


https://core.epventures.co/api/v1/case/case_chart_data_v1/square_data
https://core.epventures.co/api/v1/case/case_chart_data_v1/barchart_data
https://core.epventures.co/api/v1/case/case_chart_data_v1/butterfly_data
https://core.epventures.co/api/v1/case/case_chart_data_v1/waterfall_data


https://core.epventures.co/api/v1/case/MarnerHoldingsB/square_data
https://core.epventures.co/api/v1/case/MarnerHoldingsB/barchart_data
https://core.epventures.co/api/v1/case/MarnerHoldingsB/butterfly_data
https://core.epventures.co/api/v1/case/MarnerHoldingsB/waterfall_data




"""
