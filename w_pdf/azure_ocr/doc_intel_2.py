print ("python -m pip install azure-ai-documentintelligence")
#https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md
"""
Azure AI Document Intelligence client library for Python
Azure AI Document Intelligence (previously known as Form Recognizer) is a cloud service that uses machine learning to analyze text and structured data from your documents. It includes the following main features:

Layout - Extract content and structure (ex. words, selection marks, tables) from documents.
Document - Analyze key-value pairs in addition to general layout from documents.
Read - Read page information from documents.
Prebuilt - Extract common field values from select document types (ex. receipts, invoices, business cards, ID documents, U.S. W-2 tax documents, among others) using prebuilt models.
Custom - Build custom models from your own data to extract tailored field values in addition to general layout from documents.
Classifiers - Build custom classification models that combine layout and language features to accurately detect and identify documents you process within your application.
Add-on capabilities - Extract barcodes/QR codes, formulas, font/style, etc. or enable high resolution mode for large documents with optional parameters.
[Source code][python-di-src] | [Package (PyPI)][python-di-pypi] | [Samples][python-di-samples]
Model			v3.1
Request URL prefix			https://{your-form-recognizer-endpoint}/formrecognizer
General document			/documentModels/prebuilt-document:analyze
Layout			/documentModels/prebuilt-layout:analyze
Custom			/documentModels/{modelId}:analyze
Invoice			/documentModels/prebuilt-invoice:analyze
Receipt			/documentModels/prebuilt-receipt:analyze
ID document			/documentModels/prebuilt-idDocument:analyze
Business card			/documentModels/prebuilt-businessCard:analyze
W-2			/documentModels/prebuilt-tax.us.w2:analyze
Health insurance card			/documentModels/prebuilt-healthInsuranceCard.us:analyze
Contract			/documentModels/prebuilt-contract:analyze


"""


from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

# Your provided key and endpoint
key = "daea17b7fe35431d9e048c854e1f3af1"
endpoint = "https://eastus.api.cognitive.microsoft.com/"

# The URL of the document you want to analyze
docUrl = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"

# Initialize the Document Intelligence Client
document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

path_to_sample_documents='image snapshot of page.jpg'
path_to_sample_documents='aac18e37-dc9e-4343-9c73-4cebbc08c043_page_162.pdf'
with open(path_to_sample_documents, "rb") as f:
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", analyze_request=f, locale="en-US", content_type="application/octet-stream"
    )

# Wait for the analysis to complete and extract the result
result = poller.result()

# Process and print the result line by line
for page in result.pages:
    print(f"Page Number: {page.page_number}\n")
    for line in page.lines:
        print(line.content)
    print("\n--- End of Page ---\n")

