import os
import sys
import codecs
import json
import re
import uuid

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")


#0v1# JC  Sep  7, 2023  Init


## NOTES:
#- ideally use rdflib or as cypher constraints but easier to use this

print ("[ ] collect source_schema.py into SCHEMA_KBAI or similar")

## One pdf file with 140 pages, 12 statements
# ^ assume one account?? or running pointer?

"""
SUPPORT FOR PROCESSING:
- 1 file
- pdf 'images'
- multiple statements in file
- possibly multiple accounts in a file
- statement has multiple sections (flow across pages)

- use a page_pointer to track active statement/doc/page info

- Text extraction at page-level via various methods
   ^^ multiple raw text extraction content

"""

## Add full test for fields (keep condensed esp since use at various points)

## [case]
PTR_SCHEMA={}
PTR_SCHEMA['case_id']=''

## [file]
PTR_SCHEMA['file']={}
PTR_SCHEMA['file']['filename']=''
PTR_SCHEMA['file']['id']=PTR_SCHEMA['case_id']+"-"+PTR_SCHEMA['file']['filename']
PTR_SCHEMA['file']['file_page_num']=0
PTR_SCHEMA['file']['path_filename']=''

## [statement]
PTR_SCHEMA['statement']={}
PTR_SCHEMA['statement']['statement_page_num']=0
PTR_SCHEMA['statement']['statement_id']=''   #ideally listed but tbd
PTR_SCHEMA['statement']['account']={}
PTR_SCHEMA['statement']['account']['id']=''  #ok for account to be subset of statement

## [page]
PTR_SCHEMA['page']={}
## Page id vs file or vs statement (statemen_id is tbd)
PTR_SCHEMA['page']['id']=PTR_SCHEMA['file']['id']+"-"+str(PTR_SCHEMA['file']['file_page_num'])
PTR_SCHEMA['page']['content']={}
PTR_SCHEMA['page']['content']['method']='text'

## [section]
#    (ie/ active section across page?)
PTR_SCHEMA['section']={}
PTR_SCHEMA['section']['name']=''

## Extra meta
PTR_SCHEMA['chunk_id']=''  #ie/ page id chunk


## BELOW IS UNUSED FOR DEMO/DEV ONLY::
SOURCE_SCHEMA = {
    'Case': {
        'type': 'Class',
        'label': 'Case',
        'comment': 'An investigative case',
        'relationships': {
            'hasDocument': 'Document'
        }
    },
    'Document': {
        'type': 'Class',
        'label': 'Document',
        'comment': 'A document in a case',
        'relationships': {
            'hasPage': 'Page',
            'hasStatement': 'Statement',
            'hasSection': 'Section'
        },
        'properties': {
            'lineLocation': 'Line Location in the document'
        }
    },
    'Page': {
        'type': 'Class',
        'label': 'Page',
        'comment': 'A page in a document'
    },
    'Statement': {
        'type': 'Class',
        'label': 'Statement',
        'comment': 'A statement in a document'
    },
    'Section': {
        'type': 'Class',
        'label': 'Section',
        'comment': 'A section in a document'
    }
}


def dev1():
    return


if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()


"""
"""