import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import fitz

import os
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.files.storage import FileSystemStorage
import fitz

def extract_pdf_text(pdf_path):
    # Open the PDF file
    document = fitz.open(pdf_path)

    # Loop through each page in the PDF
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        
        # Extract text from the page
        page_text = page.get_text("text")
        text += page_text

    # Split the extracted text into an array based on newlines
    text_array = text.split('\n')
    return text_array

def process_pdf_array(pdf_array):
    # Find the index where "Net Worth of Client :" is located
    start_index = None
    for i, line in enumerate(pdf_array):
        if line.strip() == "Net Worth of Client :":
            start_index = i
            break
    
    # If "Net Worth of Client :" is found, slice the array to get the part after it
    if start_index is not None:
        pdf_array = pdf_array[start_index + 1:]
    
    # return pdf_array
    # Now extract consecutive stock names
    stock_names = []
    for line in pdf_array:
        # Assuming stock names are strings with all uppercase letters and not numbers
        if line.isupper() and len(line.split()) == 1:
            stock_names.append(line.strip())

    rows = len(stock_names)
    net_quantity = pdf_array[rows:rows*2]

    start_index = None
    for i, line in enumerate(pdf_array):
        if line.strip() == "Market Value":
            start_index = i
            break
    
    if start_index is not None:
        pdf_array = pdf_array[start_index + 1:]

    avg_rate = pdf_array[:rows]

    data = []
    for i in range(0, rows):
        data.append({"stock_symbol":stock_names[i], "shares": net_quantity[i], "price_per_share": avg_rate[i]})

    return data

class PdfExtractView(APIView):
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        fs = FileSystemStorage()
        pdf_path = os.path.join(fs.location, uploaded_file.name)
        with open(pdf_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        pdf_text_array = extract_pdf_text(pdf_path)

        res = process_pdf_array(pdf_text_array)

        return Response(res, status=status.HTTP_200_OK)
