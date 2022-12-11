'''
pre-crawler
this is a simplistic crwaler, just for
testing procedures and data structures

versión OO
'''
import re
import os
import requests
import magic
import signal
from urllib.parse import urljoin, urldefrag, quote
from operator import itemgetter
from sys import argv, exit

class crawler:
	# the main class
	def __init__(self):
		# begins by setting some default values
	
		# main list of URLs to visit, list of tuple:(URL, coef.)
		# by the moment, coef is the freq of URL
		self.to_visit={} # key=URL, value=(num. sorting, level)
		
		# keep track of number of visited URLs
		self.rank=0

		# keep record of already visited URLs
		self.visited={} # 

		# some patterns
		self.plink=re.compile('href=\"(.*?)\"', re.M)
		# rules, have the schema: +regexp
		# exampl. '+\.usal\.es'
		
		# for pre-compiling and keeping regexps
		self.rulesYES=[]
		self.rulesNOT=[]

		self.cyberrulesYES=[]
		self.cyberrulesNOT=[] 
	
		# mode of exploring: queue, stack, top value
		self.mode='queue'
		self.max_level=5
		self.max_nodes=50000
		self.max_list_size=10000
		self.cyberfile=''
		self.seedsfile=''
		self.configfile=''

	# -- procs	
	def visit(self,url):
		'''
		downloads a single URL
		returns status code and URL content
		'''
		try:
			x=requests.get(url)
		except:
			self.visited[url]=True
			return(0,'')
		# check for status code, if timeout, may be we should
		# to re-try later ??
		# by the moment, we forget this
		self.visited[url]=True
		return x.status_code, x.text
	
	def scan(self, content, url_base, level):
		'''
		receives the content of a downloaded url
		looking for links to another pages
		returns a list of retrieved links and level
		as a list of tuples (link, level)
		'''
		# scan only if content is HTML
		url_type=guess_type(content)
		if url_type=='HTML':
			links=self.plink.findall(content)
		elif url_type=='PDF':
			return [] # by the moment, we don't scan PDFs
		else:
			return []
		# absolutizing and normalizing links, avoinding duplicates
		uniq_links={}
		for link in links:
			link=urljoin(url_base,link)
			link=urldefrag(link)[0]
			# sorting query parameters, if any
			parts=link.split('?')
			if len(parts)==2:
				query=sorted(parts[1].split('&'))
				norm_query=quote('&'.join(query))
				link=parts[0]+'?'+norm_query
			# add to dict of unique links
			uniq_links[link]=True
		# return the list of unique links
		return [(l, level+1) for l in uniq_links.keys()]
	
	def link_filter(self, link, level):
		# apply filters to extracted link from a web page
		# tipycally, those filters discard non wanted extensions
		# (ej: .png, .exe, .iso etc etc)
		# Also apply rules to decide if crawler must visit an URL or not
		#  
		# applies YES rules before
		# URLs which match at less one YES rule, are then confronted 
		# against NOT rules. If they dont' match any of them, URLs is visited
		#
		# rules are pre-compiled regular expresions
		#
		# receives link and level, returns True oor False
		
		if level > self.max_level:
			return False
		ok=False
		for ruleY in self.rulesYES:
			if ruleY.search(link): 		
				ok=True
				for ruleN in self.rulesNOT:
					if ruleN.search(link):
						ok=False
						break
				break
		if ok:
			return True
		else:
			return False
			
	def cyber_link_filter(self,link):
		# match link against cyberrules
		# note that they are different rules to follow links
		# and cyberrules to keep links for further cybermetric analysis
		ok=False
		for ruleY in self.cyberrulesYES:
			if ruleY.search(link): 		
				ok=True
				for ruleN in self.cyberrulesNOT:
					if ruleN.search(link):
						ok=False
						break
				break
		return ok
		
		
	def following(self):
		# returns next URL to be visited
		# from to_visit list
		# and removes it 
		if self.mode=='queue':
			x=min(self.to_visit.items(), key=itemgetter(1))
			# x is a tuple (URL,(sorting num, level))
			del self.to_visit[x[0]]
		elif self.mode=='stack':
			x=max(self.to_visit.items(), key=itemgetter(1))
			# x is a tuple (URL,(sorting num, level))
			del self.to_visit[x[0]]
		elif self.mode=='freq':
			x=max(self.to_visit.items(), key=itemgetter(1))
			# x is a tuple (URL,(sorting num, level))
			del self.to_visit[x[0]]
		else:
			print('Bad mode setting')
			exit(88)
		return (x[0], x[1][1])
		
	def configure(self,fileconf):
		# reads in a conf file
		# sintax of file:
		#	blank lines or starting with # means nothing
		# lines have:
		#	parameter:value
		# example:
		# max_level:10
		# -----------------------------
		try:
			F=open(fileconf,'r')
		except:
			return False
		for line in F:
			line=line.strip('\n')
			line=line.replace('\t','').replace(' ','')
			if line.startswith('#') or line=='':
				continue
			a=line.split(':')
			if len(a) < 2:
				continue
			#if len(a) > 2:
			# it has more tha one colon
			parameter=a[0].lower()
			value=':'.join(a[1:])
			'''
			else:
				parameter=a[0].lower()
				value=a[1]
			'''
			# setting value
			if parameter=='max_level':
				self.max_level=int(value)
			elif parameter=='max_nodes':
				self.max_nodes=int(value)
			elif parameter=='max_list_size':
				self.max_list_size=int(value)
			elif parameter=='seedsfile':
				self.seedsfile=value
			elif parameter=='cyberfile':
				self.cyberfile=value
			elif parameter=='mode':
				self.mode=value
			elif parameter=='rule':
				part1=value[0]
				part2=value[1:]
				if part1=='+':
					self.rulesYES.append(re.compile(part2))
				elif part1=='-':
					self.rulesNOT.append(re.compile(part2))
			elif parameter=='cyberrule':
				part1=value[0]
				part2=value[1:]
				if part1=='+':
					self.cyberrulesYES.append(re.compile(part2))
				elif part1=='-':
					self.cyberrulesNOT.append(re.compile(part2))
			
		F.close()
		
		
	def inject_seeds(self,seed):
		# if single seed, add it to main list
		# else, take seeds from file
		if seed !='':
			self.to_visit[seed]=(self.rank,0)
			self.rank=self.rank+1 # ??? better with an specific function for ranking
		else:
			# take seeds from file
			try:
				F=open(self.seedsfile,'r')
				s=[s.strip('\n') for s in F.readlines() if s !='\n']
				F.close()
			except:
				print('Error with seeds file')
				return
			for seed in s:
				to_visit[seed]=(self.rank,0)
				self.rank=self.rank+1 # ??? better with an specific function for ranking
	
	def cybermetrics(self, sourcelink,links):
		# save links from visited page, to perform SNA later
		# save all links, we can filter them in futher steps
		# in processing cyberfile
		if self.cyberfile =='':
			return
		try:
			F=open(self.cyberfile,'a')
			for link, level in links:
				if self.cyber_link_filter(link):
					F.write(str(sourcelink)+' '+str(link)+'\n')
			F.close()
		except:
			print('ERROR with cyberfile')
			return
		
		
	def crawl(self,seed='', max_level=5):
		signal.signal(signal.SIGINT, signal_handler)
		# doing a full crawl
	
		# injecting seeds
		self.inject_seeds(seed)
		
		#--- loop
		while len(self.to_visit.keys()) > 0:
			this=self.following() # this is a tuple(URL, level)
			status, content=self.visit(this[0])
			print(this[0], this[1], status, len(self.to_visit.keys()))
			if status !=200:
				continue
			# add to visited URLS
			self.visited[this[0]]=True
			# check max visited nodes
			if len(self.visited.keys()) > self.max_nodes:
				print('Reached Max visited nodes')
				break
			# -- proc following() already deletes URL from to_visit
			links=self.scan(content, this[0], this[1])
			self.cybermetrics(this[0],links)
			
			# adding links to main list to_visit
			for link, level in links:	
				if link in self.visited:
					continue
				if link in self.to_visit:
					if self.mode=='freq':
						f,l=self.to_visit[link]
						self.to_visit[link]=(f+1,l)
					# as already in to_visit, it passed filters
					continue
				if self.link_filter(link, level):
					if self.mode=='queue' or self.mode=='stack':
						self.to_visit[link]=(self.rank, level)
					elif self.mode=='freq': # as not in to_visit, frequency=1
						self.to_visit[link]=(1,level)
					
					# check max_list_size
					if len(self.to_visit.keys()) > self.max_list_size:
						print('Reache Max waiting nodes')
						exit(88)
					self.rank=self.rank+1
			

	def pparameters(self):
		# print all config parameters
		# just for check
		print('max_level', self.max_level)
		print('max_nodes', self.max_nodes)
		print('max_list_size', self.max_list_size)
		print('seedsfile', self.seedsfile)
		print('cyberfile',self.cyberfile)
		print('mode',self.mode)
		for ruleY in self.rulesYES:
			print('ruleYES', ruleY)
		for ruleN in self.rulesNOT:
			print('ruleNOT', ruleN)
		for ruleY in self.cyberrulesYES:
			print('cyberruleYES', ruleY)
		for ruleN in self.cyberrulesNOT:
			print('cyberruleNOT', ruleN)
		
	
		
		
### utilities 
def guess_type(content):
	# guess the type of a web page content
	# NOTE: this proc may change as magic module
	# seems don't be standard 
	page_type=magic.from_buffer(content).split(' ')[0]
	return page_type
	
def signal_handler(signal, frame):
    # keyboard interrupt handler
    proceso=os.getpid()
    os.system('kill -9 '+str(proceso))

#--------------   -------------------
# instantiate class
X=crawler()

# some initial values
configfile=''
cyberfile=''
max_level=2
seed=''
print_parameters=False

# reads in arguments
for e in range(1, len(argv)):
	try:
		if argv[e]=='-c':
			X.configfile=argv[e+1]
		elif argv[e]=='-o':
			cyberfile=argv[e+1]			
		elif argv[e]=='-l':
			max_level=int(argv[e+1])
			pass
		elif argv[e]=='-s':
			seed=argv[e+1]
		elif argv[e]=='-p':
			print_parameters=True
	except:
		print('Error in arguments')
		exit(88)
		
# first, configure		
X.configure(X.configfile)
if len(X.rulesYES)==0:
	# if there aren't positive rules at all
	# we visit any link
	X.rulesYES.append(re.compile('.*'))

# overwriting parameters
if cyberfile!='':
	X.cyberfile=cyberfile
# better overwrite cyberfile, if exists
if X.cyberfile !='':
	try:
		F=open(X.cyberfile,'w')
		F.close()
	except:
		print('Bad cyberfile', X.cyberfile)
		exit(88)

if X.max_level !=0:
	X.max_level=max_level

if print_parameters:
	X.pparameters()

# proceed
X.crawl(seed=seed, max_level=max_level)


