# robotito
*robotito* is a small light web crawler, that is, a program which navigates across the web in an autonomous way. 
It's main pourpose is to collect cybermetric data about the web pages, but it can be easily tunned for collect 
every kind of data.
### Install
*robotito* is a single Python file plus a config file
- requires Python 3 with libraries:
  - sys, os, re, requests, urllib, operator, magic and signal 
- assuming you already have Python 3, you certainment also have sys, os, re and operator; install the other with pip, example:

`pip install requests`
- then simply copy *robotito.py* in a folder of your convenience

### Basic Usage
- need, at less, one URL as starting point (*seed*). 
- admit a number of parameters in order to set rules delimiting web pages to explore, set max of pages to explore, etc.
- most of those parameters can be setted in a config file
So, the mos basic usage is:

`python3 robotito.py -c config_file`
