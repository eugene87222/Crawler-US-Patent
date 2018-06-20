import warnings
warnings.filterwarnings('ignore')

import os
import time
import requests
from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

###############################################################
# Download each patent as html file.                          #
# param: rows   -> 50 results of each page                    #
#        folder -> folder which html file will be saved at    #
###############################################################
def GetHtml(rows, folder):
    # if the folder doesn't exist, create one
    if not os.path.exists(folder+'/html'):
        os.makedirs(folder+'/html')

    # download each patent in the rows
    for row in rows:
        link = row.findAll('td')[1].find('a')['href']
        link = 'http://patft.uspto.gov'+link

        while True:
            res = requests.get(link)
            html = BeautifulSoup(res.text, 'html5lib')
            title = html.find('title')
            if title:
                break

        title = title.text
        filename = title+'.htm'
        filename = filename.replace(':', '_')

        file = open(folder+'/html/'+filename, 'w')
        file.write(res.text)
        file.close()
        print(filename)

################################################
# Tell selenium to input term1 / term2         #
# param: browser -> selenium webdriver object  #
#        termID  -> ID of input box            #
#        term    -> term which will be input   #
################################################
def InputKeyword(browser, termID, term):
    browser.find_element_by_id(termID).click()
    browser.find_element_by_id(termID).clear()
    browser.find_element_by_id(termID).send_keys(term)

def SelectField(browser, fieldID, value):
    browser.find_element_by_id(fieldID).click()
    browser.find_element_by_xpath("//option[@value='"+value+"']").click()

###############################################
# Check if the current page is not last page  #
# param: html -> html code of current page    #
###############################################
def GetNextPage(html):
    tables = html.findAll('table')
    if tables:
        for table in tables:
            table = table.extract()
    A = html.findAll('a')
    link = 'None'
    for a in A:
        if a.find('img') and a.find('img')['alt'] == '[NEXT_LIST]':
            link = a['href']
            break
    return link

####################################################################
# Download the searching result of two input terms (term1, term2)  #
# param: term1, term2 -> two terms                                 #
####################################################################
def DownloadHtml(term1, field1, term2, field2, BooleanOp):
    folder = term1+'_'+BooleanOp+'_'+term2
    if not os.path.exists(folder):
        os.makedirs(folder)

    # open a Firefox browser (can be changed to Chrome if you like)
    browser = webdriver.Firefox()
    url = 'http://patft.uspto.gov/netahtml/PTO/search-bool.html'
    browser.get(url)
    
    time.sleep(5)

    InputKeyword(browser, 'trm1', term1)
    SelectField(browser, 'fld1', field1)
    InputKeyword(browser, 'trm2', term2)
    SelectField(browser, 'fld2', field2)
    
    browser.find_element_by_name("co1").click()
    browser.find_element_by_xpath("//option[@value='"+BooleanOp+"']").click()
    
    browser.find_element_by_xpath("//input[@value='Search']").click()
    time.sleep(10)

    while 1:
        current_url = browser.current_url
        if current_url != url:
            break

    last_page = False
    show_load_time = True # show a loading time of each page
    while not last_page:
        ############################
        if show_load_time:
            START = time.clock()
        #############################
        res = requests.get(current_url)
        ############################
        if show_load_time:
            print(time.clock()-START)
        #############################
        html = BeautifulSoup(res.text, 'html5lib')
        tables = html.findAll('table')
        table = tables[1]
        rows = table.findAll('tr')[1:]
        print("Rows:", len(rows))
        PRE_patentNo = rows[0].findAll('td')[1].text
        print("1st No:", PRE_patentNo)

        GetHtml(rows, folder)

        link = GetNextPage(html)
        if link == 'None':
            last_page = True
        else:
            current_url = 'http://patft.uspto.gov/'+link
        
    # browser.close()