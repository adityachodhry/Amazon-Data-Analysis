import requests

# URL of the Amazon page
url = "https://www.amazon.in/s?k=motorola%20phone%205g&page=3"

# Headers to mimic a real browser (helps avoid blocking)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# Send GET request
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Save the response content to an HTML file
    with open("amazon_page.html", "w", encoding="utf-8") as file:
        file.write(response.text)
    print("HTML page saved as 'amazon_page.html'")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
