import os, sys

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Query

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from services.graph_services import generate_waterfall_graph_data
from services.graph_services import generate_butterfly_graph_data


#0v1# JC Nov 23, 2023


"""
    waterfall + butterfly individual endpoints
    TESTS AT: w_test\test_fastapi\api\v1\test_chart_waterfall.py
"""

router = APIRouter()


@router.get("/{case_id}/waterfall")
@router.get("/{case_id}/waterfall_data")
async def get_waterfall(case_id: str, request: Request):
    """
    Retrieve waterfall data for a specific case.

    This endpoint returns a JSON object containing balance data by date, waterfall data by date,
    and styling information for presenting this data, such as axis titles and main title.

    Parameters:
    - **case_id**: Unique identifier of the case for which to retrieve data.

    Returns:
    - **balance_by_date**: A dictionary mapping dates to balance amounts.
    - **waterfall_by_date**: A dictionary mapping dates to debit and credit amounts.
    - **style**: Styling information for the graph presentation.

    Example response:
    {
        "balance_by_date": {
            "2021-06-01": 7349.72,
            ...
        },
        "waterfall_by_date": {
            "2021-06-01": {
                "debit": -132106.68,
                "credit": 26105.21
            },
            ...
        },
        "style": {
            "x_axis_title": "Debit/Credit Amounts",
            "y_axis_title": "Amount",
            "main_title": "Balance over Time"
        }
    }
    """
    the_json = {
        'data': {},  # This should be populated with actual data fetching logic
        'style': {
            'x_axis_title': 'Debit/Credit Amounts',
            'y_axis_title': 'Amount',
            'main_title': 'Balance over Time'
        }
    }

    # Replace the following line with your actual data fetching logic
    the_json['data'], meta = generate_waterfall_graph_data(case_id)

    #returns data.data and data.style
    return the_json


@router.get("/{case_id}/butterfly")
@router.get("/{case_id}/butterfly_data")
async def get_butterfly(case_id, request: Request):
    """
    data={'butterfy_sorted': [{'name': 'Beam-Premium', 'debit_total': 111.72, 'credit_total': 0.0}, {'name': 'Card 7413', 'debit_total': 579.42, 'credit_total': 0.0}, {'name': 'Afterpay US, Inc', 'debit_t
        
    the_json['data']['style']={}
    the_json['style']['x_axis_title']='Debit/Credit Amounts'
    the_json['style']['y_axis_title']='Entities'

    """

    the_json={}
    bdata,meta=generate_butterfly_graph_data(case_id)
    #Butterfly data comes in as data, style already in top. No nested data like above.
    
    the_json={}
    the_json['data']=bdata['data']
    the_json['style']=bdata['style']

    #returns data and style
    return the_json
