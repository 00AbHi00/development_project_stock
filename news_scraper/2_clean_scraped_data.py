# Out put of this file is 

#  {
#     "newsid1": {
#       "image": "https://english.onlinekhabar.com/wp-content/uploads/2025/07/Sunchadi-Byabasayi-Aandolan-9.jpg",
#       "title": "Gold and silver traders stage protest against luxury tax and VAT",
#       "link": "https://english.onlinekhabar.com/gold-and-silver-traders-stage-protest-against-luxury-tax-and-vat.html"
#  }, #  {
#     "newsid2: {
#       "image": "https://english.onlinekhabar.com/wp-content/uploads/2025/07/Sunchadi-Byabasayi-Aandolan-9.jpg",
#       "title": "Gold and silver traders stage protest against luxury tax and VAT",
#       "link": "https://english.onlinekhabar.com/gold-and-silver-traders-stage-protest-against-luxury-tax-and-vat.html"
#  }
# }...

import json
# Load your existing JSON file
with open('news_scraper/newsarticle_v1.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# Flatten and clean entries
cleaned_data = {}
count = 1

for item in raw_data:
    # Each item is a dict with one key-value pair
    for key, value in item.items():
        title = value.get("title", "").strip()
        image = value.get("image")

        if title == "1" or not image:
            continue  # Skip if title is "1" or image missing

        cleaned_data[f"newsid{count}"] = value
        count += 1

# Save cleaned and serial JSON
with open('news_scraper/cleaned_json_file.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("Cleaned and renumbered JSON saved as 'cleaned_json_file.json'")
