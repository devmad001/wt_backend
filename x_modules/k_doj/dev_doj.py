import os,sys
import re
import json
import time
import copy
import codecs

import requests

from pathlib import Path
import shutil

import numpy as np

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)


CHECK_MEDIA_STORAGE_DIR=LOCAL_PATH+"CHECK_MEDIA_STORAGE"


#0v1# JC  Feb  1, 2024  Init


"""
    DOJ OPTIONS
    - 

"""



def dev_plan_for_doj():

    """
        leanest real-time
        - FE transactions to names, lookup each name.
        
        lean stand-alone
        - mysql person, business record.
                    -> keep to just name + case_id
                    
        lean KB
        - add to KB  (but, do so via external markup process)

        internal query for names from case
        - do via m_query or cypher playground

    """
    
    return



def dev1():
    endpoint='https://registry.epventures.co/v1/wt_services/doj_and_ofac?query='
    
    names=[]
    names+=['Joaquin GUZMAN LOERA']
    
    for name in names:
        url=endpoint+name
        print (url)

    return




if __name__ == "__main__":
    dev1()



"""
https://registry.epventures.co/v1/wt_services/doj_and_ofac?query=

Joaquin GUZMAN LOERA

{"data":{"results":{"doj":[{"_id":"65bbb03209bd8b2e928ee2b8","uuid":"96443e3e-5303-4f6f-a2ab-ef15438a3e5b","content":"{\"body\":\"Ovidio Guzman Lopez, 33, of Culiacan, Mexico, was arraigned in federal court in Chicago today after his extradition from Mexico to the United States on Sept. 15. In January, Guzman Lopez was arrested in Mexico pursuant to a U.S. request for his provisional arrest with a view toward extradition.Guzman Lopez, aka El Raton and Raton Nuevo, is charged in the Northern District of Illinois with five counts in a nine-count 12th superseding indictment alleging that from around May 2008 and continuing to at least Oct. 21, 2021, he engaged in a drug trafficking Continuing Criminal Enterprise (CCE), along with additional drug, money laundering, and firearms charges. Guzman Lopez is charged with conspiring to distribute cocaine, heroin, methamphetamine, and marijuana from Mexico and elsewhere for importation into the United States.According to court documents, the charges stem from a decades-long, collaborative, multi-district effort between the Criminal Division’s Narcotic and Dangerous Drug Section (NDDS), based in Washington, D.C., the Northern District of Illinois, the Southern District of California, and their law enforcement partners.Under the terms of the U.S.-Mexico extradition treaty, the United States had up to 60 days to present a fully supported request, one in compliance with the terms of the treaty. The United States submitted that request in February 2023. A Mexican court reviewed the U.S. request and last month favorably recommended his extradition. The Foreign Ministry reviewed the decision and similarly concluded that Guzman Lopez should be extradited to the United States. Guzman Lopez was subsequently extradited to the United States on Sept. 15. He was arraigned on the charges earlier today before U.S. District Judge Sharon Johnson Coleman of the U.S. District Court for the Northern District of Illinois and pleaded not guilty. He waived his right to a detention hearing and was ordered to remain detained without bond.Guzman Lopez is one of the sons of Joaquin Guzman Loera, aka El Chapo, who was&nbsp;convicted&nbsp;by a jury in the Eastern District of New York for his role as the leader of the Sinaloa Cartel. Following Guzman Loera’s arrest in January 2016 and extradition to the United States in January 2017, Guzman Lopez and his three brothers, Ivan Archivaldo Guzman Salazar, Jesus Alfredo Guzman Salazar, and Joaquin Guzman Lopez, aka “the Chapitos,” who are also charged in the indictment, allegedly assumed their father’s former role as leaders of the Sinaloa Cartel, along with Zambada Garcia and Damaso Lopez Nunez, aka Licenciado. The Chapitos subsequently amassed greater control over the Sinaloa Cartel by allegedly threatening and causing violence against Lopez Nunez, his family, and his associates and, as a result, became principal leaders and drug traffickers within the Sinaloa Cartel.Guzman Lopez was also indicted in the Southern District of New York on charges of continuing criminal enterprise, fentanyl importation conspiracy, fentanyl distribution conspiracy, possession of machineguns and destructive devices, conspiracy to possess machineguns and destructive devices, and conspiracy to commit money laundering.Acting Assistant Attorney General Nicole M. Argentieri of the Justice Department’s Criminal Division, Acting U.S. Attorney Morris Pasqual for the Northern District of Illinois, Acting U.S. Attorney Andrew R. Haden for the Southern District of California, Assistant Director Luis Quesada of the FBI’s Criminal Investigative Division, Executive Associate Director Katrina W. Berger of Homeland Security Investigations (HSI), and U.S. Drug Enforcement Administration (DEA) Administrator Anne Milgram made the announcement.This case is the result of the ongoing efforts by the Organized Crime Drug Enforcement Task Forces (OCDETF), a partnership that brings together the combined expertise and unique abilities of federal, state, and local law enforcement agencies.The FBI Washington, San Diego, and El Paso Field Offices, HSI Nogales Office, DEA’s Chicago and San Diego Divisions, and IRS Criminal Investigation’s Chicago Office investigated the case.The Justice Department’s Office of International Affairs handled the extradition, in collaboration with the U.S. Marshals Service. The Office of Enforcement Operations also provided significant assistance in the case.The Justice Department thanks the Government of Mexico, including the Mexican Foreign Ministry and the Mexican Attorney General’s Office. Earlier today, U.S. Attorney General Merrick B. Garland spoke by phone with Mexico’s Attorney General Alejandro Gertz Manero to express his gratitude to Attorney General Gertz and the Government of Mexico for successfully extraditing Guzman Lopez.&nbsp;Trial Attorney Kirk Handrich of NDDS, Assistant U.S. Attorneys Andrew Erskine and Erika Csicsila for the Northern District of Illinois, and Assistant U.S. Attorney Matthew Sutton for the Southern District of California are prosecuting the case.An indictment is merely an allegation. All defendants are presumed innocent until proven guilty beyond a reasonable doubt in a court of law.\",\"teaser\":\"Ovidio Guzman Lopez, 33, of Culiacan, Mexico, was arraigned in federal court in Chicago today after his extradition from Mexico to the United States on Sept. 15. In January, Guzman Lopez was arrested in Mexico pursuant to a U.S. request for his provisional arrest with a view toward extradition.\\n\",\"title\":\"Son of Joaquin Guzman Loera aka “El Chapo” Arraigned on Federal Criminal Charges Following his Extradition from Mexico to the United States for International Drug Trafficking\"}","createdAt":"2024-02-01T14:52:34.270Z","updatedAt":"2024-02-01T14:52:37.018Z"}],"ofac":[{"ofac_alt_ent_num":6861,"ofac_alt_num":4617,"ofac_alt_type":"aka","ofac_alt_name":"AREGON, Max","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4618,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN, Chapo","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4619,"ofac_alt_type":"aka","ofac_alt_name":"GUIERREZ LOERA, Jose Luis","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4620,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN FERNANDEZ, Joaquin","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4621,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN LOESA, Joaquin","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4622,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN PADILLA, Joaquin","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4623,"ofac_alt_type":"aka","ofac_alt_name":"GUMAN LOERAL, Joaquin","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4624,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN, Archibaldo","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4625,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN, Aureliano","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4626,"ofac_alt_type":"aka","ofac_alt_name":"ORTEGA, Miguel","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4627,"ofac_alt_type":"aka","ofac_alt_name":"RAMIREZ, Joise Luis","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4628,"ofac_alt_type":"aka","ofac_alt_name":"CARO RODRIGUEZ, Gilberto","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4629,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN, Joaquin Chapo","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4630,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN LOREA, Chapo","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4631,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN LOEIA, Joaguin","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4632,"ofac_alt_type":"aka","ofac_alt_name":"GUZMAN, Achivaldo","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4633,"ofac_alt_type":"aka","ofac_alt_name":"OSUNA, Gilberto","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_alt_ent_num":6861,"ofac_alt_num":4634,"ofac_alt_type":"aka","ofac_alt_name":"RAMOX PEREZ, Jorge","ofac_alt_remarks":"","type":"ofac_alt"},{"ofac_add_ent_num":6861,"ofac_add_num":4888,"ofac_add_address":"","ofac_add_city":"","ofac_add_state_province":"","ofac_add_postal_code":"","ofac_add_country":"","ofac_add_remarks":"","type":"ofac_add"}]}}}

"""



