import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
import random

def get_random_book():
    #get today's date
    today = date.today().strftime('%Y-%m-%d')

    #open text file
    file_name = f'daily_uploads/{today}.txt'
    if not os.path.exists(file_name):
        print(f"error: 'file_name' does not exist")
        return None
    with open(file_name,'r') as file:
        lines = file.readlines()
    
    #pick a random line from the file
    random_line = random.choice(lines)

    #parse the line to find the book number - need to find a more robust way to do this but should work
    book_number = None
    title = None
    parts = random_line.split('\t')
    if len(parts) >= 2:
        title = parts[0].strip().rstrip("'")
        url = parts[1].strip()
        book_number = url.split('/')[-1]
    return book_number, title

def retrieve_book(book_number,title):
    #create an irregular_library folder
    if not os.path.exists('irregular_library'):
        os.makedirs('irregular_library')

    if not os.path.exists(f'irregular_library/{today}'):
        os.makedirs(f'irregular_library/{today}')

    #url to books text file
    url = f'https://www.gutenberg.org/cache/epub/{book_number}/pg{book_number}.txt'
    
    #error check book exists
    try:
        with urllib.request.urlopen(url) as response:
            response.status_code = 200
    except urllib.error.HTTPError as e:
        print(f"Error: book with number {book_number} does not exist as a text file")
        return
    
    #download books text file and add it to the irregular_libray
    response = urllib.request.urlopen(url)
    file_name = f"irregular_library/{today}/{title}.txt"
    if not os.path.exists(file_name):
        with open(file_name, 'w+', encoding='utf-8') as file:
            file.write(response.read().decode('utf-8'))
    
        print(f"{title} has been saved")


#create a folder to store the daily uploads if it doesn't exist
if not os.path.exists('daily_uploads'):
    os.mkdir('daily_uploads')

#download rss feed
url = 'https://www.gutenberg.org/cache/epub/feeds/today.rss'
urllib.request.urlretrieve(url,'today.rss')

#parse the rss feed
tree = ET.parse('today.rss')
root = tree.getroot()

today = date.today().strftime('%Y-%m-%d');

#open a text file to store the book title and urls
file_name = f'daily_uploads/{today}.txt'

with open(file_name, 'w+') as file:
    #find <items>
    items = root.findall('channel/item')

    #loop through each upload
    for item in items:
        title = item.find('title').text
        #get the url of books plaintext file
        links = item.findall('link')
        file_url = None
        for link in links:
            if link.text:
                file_url = link.text
                break
        if file_url is None:
            print(f"no URL found for '{title}'")
            continue

        #write the title and URL to the text file
        file.write(f"{title}'\t{file_url}\n")
file.close()
os.remove('today.rss')

#get random book number from text file - change this to get book txt file from project Gutenberg
book_number, title = get_random_book()
if book_number is not None:
    print(f"Book of the day for {today} is {title}: {book_number}")
    retrieve_book(book_number, title)
else:
    print("Error getting book number")
