"""
Test script for PDF document upload API using existing PDF file
"""

import requests
import os

def test_pdf_upload():
    """Test PDF document upload"""
    url = "http://localhost:8000/api/upload/document"
    
    # Use the existing PDF file
    pdf_file_path = "uploads/AI-Powered Document Q&A & Knowledge Assistant.pdf"
    
    if not os.path.exists(pdf_file_path):
        print(f"ERROR: PDF file not found at {pdf_file_path}")
        return False
    
    try:
        with open(pdf_file_path, "rb") as f:
            files = {"file": (os.path.basename(pdf_file_path), f, "application/pdf")}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_pdf_upload():
        print("SUCCESS: PDF upload test passed")
    else:
        print("FAILED: PDF upload test failed")