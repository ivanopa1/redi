import datetime
import time
import requests
from bs4 import BeautifulSoup
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

link = "https://www.wassertemperatur.org/chiemsee/"

#regexp pattern to find needed Tempreature (first find will do)
pattern = r'<span[^>]*>(?:<span[^>]*>)?(?P<temperature>\d+)\s*°C<\/span>(?:<\/span>)?'

#find all links on the initial page
links = soup.find_all("a") # Find all elements with the tag <a>
SeeLinks = []

for link in links:
    if "Wassertemperatur" in str(link.string) and str(link.string)[-3:].upper() == 'SEE':
        #print("Link:", link.get("href"), "Text:", link.string)
        SeeLinks.append([link.get("href"), link.string.replace('Wassertemperatur ' , '')])

print('\n')
print(SeeLinks)
print("Total Lakes number is:" , len(SeeLinks))

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

print(SeeLinks)
print(f'Checking all site Pages takes: {round(time.time()-start_time, 2)} sec')
time_part1 = round(time.time()-start_time, 2) # web site part running time (in Sec_)

timesqlstart=time.time()

#  SeeLinks - LIST OF LISTS it contains folowibg data structure: link, Name, Temp
'''[['https://www.wassertemperatur.org/ammersee/', 'Ammersee', '15'],
    ['https://www.wassertemperatur.org/attersee/', 'Attersee', '14'],
    ['https://www.wassertemperatur.org/bodensee/', 'Bodensee', '16'],
'''

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
print('Value list to insert:')
print(values_list)

# Create the SQL insert statement
stmt = table.insert().values(values_list)

print(f'stmt = {stmt}')

# Execute the statement
with engine.connect() as conn:
    conn.execute(stmt)
    conn.commit()  # commit statement (very important!!!)

conn.close()

print(f'Writing to the MySQL db takes: {round(time.time()-timesqlstart, 2)} sec')
time_part2 = round(time.time()-timesqlstart, 2)   # Writing to the DB time in SEC
print(f'Total time of the script run is {str(datetime.timedelta(seconds=(time_part2+time_part1)))}')