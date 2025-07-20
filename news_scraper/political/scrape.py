# This scraper is responsible for scraping
#  {
#     "newsid[page1]_[count]": {
#       "image": "https://english.onlinekhabar.com/wp-content/uploads/2025/07/Sunchadi-Byabasayi-Aandolan-9.jpg",
#       "title": "Gold and silver traders stage protest against luxury tax and VAT",
#       "link": "https://english.onlinekhabar.com/gold-and-silver-traders-stage-protest-against-luxury-tax-and-vat.html"
#  }, 

#processing time: Around 10-15 minutes 
#Taking only the title of the political news

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re

def parse_relative_time(text):
    # Example: "2 weeks ago"
    match = re.match(r"(\d+)\s+(day|week|month|year)s?\s+ago", text)
    if not match:
        return None

    quantity = int(match.group(1))
    unit = match.group(2)

    # Get today's date
    now = datetime.now()

    # Map units to timedelta
    if unit == "day":
        delta = timedelta(days=quantity)
    elif unit == "week":
        delta = timedelta(weeks=quantity)
    elif unit == "month":
        # Approximate a month as 30 days
        delta = timedelta(days=30 * quantity)
    elif unit == "year":
        # Approximate a year as 365 days
        delta = timedelta(days=365 * quantity)
    else:
        return None

    return now - delta



#Since there are 241 pages in onlinekhabar
pageId=1
while pageId<241:
    url = f"https://english.onlinekhabar.com/category/political/page/{pageId}"

    # Send GET request
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    relevant_html= soup.find_all('div', class_='ok-details-content-left')
    extracted_html= []
    dateText=[]
      
    for news in relevant_html:
        # Get the date from the block
        date_str = None
        span = news.find_all('span', class_='ok-post-hours')
        
        for spn in span:
            relative=spn.find('span').get_text(strip=True)
            date_result = parse_relative_time(relative)
            if date_result:
                date_str = date_result.strftime("%Y-%m-%d")
            else:
                date_str=None
            dateText.append(date_str)                    
        a_tags = news.find_all('a')
        for a_tag in a_tags:
            if 'page-numbers' in a_tag.get('class', []):
                    continue
            extracted_html.append(a_tag)
            
    
    # Build JSON
    news_data = {}
    news_id = 1
    temp_entry = {}

    

    print(len(dateText),len(extracted_html))
    # Keep only even-indexed items (0, 2, 4, ...) — i.e., remove odd ones
    extracted_html = [x for i, x in enumerate(extracted_html) if i % 2 != 0]
    print(len(dateText),len(extracted_html))

    
    for index, tag in enumerate(extracted_html):
        href = tag.get('href')
        img_tag = tag.find('img')
        text = tag.get_text(strip=True)
        date=dateText[index]       

        if img_tag:
            # It's an image link
            img_src = img_tag.get('src')
            temp_entry['image'] = img_src
        elif text:
            # It's a title/text link
            temp_entry['title'] = text
            temp_entry['link'] = href
            temp_entry['date'] = date  

            # Save the full entry once both image and title/link are collected
            news_data[f'newsid{pageId}_{news_id}'] = temp_entry
            news_id += 1
            temp_entry = {}
    
    print(json.dumps(news_data,indent=2))        
    pageId+=1
    file_path = 'news_scraper/political/newsarticle_v1.json'
    # Load existing data or start with empty list
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new data 
    data.append(news_data)  # or data.extend(news_data) if news_data is a list

    # Write back full JSON list
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(pageId)
