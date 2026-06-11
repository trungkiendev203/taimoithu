import requests

# Define the URL with parameters
url = "https://s6.tuoitre.vn/api/diem-thi-thpt.htm?sbd=34000001&year=2026"

# Set headers dictionary
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "dnt": "1",
    "origin": "https://tuoitre.vn",
    "priority": "u=1, i",
    "referer": "https://tuoitre.vn/",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

# Send GET request with headers
response = requests.get(url, headers=headers)

# Check for successful response
if response.status_code == 200:
  # Print the response data (assuming JSON format)
  print(response.json())
else:
  # Handle error
  print(f"Error: {response.status_code}")