import os
import json

# Folder containing all your JSON files
dir_path = 'C:\CSIT\Abhi Semester 7\project\\0 Program\\news_scraper\economic'

# Output combined file
output_file = os.path.join(dir_path, '4_combined_news.json')

combined_data = {}

file_num=20
while (file_num<3080):
    filename=f'file{file_num}.json'
    filepath = os.path.join(dir_path, filename)
    
    file_num+=20
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # Prefix keys with 'newsid' and add to combined_data
            for key, value in data.items():
                combined_data[f"newsid{key}"] = value
        except json.JSONDecodeError as e:
            print(f"Skipping {filename} due to invalid JSON: {e}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Write to output file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=2)

print(f"\n Combined {len(combined_data)} entries into: {output_file}")
