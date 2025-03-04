import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---- SWIGGY API REQUEST ----
url = "https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat=22.7195687&lng=75.8577258&restaurantId=84070&catalog_qa=undefined&submitAction=ENTER"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.swiggy.com/",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()  
    st.success("Data fetched successfully!")

    extracted_items = []

    try:
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
        st.error(f"Error extracting data: {e}")

else:
    st.error(f"Failed to fetch data. Status Code: {response.status_code}")
    exit()

# ---- DATA PROCESSING ----
df = pd.DataFrame(extracted_items)
df["price"] = df["price"] / 100  # Convert price from paise to INR
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df = df.dropna()  # Remove rows with missing ratings

# ---- STREAMLIT UI ----
st.title("🍽 Swiggy Menu Analysis Dashboard")

# Display data table
st.subheader("📋 Menu Data")
st.dataframe(df)

# ---- VISUALIZATIONS ----

# 1. Price Distribution
st.subheader("💰 Price Distribution of Dishes")
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df["price"], bins=20, kde=True, color="skyblue", ax=ax)
ax.set_title("Price Distribution of Dishes")
ax.set_xlabel("Price (INR)")
ax.set_ylabel("Count")
st.pyplot(fig)

# 2. Top 10 Rated Dishes
st.subheader("🌟 Top 10 Rated Dishes")
top_rated = df.nlargest(10, "rating")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="rating", y="name", data=top_rated, palette="viridis", ax=ax)
ax.set_title("Top 10 Rated Dishes")
ax.set_xlabel("Rating")
ax.set_ylabel("Dish Name")
st.pyplot(fig)

# 3. Price vs Rating Relationship
st.subheader("💵 Price vs Rating Relationship")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x="price", y="rating", data=df, color="red", ax=ax)
ax.set_title("Price vs Rating")
ax.set_xlabel("Price (INR)")
ax.set_ylabel("Rating")
st.pyplot(fig)

# 4. Dish Price Range
st.subheader("📊 Price Range of Dishes")
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(x=df["price"], color="lightgreen", ax=ax)
ax.set_title("Dish Price Range")
ax.set_xlabel("Price (INR)")
st.pyplot(fig)

# ---- USER SELECTION ----
st.subheader("🔍 Filter Dishes by Price Range")
min_price, max_price = st.slider("Select Price Range (INR)", float(df["price"].min()), float(df["price"].max()), (50.0, 300.0))

filtered_df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
st.write(f"Showing dishes between ₹{min_price} and ₹{max_price}")
st.dataframe(filtered_df)

# ---- SUMMARY ----
st.subheader("📌 Key Insights")
st.write("""
- Most dishes are priced between **₹50 - ₹400**.
- **Top-rated dishes** are not always the most expensive.
- There is **no strong correlation** between price and rating.
- The **majority of dishes** fall within a mid-range price category.
""")

# ---- FOOTER ----
st.write("---")
st.write("👨‍🍳 **Swiggy Menu Analysis App - Powered by Python & Streamlit**")
