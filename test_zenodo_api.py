import os
import requests
from dotenv import load_dotenv

def test_api_key_access():
    """
    Tests if the Zenodo API key provided in .env allows access.
    Makes a request to list depositions, which requires authentication.
    """
    load_dotenv()
    access_token = os.getenv("ZENODO_TOKEN")

    if not access_token or access_token == "YOUR_API_KEY_HERE":
        print("Error: ZENODO_API_KEY not found or not set in .env file.")
        print("Please create a .env file and add your Zenodo API key as ZENODO_API_KEY=YOUR_KEY")
        return

    # Using sandbox URL for testing by default
    # Change to "https://zenodo.org/api/deposit/depositions" for production
    api_url = "https://sandbox.zenodo.org/api/deposit/depositions"

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Alternative: pass as a parameter
    # params = {'access_token': access_token}
    # response = requests.get(api_url, params=params)

    print(f"Attempting to connect to: {api_url}")

    try:
        response = requests.get(api_url, headers=headers, timeout=10) # Added timeout

        if response.status_code == 200:
            print(f"Successfully accessed Zenodo API (Status Code: {response.status_code}). Your API key is working.")
            print("Response snippet (first 100 chars):")
            print(response.text[:100] + "...")
        elif response.status_code == 401:
            print(f"Authentication failed (Status Code: {response.status_code}).")
            print("Please check your ZENODO_API_KEY in the .env file.")
            print("Response from server:")
            print(response.json())
        elif response.status_code == 403:
            print(f"Forbidden (Status Code: {response.status_code}).")
            print("Your API key may not have the required permissions (scopes) for this action.")
            print("Ensure your token has at least 'deposit:write' and 'deposit:actions' scopes for uploading.")
            print("Response from server:")
            print(response.json())
        else:
            print(f"An error occurred (Status Code: {response.status_code}).")
            print("Response from server:")
            try:
                print(response.json())
            except requests.exceptions.JSONDecodeError:
                print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")

if __name__ == "__main__":
    test_api_key_access()
