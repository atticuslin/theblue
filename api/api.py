#LSPT Search Engine, Team theblue
from flask import Flask, request, jsonify
from flask_api import status
import requests
import queries
import sys
import CrawlManager

app = Flask(__name__)


CRAWLING_ENDPOINTS = ["lspt-crawler1.cs.rpi.edu", "lspt-crawler2.cs.rpi.edu"]
alternator = 0
MAX_LINKS = 10

crawl_links = ["rpi.edu", "cs.rpi.edu", "info.rpi.edu", "admissions.rpi.edu", "rpiathletics.com"]
graph = queries.Driver() #Neo4j Graph Interface Initialization

def get_crawling_endpoint():
	alternator = not alternator
	return CRAWLING_ENDPOINTS[alternator]

@app.route('/rank_list', methods = ['POST'])
def rank_list():
	if request.method == 'POST':
		print("Received Ranking Request")
		docids = request.get_json(force=True)['urls']
		print("Docid list: ", docids)
		try:
			pagerank_vals = rank(docids)
			print("Values: ", pagerank_vals)
			return jsonify(pagerank_vals), status.HTTP_200_OK
		except Exception as e:
			print(e)
			print("Tried to rank empty graph --> Sending empty json object")
			return jsonify({})
		#TODO: Need to catch case in which the graph is empty
	else:
		return "Error", status.HTTP_405_METHOD_NOT_ALLOWED

@app.route('/update', methods = ['POST'])
def update():
	if request.method == 'POST':
		print("Received update:")
		request_data = request.get_json(force=True)
		crawled_link = request_data['crawled_link']
		print("Crawled link: ", crawled_link)
		docid = request_data['docid']
		print("docid: ", docid)
		outlinks = request_data['outlinks']
		print("outlinks: ", outlinks)
		#TODO: If receiving multiple links, add loop here
		result = update(docid, crawled_link, outlinks)
		print("result: ", result)
		if result:
			print("Returned Success")
			return "ok", status.HTTP_200_OK
		else:
			#TODO: Proper error messages
			print("Error")
			return "not ok", status.HTTP_500_INTERNAL_SERVER_ERROR
	else:
		return "Error", status.HTTP_405_METHOD_NOT_ALLOWED


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
Returns true if url exists in graph
@param url URL whose existance this function checks
@return True if URL is in graph
'''
def exists(url):
	pass

'''
Insert link into webgraph and return success or fail
@param docid, the docid associated to the link being added to the graph
@param links, the url being added
@param url_list list of out links for the url being added
@modify Graph by adding outlinks from url to corresponding nodes in graph and new nodes if outlinked urls are new
@modify Queue if a key URL is not in the graph already 
@Return True if successful and False otherwise
TODO: If leaf node's inlinks are deleted, remove from graph so it's not just floating around?
'''
def update(docid, link, url_list):
	graph.update(docid, link, url_list)
	#TODO: Return Success or Fail

'''
Get next links, post to crawling, and remove from queue after confirmation
@param max_links Maximum number of links to crawl
@modify queue by removing links once 200 success has been received from crawling
@return Returns list of max number of links to be crawled
'''
def get_next_crawl():
	outlist = []
	for ii in range(min(len(crawl_links), MAX_LINKS)):
		outlist.append(crawl_links.pop(0))
	return outlist

#TODO: Test POST request success
def crawl():
	linkstosend = dict()
	linkstosend['urls'] = get_next_crawl()
	response = requests.post(get_crawling_endpoint() + '/crawl', json=linkstosend)
	response.raise_for_status()

'''
l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
@param l list of links to rank in order
@return dictionary of links -> pagerank score
'''
def rank(l):
	graph.run_pagerank()
	return graph.get_pagerank(l)

@app.route('/start', methods = ['GET'])
def start_crawling():
	if request.method == 'GET':
		while(True):
			if len(crawl_links) != 0:
				crawl()

if __name__ == '__main__':
	app.run(host='0.0.0.0')