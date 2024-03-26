#!/usr/bin/env python3
# -*- coding: utf-8 -*-



# Import Libraries
import json
from typing import Tuple, cast
from io import BytesIO
import os
import argparse
import re
import fitz



#0v3# JC Jan 18, 2024  Support for without comma searches caused conflict on search terms 60,000 == 60000
#0v2# JC Jan 11, 2024  Applied via filerepo.py -> top_highlight_terms.  Extend for single term highlighting
#0v1# AS Dec 28, 2023  Initial version 



def extract_info(input_file: str):
    """
    Extracts file info
    """
    # Open the PDF
    pdfDoc = fitz.open(input_file)
    output = {
        "File": input_file, "Encrypted": ("True" if pdfDoc.isEncrypted else "False")
    }
    # If PDF is encrypted the file metadata cannot be extracted
    if not pdfDoc.isEncrypted:
        for key, value in pdfDoc.metadata.items():
            output[key] = value
    # To Display File Info
    print("## File Information ##################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in output.items()))
    print("######################################################################")
    return True, output


def search_for_text_org(lines, search_str):
    # ['165.00', 'S00389023230063399']

    """
    Search for the search string within the document lines and return the entire sentence
    """
    for (rect, line) in lines:
        line_without_commas=line.replace(',','')
        for x in search_str:
            x=x.replace(',','')
            if re.search(fr'\b{x}\b', line_without_commas, re.IGNORECASE):
                yield rect

def search_for_text(lines, search_str):
    # search_str sample: ['165.00', 'S00389023230063399']
    #; remove requirement for commas
    """
    Search for the search string within the document lines and return the entire sentence
    ** See JLOGIC MODIFY
    """

    keepers=[]
    saw={}

    saw_count_mem={}
    for (rect, line) in lines:
        line_without_commas=line.replace(',','')
        saw_count=0
        sawx={}  #Watch double count from comma removal
        for x in search_str:
            x=x.replace(',','') #Normalize without commas **but can lead to double count if 60000 and 60,000 as search strings
            if x in sawx:continue
            sawx[x]=1
            escaped_x=re.escape(x)
            if re.search(fr'\b{escaped_x}\b', line_without_commas, re.IGNORECASE): #Throws error if not escaped
                saw[x]=saw.get(x,0)+1  #Count occurences
                keepers+=[(rect,x)]
                saw_count+=1
        saw_count_mem[rect]=saw_count
    print ("DONE")

    """
    #JLOGIC:
        1) If max 1 occurence then yield that one
        2) If multiple search terms in same rect then use that one (*almost like row)
    """
    ## LOGIC 1:   If max 1 occurence then use that one
    if any([v==1 for v in saw.values()]):
        for rect,x in keepers:
            if saw[x]==1:
                yield rect
                break
    ## LOGIC 2:   If saw_count_mem>1 then multiple search terms found in rect use that one
    elif any([v>1 for v in saw_count_mem.values()]):
        for rect,x in keepers:
            if saw_count_mem[rect]>1:
                yield rect
                break
    else:
        ## Highlight possibly multiple occurences
        for rect,x in keepers:
            yield rect
    return

def highlight_matching_data(page, matched_values, type):
    """
    Highlight entire sentences containing matching values
    """
    matches_found = 0
    for line in matched_values:
        matches_found += 1
        highlight = None
        if type == 'Highlight':
            highlight = page.add_highlight_annot(line)
        highlight.update()
    return matches_found


def process_data_org(input_file: str, output_file: str, search_str: str, pages: Tuple = None, action: str = 'Highlight'):
    """                                                                                         
    Process the pages of the PDF File
    """
    # Open the PDF
    pdfDoc = cast(fitz.Document, fitz.open(input_file))
    # Save the generated PDF to memory buffer
    output_buffer = BytesIO()
    total_matches = 0
    # Iterate through pages
    for pg in range(pdfDoc.page_count):
        # If required for specific pages
        if pages:
            if str(pg) not in pages:
                continue
        # Select the page
        page = pdfDoc[pg]
        # Get Matching Data
        # Split page by lines
        lines = {}
        rects = {}
        words = list(page.get_text("words"))
        words.sort(key=lambda x: x[1]*1000000+x[0])
        # print(json.dumps(words, indent=1))
        # exit()
        for (x0, y0, x1, y1, word, block_no, line_no, word_no) in words:
            y0 = int(y0)
            line = lines.get(y0, [])
            if len(line) == 0:
                rects[y0] = fitz.Rect(0, y0, page.bound().width, y1)
            line.append(word)
            lines[y0] = line
        lines = [[rects[y0], ' '.join(line)] for y0, line in lines.items()]
        page_lines = lines
        matched_values = search_for_text(page_lines, search_str)
        if matched_values:
            matches_found = highlight_matching_data(page, matched_values, 'Highlight')
            total_matches += matches_found

    print(f"{total_matches} Match(es) Found of Search String {search_str} In Input File: {input_file}")
    # Save to output
    pdfDoc.save(output_buffer)
    pdfDoc.close()
    # Save the output buffer to the output file
    with open(output_file, mode='wb') as f:
        f.write(output_buffer.getbuffer())


#page_content=fp.getvalues()  #binary bytes
def process_highlighting(page_content: bytes, search_str:str, output_file: str='', action: str = 'Highlight'):
    """
    Process the single-page PDF content.
    """
    # Open the PDF from the binary bytes
    pdfDoc = fitz.open("pdf", page_content)
    
    # Save the generated PDF to a memory buffer
    output_buffer = BytesIO()
    total_matches = 0
    
    # Select the page
    page = pdfDoc[0]  # Assuming there is only one page
    
    # Get Matching Data
    # Split page by lines
    lines = {}
    rects = {}
    words = list(page.get_text("words"))
    words.sort(key=lambda x: x[1]*1000000+x[0])
    
    for (x0, y0, x1, y1, word, block_no, line_no, word_no) in words:
        y0 = int(y0)
        line = lines.get(y0, [])
        if len(line) == 0:
            rects[y0] = fitz.Rect(0, y0, page.bound().width, y1)
        line.append(word)
        lines[y0] = line
    
    lines = [[rects[y0], ' '.join(line)] for y0, line in lines.items()]
    page_lines = lines
    matched_values = search_for_text(page_lines, search_str)
    
    if matched_values:
        matches_found = highlight_matching_data(page, matched_values, 'Highlight')
        total_matches += matches_found
    
    print(f"{total_matches} Match(es) Found of Search String {search_str}")
    
    # Save to output
    pdfDoc.save(output_buffer)
    pdfDoc.close()
    
    output= output_buffer.getvalue()
    # Save the output buffer to the output file
    if output_file:
        with open(output_file, mode='wb') as f:
            f.write(output)
    return output

def process_file(**kwargs):
    """
    To process one single file
    Redact, Frame, Highlight... one PDF File
    Remove Highlights from a single PDF File
    """
    input_file = kwargs.get('input_file')
    output_file = kwargs.get('output_file')
    if output_file is None:
        output_file = input_file
    search_str = kwargs.get('search_str')
    pages = kwargs.get('pages')
    process_data(input_file=input_file, search_str=search_str, output_file=output_file, pages=pages)


def process_folder(**kwargs):
    """
    Redact, Frame, Highlight... all PDF Files within a specified path
    Remove Highlights from all PDF Files within a specified path
    """
    input_folder = kwargs.get('input_folder')
    search_str = kwargs.get('search_str')
    # Run in recursive mode
    recursive = kwargs.get('recursive')
    pages = kwargs.get('pages')
    # Loop though the files within the input folder.
    for foldername, dirs, filenames in os.walk(input_folder):
        for filename in filenames:
            # Check if pdf file
            if not filename.endswith('.pdf'):
                continue
             # PDF File found
            inp_pdf_file = os.path.join(foldername, filename)
            print("Processing file =", inp_pdf_file)
            process_file(input_file=inp_pdf_file, output_file=None,
                         search_str=search_str, pages=pages)
        if not recursive:
            break


def is_valid_path(path):
    """
    Validates the path inputted and checks whether it is a file path or a folder path
    """
    if not path:
        raise ValueError(f"Invalid Path")
    if os.path.isfile(path):
        return path
    elif os.path.isdir(path):
        return path
    else:
        raise ValueError(f"Invalid Path {path}")


def parse_args():
    """Get user command line parameters"""
    parser = argparse.ArgumentParser(description="Available Options")
    parser.add_argument('-i', '--input_path', dest='input_path', type=is_valid_path,
                        required=True, help="Enter the path of the file or the folder to process")
    parser.add_argument('-p', '--pages', dest='pages', type=tuple,
                        help="Enter the pages to consider e.g.: [2,4]")

    parser.add_argument('-s', '--search_str', dest='search_str'                            # lambda x: os.path.has_valid_dir_syntax(x)
                            , type=str, nargs='+', required=True, help="Enter a valid search string")
    path = parser.parse_known_args()[0].input_path
    if os.path.isfile(path):
        parser.add_argument('-o', '--output_file', dest='output_file', type=str  # lambda x: os.path.has_valid_dir_syntax(x)
                            , help="Enter a valid output file")
    if os.path.isdir(path):
        parser.add_argument('-r', '--recursive', dest='recursive', default=False, type=lambda x: (
            str(x).lower() in ['true', '1', 'yes']), help="Process Recursively or Non-Recursively")
    args = vars(parser.parse_args())
    # To Display The Command Line Arguments
    print("## Command Arguments #################################################")
    print("\n".join("{}:{}".format(i, j) for i, j in args.items()))
    print("######################################################################")
    return args


if __name__ == '__main__':
    # Parsing command line arguments entered by user
    args = parse_args()
    # If File Path
    if os.path.isfile(args['input_path']):
        # Extracting File Info
        extract_info(input_file=args['input_path'])
        # Process a file
        process_file(
            input_file=args['input_path'], output_file=args['output_file'],
            search_str=args['search_str'] if 'search_str' in (args.keys()) else None,
            pages=args['pages']
        )
    # If Folder Path
    elif os.path.isdir(args['input_path']):
        # Process a folder
        process_folder(
            input_folder=args['input_path'],
            search_str=args['search_str'] if 'search_str' in (args.keys()) else None, pages=args['pages'], recursive=args['recursive']
        )
