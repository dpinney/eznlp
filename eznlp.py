''' eznlp - Easy Natural Language Processing Functions for Python. '''

from ktrain import text
import os
import urllib
import shutil
import textract
from multiprocessing import Process, Queue
import requests
from urllib.parse import quote_plus

def get_text(target, is_url=False):
	'''
	Get text from the [target] file or url regardless of format.
	User [is_url] flag to indicate the [target] is a url.
	Supports everthing textract does: https://textract.readthedocs.io/en/stable/
	'''
	if not is_url:
		text = textract.process(target)
		#TODO: Additional PDF options:
		#text2 = textract.process(ermco_doc).decode(sys.stdout.encoding)
		#text3 = textract.process(ermco_doc, method='pdfminer').decode(sys.stdout.encoding)
	else:
		response = urllib.request.urlopen(target)
		text = response.read()
	return str(text)

def summarize(string):
	'''
	Summarize the given [string].
	'''
	ts = text.TransformerSummarizer()
	return ts.summarize(string)

def sentiment(string):
	'''
	Determine whether a text is positive or negative.
	Derived from https://nbviewer.jupyter.org/github/amaiya/ktrain/blob/master/examples/text/zero_shot_learning_with_nli.ipynb
	'''
	zsl = text.ZeroShotClassifier()
	res = zsl.predict(
		string,
		labels=['negative', 'positive'],
		include_labels=True,
		nli_template="The article is {}."
	)
	return res

def subjects(string, string_list):
	'''
	Determine whether [string] is about the given subjects in [string_list].
	'''
	zsl = text.ZeroShotClassifier()
	res = zsl.predict(
		string,
		labels=string_list,
		include_labels=True,
		nli_template="The article is about {}."
	)
	return res

def search_make_index(docs_folder, index_folder, rebuild=False):
	'''
	Create a semantic search index for a [docs_folder] which contains .txt files storing the index in [index_folder].
	Returns a question answering object used by the search function.
	'''
	if rebuild:
		shutil.rmtree(index_folder, ignore_errors=True)
	text.SimpleQA.initialize_index(index_folder)
	docs = []
	fnames = [x for x in os.listdir(docs_folder) if x.endswith('.txt')]
	for fn in fnames:
		raw_text = open(docs_folder + fn).read()
		encd = str(raw_text).encode('ascii', 'ignore')
		docs.append(str(encd))
	# indexing from folder had encoding problems, couldn't find working recode syntax 
	# !apt install recode
	# !recode UTF8..ISO-8859-15 ./en_docs/*.txt
	# text.SimpleQA.index_from_folder(
	#     './en_docs',
	#     index_folder,
	#     use_text_extraction=False, #MIGHT TAKE FOREVER IF TRUE!?
	#     multisegment=True,
	#     procs=4, # speed up indexing with multiple cores
	#     breakup_docs=True, # this slows indexing but speeds up answer retrieval
	# )
	text.SimpleQA.index_from_list(
		docs,
		index_folder,
		commit_every=len(docs),
		multisegment=True,
		procs=4, # speed up indexing with multiple cores
		breakup_docs=True # this slows indexing but speeds up answer retrieval
	)
	return text.SimpleQA(index_folder)

def search(qae, query, show_html=False):
	'''
	Answer [query] using the [qae] q&a object returned by search_make_index().
	If [show_html] is True, display html table of results (in jupyter or for inclusion in a web page).
	'''
	answers = qae.ask(query)
	if show_html:
		qae.display_answers(answers)
	return answers

def named_entities(doc):
	''' 
	Identify all named entities (persons, places, organizations) in the [doc].
	'''
	queue = Queue()
	def inner_func(doc2):
		os.environ['DISABLE_V2_BEHAVIOR'] = '1'
		ner = text.shallownlp.NER()
		outs = ner.predict(doc2, merge_tokens=True)
		queue.put(set(outs))
	p = Process(target=inner_func, args=(doc,))
	p.start()
	p.join()
	return queue.get()

def _google_answer():
	'''
	Get semantic answers from google.
	This is a non-functional proof-of-concept.
	#TODO: complete one or more of these methods.
	'''
	question = 'how do you earn bitcoins?'
	# question = 'how much does energy storage cost?' #Has a featured snippet, https://google.com/search?q=how+much+does+energy+storage+cost
	# SERP API approach
	clean_q = quote_plus(question)
	query = f'https://serpapi.com/search.json?q={clean_q}&location=Dallas&hl=en&gl=us&source=test'
	r = requests.get(query)
	ans = r.json()
	just_snippets = [(f'ANSWER: {x["snippet"]}',f'PAGE: {x["title"]}',f'URL: {x["link"]}') for x in ans['organic_results']]
	related_questions = [x for x in ans['related_questions']]
	print(just_snippets)
	print(related_questions)
	# Parsing the raw HTML approach
	question = 'how much does energy storage cost?' #Has a featured snippet, https://google.com/search?q=how+much+does+energy+storage+cost
	clean_q = quote_plus(question)
	query = f'https://google.com/search?q={clean_q}'
	r = requests.get(query)
	raw_results = r.content; #it's there? but it's gross to parse.
	# Google custom search api approach
	#!pip install google-api-python-client
	from googleapiclient.discovery import build
	from keys import *
	def google_search(search_term, api_key, cse_id, **kwargs):
		service = build("customsearch", "v1", developerKey=api_key)
		res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
		return res['items']
	results = google_search("how much does energy storage cost?",my_api_key,my_cse_id,num=10)
	print(results) # clean, but it's just the search results.
	# Using selenium approach. Fully capable but a horrible parsing challenge.
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.chrome.options import Options
	chrome_options = Options()
	chrome_options.add_argument("--window-size=1024x768")
	chrome_options.add_argument("--headless")
	chrome_options.add_argument('log-level=3') #ignore js exceptions
	driver = webdriver.Chrome(chrome_options=chrome_options)
	def ask_google_selenium(query):
		# Search for query
		query = query.replace(' ', '+')
		driver.get('http://www.google.com/search?q=' + query)
		# Get text from Google answer box
		#answer = driver.find_element_by_tag_name('body').text
		answer = driver.execute_script(
			"return document.elementFromPoint(arguments[0], arguments[1]);",
			350, 230).text
		return answer
	ask_google_selenium('price of bitcoin?')

def _get_sample_data():
	url_pge = 'https://drive.google.com/uc?export=download&id=13dd5nWDvdzrSf01d8g-tZzhh32ewZ-Rc'
	url_ev = 'https://drive.google.com/uc?export=download&id=1h-Hy2WP9V9Fk3qibTbFfK1fDo6TlCtTL'
	url_en_docs = 'https://drive.google.com/uc?export=download&id=1fJzsbxphNo_r95EyqV3swlgKQIXHxXl3'
	urllib.request.urlretrieve(url_en_docs, 'en_docs.zip')
	urllib.request.urlretrieve(url_pge, 'demo_doc.txt')
	urllib.request.urlretrieve(url_ev, 'ev_doc.txt')
	pge_doc = open('demo_doc.txt').read()
	ev_doc = open('ev_doc.txt').read()
	shutil.rmtree('en_docs', ignore_errors=True)
	os.system('unzip en_docs.zip -d en_docs')
	return pge_doc, ev_doc

def _run_all_tests():
	pge_doc, ev_doc = _get_sample_data()
	blarg = get_text('https://drive.google.com/uc?export=download&id=13dd5nWDvdzrSf01d8g-tZzhh32ewZ-Rc', is_url=True)
	named_entities(pge_doc)
	summarize(pge_doc)
	sentiment(pge_doc)
	subjects(pge_doc, ['wildfires','energy','bacon','pge'])
	ENINDEXDIR = './ENERGY_INDEX'
	qae = search_make_index('./en_docs/', ENINDEXDIR, rebuild=True)
	search(qae, 'How much does solar cost?')
	search(qae, 'solar?')
	search(qae, 'what are small modular nuclear reactors?')