import boto3
import json
import re
import usaddress
import requests


#0v3# JC  Jan 21, 2024  Upgrade to google option (Amazon is not reliable)
#0v2# JC  Jan 15, 2024  Watch encoding on 'place' text !
#0v1# JC  Oct  8, 2023



"""
    Given blob of text (description?) try to find the geo locations

"""



GOOGLE_API_KEY="AIzaSyDb6dY-IaCiz0GLSRcgJYguTS-Id-eI9MY" #watchtowergroupai@gmail.com


def is_look_like_address(astring):
    ## Consider retiring since Google lookup is more flexible
    global US_STATES
    places=US_STATES+['USA','Canada','Mexico','United States']
    places+=['United Kingdom']
    # can't try them all
    is_like_address=False
    
    ## zipcode?
    if re.search(r'\b\d{5}\b',astring):
        is_like_address=True
        return is_like_address

    ## place?
    for place in places:
        if re.search(place,astring,re.IGNORECASE):
            is_like_address=True
            print ("[debug] looks like because: "+str(place))
        if is_like_address: break
    return is_like_address
    
def lookup_address_amazon(address):
    location = boto3.client('location', 
                            aws_access_key_id='AKIAXC5UOBG2L26O24EM',
                            aws_secret_access_key='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',
                            region_name='us-east-1')
    
    response = location.search_place_index_for_text(
        Text=address,
        IndexName='explore.place.Esri'  # Replace with your actual place index name
    )
    return response

def alg_resolve_address_v0(blob):
    ## Two part including cleaning
            
    ## Normalize blob
    blob=blob.encode('utf-8').decode('utf-8')
    
    meta={}
    address=''

#D1    print("GIVEN CANDI  DATE: "+(str(blob)))
    blob,is_like_address=clean_to_address(blob)
#D1    print (" ---. IS LIKE ADDRESS: "+str(is_like_address))

    meta['is_like_address']=is_like_address
    place={}
    if is_like_address and blob:

        data=lookup_address_amazon(blob)
#D1        print("dataa CANDIDATE: "+(str(data)))
        
        # Extract lat, lng, relevance, and label (as ID)
        for result in data['Results']:
#D1            print ("[data can]: "+str(result))
            #ERR REVERSED!#  lat, lng = result['Place']['Geometry']['Point']
            lng, lat = result['Place']['Geometry']['Point']
            relevance = result['Relevance']
            label = result['Place']['Label']  # Extracting Label as ID
            
            ## aws is bad.
            #  ATM Check Deposit | 08/02 6400 Laurel Canyon Blv North Hollywo CA Card 7413
            #   6400, Laurel, Canyon, Blv, North, Hollywo, CA, Card, 7413
            #   7413, Fürstenau, Graubünden, CHE
            #    'label': 'Laurel, San Mateo, CA, USA', 'id': 'Laurel, San Mateo, CA, USA'}
            
            ## LOGIC:
            #[1]  Stop if address has partial content   > extracted address SOMETHING must be in blob one of:
            must_have_one=['Municipality','Neighborhood','Region','SubRegion']
            keep_it=False
            for must in must_have_one:
                if result['Place'].get(must,'') and re.search(result['Place'][must],blob,re.IGNORECASE):
                    keep_it=True
                    break
                
            #[2]  Stop if >80%
            if relevance>0.80: keep_it=True

            if not keep_it:continue

#D1            print(f"Latitude: {lat}, Longitude: {lng}, Relevance: {relevance}, ID: {label}")
            place['lat']=lat
            place['lng']=lng
            place['relevance']=relevance
            place['label']=label
            place['id']=label

            break #Break at first find
        
    ## Encode Place to normal (May be hebrew etc)
    if place:
        for key in place:
            if isinstance(place[key], str):
                place[key] = place[key].encode('utf-8').decode('utf-8')
        
            try:
                print("[alg_resolve_address] PLACE: " + str(place)) #.encode('utf-8').decode('utf-8'))
            except UnicodeEncodeError as e:
                print("Error encoding the place information: {}".format(e))
        
    #place: lat,lng,relevance,label,id
    return place,meta

def alg_resolve_address(blob):
    ## Upgrade to google
    #[ ] again, watch encoding because may not non utf-8
            
    ## Normalize blob
    blob=blob.encode('utf-8').decode('utf-8')
    
    meta={}
    place={}

    place,meta=lookup_address_google(blob)

    return place,meta


def load_states():
    states=[]
    states+=[("1","Alabama","AL")]
    states+=[("2","Alaska","AK")]
    states+=[("3","Arizona","AZ")]
    
    states+=[("4","Arkansas","AR")]
    states+=[("5","California","CA")]
    states+=[("6","Colorado","")]
    #states+=[("6","Colorado","CO")]
    states+=[("7","Connecticut","CT")]
    states+=[("8","Delaware","DE")]
    states+=[("9","Florida","FL")]
    states+=[("10","Georgia","GA")]
    states+=[("11","Hawaii","HI")]
    states+=[("12","Idaho","")]
#    states+=[("12","Idaho","ID")]
    states+=[("13","Illinois","IL")]
    states+=[("14","Indiana","IN")]
    states+=[("15","Iowa","IA")]
    states+=[("16","Kansas","KS")]
    states+=[("17","Kentucky","KY")]
    states+=[("18","Louisiana","LA")]
    states+=[("19","Maine","ME")]
    states+=[("20","Maryland","MD")]
    states+=[("21","Massachusetts","MA")]
    states+=[("22","Michigan","MI")]
    states+=[("23","Minnesota","MN")]
    states+=[("24","Mississippi","MS")]
    states+=[("25","Missouri","MO")]
    states+=[("26","Montana","MT")]
    states+=[("27","Nebraska","NE")]
    states+=[("28","Nevada","NV")]
    states+=[("29","New Hampshire","NH")]
    states+=[("30","New Jersey","NJ")]
    states+=[("31","New Mexico","NM")]
    states+=[("32","New York","NY")]
    states+=[("33","North Carolina","NC")]
    states+=[("34","North Dakota","ND")]
    states+=[("35","Ohio","OH")]
    states+=[("36","Oklahoma","OK")]
    states+=[("37","Oregon","OR")]
    states+=[("38","Pennsylvania","PA")]
    states+=[("39","Rhode Island","RI")]
    states+=[("40","South Carolina","SC")]
    states+=[("41","South Dakota","SD")]
    states+=[("42","Tennessee","TN")]
    states+=[("43","Texas","TX")]
    states+=[("44","Utah","UT")]
    states+=[("45","Vermont","VT")]
    states+=[("46","Virginia","VA")]
    states+=[("47","Washington","WA")]
    states+=[("48","West Virginia","WV")]
    states+=[("49","Wisconsin","WI")]
    states+=[("50","Wyoming","WY")]
    states+=[("52","Puerto Rico","PR")]
    states+=[("53","U.S. Virgin Islands","VI")]
    states+=[("54","American Samoa","AS")]
    states+=[("55","Guam","GU")]
    states+=[("56","Northern Mariana Islands","MP")]
    ss=[]
    for stup in states:
        ss+=[stup[1]]
        if stup[2]:
            ss+=[r'\b'+stup[2]+r'\b']

    return ss


US_STATES=load_states()


def clean_to_address(blob):
    is_like_address=is_look_like_address(blob)
    
    try:
        #print ("LOOK LIKE: "+str(is_like_address))
        
        # May be description | delimited where hard to clean so split and keep
        # ATM Withdrawal | August 24, 2021 | 6400 Laurel Canyon B North Hollywo CA | Card 7413 | $700.00
        cols=re.split(r'\|',blob)
        if is_like_address and len(cols)>2:
            for mblob in cols:
                if is_look_like_address(mblob):
                    blob=mblob
                    print ("[dev] clean address assuming | or delimited now: "+str(blob))
                    break
        
        if is_like_address:
            raw=re.sub(r'^\W+|\W+$', '', blob)
            data_tups=usaddress.parse(raw)
            
            # Keys to be removed
            remove_keys = ['BuildingName'] #May have address too
            remove_keys = ['Recipient']
            
            if 'ZipCode' in data_tups:
                # Clean the ZipCode value in place
                data_tups['ZipCode'] = re.sub(r'\W+$', '', data_tups['ZipCode'])
        
            # Combine remaining key-value pairs
            
            ## If only one then just use it
#D#            print ("DD: "+str(data_tups))
            keys_list = [item[1] for item in data_tups]  # [('text','label')]
            if keys_list==['Recipient']:
                combined_string = next((item[0] for item in data_tups if item[1] == 'Recipient'), '')
            else:
                # Using list comprehension to construct the string with the first element of the tuples
                combined_string = ', '.join(str(item[0]) for item in data_tups if item[1] not in remove_keys)
    
                combined_string=re.sub(r'^\W+|\W+$', '', combined_string)
                # Remove any ,,
                combined_string=re.sub(r',\s*,',',',combined_string)
    
            print ("[debug] usaddress FROM: "+str(blob)+" --> "+str(data_tups)+" --> "+str(combined_string))
            blob=combined_string
    except Exception as e:
        logging.dev("[error] could not clean_to_address: "+str(blob)+" because: "+str(e))
        blob=''
        
    return blob,is_like_address


def dev_clean_raw():
    # pip install usaddress
    # https://parserator.datamade.us/usaddress
    # import usaddress
    # usaddress.tag(addr)
    
    raw=" #Integrated Call Center Solutions, Florham Park NJ, 07932- US'})"
    print ("GIVEN: "+str(raw))
    raw=re.sub(r'^\W+|\W+$', '', raw)
    
    tags=usaddress.tag(raw)
    print ("GOT: "+str(tags))
    
    
    # Keys to be removed
    remove_keys = ['BuildingName'] #May have address too
    remove_keys = ['Recipient']
    
    
    # Extract the OrderedDict from the tuple
    data_dict = tags[0]
    
    if 'ZipCode' in data_dict:
        # Clean the ZipCode value in place
        data_dict['ZipCode'] = re.sub(r'\W+$', '', data_dict['ZipCode'])

    # Combine remaining key-value pairs
    #combined_string = ', '.join(f"{k}: {v}" for k, v in data_dict.items() if k not in remove_keys)
    combined_string = ', '.join(f"{v}" for k, v in data_dict.items() if k not in remove_keys)
    combined_string=re.sub(r'^\W+|\W+$', '', combined_string)

    print ("COMBINED: "+str(combined_string))


    return

def lookup_address_google(blob,verbose=False):
    global GOOGLE_API_KEY
    ## NOTES:
    #[ ] use the is_like_address or just try to do ALL of them?
    #- ref: https://www.codingforentrepreneurs.com/blog/python-tutorial-google-geocoding-api/

    place={}
    meta={}

    lat, lng = None, None

    api_key = GOOGLE_API_KEY

    cleaned_blob,meta['is_like_address']=clean_to_address(blob)
    
    if not cleaned_blob:
        cleaned_blob=blob
        
    if not cleaned_blob or not meta['is_like_address']:
        return place,meta
    
    encoded_address = requests.utils.quote(cleaned_blob)

    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?address={encoded_address}&key={api_key}"
    
    if verbose:
        print ("[endpoint]: "+str(endpoint))

    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    got_response=False
    try:
        r = requests.get(endpoint)
        got_response=True
    except Exception as e:
        print ("[error] could not get response: "+str(e))

    if r.status_code not in range(200, 299) or not got_response:
        meta['got_response']=got_response
        return place,meta

    try:
        if verbose:
            print ("RAW: "+str(json.dumps(r.json(),indent=4)))
            
        all_results=r.json()['results']
    
        
        if all_results:
            results = all_results[0]
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
            
            place['label']=results['formatted_address']
            place['id']=results['place_id']
            
            if verbose:
                print ("[full resp]: "+str(results))

    except Exception as e:
        raise e

    ## Map to standard dict
    if lat is not None:
        place['lat']=lat
        place['lng']=lng
        place['relevance']=0.90
        #place['label']=label
        #place['id']=label

    return place,meta


def dev_sample_queries():
    aa=[]
    aa+=["1600 Amphitheatre Parkway, Mountain View, CA"]
#    aa+=["""Book Transfer Credit B/O: United Call Center Solutions LLC Florham Park NJ | $45,956.11 | 07932- US Ref: Medical Account 11-4-21 Trn: 6116100336Jo | YOUR REF:  ATS OF 21/12/02","""]
#    aa+=["PAYCHEX - RCX    DES:PAYROLL    ID:95475300004896X  INDN:SKYVIEW\nCAPITAL GROUP   CO ID:1161124166 CCD"]
#    aa+=[" #Integrated Call Center Solutions, Florham Park NJ, 07932- US'})"]
    
    for place in aa:
        print ("[place]: "+str(place))
        print ("Is like address: "+str(is_look_like_address(place)))
        
        if 'amazon method' in []:
            place,meta=alg_resolve_address_v0(place)
            print(place)
        else:
            lat,lng=lookup_address_google(place)
            print ("GOT LAT LNG: "+str(lat)+","+str(lng))

    return



if __name__=='__main__':
    branches=['dev_clean_raw']
    branches=['dev_sample_queries']

    for b in branches:
        globals()[b]()




"""
MY KEY:
v1.public.eyJqdGkiOiJjZGVmNWRmMi0yNzRiLTRhOWItYmQ1Zi02ZWVkMDBiMDYxMjkifTfg432tsDiP2LK67yuhA1SpI9VKmtpaf3eK1R2HS8cipDAsdQq0RM_lFbdc8m6YYoIfbY7R9Mk5fiM7MhqdIF9Cs_6QIlacVYw6tLQVzyLbWQUQfEHCM8cN8_n7FmA_p7GdWQt4QhIc5e3osa0pFLGUmmrMrDlwOOwsZjHBN2t2SpYKfbWibGcObt9Mb4D-LxXdkfbNlYj-ifjxcHzH_r-b9TCNVFvCn8x0wRth-xmqCIS0CISr_nFwp87-6vPs4aIoXNUz6domUp4xTK_j6HvZixoMU8ADAOvPoucma2bkJCkr-4a7jF0q20acGrdseO6GaYFlp_1_YfkaY-UguDk.ZWU0ZWIzMTktMWRhNi00Mzg0LTllMzYtNzlmMDU3MjRmYTkx

explore.place.Esri
- place index exists but needs to hvae keys attached
https://us-east-1.console.aws.amazon.com/location/places/home?region=us-east-1#/describe/explore.place.Esri


https://us-east-1.console.aws.amazon.com/location/api-keys/home?region=us-east-1#/describe/esri_places_key

Resources
Resources accessible with this API key.

arn:aws:geo:us-east-1:487320324532:place-index/explore.place.Esri
Actions
This key authorizes the following actions.

Service
Actions
Maps	N/A
Places	GetPlace, SearchPlaceIndexForPosition, SearchPlaceIndexForSuggestions, SearchPlaceIndexForText
Routes	N/A


CREATE MAP:
"""

"""
CREATE MAP
watchtower_map_here_hybrid
key:  per above
esri_places_key

Name
watchtower_map_here_hybrid
Map style
HERE Hybrid
Description
 
ARN
 arn:aws:geo:us-east-1:487320324532:map/watchtower_map_here_hybrid

 

"""