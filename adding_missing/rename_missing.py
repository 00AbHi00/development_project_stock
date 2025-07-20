# First job adding codes by generating so that no data is found missing
#completed


# Since so many datas are still missing code Api Finance (maybe the stock symbol changed name or value)
#So making them as xAPI, 

#Second job determining the category
#commercial bank= contains bank no development or bikas
#hydropower= power or hydropower
#life insurance = life insurence
#development banks = bikas bank, development bank
#finance= contains finance
#microfinance- microfinance, lagubitta
# promoter share= "promoter" share(skip everything banks can have promoter share, but if promoter seprate it as promoter and move on)
# debenture = same
#mutual fund= fund 
# others => undetermined 
import pandas as pd
import re
df=pd.read_csv('clean_outputs/error.csv')
listofCompany = []

def classify_company(name):
    name_lower = name.lower()

    # Check promoter first
    if 'promoter' in name_lower or 'promotor' in name_lower:
        return 'Promoter Share'

    if 'bond' in name_lower:
        return('Government Bond')

    # Check debenture next
    if 'debenture' in name_lower:
        return 'Debenture'

    # Commercial Bank: has 'bank' but NOT 'development' or 'bikas'
    if 'bank' in name_lower and 'development' not in name_lower and 'banking' not in name_lower and  'bikas' not in name_lower:
        return 'Commercial Bank'

    # Hydropower: 'power' or 'hydropower'
    if 'power' in name_lower or 'hydropower' in name_lower:
        return 'Hydropower'

    # Life Insurance
    if 'life insurance' in name_lower:
        return 'Life insurance'

    #For non life since containing life is out of the eqation
    if 'insurance' in name_lower:
        return 'Non life insurance'
    # Development Bank: 'bikas' or 'development bank'
    if 'bikas' in name_lower or'vikas' in name_lower or 'development bank' in name_lower:
        return 'Development Bank'

    # Microfinance: contains 'microfinance' or 'laghubitta' Microfinance should be checked before finance
    if 'microfinance' in name_lower or 'laghubitta' in name_lower:
        return 'Microfinance'
    
    # Finance Company: contains 'finance'
    if 'finance' in name_lower:
        return 'Finance Company'

    # Mutual Fund: contains 'fund'
    if 'fund' in name_lower:
        return 'Mutual Fund'

    # Else undetermined
    return 'Undetermined'




# Get all companies with missing company.code
x = df.loc[df['company.code'].isna()]

for index, row in x.iterrows():
    # Generate base abbreviation
    abbr = 'x' + ''.join([word[0].upper() for word in row['company.name'].split()])
    abbr = re.sub(r'[&()]', '', abbr)
    # Check if already exists
    while abbr in listofCompany:
        abbr += 'xx'  # Append 'xx' repeatedly until it's unique

    df.at[index, 'company.code'] = abbr
    # listofCompany.append(abbr)
    # print(abbr)

df['company.cat'] = df['company.name'].apply(classify_company)
print(df[['company.name', 'company.cat']])
df.to_csv('adding_missing/clean1.csv')




# Convert to Series and show final list
# df2 = pd.Series(listofCompany)
# print(df2[df2.duplicated()])  # is empty
# print(len(x))
# print(len(df2)) Equal lengths all data has been sorted
