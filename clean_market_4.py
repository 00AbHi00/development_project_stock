import pandas as pd

df=pd.read_csv("clean_outputs/output2_unique_shares.csv")
df.dropna(subset=['company.cat','company.code'],inplace=True)
df.drop_duplicates(subset=['company.name'],inplace=True)
unique_companies = df[['company.code', 'company.name','company.cat']].drop_duplicates()

x=pd.unique(unique_companies['company.name'])

x = pd.unique(unique_companies['company.name'])

all_rows=[]
for i in x:
    rows = df.loc[df['company.name'] == i, ['company.code', 'company.name', 'company.cat']].drop_duplicates()
    all_rows.extend(rows.values.tolist())

result_df = pd.DataFrame(all_rows, columns=['company.code', 'company.name', 'company.cat'])

# result_df.to_csv('clean_outputs/output3_uniquedataset.csv')
print(result_df.groupby(['company.cat']).nunique())
print(result_df.count())

