#LSPT Search Engine, Team theblue

from api_resources import UpdateResource, RankingResource


crawl_links = []
graph = {} #Will be created in neo4j, dictionary is just a placeholder


'''
Returns true if url exists in graph
@param url URL whose existance this function checks
@return True if URL is in graph
'''
def exists(url):
	pass

'''
Insert link into webgraph and return success or fail
POST at /update
@param url_list URL list to be inserted/updated in graph
@modify Graph by adding outlinks from url to corresponding nodes in graph
@modify Queue if a URL is not in the graph already
@Return True if successful and return 200 code
'''
def update(url_list):
	pass

'''
Get next links, post to crawling, and remove from queue after confirmation
POST links to /crawl
@param max Maximum number of links to crawl
@modify queue by removing links once 200 success has been received from crawling
@return Returns list of max number of links to be crawled
'''
def get_next_crawl(max):
	pass

'''
l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
POST received at /rank_list
@param l list of links to rank in order
@return dictionary of links -> pagerank score
'''
def rank(l):
	pass
