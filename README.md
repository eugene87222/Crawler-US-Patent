# US-Patent

## Environment
- windows 10 home
- Python 3.6.4

## Prerequisite
- [install Python](https://www.python.org/)
- install requests, beautifulsoup, pandas, selenium
```
pip3 install requests
pip3 install beautifulsoup4
pip3 install pandas
pip3 install selenium
```
- [download selenium drivers](http://selenium-python.readthedocs.io/installation.html#drivers)

---
## How to use
You can either set the input terms by yourself or let the program to read input terms from input_terms.txt
- If you want to set them by yourself, switch "input_from_txt" to "False" in "\_\_main\_\_" scope and assign two terms to term1 and term2 directly.
- If you want the program read terms from txt file, switch "input_from_txt" to "True" in "\_\_main\_\_" scope.
In "input_terms.txt", each pair of terms in one line and two terms of each pair must be separated by ','  
e.g.  
Electric vehicle,lithium battery  
another term1,another term2  
...  

You can also set "switch_DOWNLOAD", "switch_PARSE", "switch_TXT" in "do_the_job" if you want the program to do speific things.  

After all, use the command below to run the program.
```
python tool.py
```
__Note: the program will open a browser automatically when you start it, do not close the browser or there will be some errors.__
