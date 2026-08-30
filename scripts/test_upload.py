"""
Test script for document upload API
"""

import requests
import os

def test_upload():
    """Test document upload"""
    url = "http://localhost:8000/api/upload/document"
    
    # Create a test file
    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test document for upload testing.")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path, f, "text/plain")}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    if test_upload():
        print("SUCCESS: File upload test passed")
    else:
        print("FAILED: File upload test failed")