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

NOTE: if you intend use *robotito* in the Tor network, you will need *torsocks* running in your computer (see below)
### Basic Usage
- need, at less, one URL as starting point (*seed*). 
- admit a number of parameters in order to set rules delimiting web pages to explore, set max of pages to explore, etc.
- most of those parameters can be setted in a config file
So, the most basic usage is:

`python3 robotito.py -c config_file`

### Configuration
robotito needs some parameters to do its work. Those parameters are setted in three steps, which are

- some safe defaults, setted inside the code
- parameter values setted by means of a configuration file(they override default values)
- parameter values passed as option in the command line (they override values in config file)

### Config file
Config file has directives in the form parameter_name:parameter_value
Lines starting with # are ignored.
Available parameters are:

- **max_level**: integer value, telling the max recursion level
- **max_nodes**: integer value telling wanted max of visited pages
- **max_list_size**: integer value wiht the max size of to_visit list
- **seed**: either a filepath with a list of seeds; or a single URL as only seed. If filepath, expect to be a textfile wiht an URL per line
- **cyberfile**: filepath where saving finded links for later analysis; optional, if None no nothing is recorded
- **session_mode**: value can be 'fresh' (for a new crawl starting from the begining) or 'resume' (resuming a previous interrumpted crawl)
- **session_visited_file**: filename where keeping visited URLs, preventing a crawl interrumption
- **session_tovisit_file**: filename where keeping URLs to yet visit
- **proxyhost**: if connecting through a proxy, the proxy host address
- **proxyport**: if connectign thorugh a proxy, the proxy port number
- **rule**
    - can (should) be several rules defining which links the crawler must follow, and which not.
    - rules are regular expressions preceded with '+' or '-'. 
    - '-' rules mean the crawler not follow links matching regular expression
    - '+' rules mean the crawler must follow links matching regular expression
- **cyberrule**: same as rule, but just for save links in cyberfile
- **proxyhost**: proxy address, if any
- **proxyport**: proxy port, if any
- **mode**: queue|stack|freq
- **useragent**: agent self-identification (defalut='robotito')

### Options in command line
Some parameter can be setted also as option in command line

- **-c**: pathfile of config file
- **-o**: pathfile to cyberfile
- **-l**: max level recursion
- **-s**: single seed or filepath with a list of seeds
- **-resume**: continue with a prevous interrumpted crawl
- **-p**: print parameters and settings

### robotito and Tor
robotito can to explore and crawl the Tor network. To do that, it needs software *torsocks* (see [https://github.com/dgoulet/torsocks](https://github.com/dgoulet/torsocks)) working on your computer. *torsocks* also comes in major Linux distros repositories.

*torsocks* set a kind of proxy, tipically running on your localhost, port 9050 (although you can change those parameters trough the configuration of torsocks). All you need, in addition to torsocks itself, is set proxyhoist y proxyport in your config file; as well as some good Tor addresses as seeds.
