import warnings
warnings.filterwarnings('ignore')

import os
import re
from bs4 import BeautifulSoup

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