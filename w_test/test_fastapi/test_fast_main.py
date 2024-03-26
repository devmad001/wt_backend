# test_main.py
import os,sys
from fastapi.testclient import TestClient

LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../../")
        
from z_apiengine.fast_main import app  # Import the FastAPI app instance from your main module

client = TestClient(app)

"""
    RECALL TESTING USING:
    - python -m pytest
    - pytest to run all
    - pytest tests/test_timeline.py for specific


"""

#def test_serve_static_js_file():
#    response = client.get("/static/example.js")
#    assert response.status_code == 200
#    assert response.headers["content-type"] == "application/javascript"

def test_favicon():
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/vnd.microsoft.icon"
    



"""

project_root/
│
├── app/
│   ├── main.py            # FastAPI initialization and application instance
│   ├── api/
│   │   ├── v1/            # Versioning your API
│   │   │   ├── router.py  # Collects all the routers
│   │   │   ├── case.py
│   │   │   ├── timeline.py
│   │   │   └── ...
│   ├── models/
│   ├── services/
│   └── database.py
│
├── tests/                 # Dedicated directory for tests
│   ├── conftest.py        # Configuration for pytest, fixtures, etc.
│   ├── test_main.py       # Tests for main application behaviors
│   ├── api/               # Tests structured similarly to your API structure
│   │   ├── v1/            # Tests for v1 of your API
│   │   │   ├── test_case.py
│   │   │   ├── test_timeline.py
│   │   │   └── ...
│   └── ...
│
└── ...



project_root/
│
├── app/
│   ├── api/
│   │   ├── v0/            
│   │   │   ├── timeline_router.py  # v0 specific timeline router
│   │   │   └── ...                 # Other v0 routers
│   │   ├── v1/            
│   │   │   ├── timeline_router.py  # v1 specific timeline router
│   │   │   └── ...                 # Other v1 routers
│   ├── services/
│   │   ├── timeline_service.py     # Shared service logic for timeline
│   └── ...
└── ...



"""



