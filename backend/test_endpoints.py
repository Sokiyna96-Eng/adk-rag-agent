import requests
import json
import os

# Test configuration
BASE_URL = "http://localhost:8000"

def test_upload():
    """Test file upload endpoint"""
    print("Testing file upload...")
    
    # Create a test file
    test_content = """
    This is a test document about earthwork operations.
    Earthwork involves excavation, grading, and soil management.
    Common earthwork activities include:
    - Site preparation
    - Foundation excavation
    - Land grading
    - Soil compaction
    """
    
    with open("test_earthwork.txt", "w") as f:
        f.write(test_content)
    
    # Upload the file
    files = {"file": ("test_earthwork.txt", open("test_earthwork.txt", "rb"), "text/plain")}
    
    try:
        response = requests.post(f"{BASE_URL}/upload", files=files)
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Upload failed: {e}")
        return False

def test_query():
    """Test query endpoint"""
    print("\nTesting query endpoint...")
    
    query_data = {
        "query": "What are earthwork operations?",
        "corpus_name": "earthwork"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/query", json=query_data)
        print(f"Query response status: {response.status_code}")
        print(f"Query response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Query failed: {e}")
        return False

def test_corpus_status():
    """Test corpus status endpoint"""
    print("\nTesting corpus status...")
    
    try:
        response = requests.get(f"{BASE_URL}/corpus/earthwork")
        print(f"Corpus status response status: {response.status_code}")
        print(f"Corpus status response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Corpus status failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ADK RAG Agent endpoints...")
    print("=" * 50)
    
    # Test upload
    upload_success = test_upload()
    
    # Test corpus status
    corpus_success = test_corpus_status()
    
    # Test query
    query_success = test_query()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Upload: {'✅ PASS' if upload_success else '❌ FAIL'}")
    print(f"Corpus Status: {'✅ PASS' if corpus_success else '❌ FAIL'}")
    print(f"Query: {'✅ PASS' if query_success else '❌ FAIL'}")
    
    # Cleanup
    if os.path.exists("test_earthwork.txt"):
        os.remove("test_earthwork.txt") 