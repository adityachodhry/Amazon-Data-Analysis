import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# API URL for fetching Swiggy restaurant menu
url = "https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat=22.7195687&lng=75.8577258&restaurantId=84070&catalog_qa=undefined&submitAction=ENTER"

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.swiggy.com/",
}

# Send GET request
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()  # Convert response to JSON
    print("Data fetched successfully!")

    extracted_items = []

    try:
        # Extract menu items from JSON
        menu_sections = (
            data.get("data", {}).get("cards", [])[4]
            .get("groupedCard", {})
            .get("cardGroupMap", {})
            .get("REGULAR", {})
            .get("cards", [])
        )

        for section in menu_sections:
            item_cards = section.get("card", {}).get("card", {}).get("itemCards", [])

            for item in item_cards:
                dish_info = item.get("card", {}).get("info", {})

                if "name" in dish_info and "price" in dish_info:
                    item_data = {
                        "name": dish_info.get("name"),
                        "price": dish_info.get("price"),  # Price in paise
                        "rating": dish_info.get("ratings", {}).get("aggregatedRating", {}).get("rating"),
                        "ratingCountV2": dish_info.get("ratings", {}).get("aggregatedRating", {}).get("ratingCountV2"),
                    }
                    extracted_items.append(item_data)

    except Exception as e:
        print(f"Error extracting data: {e}")

    # # Save extracted data to a JSON file
    # with open("extracted_swiggy_menu.json", "w", encoding="utf-8") as outfile:
    #     json.dump(extracted_items, outfile, indent=4, ensure_ascii=False)

    print("Extracted data saved to extracted_swiggy_menu.json")

else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")
    exit()

# ---- ANALYSIS ----

# Load the extracted data
with open("extracted_swiggy_menu.json", "r", encoding="utf-8") as file:
    menu_data = json.load(file)

# Convert to DataFrame
df = pd.DataFrame(menu_data)

# Convert price to INR (Swiggy gives price in paise)
df["price"] = df["price"] / 100  

# Convert rating to numeric and handle missing values
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# Drop rows with missing ratings for analysis
df = df.dropna()

## --- VISUALIZATIONS ---

# 1. Price Distribution
plt.figure(figsize=(8, 5))
sns.histplot(df["price"], bins=20, kde=True, color="skyblue")
plt.title("Price Distribution of Dishes")
plt.xlabel("Price (INR)")
plt.ylabel("Count")
plt.show()

# 2. Top 10 Rated Dishes
top_rated = df.nlargest(10, "rating")
plt.figure(figsize=(10, 5))
sns.barplot(x="rating", y="name", data=top_rated, palette="viridis")
plt.title("Top 10 Rated Dishes")
plt.xlabel("Rating")
plt.ylabel("Dish Name")
plt.show()

# 3. Price vs Rating Relationship
plt.figure(figsize=(8, 5))
sns.scatterplot(x="price", y="rating", data=df, color="red")
plt.title("Price vs Rating")
plt.xlabel("Price (INR)")
plt.ylabel("Rating")
plt.show()

# 4. Count of Dishes in Different Price Ranges
plt.figure(figsize=(10, 5))
sns.boxplot(x=df["price"], color="lightgreen")
plt.title("Dish Price Range")
plt.xlabel("Price (INR)")
plt.show()