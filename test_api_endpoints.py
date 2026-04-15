import requests
import uuid

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
TEST_USER_EMAIL = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
TEST_USER_PASSWORD = "testpassword123"

def test_user_signup():
    url = f"{BASE_URL}/users/signup"
    payload = {
        "name": "Test User",
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    print(f"Testing signup with email: {TEST_USER_EMAIL}")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201 or response.status_code == 200:
            print("Signup successful!")
            return response.json()
        else:
            print(f"Signup failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def test_user_login():
    url = f"{BASE_URL}/users/login"
    # FastAPI OAuth2 typically expects data in form field format or JSON depending on implementation.
    # Looking at common FastAPI patterns, it might be form data.
    # Let's try JSON first as it's common in this codebase based on previous context.
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    print(f"Testing login with email: {TEST_USER_EMAIL}")
    try:
        # Some FastAPI login endpoints expect x-www-form-urlencoded
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Login successful!")
            return response.json()
        else:
            # Try JSON if form data fails
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Login successful (JSON)!")
                return response.json()
            
            print(f"Login failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    signup_data = test_user_signup()
    if signup_data:
        login_data = test_user_login()
        if login_data:
            print("Backend test completed successfully!")
