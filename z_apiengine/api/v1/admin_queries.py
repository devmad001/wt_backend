import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

## [ ] move to services
from w_storage.gstorage.gneo4j import Neo


#0v1# JC Jan 27, 2024

## TODOS:
#[ ] add pw control

"""
    Allow direct queries to neo4j
    - for dev or to support internal systems
    
    ORG SAMPLE:
    http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/run_query?query=jon
    
"""

router = APIRouter()


## [ ] upgrade to sessions based
def get_db_session():
    return


@router.get("/{case_id}/run_query", include_in_schema=False) #*HIDE FROM DOCS AND ADD PW
async def handle_run_query(case_id: str, request: Request, query: str = Query(...)):
    # Validate the query parameter
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")

    the_json = {'data': {}}

    if False:
        try:
            # Obtain a session from the Neo4j driver
            with get_db_session() as session:
                # Run the query
                result = session.run(query)
                
                # Process the result (example)
                records = [record for record in result]
                the_json['data'] = records
    
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        the_json['data']=local_cypher_transactions(case_id=case_id)

    return the_json


def local_cypher_transactions(case_id=''):
    #** via z_apiengine/services/timeline_service

    stmt="""
    MATCH (t:Transaction)
    WHERE t.case_id='"""+str(case_id)+"""'
    return t
    """
    jsonl,df,tx,meta=Neo.run_stmt_to_normalized(stmt)
    records=[]
    for record in jsonl:
        records.append(record['t'])
    return records


def local_query_dev():
    # new age evan
    # http://127.0.0.1:8008/api/v1/case/65a8168eb3ac164610ea5bc2/run_query?query=jon
    case_id='65a8168eb3ac164610ea5bc2'

    return


if __name__=='__main__':
    branches=['local_query_dev']
    for b in branches:
        globals()[b]()
