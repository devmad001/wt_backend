import os
import sys
import codecs
import json
import re

from fastapi import APIRouter

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from api.v1.route_checks import router as route_checks


#0v1# JC Jan 30, 2024  Setup


"""
    API FOR INTERNAL SYSTEMS
    i)  Support check meta data integration

"""

router_v1 = APIRouter()
router_v1.include_router(route_checks, prefix="", tags=[])





