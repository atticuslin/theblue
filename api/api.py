#LSPT Search Engine, Team theblue
from flask import Flask, request, jsonify
from flask_api import status
import requests
import queries


app = Flask(__name__)


CRAWLING_ENDPOINTS = ["lspt-crawler1.cs.rpi.edu", "lspt-crawler2.cs.rpi.edu"]
alternator = 0

crawl_links = ["rpi.edu", "cs.rpi.edu", "info.rpi.edu", "admissions.rpi.edu",
	"rpiathletics.com"]
graph = queries.Driver()#Neo4j Graph Interface Initialization

def get_crawling_endpoint():
	alternator = not alternator
	return CRAWLING_ENDPOINTS[alternator]

@app.route('/rank_list', methods = ['POST'])
def rank_list():
	if request.method == 'POST':
		print("Received Ranking Request")
		url_list = request.get_json(force=True)['urls']
		print("Url list: ", url_list)
		pagerank_vals = rank(url_list)
		print("Values: ", pagerank_vals)
		return jsonify(pagerank_vals), status.HTTP_200_OK
	else:
		#TODO: Confirm Error state
		return "Error", status.HTTP_501_NOT_IMPLEMENTED

#TODO: Currently assumes there is just one link and docid but double check
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
		#TODO: Confirm Error state
		return "Error", status.HTTP_501_NOT_IMPLEMENTED

#TODO: Test POST request success
def crawl():
	linkstosend = dict()
	linkstosend['urls'] = get_next_crawl()
	response = requests.post(get_crawling_endpoint() + '/crawl', json=linkstosend)
	response.raise_for_status()

@app.route('/test')
def testAPI():
	return "Working!"

'''
Returns true if url exists in graph
@param url URL whose existance this function checks
@return True if URL is in graph
'''
def exists(url):
	pass

'''
TODO: Fix comments to reflect single link being added, not multiple
Insert link into webgraph and return success or fail
POST at /update
@param url_list dictionary of links and links they list to to be inserted/updated in graph
@modify Graph by adding outlinks from url to corresponding nodes in graph and new nodes if outlinked urls are new
@modify Queue if a key URL is not in the graph already 
@Return True if successful and return 200 code
TODO: If leaf node's inlinks are deleted, remove from graph so it's not just floating around?
'''
def update(docid, link, url_list):
	graph.update(docid, link, url_list)
	#TODO: Return Success or Fail

'''
Get next links, post to crawling, and remove from queue after confirmation
POST links to /crawl
@param max Maximum number of links to crawl
@modify queue by removing links once 200 success has been received from crawling
@return Returns list of max number of links to be crawled
'''
def get_next_crawl():
	outlist = []
	for ii in range(len(crawl_links)):
		outlist.append(crawl_links.pop(0))
	return outlist

'''
l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
POST received at /rank_list
@param l list of links to rank in order
@return dictionary of links -> pagerank score
'''
def rank(l):
	graph.run_pagerank()
	return graph.get_pagerank(l)


def testing():
	def exists_test():
		'''
		Add test link to graph
		Assert that exists returns true with that same test link
		Assert that exists returns false with a different test link
		Add that different test link to graph
		Assert that exists returns true now with that different test link
		Assert that exists returns false with an empty/integer input
		'''
	def update_test():
		'''
		*Use neo4j get functions to test if links are added to graph
		Call update on an empty graph with test url
		Assert that graph now has test url
		Call update with list of one test url that is in the graph already
		Assert that new outlinks are created and that old inlinks are deleted
		'''

	def get_next_crawl_test():
		'''
		Call get_next_crawl(100) on empty graph and assert that it returns an empty list
		Create basic graph with 10 nodes
		Call get_next_crawl(3) on graph and assert that it returns three nodes to be crawled that are leaf nodes
		'''

	def rank_test():
		'''
		Create graph with 10 nodes
		Assert that rank(list of the 10 urls in graph) returns a list with expected PageRank scores
		Assert that rank(empty list) returns empty dictionary
		Assert that rank(list of 3 urls not in graph) returns has all zero values
		'''

if __name__ == '__main__':
	app.run(host='0.0.0.0', port = 80)