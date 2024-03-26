import os,sys
import time
import re
import copy
import pandas as pd
import matplotlib.pyplot as plt

import configparser as ConfigParser
LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")


from get_logger import setup_logging
logging=setup_logging()



#0v1# JC  Nov 25, 2023  Setup


"""
    NORMALIZE ENTITY NAME FOR VIEW
    - real-time (no libraries)

"""

def get_sample_names():
    # MarnerHoldings
    sample=['2Staples', '2Staples Centr14547301', '800-4633339 TN', 'Affirm, Inc', 'American Express', 'Amzn Mkip', 'Amzn Mkip US*2X0K70T', 'Amzn Mkip US*2X2015J', 'Amzn.Com/Bill WA', 'Beverly Hills CA', 'Card 6034', 'Chase Card', 'Chk', 'Chk ...5635', 'Coldhearted Studio', 'Doordash*Chick-Fil-A', 'Etsy.Com', 'Etsy.Com 718-8557955', 'Fedex', 'Fedex 412230591', 'Foreign Exch Rt ADJ', 'Four Season', 'Luxury Lea- 5086', 'Marner Holdings Inc', 'Rp Shopify', 'Sav', 'Shopify Capital', 'The Guardian', 'The Home Depot', 'The Home Depot #0654', 'main_account', 'unknown', 'Afterpay US, Inc', 'Amzn Mktp US', 'Chubb-Sci', 'Eddie Rojas', 'Fedex 338125096', 'Fedex 412453842', 'Google *Gsuite_Ruepo', 'Google *Gsuite_Ruepo Cc', 'Google *Gsuite_Ruepo Cc@ Google.Com', 'Gusto', 'Indeed', 'Indeed 203-564-2400', 'Kaner Vonap', 'Marner Holdings', 'Rolling Tires & Wheel', 'Rolling Tires & Wheel Bell Gardens', 'Rue Porter', 'Rue Porter Afterpay', 'Shell Service Station', 'Shell Service Station Long Beach', 'Ssbtrustops', 'Usps', 'Usps Change of Addres', 'Usps Change of Addres 800-238-3150', 'Amzn Mkip US*2R26G7Y', 'Beam-Premium', 'Lzc* Legal Plan', 'Wells Fargo Bank, N.A.', 'Fedex 338211046', 'Hooters of Long Beach', 'Portos Bakery', 'Sprint *Wireless', 'Adobe', 'Adobe *800-833-6687 Adobe.Ly/Enus', 'Apintego', 'Doordash*Benihana', 'Fedex 338249012', 'Guideline Inc', 'Kaner Apelacio', 'So Cal Edison', 'Spectrum', 'The Home Depot #0608', 'The Home Depot #6627', 'Watch Chest LLC', 'Watch Chest LLC Branson MO 65616 US', 'Fedex 338175208', 'Gaucho Grill', 'Wal-Mart', 'Wal-Mart #5045', 'Bcbs Health Hps', 'CA', 'Uber', '0007Marner Holdings', 'All IN One Suppliers', 'Apple.Com/Bill', 'Bbva USA', 'Mach 1', 'Paypal *Shop Nyt Ebay', 'Paypal *Shop Nyt Ebay 402-935-7733', 'Petsuites', 'Petsuites Spring', 'United Healthcar', '800-288-2020', 'Amzn Mkip US*2X1DR6M Amzn.Com/Bill WA', 'Amzn.Com/Bill', 'Armindo Freitas', 'Att*Bill Payment 800-288-2020 TX', 'Card 7413', 'Citibank West Fsb', 'Fedex 338449916 800-4633339', 'Fedex 940613118321 Memphis TN', 'Fitness Mania', 'Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107', 'Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107 US', 'Hitpsshopify', 'Microsoft', 'Microsoft*Ultimate 1 M Msbill.Info WA', 'Msbill.Info', 'SKYVIEW CAPITAL GROUP', 'Shopify', 'Shopify* 111567098 Hitpsshopify. IL', 'cash', '800-4633339', '888-202-3007', 'Adobe.Ly/Enus', 'All IN One Suppliers 212-5646240 NY', 'Apple.Com/Bill 866-712-7753 CA', 'Fedex 338488188 800-4633339 TN', 'GREAT-WEST TRUST', 'Gucci Store', 'Gucci Store 21', 'Hiscox Inc', 'Paypal', 'Skyview Capital', 'Transaction#: 11973738486', 'Autozone', 'Autozone 3980', 'Guideline Retire', 'Shoppayinst Afrm', 'Bookly - Kpmg', 'Costco', 'Costco Whse #0569 Commerce', 'Fedex 338689542', 'Fedex 414124703', 'Ferrari Financia', '512-485-4282', '858-2083835', 'Airbnb', 'Airbnb Hmcck55Er9', 'Airbnb.Com', 'Fedex 338728895', 'Fedex 338779923', 'Marner Holdings Inc.', 'Osha4dless 858-2083835', 'Shipstation 512-485-4282 TX', '650-5434800', 'Allstate Nbindco', 'Facebk', 'Facebk Mk8635P3U2 650-5434800', 'Fernish', 'Fernish Hitpswww.Fern', 'Hitpsshopify.', 'Shopify* 112556669 Hitpsshopify.', 'Facebk 35Q346F3U2 650-5434800 CA', 'Fedex 414454453 800-4633339 TN', 'Fedex 414682087 800-4633339 TN', 'Airbnb Hmcckb55Er9 Airbnb.Com CA', 'American Clothing Supp', 'American Clothing Supp Los Angeles CA', 'Fedex 338833982 800-4633339 TN', 'Fedex 338888039 800-4633339 TN', 'Fedex 338905312 800-4633339 TN', 'NEWNET COMMUNICATION TECHN', 'Ssense.Com', 'Ssense.Com Montreal Qc', 'Staples', 'Staples 1367 Huntington PA', 'Staples 1367 Huntington PA CA', 'Amzn Mktp', 'Fedex 338929732', 'Fedex 338945714', 'Fedex 338945714 800-4633339 TN', 'Foreign Cur Bus Acct', 'Amstelveen', 'Cafe Santiago Porto', 'Fedex 338967855', 'Fedex 339017149', 'Fedex 415232932', 'KIm Netherla07415046', 'KIm Netherla07415046 Gp Amstelveen', 'Kim Netherla07415046 Gp', 'Kim Netherla07415046 Gp Amstelveen', 'Porto', 'R De Passos Manuel', 'Shahnaz Akter', "Tam's Super Burgers #2", "Tam's Super Burgers #2 310-6373433", 'Uber Trip', 'Vaccarum', 'Chk...5635', 'Commerzbank Aktiengesellschaft Frankfurt Am Main Germany', 'Hakan Bagci', 'Card 5929', 'Parque Silo Auto Porto']
    return sample


def alg_normalize_entity_name(name,verbose=False):
    ## OPTIONAL FUTURE
    #** real-time ok

    #- NER tool for name
    #- NER tool for address
    #- NER tool for phone
    #- NER tool for normalizing business name  (recall miner)

    ## LEVELS OF LOGIC
    
    ##  Normalize name
    org_name=copy.deepcopy(name)
    org_words_len=len(name.split())
    
    ##  if all upper or all lower then title
    if name.isupper() or name.islower():
        name = name.title()

    ## regex add dash to generic missing phone numbers ie: 718-8557955
    name=re.sub(r'(\d{3})-(\d{3})(\d{4})\b',r'\1-\2-\3',name)
    
    ## Space at suffix ([ ] see company norm library)
    suffixes = ['Inc', 'LLC', 'Corp', 'Ltd', 'Co']
    for suffix in suffixes:
        pattern = re.compile(r'\b' + suffix + r'\b', re.IGNORECASE)
        name = pattern.sub(suffix, name)
    ## Remove period from: Inc. -> Inc, etc
    nop=[r'Inc\.',r'LLC\.',r'Corp\.',r'Ltd\.',r'Co\.'] 
    for n in nop:
        name = re.sub(n, n[:-2], name)  # Removes the period from the pattern

    ## Fedex322444 -> Fedex 322444  Add space between at least three consecutive letters and three consecutive numbers
    name = re.sub(r'([A-Za-z]{3})(\d{3})', r'\1 \2', name)

    ## Raw remove address  City, State, Zip ST
    name=re.sub(r'\b(?:[A-Z][a-z]+ ){1,2}[A-Z]{2} \d{5}(?: [A-Z]{2})?\b','',name)

    ## Remove 832-232-3433 TX   phone state *unless blank?
    name=re.sub(r'(\d{3}-\d{3}-\d{4}|\d{10})\s+[A-Za-z]{2}','',name)
    
    ## Remove 832-232-3433 AT END
    name=re.sub(r'(\d{3}-\d{3}-\d{4}|\d{10})\s*$','',name)
    
    #### SPECIAL CASES
    
    ## Keep 1 one upper as upper
    if org_words_len==1 and name.isupper():
        name=name.upper()
    
    #### CUSTOM ENTITIES (force)
    
    ## Fedex \d+$
    name=re.sub(r'Fedex \d+$','Fedex',name.strip())
#D    if 'Fedex' in name: print ("FED: "+str(name))


    ## Strip
    name=name.strip()

    ####  VERBOSE NOTES
    if not name and org_name:
        name=org_name
        if verbose:
            print ("[restore name]: "+str(org_name))
    elif not name==org_name:
        if verbose:
            print ("[normalize name]: "+str(org_name)+" -> "+str(name))

    return name

def dev1():
    names=get_sample_names()
    for name in names:
        name=normalize_name(name,verbose=True)

    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()
    























