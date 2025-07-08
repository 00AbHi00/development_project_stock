# This scraper is responsible for scraping
#  {
#     "newsid[page1]_[count]": {
#       "image": "https://english.onlinekhabar.com/wp-content/uploads/2025/07/Sunchadi-Byabasayi-Aandolan-9.jpg",
#       "title": "Gold and silver traders stage protest against luxury tax and VAT",
#       "link": "https://english.onlinekhabar.com/gold-and-silver-traders-stage-protest-against-luxury-tax-and-vat.html"
#  }, 
import requests
from bs4 import BeautifulSoup
import json
import os



pageId=1
# Define target URL
while pageId<164:
    url = f"https://english.onlinekhabar.com/category/economy/page/{pageId}"

    # Send GET request
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    relevant_html= soup.find_all('div', class_='ok-details-content-left')
    extracted_html= []
    for news in relevant_html:
        extracted_html.extend(news.find_all('a'))

    # Build JSON
    news_data = {}
    news_id = 1
    temp_entry = {}

    for tag in extracted_html:
        href = tag.get('href')
        img_tag = tag.find('img')
        text = tag.get_text(strip=True)
        
        # Skip pagination links: titles like digits or "Next", "Prev"
        if text.isdigit() or text.lower() in {"next", "prev"}:
            # Also skip if href is a pagination URL
            if href and "/category/economy/page/" in href:
                continue
        
        if img_tag:
            # It's an image link
            img_src = img_tag.get('src')
            temp_entry['image'] = img_src
        elif text:
            # It's a title/text link
            temp_entry['title'] = text
            temp_entry['link'] = href

            # Once we have both image and title+link, save entry
            news_data[f'newsid{pageId}_{news_id}'] = temp_entry
            news_id += 1
            temp_entry = {}

    file_path = 'news_scraper/newsarticle_v1.json'

    # Load existing data or start with empty list
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new data (assuming news_data is a dict or list)
    data.append(news_data)  # or data.extend(news_data) if news_data is a list

    # Write back full JSON list
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    pageId+=1
    print(pageId)
