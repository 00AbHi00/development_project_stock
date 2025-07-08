import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time

with open('news_scraper/newsarticle_v2.json', mode='r', encoding='utf-8') as file:
    raw_data = json.load(file)

start_processing = False
chunk = {}
chunk_size = 20
counter = 0
file_index = 1950

for newsid, details in raw_data.items():
    if newsid == 'newsid1955':
        start_processing = True
    if not start_processing:
        continue
    
    try:
        url = details.get('link')
        print(f"Fetching: {url}")

        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract and format date
        raw_date_tag = soup.find('span', class_='ok-post-date')
        if not raw_date_tag:
            print(f" Skipping {newsid}: No date found")
            continue
        raw_date = raw_date_tag.get_text(strip=True)
        clean_date = datetime.strptime(raw_date, "%A, %B %d, %Y").strftime("%Y-%m-%d")

        # Extract and concatenate full text
        content_div = soup.find('div', class_='post-content-wrap')
        if not content_div:
            print(f"Skipping {newsid}: No content found")
            continue
        paragraphs = content_div.find_all('p')
        full_text = ' '.join(p.get_text(strip=True) for p in paragraphs)

        # Update entry
        details['date'] = clean_date
        details['full_text'] = full_text
        chunk[newsid] = details
        counter += 1

        # Write chunk to file every 20 entries
        if counter % chunk_size == 0:
            filename = f'news_scraper/file{file_index}.json'
            with open(filename, mode='w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2, ensure_ascii=False)
            print(f" Saved {filename} with {chunk_size} entries.")
            chunk.clear()
            file_index += 20

        time.sleep(1)

    except Exception as e:
        print(f"Error processing {newsid}: {e}")
        continue

# Save any remaining entries
if chunk:
    filename = f'news_scraper/file{file_index}.json'
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=2, ensure_ascii=False)
    print(f" Saved final chunk: {filename}")

print(" All entries processed and saved in chunks.")
