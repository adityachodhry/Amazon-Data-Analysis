import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from pymongo import MongoClient

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Amazon"]  
collection = db["ProductCollection"]  

product_value = "motorola phone 5g"
page_count = 1
base_url = "https://www.amazon.in/s?k=motorola%20phone%205g&page="

while True:
    url = f"{base_url}{page_count}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} for page {page_count}. Stopping.")
        break

    soup = BeautifulSoup(response.text, "lxml")
    products = soup.find_all("div", {"data-component-type": "s-search-result"})

    if not products:
        print(f"No products found on page {page_count}. Stopping.")
        break

    data_list = []  # Temporary storage for batch insertion

    for product in products:
        try:
            name_element = (
                product.find("span", class_="a-size-medium a-color-base a-text-normal")
                or product.find("span", class_="a-text-normal")
                or product.find("h2", class_="a-size-mini a-spacing-none a-color-base s-line-clamp-2")
                or product.find("h2")
            )
            phone_name = name_element.get_text(strip=True) if name_element else "N/A"

            rating_element = product.find("span", class_="a-icon-alt")
            rating = float(re.search(r"(\d+\.\d+)", rating_element.get_text()).group(1)) if rating_element else None

            purchases_element = product.find("span", class_="a-size-base s-underline-text")
            bought_count = purchases_element.get_text(strip=True) if purchases_element else "N/A"

            price_offscreen = product.find("span", class_="a-price a-text-price")
            price_whole = product.find("span", class_="a-price-whole")

            original_price = float(price_offscreen.find("span", class_="a-offscreen").text.replace("₹", "").replace(",", "")) if price_offscreen else None
            discounted_price = float(price_whole.text.replace(",", "")) if price_whole else None

            discount_element = product.find("span", string=re.compile(r"\(\d+% off\)"))
            discount_percentage = float(re.search(r"(\d+)%", discount_element.text).group(1)) if discount_element else None

            free_delivery_span = product.find("span", class_="a-color-base")
            free_delivery = free_delivery_span.get_text(strip=True) if free_delivery_span else "N/A"
            is_free_delivery = True if free_delivery == "FREE delivery" else False

            delivery_span = product.find("span", class_="a-color-base a-text-bold")
            if delivery_span:
                delivery_date_text = delivery_span.get_text(strip=True)
                delivery_date_match = re.search(r"(\d{1,2})\s([A-Za-z]+)", delivery_date_text)
                if delivery_date_match:
                    day, month_str = delivery_date_match.groups()
                    current_year = datetime.now().year
                    month_number = datetime.strptime(month_str[:3], "%b").month
                    delivery_date = f"{int(day):02d}-{month_number:02d}-{current_year}"
                else:
                    delivery_date = "Unknown"
            else:
                delivery_date = "Unknown"

            data_list.append({
                "productName": phone_name,
                "rating": rating,
                "reviews": bought_count,
                "discountedPrice": discounted_price,
                "originalPrice": original_price,
                "discountPercentage": f"{discount_percentage}%" if discount_percentage else "N/A",
                "freeDelivery": is_free_delivery,
                "deliveryDate": delivery_date
            })

        except Exception as e:
            print(f"Error extracting product: {e}")

    # Insert data into MongoDB
    if data_list:
        collection.insert_many(data_list)
        print(f"Extracted {len(data_list)} products from page {page_count} and saved to MongoDB.")

    # Increment page count for the next page
    page_count += 1