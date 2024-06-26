﻿import datetime
import time
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
from tqdm import tqdm #progress bar
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

username = 'pharmcon_lake'
password = '9Ca89(nd_J'
host = 'pharmcon.mysql.tools'
port = '3306'
database = 'pharmcon_lake'

start_time = time.time()
page = requests.get('https://www.wassertemperatur.org/tegernsee/')
soup = BeautifulSoup(page.text, features="lxml")

#regexp pattern to find needed Tempreature (first find will do)
pattern = r'<span[^>]*>(?:<span[^>]*>)?(?P<temperature>\d+)\s*°C<\/span>(?:<\/span>)?'

#find all links on the initial page
links = soup.find_all("a") # Find all elements with the tag <a>
SeeLinks = []

for link in links:
    if "Wassertemperatur" in str(link.string) and str(link.string)[-3:].upper() == 'SEE':
        #print("Link:", link.get("href"), "Text:", link.string)
        SeeLinks.append([link.get("href"), link.string.replace('Wassertemperatur ' , '')])

#print('\n')
#print(SeeLinks)
print("Total number of Lake-links is:" , len(SeeLinks))

for i in tqdm(range(0,len(SeeLinks)-1)):
    link = SeeLinks[i][0]  # link to the page of the specific lake
    page = requests.get(link)
    soup = BeautifulSoup(page.text, features="lxml")
    spans = soup.find_all('span')
    s = 0
    for span in spans:
        match = re.search(pattern, str(span))
        if match and s == 0:
            temperature = match.group('temperature')
            SeeLinks[i].append(temperature)
            s += 1

#print(SeeLinks) # List of Lists

print(f'Checking all site Pages takes: {round(time.time()-start_time, 2)} sec')

# Using PyMySQL as the MySQL driver
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')

# Test the connection
try:
    connection = engine.connect()
    print("Connection successful!")
    connection.close()
except Exception as e:
    print(f"An error occurred: {e}")

# Define metadata
metadata = MetaData()

# Define the table
table = Table(
    'bavarianlakes', metadata,
    Column('link', String),
    Column('lake', String),
    Column('temp', Integer)
)

# Given list of lists
list_of_lists = SeeLinks

# problem is not every sublist contains a tempreature.
print(f'LEn of List of lists is {len(list_of_lists)}')

# Convert list of lists to list of dictionaries
list_of_dicts = [{'link': sublist[0], 'lake': sublist[1], 'temp': int(sublist[2])} for sublist in list_of_lists if len(sublist)==3]
print(f'LEn of List of Dics is {len(list_of_dicts)}')

# Your list of dictionaries
data = list_of_dicts

# Convert each dictionary into a list of values
values_list = [{'link': d['link'], 'lake': d['lake'], 'temp': d['temp']} for d in data]

#print('Value list to insert:')
#print(values_list)

timesqlstart= time.time()

# Create the SQL insert statement
stmt = table.insert().values(values_list)

# Execute the statement
if len(list_of_dicts) != 0:
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
    conn.close()

time_part2 = round(time.time()-timesqlstart, 2)   # Writing to the DB time in SEC
time_part3 = round(time.time()-start_time, 2)   # Total Script time
print(f'Writing to the MySQL db takes: {round((time_part2), 2)} sec')
print(f'Total script runtime is : {round((time_part3), 2)} sec')
