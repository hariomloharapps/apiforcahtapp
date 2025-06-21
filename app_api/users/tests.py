import requests
import json

# API endpoint
url = "https://mfqdh2s3-8000.inc1.devtunnels.ms//api/chat"

# JSON payload
payload = {
    "message": "hy",
    "history": [
        {"content": "Hello! How can I help you today?", "isUser": False},
        {"content": "hy", "isUser": True}
    ],
    "userId": "b77fa94872e545d3adb8be43e591b83f"
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Send the POST request
response = requests.post(url, headers=headers, json=payload)

# Print the response
print("URL:", url)
print("Headers:", headers)
print("Payload:", json.dumps(payload))
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
