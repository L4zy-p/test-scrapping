import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import pandas as pd

def get_restaurant_name(soup):
    try:
        restaurant_header = soup.find("div", class_="restaurant-details__heading")
        restaurant_name_tag = restaurant_header.find("h2")
        restaurant_name = restaurant_name_tag.text.strip()
    except AttributeError:
        restaurant_name = ""
    return restaurant_name

def get_resturent_country(soup):
    try:
        restaurant_breadcrumb = soup.find("ol", class_="breadcrumb pt-0")
        restaurant_contry = restaurant_breadcrumb.find_all("li")[1].get_text()
    except AttributeError:
        restaurant_contry = ""
    return restaurant_contry

def get_resturent_province(soup):
    try:
        restaurant_breadcrumb = soup.find("ol", class_="breadcrumb pt-0")
        resturent_province = restaurant_breadcrumb.find_all("li")[2].get_text().replace(" Region", "")
    except AttributeError:
        resturent_province = ""
    return resturent_province

def get_restaurant_type(soup):
    try:
        restaurant_price_tag = soup.find("li", class_="restaurant-details__heading-price")
        restaurant_span_tag = restaurant_price_tag.find("span")
        restaurant_type = restaurant_span_tag.text.replace(" ", "").split("·")[-1]
    except AttributeError:
        restaurant_type = ""
    return ''.join(restaurant_type.split())

if __name__ == "__main__":
    # Headers for request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
    }

    # Selecting main page
    main_page_url = "https://guide.michelin.com/th/en/selection/thailand/restaurants"
    main_page = requests.get(main_page_url, headers=HEADERS)

    soup = BeautifulSoup(main_page.content, "html.parser")

    # Get last page from pagination 
    last_page = int(soup.find_all("a", class_="btn btn-outline-secondary btn-sm")[-2].get_text())
    print(f"waiting load {last_page} page")

    
    link_restaurants = []
    
    # loop from page count
    for i in range(1,last_page + 1):
        page_url = f"https://guide.michelin.com/th/en/selection/thailand/restaurants/page/{i}"
        page = requests.get(page_url, headers=HEADERS)
        
        page_soup =  BeautifulSoup(main_page.content, "html.parser")

        # Get link from restaurant card list
        restaurants_card = page_soup.find_all("div", class_="card__menu")

        # loop card list
        for card in restaurants_card:
            # find link from tag and append to link restaurents
            a_tag = card.find("a")
            link_text = "https://guide.michelin.com" + a_tag["href"]
            link_restaurants.append(link_text)
    
    # Dictionary schema
    result: Dict[str, List[str]] = {
        "Name": [],
        "Restaurant_Type": [],
        "Country": [],
        "Province": [],
        "Link": []
    }

    # Loop detail each link
    for link in link_restaurants:
        restaurant_page = requests.get(link, headers=HEADERS)
        print("status", restaurant_page.status_code, link)
        restaurant_soup = BeautifulSoup(restaurant_page.content, "html.parser")

        result["Name"].append(get_restaurant_name(restaurant_soup))
        result["Restaurant_Type"].append(get_restaurant_type(restaurant_soup))
        result["Country"].append(get_resturent_country(restaurant_soup))
        result["Province"].append(get_resturent_province(restaurant_soup))
        result["Link"].append(link)

   # Creating pandas dataframe
    dataset_restaurants = pd.DataFrame.from_dict(result)

    # Exporting dataset as .csv file
    dataset_restaurants.to_csv("michelin_thailand_restaurants.csv", index=False)

   
