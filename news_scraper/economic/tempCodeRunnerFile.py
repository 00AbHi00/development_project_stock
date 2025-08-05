with open(fileName,mode='r', encoding='utf-8') as f:
    raw_data=json.load(f)
    
print(raw_data)