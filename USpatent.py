import warnings
warnings.filterwarnings('ignore')

import os
from bs4 import BeautifulSoup
import DownloadHtml
import ParseHtml

def GetFieldList():
    field_dict = {}
    file = open('FieldAbbrList.txt', 'r')
    for line in file:
        op = line.split(',')
        field_dict[op[0].strip().lower()] = op[1].strip()
    return field_dict

def ProcessPatents(line, switch_DOWNLOAD, switch_PARSE, switch_TXT):
    field_dict = GetFieldList()
    item = line.split(',')
    terms = item[0::3]
    fields = [field_dict[field.strip().lower()] for field in item[1::3]]
    bool_op = item[2::3]
    print(terms)
    print(fields)
    print(bool_op)

    query = ''
    bool_idx = -1
    for i in range(len(terms)):
        if bool_idx > -1:
            query += f'+{bool_op[bool_idx].strip()}+'
        if fields[i].strip():
            query += f'{fields[i].strip()}%2F{terms[i].strip()}'
        else:
            query += terms[i].strip()
        bool_idx += 1
    
    print(query)
    url = f'http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO2&Sect2=HITOFF&p=1&u=%2Fnetahtml%2FPTO%2Fsearch-adv.htm&r=0&f=S&l=50&d=PTXT&Query={query}'

    if switch_DOWNLOAD:
        DownloadHtml.DownloadHtml(url, query)
    
    if switch_PARSE:
        folder = query
        files = os.listdir(folder + '/html')

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
            soup = BeautifulSoup(open(folder + '/html/' + file, 'r'), 'lxml')

            country, patentNo, date, title, abstract, applicant, CPC, IPC = ParseHtml.ParseHtml(soup)

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
            
        ParseHtml.PatentInfo2excel(folder, countries, patentNos, dates, titles, abstracts, applicants, CPCs, IPCs)
        # CPC2excel(folder, list(CPC_dict.keys()))
        # IPC2excel(folder, list(IPC_dict.keys()))
        ParseHtml.Statistic2excel(folder, IPC_dict, CPC_dict)

    if switch_TXT:
        folder = query
        if not os.path.exists(folder + '/txt'):
            os.makedirs(folder + '/txt')
        ParseHtml.GetAbsClaimDesc(folder)