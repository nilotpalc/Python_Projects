# %%
# access the sample.db sqlite3 database
import sqlite3
# conn = sqlite3.connect(r'C:\Users\Nilotpal.Choudhury\OneDrive - Shell\Github Repos\Codespace-ominous-parakeet\data\sample.db')
conn = sqlite3.connect('/workspaces/codespaces-jupyter/data/datasets.db')

# %%
# import dataset from kaggle given the API key
#import requests
import os

# Replace 'username' and 'api_key' with your own Kaggle username and API key
username = 'USERNAME'
api_key = 'my_api_key'

# Set the Kaggle API credentials
os.environ['KAGGLE_USERNAME'] = username
os.environ['KAGGLE_KEY'] = api_key

# Download the dataset using the Kaggle API
!kaggle competitions download -c playground-series-s3e20

"""
# extract all the csv files from the zip archive and save them as individual dataframe
# save all the dataframes in a dictionary with the name of the csv file as the key
"""
from zipfile import ZipFile
zf = ZipFile('playground-series-s3e20.zip')
dfs = {}
for text_file in zf.infolist():
    if text_file.filename.endswith('.csv'):
        dfs[text_file.filename] = pd.read_csv(zf.open(text_file.filename, 'r'),encoding_errors='ignore')

# %%
# access the file to upload into sample.db database
"""
! Set of instructions to load CSV files into Pandas DataFrame
"""
import pandas as pd
df = pd.read_csv('data/playground-series-s3e20/test.csv')
df1 = pd.read_csv('data/playground-series-s3e20/train.csv')

# %%
# concatenate the two dataframes df and df1
"""
! Set of instructions to concatenate two Pandas DataFrames if required
"""
# df = pd.concat([df, df1], axis=0)
# %%
df.to_sql('CO2EmissionsRwandaTEST', conn, if_exists='replace', index=False)

# %%
# test the table creation in sample.db database
tblquery = 'SELECT * FROM CO2EmissionsRwandaTRAIN'
testtable = pd.read_sql(tblquery, conn)
testtable.head()
# %%
# delete table from sample.db database
# conn.execute('DROP TABLE CO2EmissionsRwanda')
# %%
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)

# %%
tables
# %%
# Close the sqlite sample.db connection
conn.close()
# %%
