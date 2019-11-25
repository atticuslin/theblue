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
		Assert that rank(list of the 10 urls in graph) returns a list with them properly ranked via PageRank
		Assert that rank(empty list) returns empty list
		Assert that rank(list of 3 urls not in graph) returns empty list
		'''
