import os,sys
import re
import subprocess
import ocrmypdf


LOCAL_PATH = os.path.abspath(os.path.dirname(__file__))+"/"


def downsample_pdf(input_pdf, output_pdf, dpi=300):
    gs_command = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-r{dpi}',  # Set resolution
        '-dNOPAUSE',
        '-dBATCH',
        f'-sOutputFile={output_pdf}',
        input_pdf
    ]
    subprocess.run(gs_command)




def dev1():

    test_case_1_fpath=LOCAL_PATH+"../pdf_samples/TEST_CASE_1_PAGE_ORG_IMAGE_Management-Properties-v-Brusko-Copy-of-First-Citizens-Bank-Checks-2020.pdf"
    dpi=300
    input_pdf = test_case_1_fpath
    output_pdf = re.sub(r'\.pdf','_DPI'+str(dpi)+'.pdf',input_pdf)

    downsample_pdf(input_pdf,output_pdf,dpi=dpi)
    print ("REDUCING TO: "+str(dpi)+" dpi to: "+str(output_pdf))



    return
    # Set the options
    options = {
        'output_type': 'pdf',
        'dpi': dpi,  # Set to a lower DPI to reduce memory usage
        'rotate_pages': True,
        'deskew': True,
        'force_ocr': True
    }
    
    
    ocrmypdf.ocr(input_pdf, output_pdf, **options)

    return


dev1()
