import warnings
warnings.filterwarnings('ignore')

import re
import operator
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame

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

    print(patentNo)
    print(title)
    print(date)
    print(country)
    print(abstract)

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

    print(applicant)

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

    print('=================')

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