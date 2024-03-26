import os
import sys
import codecs
import json
import re



LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"
sys.path.insert(0,LOCAL_PATH)
sys.path.insert(0,LOCAL_PATH+"../")

from w_ui.sim_user import interface_dump_excel
from w_mindstate.mindstate import Mindstate
from w_file_repo.manage_pdfs import interface_get_pdf_content

from flask import Flask, render_template, send_from_directory, request, Response, jsonify
from flask_cors import CORS

from get_logger import setup_logging
logging=setup_logging()


#0v2# JC  Oct 14, 2023  More components served here:  pdf_viewer, dump excel, view status?
#0v1# JC  Oct  4, 2023  Init

"""
    CENTRALIZED UI COMPONENTS
    - for use in various dashboards views
    - for use in various widgets
    
  NOTES:
  - timeline + chatbot are stand-alone not included here

"""

### CONFIG
config_file=LOCAL_PATH+'../'+'w_config_dashboard.json'
def load_config():
    global config_file
    DASH={}
    with open(config_file, 'r') as fp:
        CONFIG = json.load(fp)
    DASH=CONFIG['dashboards']['square']
    return CONFIG,DASH

CONFIG,DASH=load_config()
print("dashboard:", DASH)
PORT=int(DASH['port'])
app = Flask(__name__, static_url_path='/nonexistentstatic', static_folder='static', template_folder='templates')
CORS(app)  #Allow CORS so that parent html can adjust iframe height

@app.route('/square')
def index():
    return render_template('square1.html')

#[x] migrated to fastapi
@app.route('/static/<path:filename>')
def serve_static(filename):
    print("Serving:", filename)
    if filename.endswith('.js'):
        response = send_from_directory('static', filename)
        response.headers['Content-Type'] = 'application/javascript'
        return response
    return send_from_directory('static', filename)

def local_load_multimodal(case_id):
    ## Can access via api or module
    Mind=Mindstate()
    sesh,session_id,is_created=Mind.start_or_load_session(case_id=case_id)
    
    answer_dict=Mind.get_field(session_id,'last_answer_meta')

    return Mind,session_id,answer_dict

@app.route('/dynamic_square')
def dynamic_html():
    html='No html found - empty Square'

    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))

    
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    
    try: html=answer_dict.get('multimodal',{}).get('html','')
    except: html=''
    
    if not html:
        html="" #"- at session_id: "+str(session_id)
    
    return render_template('square_jinja1.html', dynamic_content=html)


#################################################################
### MIGRATE PDF VIEWER ENDPOINT HERE
#https://storage.epventures.co/case/case_wells_fargo_small/pdf/Wells%20Fargo%20Bank%20Statement-pages-2-5.pdf?page=0&key=94402ad68cae74b63f7f6179e0d73fdd5ef9cc1000f6756e77d743b0044bccd6
@app.route('/case/<case_id>/pdf/<filename>', defaults={'page_num': 0})
@app.route('/case/<case_id>/pdf/<filename>/<page_num>', methods=['GET'])
def view_pdf(case_id, filename, page_num):
    logging.info("[debug] at view pdf but serve_ui??")
    a=stopp_no_flask
    print ("[ ] view pdf key must match -- watch cause auto pre-generated in some cases")

    # Get the 'page' query parameter
    page_param = request.args.get('page')
    key_param = request.args.get('key') # <A HREF="http://www.example.com/myfile.pdf?page=4&key=123">

    # If 'page' query parameter exists, use it instead of path 'page_num'
    if page_param:
        page_num = page_param

    # Decide whether to fetch the full PDF content or just a page's content based on page_num's value
    if not page_num or str(page_num)=='0':
        pdf_content, pdf_key,page_content,page_key = interface_get_pdf_content(case_id, filename=filename)
        response_content = pdf_content
    else:
        pdf_content, pdf_key,page_content,page_key = interface_get_pdf_content(case_id, filename=filename, page_num=page_num)
        response_content = page_content
        
    logging.info("[debug content length]: "+str(len(response_content)))

    # Create a Flask Response object to send the PDF data and set appropriate headers
    response = Response(response_content)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={filename}"
    
    logging.info("[pdf key]: "+str(pdf_key))
    
    return response


#################################################################
#################################################################
#    EXTRA COMPONENT ENDPOINTS
# *** MOVE FROM pyfiledrop.py which was there temporarily!

print ("[sample excel]: /case/case_wells_fargo_small/get_excel?case_id=case_wells_fargo_small&session_id=1")
@app.route("/case/<case_id>/get_excel", methods=["GET"])
def handle_dump_excel(case_id):
    #** see:  generate_excel

    ###################################################################
    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    ###################################################################

    full_filename = ''
    case_filename = ''
    rr = {}

    #** make visible until steady
    try:
        full_filename, case_filename = interface_dump_excel(case_id=case_id)
    except Exception as e:
        logging.error("[ERROR CREATING EXCEL] "+str(e))
        rr['error'] = str(e)
        return jsonify(rr)

    relative_filename = os.path.relpath(full_filename, os.path.join(LOCAL_PATH, '..'))
    
    logging.info("[ready to dump excel?]")
    if os.path.exists(full_filename):
        print("[debug] want to dump excel: " + str(full_filename))
        print("[debug] want to dump excel relative: " + str(relative_filename))
        print("[debug] LOCAL PATH: " + str(LOCAL_PATH))
        print("[debug] Full path: " + os.path.join(LOCAL_PATH, '..', relative_filename))
        
        # Get directory from full_filename
        directory = os.path.dirname(full_filename)
        filename= os.path.basename(full_filename)
        
        return send_from_directory(directory, filename, as_attachment=True, download_name=case_filename)
    
    else:
        logging.warning("[WARNING] excel file does not exist: "+str(full_filename))
        rr['status'] = f"Dumping Excel for {case_id}"
        rr['warning'] = 'Excel file not produced'
        return jsonify(rr)


"""
    IS CASE PROCESSING?  Check status for done, started time,
    CHECK IF running in background.
  rr['status']=f"Checking processing for {case_id}"
    try:
        job=interface_get_job_dict(case_id=case_id)
        rr['job']=job
        if not job:
            rr['status']='Job not created for: '+str(case_id)
"""
@app.route('/view_runnings')
def view_runnings():
    print ("> see app_parenty")
    html='view_runnings recall elsewhere too'
    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    return html


@app.route('/dev_view_case_report')
@app.route('/dev_view_case_graph')
@app.route('/dev_runnings_debug')
def view_runnings_debug():
    print ("> see app_parenty")
    html='view_runnings_debug recall elsewhere too'
    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    return html

@app.route('/start_case_processing')
def start_case_processing():
    print ("> see app_parenty")
    html='start case processing *yes, elsewhere too'
    ## Case + auth
    case_id = request.args.get('case_id')
    session_id = request.args.get('session_id')
    print ("CASE: "+str(case_id))
    ## Load from cache (mind state)
    Mind,session_id,answer_dict=local_load_multimodal(case_id)
    return html



if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=PORT)
    

"""

"""
