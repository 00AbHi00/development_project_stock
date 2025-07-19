import pandas as pd

# Load both CSVs
shares_df = pd.read_csv("clean_outputs/output2_unique_shares.csv")
ref_df = pd.read_csv("clean_outputs/output3_uniquedataset.csv")

# Merge using company.name
merged_df = pd.merge(shares_df, ref_df, on="company.name", how="left", suffixes=('', '_ref'))

# Fill missing company.code and company.cat from reference dataset
merged_df['company.code'] = merged_df['company.code'].fillna(merged_df['company.code_ref'])
merged_df['company.cat'] = merged_df['company.cat'].fillna(merged_df['company.cat_ref'])

# Drop the reference columns
merged_df.drop(columns=['company.code_ref', 'company.cat_ref'], inplace=True)

missing_cats = merged_df[merged_df['company.cat'].isna()].drop_duplicates(subset=["company.name"])
missing_cats=missing_cats[['company.name', 'company.code']]

missing_cats.to_csv("clean_outputs/error.csv")
# merged_df.to_csv("clean_outputs/output4_fullFinal.csv")


