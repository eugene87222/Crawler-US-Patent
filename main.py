import warnings
warnings.filterwarnings('ignore')

import time
import USpatent

if __name__ == '__main__':
    START_TIME = time.clock()

    # "True" if want to download patent file
    switch_DOWNLOAD = False
    # "True" if want to parse patent file
    switch_PARSE = True
    # "True" if want to get abstract, claims and description of patent file
    switch_TXT = False

    input_from_txt = True
    if input_from_txt:
        input_terms = open('input_terms.txt', 'r')
        for line in input_terms:
            USpatent.ProcessPatents(line, switch_DOWNLOAD, switch_PARSE, switch_TXT)
    else:
        line = 'compressor, all fields, AND, magnetic, all fields, AND, Daikin, Assignee Name'
        USpatent.ProcessPatents(line, switch_DOWNLOAD, switch_PARSE, switch_TXT)

    # total spending time
    print (time.clock()-START_TIME)