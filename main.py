import warnings
warnings.filterwarnings('ignore')

import time
import USpatent

if __name__ == '__main__':
    START_TIME = time.clock()

    # "True" if you want to download patent file
    switch_DOWNLOAD = False
    # "True" if you want to parse patent file
    switch_PARSE = True
    # "True" if you want to get abstract, claims and description of patent file
    switch_TXT = True

    input_from_txt = False
    if input_from_txt:
        input_terms = open('input_terms.txt', 'r')
        for line in input_terms:
            terms = line.split(',')
            term1 = terms[0].lstrip().rstrip()
            field1 = terms[1].lstrip().rstrip()
            term2 = terms[2].lstrip().rstrip()
            field2 = terms[3].lstrip().rstrip()
            BooleanOp = terms[4].lstrip().rstrip()
            USpatent.ProcessPatents(term1, field1, term2, field2, BooleanOp, switch_DOWNLOAD, switch_PARSE, switch_TXT)
    else:
        term1 = 'dildo'
        field1 = ''
        term2 = ''
        field2 = ''
        BooleanOp = 'AND'
        USpatent.ProcessPatents(term1, field1, term2, field2, BooleanOp, switch_DOWNLOAD, switch_PARSE, switch_TXT)

    # total spending time
    print(time.clock()-START_TIME)