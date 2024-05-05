from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import ByteStringObject, NameObject

def modify_pdf_content_stream(input_pdf_path, output_pdf_path, search_text, replace_text):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Extract the original content stream
        original_content = page.get_contents()

        if original_content is not None:
            # Decode the original content stream
            decoded_content = original_content.get_data().decode('latin-1')
            print ("AT: "+str(decoded_content))

            # Perform the replacement
            modified_content = decoded_content.replace(search_text, replace_text)

            # Encapsulate the modified content in a ByteStringObject
            modified_content_bytes = ByteStringObject(modified_content.encode('latin-1'))

            # Replace the page's content stream with the new bytes
            page[NameObject('/Contents')] = modified_content_bytes

        writer.add_page(page)

    with open(output_pdf_path, 'wb') as out:
        writer.write(out)



print ("** too messy and blank output")
# Example usage
input_pdf_path = '65cd06669b6ff316a77a1d21_sample_odd_pdf2txt.pdf'
output_pdf_path = 'output.pdf'
search_text = 'old text'
replace_text = 'new text'

modify_pdf_content_stream(input_pdf_path, output_pdf_path, search_text, replace_text)
