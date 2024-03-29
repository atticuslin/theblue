#LSPT Search Engine, Team theblue
from flask import Flask, request, jsonify
from flask_api import status
import requests
import queries
import sys
from CrawlManager import CrawlManager
import time

app = Flask(__name__)

CRAWLING_ENDPOINTS = ["http://lspt-crawler1.cs.rpi.edu", "http://lspt-crawler3.cs.rpi.edu:3333"]
alternator = 0 #Flag to alternate between endpoints
MAX_LINKS = 10

crawl_links = ['http://rpi.edu',  'http://cs.rpi.edu', 'http://info.rpi.edu',
	'http://admissions.rpi.edu', 'http://rpiathletics.com' , 'https://research.rpi.edu',
	'https://news.rpi.edu', 'https://studentlife.rpi.edu', 'https://giving.rpi.edu', 
	'https://studenthealth.rpi.edu', 'https://sexualviolence.rpi.edu/', 'https://sll.rpi.edu/',
	'https://union.rpi.edu']
graph = queries.Driver() #Neo4j Graph Interface Initialization

#Initialize link manager
graph.add_initial_urls(crawl_links)
manager = CrawlManager(graph)
for link in crawl_links:
	manager.add(link)

'''
Alternate between crawling endpoints
@modifies alternator between 0 and 1
@return endpoint address
'''
def get_crawling_endpoint():
	global alternator
	alternator = not alternator
	return CRAWLING_ENDPOINTS[alternator]

'''
API Endpoint: Rank a list of docids
@return status code
@return PageRank scores for a list of input docids
'''
@app.route('/rank_list', methods = ['POST'])
def rank_list():
	if request.method == 'POST':
		print("Received Ranking Request")
		docids = request.get_json(force=True)
		print("Docid list: ", docids)
		try:
			pagerank_vals = rank(docids)
			print("Values: ", pagerank_vals)
			return jsonify(pagerank_vals), status.HTTP_200_OK
		except Exception as e:
			print(e)
			print("Tried to rank empty graph --> Sending empty json object")
			return jsonify({})
	else:
		return "Error", status.HTTP_405_METHOD_NOT_ALLOWED

'''
API Endpoint: Update graph
@modify graph By reflecting updated outlinks and crawled link
@return success code
'''
@app.route('/update', methods = ['POST'])
def update():
	global manager
	if request.method == 'POST':
		print("Received update:")
		request_data = request.get_json(force=True)
		crawled_link = request_data['crawled_link']
		docid = request_data['docid']
		outlinks = request_data['outlinks']
		result = update(docid, crawled_link, outlinks)

		print("Crawled link: ", crawled_link)
		print("docid: ", docid)
		print("outlinks: ", outlinks)
		print("result: ", result)

		#Add uncrawled links
		for r in result:
			if not r["crawled"]:
				manager.add(r["url"])
		if result:	
			print("Returned Success")
			return "ok", status.HTTP_200_OK
		else:
			print("Error")
			return "not ok", status.HTTP_500_INTERNAL_SERVER_ERROR
	else:
		return "Error", status.HTTP_405_METHOD_NOT_ALLOWED

'''
Test to verify server is running
@return Confirmation string
'''
@app.route('/')
def testAPI():
	return "Working!"

'''
Returns the outlinks for a given url
@param url URL to search the graph for
@return list of out links
'''
def get_out_links(url):
	graph.get_out_links(url)


'''
Insert link into webgraph and return success or fail
@param docid, the docid associated to the link being added to the graph
@param links, the url being added
@param url_list list of out links for the url being added
@modify Graph by adding outlinks from url to corresponding nodes in graph and new nodes if outlinked urls are new
@modify Queue if a key URL is not in the graph already 
TODO: If leaf node's inlinks are deleted, remove from graph so it's not just floating around?
'''
def update(docid, link, url_list):
	graph.update(docid, link, url_list)

'''
Get next links, post to crawling, and remove from queue after confirmation
@param max_links Maximum number of links to crawl
@modify queue by removing links once 200 success has been received from crawling
@return Returns list of max number of links to be crawled
'''
def get_next_crawl():
	global manager
	return manager.get_next_url()


'''
Crawl method to send post with urls
@return response to Crawl request
'''
def crawl():
	linkstosend = [get_next_crawl()]
	endpoint = get_crawling_endpoint()
	print("Sending to: ", endpoint)
	response = requests.post(endpoint + '/crawl', json=linkstosend)
	return response

'''
l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
@param l list of links to rank in order
@return dictionary of links -> pagerank score
'''
def rank(l):
	graph.run_pagerank()
	return graph.get_pagerank(l)

'''
Endpoint to start crawling
@return String and code
'''
@app.route('/start', methods = ['GET'])
def start_crawling():
	global manager
	if request.method == 'GET':
		while not manager.done:
			print("Sending links...")
			try:
				response = crawl()
				print(response)
			except Exception as e:
				print('EXCEPTION: ', e)
			time.sleep(5)
		return "Crawling has stopped"
	return "Invalid Request", status.HTTP_405_METHOD_NOT_ALLOWED

if __name__ == '__main__':
	app.run(host='0.0.0.0', port = 80)
