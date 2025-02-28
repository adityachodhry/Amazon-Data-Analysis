import requests

url = "https://www.amazon.in/s?k=motorola%20phone%205g&page=1"

response = requests.get(url)

with open("amazon_results.html", "w", encoding="utf-8") as file:
    file.write(response.text)
