"""
Simple test script to verify backend connection
"""
import requests

BASE_URL = "https://medgemma-service-602402744184.us-central1.run.app"

def test_health_check():
    """Test the health endpoint"""
    print("Testing health check...")
    print("Note: First request may take longer due to cold start (up to 60 seconds)...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=90)
        if response.status_code == 200:
            print("[SUCCESS] Health check passed!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"[FAILED] Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAILED] Health check failed: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    print("\nTesting chat endpoint...")
    print("Note: Chat requests may take up to 2 minutes for agent processing...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={
                'user_id': 'test_user',
                'session_id': 'test_session',
                'message': 'I have a headache and fever. What should I do?'
            },
            timeout=180
        )

        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Chat endpoint works!")
            print(f"Response: {data['response'][:200]}...")  # First 200 chars
            return True
        else:
            print(f"[FAILED] Chat failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"[FAILED] Chat failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Healthcare Assistant Backend Connection")
    print("=" * 60)

    # Run tests
    health_ok = test_health_check()

    if health_ok:
        chat_ok = test_chat()

        if chat_ok:
            print("\n" + "=" * 60)
            print("[SUCCESS] All tests passed! Backend is ready to use.")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("[WARNING] Health check passed but chat failed.")
            print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[FAILED] Backend health check failed. Please verify the service is running.")
        print("=" * 60)
