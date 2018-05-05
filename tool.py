import warnings
warnings.filterwarnings('ignore')

import os
import re
import time
import requests
import operator
import pandas as pd
from pandas import DataFrame
from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

###############################################################
# Download each patent as html file.                          #
# param: rows   -> 50 results of each page                    #
#        folder -> folder which html file will be saved at    #
###############################################################
def get_html(rows, folder):
    # if the folder doesn't exist, create one
    if not os.path.exists(folder+'/html'):
        os.makedirs(folder+'/html')

    # download each patent in the rows
    for row in rows:
        link = row.findAll('td')[1].find('a')['href']
        link = 'http://patft.uspto.gov'+link

        res = requests.get(link)
        html = BeautifulSoup(res.text, 'html5lib')

        title = html.find('title').text

        filename = title+'.htm'
        filename = filename.replace(':', '_')

        file = open(folder+'/html/'+filename, 'w')
        file.write(res.text)
        file.close()
        print (filename)

################################################
# Tell selenium to input term1 / term2         #
# param: browser -> selenium webdriver object  #
#        termID  -> ID of input box            #
#        term    -> term which will be input   #
################################################
def input_keyword(browser, termID, term):
    browser.find_element_by_id(termID).click()
    browser.find_element_by_id(termID).clear()
    browser.find_element_by_id(termID).send_keys(term)

###############################################
# Check if the current page is not last page  #
# param: html -> html code of current page    #
###############################################
def get_next_page(html):
    tables = html.findAll('table')
    if tables:
        for table in tables:
            table = table.extract()
    A = html.findAll('a')
    link = 'None' # if current page is last page, link to the next page is 'None'
    for a in A:
        if a.find('img') and a.find('img')['alt'] == '[NEXT_LIST]':
            link = a['href']
            break
    return link

####################################################################
# Download the searching result of two input terms (term1, term2)  #
# param: term1, term2 -> two terms                                 #
####################################################################
def download_html(term1, term2):
    folder = term1+'_AND_'+term2

    # open a Firefox browser (can be changed to Chrome if you like)
    browser = webdriver.Firefox()
    url = 'http://patft.uspto.gov/netahtml/PTO/search-bool.html'
    browser.get(url)

    input_keyword(browser, 'trm1', term1)
    input_keyword(browser, 'trm2', term2)
    browser.find_element_by_xpath("//input[@value='Search']").click()

    last_page = False

    while 1:
        current_url = browser.current_url
        if current_url != url:
            break

    show_load_time = True # show a loading time of each page
    while not last_page:
        #############################
        if show_load_time:
            START = time.clock()
        #############################
        res = requests.get(current_url)
        #############################
        if show_load_time:
            print (time.clock()-START)
        #############################
        html = BeautifulSoup(res.text, 'html5lib')
        tables = html.findAll('table')
        table = tables[1]
        rows = table.findAll('tr')[1:] # 50 rows of each page (may less than 50)
        print ("Rows:", len(rows))
        PRE_patentNo = rows[0].findAll('td')[1].text
        print ("1st No:", PRE_patentNo)

        if not os.path.exists(folder):
            os.makedirs(folder)

        get_html(rows, folder)

        link = get_next_page(html)
        if link == 'None':
            last_page = True
        else: # if it's not the last page, go on to the next page
            current_url = 'http://patft.uspto.gov/'+link
    # browser.close()

###########################################################################
# Parse the html file of each patent and extract the information we want  #
# param: html -> html code of the patent                                  #
###########################################################################
def parse_html(html):
    p = html.find('p')
    # Patent Abstract
    if p:
        abstract = p.text.lstrip().rstrip()
        while '\n' in abstract:
            abstract = abstract.replace('\n', '')
        abstract = re.sub(' +', ' ', abstract)
    else:
        abstract = 'None'

    tables = html.findAll('table')

    country = tables[2].findAll('td')[0].text  # Country
    patentNo = tables[2].findAll('td')[1].text
    patentNo = re.sub(',', '', patentNo)
    patentNo = patentNo.lstrip().rstrip()      # Patent Number

    date = tables[2].findAll('td')[3].text.replace('*', '').lstrip().rstrip() # Patent Date

    font = html.findAll('font')
    title = font[-1].text.lstrip().rstrip()
    while '\n' in title:
        title = title.replace('\n', '')

    title = re.sub(' +', ' ', title) # Patent Title

    print (patentNo)
    print (title)
    print (date)
    print (country)
    print (abstract)

    # Applicant
    applicant = list()
    for table in tables:
        if 'Inventors:' in table.text and 'Appl. No.' in table.text:
            trs = table.findAll('tr')
            for tr in trs:
                if 'Applicant:' in tr.text:
                    tr = tr.findAll('tr')[1]
                    tds = tr.findAll('td')

                    Name_td = str(tds[0])
                    remove_list = ['<td>', '</td>', '<b>', '</b>', '&amp; ']
                    for item in remove_list:
                        Name_td = Name_td.replace(item, '')
                    Name_td = Name_td.lstrip().rstrip()
                    Name_list = Name_td.split('<br/>')
                    Name_list.remove('')

                    City = tds[1].text.split('\n')
                    State = tds[2].text.split('\n')
                    Country = tds[3].text.split('\n')
                    for i in range(len(Name_list)):
                        applicant.append(
                            Name_list[i].replace(';', '').replace('\n', ' ').lstrip().rstrip()+', '+
                            City[i].lstrip().rstrip()+' '+
                            State[i].replace('N/A', '').lstrip().rstrip()+'('+
                            Country[i].lstrip().rstrip()+')'
                            )
                    break
            break
    print (applicant)

    # CPC
    CPC = list()
    for table in tables:
        if 'Current CPC Class' in table.text:
            CPC = table.findAll('tr')[1].findAll('td')[1].text.lstrip().rstrip()
            break
    if len(CPC):
        CPC = CPC.split('; ')
        CPC = [re.sub(r'\(.*\)', '', i).replace('\xa0', ' ').lstrip().rstrip() for i in CPC]

    # IPC
    IPC = list()
    for table in tables:
        if 'Current International Class:' in table.text:
            IPC = table.findAll('tr')[1].findAll('td')[1].text.lstrip().rstrip()
            break
    if len(IPC):
        IPC = IPC.split('; ')
        IPC = [re.sub(r'\(.*\)', '', i).replace('\xa0', ' ').lstrip().rstrip() for i in IPC]

    print ('=================')

    return country, patentNo, date, title, abstract, applicant, CPC, IPC

############################################################
# Save patent information into a csv file                  #
# param: folder -> folder which csv file will be saved at  #
#        countries, patentNos... -> patent information     #
############################################################
def PatentInfo2excel(folder, countries, patentNos, dates, titles, abstracts, applicants, IPCs, CPCs):
    df = DataFrame({
        'Patent Number': patentNos,
        'Title': titles,
        'IPC': IPCs,
        'CPC': CPCs,
        'Date for patent': dates,
        'Country': countries,
        'Applicant': applicants,
        'Abstract': abstracts
        })
    df.to_csv(folder+'/Type(1).csv', index=False,
        columns=['Patent Number', 'Title', 'IPC', 'CPC', 'Date for patent', 'Country', 'Applicant', 'Abstract'])

###########################################################
# Save statistic data of CPC and IPC to a csv file        #
# param: folder -> folder which csv file will be saved at #
#        IPC_dict, CPC_dict -> data about CPC, IPC        #
###########################################################
def Statistic2excel(folder, IPC_dict, CPC_dict):
    top = 200
    sorted_IPC = sorted(IPC_dict.items(), key=operator.itemgetter(1))
    sorted_IPC.reverse()
    top_200_IPC = sorted_IPC if len(sorted_IPC) <= top else sorted_IPC[0:top]

    sorted_CPC = sorted(CPC_dict.items(), key=operator.itemgetter(1))
    sorted_CPC.reverse()
    top_200_CPC = sorted_CPC if len(sorted_CPC) <= top else sorted_CPC[0:top]
    
    df = DataFrame({
        'Top 200 IPC': [IPC[0] for IPC in top_200_IPC],
        'Count (IPC)': [IPC[1] for IPC in top_200_IPC],
        'Top 200 CPC': [CPC[0] for CPC in top_200_CPC],
        'Count (CPC)': [CPC[1] for CPC in top_200_CPC]
        })
    df.to_csv(folder+'/Type(2).csv', index=False, columns=['Top 200 IPC', 'Count (IPC)', 'Top 200 CPC', 'Count (CPC)'])

# def CPC2excel(folder, CPC_set):
#     df = DataFrame({
#         'CPC': CPC_set
#         })
#     df.to_csv(folder+'/CPC.csv', index=False)

# def IPC2excel(folder, IPC_set):
#     df = DataFrame({
#         'IPC': IPC_set
#         })
#     df.to_csv(folder+'/IPC.csv', index=False)

###########################################################
# get Abstract, Claims, Description of each patent        #
# param: folder -> folder which txt file will be saved at #
###########################################################
def get_A_C_D(folder):
    files = os.listdir(folder+'/html')
    for file in files:
        print (file)
        html = BeautifulSoup(open(folder +'/html/'+file, 'r'))

        p = html.find('p')
        if p:
            abstract = p.text.lstrip().rstrip()
            while '\n' in abstract:
                abstract = abstract.replace('\n', '')
            abstract = re.sub(' +', ' ', abstract)
        else:
            abstract = 'None'
        centers = html.findAll('center')
        for center in centers[-2:]:
            center = center.extract()
        text = str(html)
        claim_idx = text.find('<center><b><i>Claims</i></b></center>')
        des_idx = text.find('<center><b><i>Description</i></b></center>')
        claim = BeautifulSoup(text[claim_idx:des_idx]).text.lstrip().rstrip().replace('\n', ' ').replace('Claims  ', 'Claims:\n', 1)
        des = BeautifulSoup(text[des_idx:]).text.lstrip().rstrip().replace('\n', ' ').replace('Description  ', 'Description:\n', 1)
        
        txt = open(folder+'/txt/'+file.replace('.htm', '.txt'), 'w')
        txt.write('Abstract:\n')
        txt.write(abstract)
        txt.write('\n\n')
        txt.write(claim.encode(errors='ignore').decode(encoding='cp950', errors='ignore'))
        txt.write('\n\n')
        txt.write(des.encode(errors='ignore').decode(encoding='cp950', errors='ignore'))
        txt.close()

def do_the_job(term1, term2):
    print ('Term1:', term1)
    print ('Term2:', term2)
    # "True" if you want to download patent file
    switch_DOWNLOAD = False
    # "True" if you want to parse patent file
    switch_PARSE = False
    # "True" if you want to get abstract, claims and description of patent file
    switch_TXT = False

    if switch_DOWNLOAD:
        download_html(term1, term2)
    
    if switch_PARSE:
        folder = term1+'_AND_'+term2
        files = os.listdir(folder+'/html')

        CPC_dict = dict()
        IPC_dict = dict()
        
        countries = list()
        patentNos = list()
        dates = list()
        titles = list()
        abstracts = list()
        applicants = list()
        CPCs = list()
        IPCs = list()

        for file in files:
            html = BeautifulSoup(open(folder +'/html/'+file, 'r'))

            country, patentNo, date, title, abstract, applicant, CPC, IPC = parse_html(html)

            countries.append(country)
            patentNos.append(patentNo)
            dates.append(date)
            titles.append(title)
            abstracts.append(abstract)
            if not len(applicant):
                applicants.append('None')
            else:
                applicants.append('; '.join([i for i in applicant]))
            CPCs.append("; ".join([i for i in CPC]))
            IPCs.append("; ".join([i for i in IPC]))

            for i in CPC:
                if i in CPC_dict:
                    CPC_dict[i] += 1
                else:
                    CPC_dict[i] = 1

            for i in IPC:
                if i in IPC_dict:
                    IPC_dict[i] += 1
                else:
                    IPC_dict[i] = 1
            
        PatentInfo2excel(folder, countries, patentNos, dates, titles, abstracts, applicants, CPCs, IPCs)
        # CPC2excel(folder, list(CPC_dict.keys()))
        # IPC2excel(folder, list(IPC_dict.keys()))
        Statistic2excel(folder, IPC_dict, CPC_dict)

    if switch_TXT:
        folder = term1+'_AND_'+term2
        if not os.path.exists(folder+'/txt'):
            os.makedirs(folder+'/txt')
        get_A_C_D(folder)

if __name__ == '__main__':
    START_TIME = time.clock()

    input_from_txt = True
    if input_from_txt:
        input_terms = open('input_terms.txt', 'r')
        for line in input_terms:
            terms = line.split(',')
            term1 = terms[0].lstrip().rstrip()
            term2 = terms[1].lstrip().rstrip()
            do_the_job(term1, term2)
    else:
        term1 = 'Electric vehicle'
        term2 = 'lithium battery'
        do_the_job(term1, term2)

    # total spending time
    print (time.clock()-START_TIME)