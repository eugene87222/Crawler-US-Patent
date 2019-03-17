import warnings
warnings.filterwarnings('ignore')

from bs4 import BeautifulSoup
import requests
import time
import os

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Download each patent as html file.
def GetHtml(rows, folder):
    # if the folder doesn't exist, create one
    if not os.path.exists(folder+'/html'):
        os.makedirs(folder+'/html')

    # download each patent in the rows
    for row in rows:
        link = row.select('td')[1].find('a')['href']
        link = 'http://patft.uspto.gov' + link

        while True:
            res = requests.get(link, headers=headers)
            soup = BeautifulSoup(res.text, 'lxml')
            title = soup.find('title')
            if title:
                break

        title = title.text
        filename = title + '.htm'
        filename = filename.replace(':', '_')

        file = open(folder + '/html/' + filename, 'w')
        file.write(res.text)
        file.close()
        print(filename)

# Check if the current page is not last page
def GetNextPage(soup):
    tables = soup.findAll('table')
    if tables:
        for table in tables:
            table = table.extract()
    A = soup.findAll('a')
    link = 'None'
    for a in A:
        if a.find('img') and a.find('img')['alt'] == '[NEXT_LIST]':
            link = a['href']
            break
    return link

# Download the content from <url> and store them in <folder>
def DownloadHtml(url, folder):
    show_load_time = True
    last_page = False
    
    while not last_page:
        while True:
            START = time.clock()
            res = requests.get(url, headers=headers)
            print(url)
            if show_load_time:
                print(time.clock() - START)
            soup = BeautifulSoup(res.text, 'lxml')
            tables = soup.findAll('table')
            if len(tables) > 1:
                break

        table = tables[1]
        rows = table.select('tr')[1:]
        print(f'Rows: {len(rows)}')
        prev_patent_num = rows[0].findAll('td')[1].text.strip()
        print(f'1st No: {prev_patent_num}')
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        GetHtml(rows, folder)

        link = GetNextPage(soup)
        if link == 'None':
            last_page = True
        else:
            url = 'http://patft.uspto.gov/' + link