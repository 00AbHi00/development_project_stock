import os
# Lambda function for removing csv from a particular stock
removeCsv= lambda x: x.replace('.csv','')

# Listing all files in the directory
all_files=os.listdir(os.getcwd()+'/company-wise')
all_files=[removeCsv(x) for x in all_files]

print(len(all_files))

# Each stock has: published_date,open,high,low,close,per_change,traded_quantity,traded_amount,status
