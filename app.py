#LSPT Search Engine, Team theblue

crawl_links = []
graph = {} #Will be created in neo4j


'''
Returns true if url exists in graph
@param url URL whose existance this function checks
@return True if URL is in graph
'''
def exists(url):
	pass

'''
Insert link into webgraph and return success or fail
@param url URL to be inserted/updated in graph
@modify Graph by adding outlinks from url to corresponding nodes in graph
@return True if successful
'''
def update(url):
	pass

'''
Get next links, post to crawling, and remove from queue after confirmation
@param max Maximum number of links to crawl
@modify queue by removing links once they have been sent
@return Returns list of max number of links to be crawled
'''
def get_next_crawl(max):
	pass

'''
l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
POST sent to /rank_list
@param l list of links to rank in order
@return list of links ranked by pagerank
'''
def rank(l):
	pass


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
		Call update with test url that is in the graph already
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
		Assert that rank(list of the 10 urls in graph) returns a list with them properly ranked via PageRank
		Assert that rank(empty list) returns empty list
		Assert that rank(list of 3 urls not in graph) returns empty list
		'''