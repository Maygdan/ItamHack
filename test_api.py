import requests
import json

# Test the login API
url = "http://localhost:8000/api/login_with_code/"
data = {"code": "22N3M28G"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, data=json.dumps(data), headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
