import warnings
warnings.filterwarnings('ignore')

from bs4 import BeautifulSoup
from pandas import DataFrame
import pandas as pd
import operator
import re
import os


def GetAbstract(soup):
    p = soup.find('p')
    if p:
        abstract = p.text.strip()
        abstract = re.sub('\n+', '', abstract)
        abstract = re.sub(' +', ' ', abstract)
    else:
        abstract = 'None'
    return abstract

def GetAbsClaimDesc(folder):
    files = os.listdir(folder + '/html')
    for file in files:
        print (file)
        soup = BeautifulSoup(open(folder +'/html/'+file, 'r'), 'lxml')

        abstract = GetAbstract(soup)

        centers = soup.findAll('center')
        for center in centers[-2:]:
            center = center.extract()
        text = str(soup)
        claim_idx = text.find('<center><b><i>Claims</i></b></center>')
        desc_idx = text.find('<center><b><i>Description</i></b></center>')
        claim = BeautifulSoup(text[claim_idx:desc_idx], 'lxml').text.strip().replace('\n', ' ').replace('Claims  ', 'Claims:\n', 1)
        desc = BeautifulSoup(text[desc_idx:], 'lxml').text.strip().replace('\n', ' ').replace('Description  ', 'Description:\n', 1)
        
        txt = open(folder + '/txt/' + file.replace('.htm', '.txt'), 'w')
        txt.write('Abstract:\n')
        txt.write(abstract)
        txt.write('\n\n')
        txt.write(claim.encode(errors='ignore').decode(encoding='utf-8', errors='ignore'))
        txt.write('\n\n')
        txt.write(desc.encode(errors='ignore').decode(encoding='utf-8', errors='ignore'))
        txt.close()

# Parse the html file of each patent and extract the information
def ParseHtml(soup):
    # Patent Abstract
    abstract = GetAbstract(soup)

    tables = soup.select('table')
    
    # Country
    country = tables[2].select('td')[0].text 
    
    # Patent No.
    patentNo = tables[2].select('td')[1].text
    patentNo = re.sub(',', '', patentNo)
    patentNo = patentNo.strip()

    # Date
    date = tables[2].select('td')[3].text.replace('*', '').strip()

    # Title
    font = soup.select('font')
    title = font[-1].text.strip()
    title = re.sub('\n+', '', title)
    title = re.sub(' +', ' ', title)

    print (patentNo)
    print (title)
    print (date)
    print (country)
    print (abstract)

    # Applicant
    applicant = list()
    for table in tables:
        if 'Inventors:' in table.text and 'Appl. No.' in table.text:
            trs = table.select('tr')
            for tr in trs:
                if 'Applicant:' in tr.text:
                    tr = tr.select('tr')[1]
                    tds = tr.select('td')

                    name_td = str(tds[0])
                    name_td = re.sub(r'(<td>|</td>)|<b>|</b>|&amp;|\ +', '', name_td).strip()
                    name_list = name_td.split('<br/>')
                    name_list.remove('')

                    city = tds[1].text.split('\n')
                    state = tds[2].text.split('\n')
                    country = tds[3].text.split('\n')
                    for i in range(len(name_list)):
                        _applicant = name_list[i].replace(';', '').replace('\n', ' ').strip() + ', '
                        _applicant += city[i].strip() + ' '
                        _applicant += state[i].replace('N/A', '').strip() + '('
                        _applicant += country[i].strip() + ')'
                        applicant.append(_applicant)
                    break
            break

    print (applicant)

    # CPC
    CPC = list()
    for table in tables:
        if 'Current CPC Class' in table.text:
            CPC = table.select('tr')[1].select('td')[1].text.strip()
            break
    if len(CPC):
        CPC = CPC.split('; ')
        CPC = [re.sub(r'\(.*\)', '', i).replace('\xa0', ' ').strip() for i in CPC]

    # IPC
    IPC = list()
    for table in tables:
        if 'Current International Class:' in table.text:
            IPC = table.select('tr')[1].select('td')[1].text.strip()
            break
    if len(IPC):
        IPC = IPC.split('; ')
        IPC = [re.sub(r'\(.*\)', '', i).replace('\xa0', ' ').strip() for i in IPC]

    print ('=================')

    return country, patentNo, date, title, abstract, applicant, CPC, IPC

# Save patent information into a csv file
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
    df.to_csv(folder + '/Type(1).csv', index=False,
        columns=['Patent Number', 'Title', 'IPC', 'CPC', 'Date for patent', 'Country', 'Applicant', 'Abstract'])

# Save statistic data of CPC and IPC to a csv file
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
    df.to_csv(folder + '/Type(2).csv', index=False, columns=['Top 200 IPC', 'Count (IPC)', 'Top 200 CPC', 'Count (CPC)'])

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