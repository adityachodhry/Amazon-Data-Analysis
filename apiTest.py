import requests
import json

url = "https://www.swiggy.com/dapi/menu/pl?page-type=REGULAR_MENU&complete-menu=true&lat=22.7195687&lng=75.8577258&restaurantId=84070&catalog_qa=undefined&submitAction=ENTER"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.swiggy.com/",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()  
    print("Data fetched successfully!")

    extracted_items = []

    try:
        # data.cards[4].groupedCard.cardGroupMap.REGULAR.cards[2].card.card.itemCards[1].card.info.name
        menu_sections = (
            data.get("data", {}).get("cards", [])[4].get("groupedCard", {}).get("cardGroupMap", {}).get("REGULAR", {}).get("cards", [])
        )

        for section in menu_sections:
            item_cards = section.get("card", {}).get("card", {}).get("itemCards", [])

            for item in item_cards:
                dish_info = item.get("card", {}).get("info", {})

                if "name" in dish_info and "price" in dish_info:
                    item_data = {
                        "name": dish_info.get("name"),
                        "price": dish_info.get("price"),
                        "rating": dish_info.get("ratings", {}).get("aggregatedRating", {}).get("rating"),
                        "ratingCountV2": dish_info.get("ratings", {}).get("aggregatedRating", {}).get("ratingCountV2"),
                    }
                    extracted_items.append(item_data)

    except Exception as e:
        print(f"Error extracting data: {e}")

    with open("extracted_swiggy_menu.json", "w", encoding="utf-8") as outfile:
        json.dump(extracted_items, outfile, indent=4, ensure_ascii=False)

    print("Extracted data saved to extracted_swiggy_menu.json")

else:
    print(f"Failed to fetch data. Status Code: {response.status_code}")