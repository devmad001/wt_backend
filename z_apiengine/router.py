import os
import sys
import codecs
import json
import re

from fastapi import APIRouter

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from api.v0.timeline_router import router as timeline_router
from api.v0.square_router import router as square_router
from api.v0.job_router import router as job_router
from api.v0.bot_router import router as bot_router
from api.v0.finaware_router import router as finaware_router

from api.v1.command_router import router as command_router
from api.v1.square_router_v1 import router as square_router_v1
from api.v1.graphs_router_v1 import router as graphs_router_v1
from api.v1.FE_case_view import router as FE_case_view_v1
from api.v1.FE_auth import router as FE_auth_v1
from api.v1.FE_buttons import router as FE_buttons_v1
from api.v1.bot_router import router as bot_router
from api.v1.general_router import router as general_router
from api.v1.fixed_query_router import router as fixed_query_router

from api.v1.admin_queries import router as admin_queries
from api.v1.media_router import router as media_router


#from routers import case_router
#from . import timeline, case


#0v5# JC Jan 27, 2024  Admin or graph queries
#0v4# JC Jan 23, 2024  fixed_query_router for transaction tracker etc.
#0v3# JC Dec  8, 2023  general_router (excel)
#0v2# JC Nov 24, 2023  Split to v0 for dev and v1 for prod
#0v1# JC Oct 26, 2023  Setup


"""
    NOTES:
    - /api/v1/auth_handshake  <-- via fast_main
"""

# v1 Routers:  Initial FinAware
router_v1 = APIRouter()
router_v1.include_router(FE_case_view_v1, prefix="", tags=[])

router_v1.include_router(square_router_v1, prefix="", tags=[])
router_v1.include_router(graphs_router_v1, prefix="", tags=[])
router_v1.include_router(timeline_router, prefix="", tags=[])

router_v1.include_router(bot_router, prefix="", tags=[])

#general_router: generate_excel & pdf
router_v1.include_router(general_router, prefix="", tags=[])
router_v1.include_router(FE_buttons_v1, prefix="", tags=[])

# Dec 29 for viewing of exe logfiles
router_v1.include_router(command_router, prefix="", tags=[])

# Jan 23, 2024
router_v1.include_router(fixed_query_router, prefix="", tags=[])

# Jan 27, 2024
router_v1.include_router(admin_queries, prefix="", tags=[])
# Jan 28, 2024
router_v1.include_router(media_router, prefix="", tags=[])


if False:
    # above should have test?
    
    # below no tests
    router_v1.include_router(job_router, prefix="", tags=[])
    router_v1.include_router(finaware_router, prefix="", tags=[])
    

router_v0 = APIRouter()
if False:
    router_v0.include_router(timeline_router, prefix="", tags=[])
    router_v0.include_router(square_router, prefix="", tags=[])

    router_v0.include_router(job_router, prefix="", tags=[])
    router_v0.include_router(command_router, prefix="", tags=[])
    router_v0.include_router(finaware_router, prefix="", tags=[])



"""

"""
