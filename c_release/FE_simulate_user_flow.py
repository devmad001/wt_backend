import os, sys
import time
import requests

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

#from services.square_service import get_service_square_data_records
from BE_proxy import CASE_Proxy


#0v1# JC Nov 28, 2023


"""
    FRONT-END SIMIULATE USER
    - ensures APIs exist + work for standard flows
"""

def normal_flow():
    
    ## AUTHENTICATION
    print ("X. set auth token")
    print ("X. finaware requests token refresh")

    ## STARTING A CASE
    print ("X. user on page")
    print ("X. get case (job) status")
    print ("X. get case details")
    print ("X. set or create case")
    print ("X. start processing")

    ## DASHBOARD LOAD
    print ("Y. load case buttons")
    print ("Y. load case faqs")
    print ("Y. load dashboard high level")
    print ("Y. load dashboard layout details") # drag & drop?
    
    ## ws  DASHBOARD sockets
    print ("Z. connect to ws")
    print ("Z. sync state")
    print ("Z. get componnets")
    print ("Z. ws pushes componnet updates")
    
    ## DASHBOARD USE
    print ("A.  click a button")
    print ("A.  edit a button")
    print ("A.  ?button management -- reorder etc")
    print ("A.  browse FAQs")

    print ("A.  chat ask a question")


    ## MISC:
    print ("A.  ??interact with d3 chart?")
    print ("A.  ??resize component? popout?")
    

    return

    
def dec_5_6_shivam_user_page():
    """
        DEFINITIONS
        - keep FE states separate from backend processing -- because so many-back-and-forth confusion on FE team

    """

    """
    [BUILD_PAGE_VIEW]
    - auto content loaded

    [USER_CREATE_CASE]
    - watch form submit validation
    
    [USER_VIEW_REPORTS]
    - if available (otherwise don't list as finished page)

    """
    
    #[BUILD_PAGE_VIEW]
    view_endpoints=[]
    view_endpoints+=[('load single detail view of case (details from case creation form)','')]
    view_endpoints+=[('load user list of actively processing cases','')]
    view_endpoints+=[('load user list of finished processing case ids','')]
    
    #[USER_CREATE_CASE]
    view_endpoints=[]
    view_endpoints+=[('form pre-validates files included AND case id is globally unique','')]
    view_endpoints+=[('submit create case: user_id, case_id, other','')]  #Create in DB
    view_endpoints+=[('backend download files from google [ ] code this','')]
    view_endpoints+=[('backend enqueue request as job to process','')]
    
    #[USER_VIEW_REPORTS]
    view_endpoints=[]
    view_endpoints+=[('UX link to Case specific Dashboard','')]   # tbd on where
    view_endpoints+=[("[ ] click to see report. click to dashboard... that's it.",'')]   # 




    return

def OLD_local_fe_test_call():
    case_id = 'case_test_A'

    base1_url = 'http://127.0.0.1:8008/api/v1/'
    base_url = base1_url+'case/'

    # Endpoints for GET requests
    get_endpoints = ['get_case_report', 'get_case_processing_status', 'start_case_processing']

    # Endpoints for POST requests
    post_endpoints = ['post_case_details']

    # Perform GET requests and validate responses
    for endpoint in get_endpoints:
        full_url = f"{base_url}{case_id}/{endpoint}"
        response = requests.get(full_url)
        if response.status_code == 200:
            print(f"GET {full_url} - Success")
        else:
            print(f"GET {full_url} - Error: {response.status_code}")

    # Perform POST requests and validate responses
    for endpoint in post_endpoints:
        full_url = f"{base_url}{case_id}/{endpoint}"
        response = requests.post(full_url, data={})  # Assuming no specific data is required
        if response.status_code == 200:
            print(f"POST {full_url} - Success")
        else:
            print(f"POST {full_url} - Error: {response.status_code}")

    ## auth
    #full_url=base1_url+'case/auth_handshake'
    full_url=base1_url+'auth_handshake'
    data={'user_id':case_id,'token':'1234'}
    response = requests.post(full_url, json=data)  # Assuming no specific data is required
    if response.status_code == 200:
        print(f"POST {full_url} - Success")
    else:
        print(f"POST {full_url} - Error: {response.status_code}")



def TOUCH_api(item,full_url, branch='GET',data={}):
    ## VIA LOCAL ENDPOINT  (Other option is fastapi Client)
    #
    is_good=False
    status_code=0

    if branch=='GET':
        response = requests.get(full_url)
    else:
        response = requests.post(full_url,json=data)
        
    status_code=response.status_code

    if status_code == 200:
#        print(f"REQ {full_url} - Success")
        is_good=True
    elif status_code == 422:
        print(f"REQ {full_url} - "+str(status_code)) #<-- 422 likely missing parameter but ok
        is_good=True
    else:
        print(f"REQ {full_url} - Error: {status_code}")

    return is_good,status_code


def dev_samples_and_test_for_userpage():

    case_id = 'case_test_A'
    base1_url = 'http://127.0.0.1:8008/api/v1/'
    case_base_url = base1_url+'case/'
    
    url=case_base_url+case_id+"/"

    status={}

    ## Test for GET 200 on cases
    item='get_case_details'
    status[item],status_code=TOUCH_api(item,url+item)
    item='start_case_processing'
    status[item],status_code=TOUCH_api(item,url+item)
    item='get_case_report'
    status[item],status_code=TOUCH_api(item,url+item)
    item='get_case_processing_status'
    status[item],status_code=TOUCH_api(item,url+item)

    ## Test for POST 200
    item='post_case_details'
    status[item],status_code=TOUCH_api(item,url+item,branch='POST')
    
    ### non-/case/ endpoints @FE_user.py

    ## user endpoints
    url=base1_url+'user/'

    item='list_cases_statuses'
    status[item],status_code=TOUCH_api(item,url+item)

    item='list_user_finished_cases_ids'
    status[item],status_code=TOUCH_api(item,url+item)


    ## top endpoints (global case_id exists anywhere?)
    # @FE_auth?
    url=base1_url

    item='is_case_id_exist'
    status[item],status_code=TOUCH_api(item,url+item)


    ### VIEW OUTPUT STATUSES
    for item in status:
        print ("[status]: "+str(item)+": "+str(status[item]))
        if not status[item]:
            raise Exception('status failed: '+str(item))



    return


def dev_test_full_parameter_passes():
    case_id = 'case_test_A'
    base1_url = 'http://127.0.0.1:8008/api/v1/'
    case_base_url = base1_url+'case/'
    full_case_url=case_base_url+case_id+"/"
    status={}


    ## 1//  POST CASE DETAILS
    item = 'post_case_details'
    post_data = {'case_id': 'test_case_1','user_id':'test_user_1'}
    status[item],status_code = TOUCH_api(item, full_case_url + item, branch='POST', data=post_data)
    
    
    ## 2//  BUTTON HANDLER
    item='button_handler'
    case_params='&'.join(['case_id='+case_id,'fin_session_id=123','button_id=button_test_1','button_value=button_value_1'])
    url=full_case_url+item+'?'+case_params
    status[item],status_code = TOUCH_api(item, url, branch='GET')


    ### VIEW OUTPUT STATUSES
    for item in status:
        print ("[status]: "+str(item)+": "+str(status[item]))

        if not status[item]:
            raise Exception('status failed: '+str(item))



    return


def workflow_FE_case():
    from BE_proxy import BE_Proxy, CASE_Proxy

    print ("**from perspective of FE")

    ## For view friendly testing see above.  This is pure functional
    
    BE=BE_Proxy()
    
    case_id='6570af77949fdfbf2c5810e8'
    Case=CASE_Proxy(case_id)
    Case.set_state_word('INIT')
    
    ## Precheck passed values

    #[1]#  Accept case details posted or sync files for ready
    case_details=BE.get_case_details(case_id)

    #[2]#  Proxy submit for processing
    BE_process_status=BE.get_BE_case_processing_status(case_id)

    Case.set_state_word('PROCESSING')
    BE_process_status=BE.get_BE_case_processing_status(case_id)

    #[3]#  Check/test case processing status
    
    Case.set_state_word('READY')
    #[4]#  Get case report
    BE_process_status=BE.get_BE_case_processing_status(case_id)

    case_report=BE.get_case_report(case_id)

    return



if __name__ == "__main__":
#    normal_flow()
#    local_fe_test_call()
#    nov29_shivam_priority()
#    nov30_shivam_priority()
#    dec4_shivam_priority()
#    dec_5_6_shivam_user_page()
#    dev_samples_and_test_for_userpage()
#    dev_test_full_parameter_passes()
#    workflow_FE_case()

    dev_call_case_states()
#    simulate_BE_done_processing('6570af77949fdfbf2c5810e8')








"""


    #'data': added at router
    data={"butterfly_sorted":[{"name":"Beam-Premium","debit_total":111.72,"credit_total":0.0},{"name":"Card 7413","debit_total":579.42,"credit_total":0.0},{"name":"Afterpay US, Inc","debit_total":944.54,"credit_total":297.5},{"name":"Commerzbank Aktiengesellschaft Frankfurt Am Main Germany","debit_total":1730.4,"credit_total":0.0},{"name":"Wells Fargo Bank, N.A.","debit_total":3510.95,"credit_total":0.0},{"name":"Apintego","debit_total":3726.24,"credit_total":0.0},{"name":"Sav","debit_total":5270.75,"credit_total":0.0},{"name":"So Cal Edison","debit_total":13567.5,"credit_total":0.0},{"name":"United Healthcar","debit_total":19201.2,"credit_total":0.0},{"name":"Bbva USA","debit_total":21623.36,"credit_total":0.0},{"name":"Citibank West Fsb","debit_total":30000.0,"credit_total":0.0},{"name":"Great-West Trust","debit_total":73338.36,"credit_total":0.0},{"name":"Ssbtrustops","debit_total":100272.3,"credit_total":83994.11},{"name":"Shoppayinst Afrm","debit_total":118772.61,"credit_total":18871.17},{"name":"Skyview Capital","debit_total":145998.66,"credit_total":74549.76},{"name":"Guideline Retire","debit_total":176598.68,"credit_total":0.0},{"name":"Skyview Capital Group","debit_total":203735.19,"credit_total":0.0},{"name":"Coldhearted Studio","debit_total":219761.09,"credit_total":0.0},{"name":"Gusto","debit_total":316295.91,"credit_total":48219.78},{"name":"Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107 US","debit_total":371584.29,"credit_total":173443.98},{"name":"Foreign Cur Bus Acct Bk 1 Columbus Newark De 197132107","debit_total":545316.95,"credit_total":0.0},{"name":"Affirm, Inc","debit_total":578966.07,"credit_total":40220.01},{"name":"Foreign Exch Rt ADJ","debit_total":862628.25,"credit_total":11.44},{"name":"Card 6034","debit_total":1412322.03,"credit_total":0.0},{"name":"Rp Shopify","debit_total":18535022.65,"credit_total":0.0},{"name":"Shopify Capital","debit_total":31586070.46,"credit_total":30504632.48},{"name":"KIm Netherla 07415046","debit_total":0.0,"credit_total":0.64},{"name":"KIm Netherla 07415046 Gp Amstelveen","debit_total":0.0,"credit_total":0.64},{"name":"Osha4dless","debit_total":0.0,"credit_total":5.99},{"name":"858-2083835","debit_total":0.0,"credit_total":5.99},{"name":"Usps","debit_total":0.0,"credit_total":15.75},{"name":"Card 5929","debit_total":0.0,"credit_total":18.99},{"name":"Adobe.Ly/Enus","debit_total":0.0,"credit_total":20.99},{"name":"Costco Whse #0569 Commerce","debit_total":0.0,"credit_total":28.52},{"name":"Usps Change of Addres","debit_total":0.0,"credit_total":31.5},{"name":"Cafe Santiago Porto","debit_total":0.0,"credit_total":37.07},{"name":"Fedex 94mphis TN","debit_total":0.0,"credit_total":38.88},{"name":"Fitness Mania","debit_total":0.0,"credit_total":38.88},{"name":"Amzn Mkip US*2R26G7Y","debit_total":0.0,"credit_total":49.59},{"name":"Amzn Mkip US*2X2015J","debit_total":0.0,"credit_total":52.89},{"name":"Hitpsshopify.","debit_total":0.0,"credit_total":54.09},{"name":"Shopify* 112556669 Hitpsshopify.","debit_total":0.0,"credit_total":54.09},{"name":"Adobe *obe.Ly/Enus","debit_total":0.0,"credit_total":62.97},{"name":"Kim Netherla 07415046 Gp","debit_total":0.0,"credit_total":64.68},{"name":"Amstelveen","debit_total":0.0,"credit_total":64.68},{"name":"Kim Netherla 07415046 Gp Amstelveen","debit_total":0.0,"credit_total":64.68},{"name":"Shahnaz Akter","debit_total":0.0,"credit_total":67.91},{"name":"Shell Service Station Long Beach","debit_total":0.0,"credit_total":70.0},{"name":"Costco","debit_total":0.0,"credit_total":85.56},{"name":"Microsoft*Ultimate 1 M Msbill.Info WA","debit_total":0.0,"credit_total":89.94},{"name":"Msbill.Info","debit_total":0.0,"credit_total":89.94},{"name":"Microsoft","debit_total":0.0,"credit_total":89.94},{"name":"Hooters of Long Beach","debit_total":0.0,"credit_total":90.0},{"name":"2Staples Centr 14547301","debit_total":0.0,"credit_total":92.01},{"name":"2Staples","debit_total":0.0,"credit_total":92.01},{"name":"Shipstation","debit_total":0.0,"credit_total":99.0},{"name":"512-485-4282","debit_total":0.0,"credit_total":99.0},{"name":"Amzn Mktp","debit_total":0.0,"credit_total":103.89},{"name":"Autozone 3980","debit_total":0.0,"credit_total":107.16},{"name":"Rolling Tires & Wheel","debit_total":0.0,"credit_total":114.96},{"name":"Rolling Tires & Wheel Bell Gardens","debit_total":0.0,"credit_total":114.96},{"name":"Vaccarum","debit_total":0.0,"credit_total":123.76},{"name":"Wal-Mart #5045","debit_total":0.0,"credit_total":135.96},{"name":"Wal-Mart","debit_total":0.0,"credit_total":135.96},{"name":"Uber Trip","debit_total":0.0,"credit_total":143.02},{"name":"Apple.Com/Bill","debit_total":0.0,"credit_total":146.79},{"name":"The Guardian","debit_total":0.0,"credit_total":158.45},{"name":"Shell Service Station","debit_total":0.0,"credit_total":183.92},{"name":"Etsy.Com","debit_total":0.0,"credit_total":194.7},{"name":"The Home Depot #0654","debit_total":0.0,"credit_total":239.13},{"name":"Gaucho Grill","debit_total":0.0,"credit_total":250.0},{"name":"Staples","debit_total":0.0,"credit_total":251.28},{"name":"Staples 1367 Huntington PA","debit_total":0.0,"credit_total":251.28},{"name":"Staples 1367 Huntington PA CA","debit_total":0.0,"credit_total":251.28},{"name":"Fernish Hitpswww.Fern","debit_total":0.0,"credit_total":260.78},{"name":"Parque Silo Auto Porto","debit_total":0.0,"credit_total":276.48},{"name":"The Home Depot #6627","debit_total":0.0,"credit_total":288.95},{"name":"Porto","debit_total":0.0,"credit_total":310.25},{"name":"Adobe","debit_total":0.0,"credit_total":314.85},{"name":"Autozone","debit_total":0.0,"credit_total":321.48},{"name":"Tam's Super Burgers #2","debit_total":0.0,"credit_total":344.68},{"name":"Amzn Mkip US*2X0K70T","debit_total":0.0,"credit_total":386.91},{"name":"Doordash*Chick-Fil-A","debit_total":0.0,"credit_total":390.18},{"name":"888-202-3007","debit_total":0.0,"credit_total":428.33},{"name":"Four Season","debit_total":0.0,"credit_total":435.0},{"name":"Beverly Hills CA","debit_total":0.0,"credit_total":435.0},{"name":"The Home Depot #0608","debit_total":0.0,"credit_total":440.55},{"name":"Airbnb Hmcckb55Er9 Airbnb.Com CA","debit_total":0.0,"credit_total":465.9},{"name":"Guideline Inc","debit_total":395.0,"credit_total":474.0},{"name":"Rue Porter Afterpay","debit_total":476.0,"credit_total":476.0},{"name":"Google *Gsuite_Ruepo Cc@ Google.Com","debit_total":0.0,"credit_total":576.0},{"name":"Google *Gsuite_Ruepo Cc","debit_total":0.0,"credit_total":576.0},{"name":"Google *Gsuite_Ruepo","debit_total":0.0,"credit_total":576.0},{"name":"Hakan Bagci","debit_total":0.0,"credit_total":576.8},{"name":"Amzn Mkip US*2X1DR6M Amzn.Com/Bill WA","debit_total":0.0,"credit_total":579.42},{"name":"Portos Bakery","debit_total":0.0,"credit_total":617.5},{"name":"Spectrum","debit_total":0.0,"credit_total":668.91},{"name":"Fernish","debit_total":0.0,"credit_total":782.34},{"name":"R De Passos Manuel","debit_total":0.0,"credit_total":817.29},{"name":"Lzc* Legal Plan","debit_total":0.0,"credit_total":840.0},{"name":"Amzn Mktp US","debit_total":0.0,"credit_total":844.65},{"name":"Ca","debit_total":0.0,"credit_total":880.83},{"name":"Facebk Mk8635P3U2","debit_total":0.0,"credit_total":900.0},{"name":"650-5434800","debit_total":0.0,"credit_total":900.0},{"name":"Ssense.Com","debit_total":0.0,"credit_total":1077.48},{"name":"Ssense.Com Montreal Qc","debit_total":0.0,"credit_total":1077.48},{"name":"Uber","debit_total":0.0,"credit_total":1119.51},{"name":"Bookly - Kpmg","debit_total":0.0,"credit_total":1170.0},{"name":"Amzn.Com/Bill","debit_total":0.0,"credit_total":1324.05},{"name":"Cash","debit_total":0.0,"credit_total":1686.42},{"name":"Airbnb Hmcck55Er9","debit_total":0.0,"credit_total":1747.68},{"name":"Airbnb.Com","debit_total":0.0,"credit_total":1747.68},{"name":"Att*Bill Payment","debit_total":0.0,"credit_total":1941.36},{"name":"800-288-2020","debit_total":0.0,"credit_total":1941.36},{"name":"American Clothing Supp Los Angeles CA","debit_total":0.0,"credit_total":1956.0},{"name":"American Clothing Supp","debit_total":0.0,"credit_total":1956.0},{"name":"Petsuites","debit_total":0.0,"credit_total":1992.63},{"name":"Petsuites Spring","debit_total":0.0,"credit_total":1992.63},{"name":"Hiscox Inc","debit_total":0.0,"credit_total":2161.41},{"name":"Amzn.Com/Bill WA","debit_total":0.0,"credit_total":2196.0},{"name":"Paypal *Shop Nyt Ebay","debit_total":0.0,"credit_total":2409.54},{"name":"Paypal","debit_total":0.0,"credit_total":2550.0},{"name":"The Home Depot","debit_total":0.0,"credit_total":2628.13},{"name":"All IN One Suppliers","debit_total":0.0,"credit_total":2659.09},{"name":"Facebk 35Q346F3U2","debit_total":0.0,"credit_total":2700.0},{"name":"Gucci Store","debit_total":0.0,"credit_total":2760.38},{"name":"Gucci Store 21","debit_total":0.0,"credit_total":2760.38},{"name":"Doordash*Benihana","debit_total":0.0,"credit_total":3292.3},{"name":"Ferrari Financia","debit_total":0.0,"credit_total":4179.54},{"name":"Luxury Lea- 5086","debit_total":0.0,"credit_total":5101.6},{"name":"Amzn Mkip","debit_total":0.0,"credit_total":5256.09},{"name":"Sprint *Wireless","debit_total":0.0,"credit_total":6580.35},{"name":"Airbnb","debit_total":0.0,"credit_total":10291.4},{"name":"800-4633339 TN","debit_total":0.0,"credit_total":10346.91},{"name":"800-4633339","debit_total":0.0,"credit_total":11324.47},{"name":"Indeed","debit_total":0.0,"credit_total":12067.5},{"name":"Bcbs Health Hps","debit_total":8077.76,"credit_total":14136.08},{"name":"Chk...5635","debit_total":0.0,"credit_total":16000.0},{"name":"Hitpsshopify","debit_total":0.0,"credit_total":16918.32},{"name":"Shopify* 111567098 Hitpsshopify. IL","debit_total":0.0,"credit_total":16918.32},{"name":"0007Marner Holdings","debit_total":0.0,"credit_total":19201.2},{"name":"Kaner Vonap","debit_total":0.0,"credit_total":21100.0},{"name":"Transaction#: 1","debit_total":0.0,"credit_total":25000.0},{"name":"Facebk","debit_total":0.0,"credit_total":25200.0},{"name":"Shopify","debit_total":0.0,"credit_total":33890.73},{"name":"Watch Chest LLC","debit_total":0.0,"credit_total":35000.0},{"name":"Eddie Rojas","debit_total":0.0,"credit_total":40600.0},{"name":"Chubb-Sci","debit_total":26384.4,"credit_total":56538.0},{"name":"Mach 1","debit_total":0.0,"credit_total":64870.08},{"name":"Marner Holdings","debit_total":41541.15,"credit_total":83763.48},{"name":"Newnet Communication Techn","debit_total":0.0,"credit_total":91621.62},{"name":"Chk ...5635","debit_total":0.0,"credit_total":168000.0},{"name":"American Express","debit_total":91550.0,"credit_total":322025.0},{"name":"Chase Card","debit_total":0.0,"credit_total":345713.06},{"name":"Foreign Cur Bus Acct","debit_total":0.0,"credit_total":365319.06},{"name":"Allstate Nbindco","debit_total":0.0,"credit_total":501254.79},{"name":"Chk","debit_total":215400.0,"credit_total":619000.0},{"name":"Kaner Apelacio","debit_total":72080.0,"credit_total":621309.13},{"name":"Rue Porter","debit_total":110558.17,"credit_total":831456.84},{"name":"Armindo Freitas","debit_total":0.0,"credit_total":1183993.13},{"name":"Fedex","debit_total":0.0,"credit_total":5734757.36}]}
    data['style']={}
    data['style']['x_axis_title']='Date'
    data['style']['y_axis_title']='Amount'
    return data

def get_waterfall_data_sample(case_id):
    if not case_id=='case_chart_data_v1': raise Exception('case_id must be case_chart_data_v1')
    #'data': added at router
    #** think too negative!
    data={"balance_by_date":{"2021-06-01":7349.72,"2021-06-02":-38646.21,"2021-06-03":-872170.96,"2021-06-04":-880058.81,"2021-06-07":-1060675.88,"2021-06-08":-1277785.64,"2021-06-09":-1286152.66,"2021-06-10":-1423949.72,"2021-06-11":-1660990.8,"2021-06-14":-1725711.64,"2021-06-15":-1835112.38,"2021-06-16":-1876612.23,"2021-06-17":-1927753.61,"2021-06-18":-1826971.04,"2021-06-21":-1790676.98,"2021-06-22":-1503657.06,"2021-06-23":-1434306.76,"2021-06-24":-1479683.8,"2021-06-25":-1998203.6,"2021-06-26":-2030157.71,"2021-06-28":-1970865.75,"2021-06-29":-1836231.43,"2021-06-30":-1745983.1},"waterfall_by_date":{"2021-06-01":{"debit":-132106.68,"credit":26105.21},"2021-06-02":{"debit":-194476.29,"credit":148480.36},"2021-06-03":{"debit":-883002.86,"credit":49478.11},"2021-06-04":{"debit":-53321.79,"credit":45433.94},"2021-06-07":{"debit":-197116.12,"credit":16499.05},"2021-06-08":{"debit":-300574.91,"credit":83465.15},"2021-06-09":{"debit":-46164.04,"credit":37797.02},"2021-06-10":{"debit":-172272.98,"credit":34475.92},"2021-06-11":{"debit":-270416.71,"credit":33375.63},"2021-06-14":{"debit":-139600.18,"credit":74879.34},"2021-06-15":{"debit":-216668.4,"credit":107267.66},"2021-06-16":{"debit":-75562.4,"credit":34062.55},"2021-06-17":{"debit":-78685.11,"credit":27543.73},"2021-06-18":{"debit":-28016.52,"credit":128799.09},"2021-06-21":{"debit":-13020.25,"credit":49314.31},"2021-06-22":{"debit":-3590.52,"credit":290610.44},"2021-06-23":{"debit":-43961.58,"credit":113311.88},"2021-06-24":{"debit":-98723.72,"credit":53346.68},"2021-06-25":{"debit":-775595.98,"credit":257076.18},"2021-06-26":{"debit":-31954.11,"credit":0},"2021-06-28":{"debit":-40517.52,"credit":99809.48},"2021-06-29":{"debit":-106712.42,"credit":241346.74},"2021-06-30":{"debit":-50590.69,"credit":140839.02}}}
    data['style']={}
    data['style']['x_axis_title']='Debit/Credit Amounts'
    data['style']['y_axis_title']='Entities'
    return dat
    

"""


"""
ARCHIVE

def nov30_shivam_priority():

    ## Priority list
    PL=[]
    PL+=['first set of APIs (adjust or validate): auth, case, report, jobs']
    PL+=['chart headings']
    
    COMPLAIN LIST:
----
For Faq
    Please separate the Faq section content (only) with specific url and deploy it. Then pls provide the iframe url
For buttons
    please provide the API details and note the description for that


----
For Layout
layout_type
1, 2, 3
please let me know what each layout type means
Then if we need to use websocket for layout config, please provide websocket config.


----
For chart
waterfall
barchart
butterfly
please confirm the API fields for charts
ex: x axis is for which field, y axis is for which field... etc..

----
For chat section
please provide the chat iframe url


    return


def jon_nov30():
    
    print ("GOAL:  view basic dashboard via supported api endpoints")
    print ("**prioritize architectural ie/ ws")
    
    print ("BATCH 1 APIS")

    return
"""

"""

def nov29_shivam_priority():
        OPEN REQUESTS
        i)   layout switching
        ii)  chatbox (jc: route to non for now)
        iii) dynamic buttons how?
        iv)  chart fields api (x-axis, y-axis, etc) 
        v)   FAQ content
        vi)  netlify for chart component? -- i suppose so long as it imports view/ not view websocket
    
    ## CORE APIS
    #> auth

    print("Waiting to confirm auth handshake")

    # /auth_handshake
    # /request_for_auth
    #> dashboard state
    
    ## ws APIS
    #> [ ] JON TO HAVE Full 3rd party test so clear what happening.
        { "message_type": "init", "data": { // initialization data } }
        { "message_type": "normal", "data": { // 
            {
        "action": "refreshIframe",
        "timestamp": 1234567890 }

    ## API EC CHANGE REQUESTS
    #[charts]: 'style':{}

    return

    
def dec4_shiam_priority():
        Support UserCasesPage - add full test because need to create db + sample reponses.
    return

"""