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

# Calculate dynamic price range
min_price = df["price"].min()
max_price = df["price"].max()
median_price = df["price"].median()

# Find most frequent price range using percentiles
low_percentile = df["price"].quantile(0.25)
high_percentile = df["price"].quantile(0.75)

fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df["price"], bins=20, kde=True, color="skyblue", ax=ax)
ax.set_title("Price Distribution of Dishes")
ax.set_xlabel("Price (INR)")
ax.set_ylabel("Count")
st.pyplot(fig)

st.write(f"📊 **Insight**: The dishes are priced between **₹{min_price:.2f} and ₹{max_price:.2f}**, with a peak around **₹{median_price:.2f}**. Most dishes are priced in the range of **₹{low_percentile:.2f} - ₹{high_percentile:.2f}**, indicating a mid-range pricing trend.")

# 2. Top 10 Rated Dishes
st.subheader("🌟 Top 10 Rated Dishes")
top_rated = df.nlargest(10, "rating")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="rating", y="name", data=top_rated, palette="viridis", ax=ax)
ax.set_title("Top 10 Rated Dishes")
ax.set_xlabel("Rating")
ax.set_ylabel("Dish Name")
st.pyplot(fig)
st.write("🌟 **Observation**: The highest-rated dishes are not necessarily the most expensive ones, indicating customer preference based on taste rather than price.")

# 3. Price vs Rating Relationship
st.subheader("💵 Price vs Rating Relationship")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(x="price", y="rating", data=df, color="red", ax=ax)
ax.set_title("Price vs Rating")
ax.set_xlabel("Price (INR)")
ax.set_ylabel("Rating")
st.pyplot(fig)
st.write("🔍 **Analysis**: There is no strong correlation between price and rating. Expensive dishes do not always have higher ratings.")

# 4. Dish Price Range (Box Plot)
st.subheader("📊 Price Range of Dishes")

# Calculate dynamic boxplot insights
q1 = df["price"].quantile(0.25)
q3 = df["price"].quantile(0.75)
min_price = df["price"].min()
max_price = df["price"].max()
median_price = df["price"].median()

fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(x=df["price"], color="lightgreen", ax=ax)
ax.set_title("Dish Price Range")
ax.set_xlabel("Price (INR)")
st.pyplot(fig)

st.write(f"💰 **Insight**: The price range is widely spread from **₹{min_price:.2f} to ₹{max_price:.2f}**, with most dishes priced between **₹{q1:.2f} and ₹{q3:.2f}**. The median price is **₹{median_price:.2f}**, showing that the majority of dishes fall within an affordable range.")

# ---- USER SELECTION ----
st.subheader("🔍 Filter Dishes by Price Range")
min_price, max_price = st.slider("Select Price Range (INR)", float(df["price"].min()), float(df["price"].max()), (50.0, 300.0))

filtered_df = df[(df["price"] >= min_price) & (df["price"] <= max_price)]
st.write(f"Showing dishes between ₹{min_price} and ₹{max_price}")
st.dataframe(filtered_df)

# ---- DYNAMIC KEY INSIGHTS ----
st.subheader("📌 Key Insights")

# 1. Calculate dynamic price distribution
min_price = df["price"].min()
max_price = df["price"].max()
median_price = df["price"].median()
low_percentile = df["price"].quantile(0.25)
high_percentile = df["price"].quantile(0.75)

# 2. Analyze rating vs. price correlation
correlation = df["price"].corr(df["rating"])  # Find correlation
correlation_text = "no strong correlation" if abs(correlation) < 0.3 else (
    "a slight positive correlation" if correlation > 0 else "a slight negative correlation"
)

# 3. Find most expensive and highest-rated dishes
most_expensive_dish = df.loc[df["price"].idxmax(), "name"]
highest_rated_dish = df.loc[df["rating"].idxmax(), "name"]

# 4. Generate dynamic insights
st.write(f"""
- Most dishes are priced between **₹{low_percentile:.2f} - ₹{high_percentile:.2f}**, with prices ranging from **₹{min_price:.2f} to ₹{max_price:.2f}**.
- **{highest_rated_dish}** is the highest-rated dish, but **{most_expensive_dish}** is the most expensive.
- There is **{correlation_text}** between price and rating.
- The **majority of dishes** fall within the price range of **₹{low_percentile:.2f} - ₹{high_percentile:.2f}**, indicating a mid-range price trend.
""")


# ---- FOOTER ----
st.write("---")
st.write("👨‍🍳 **Swiggy Menu Analysis App - Powered by Python & Streamlit**")
