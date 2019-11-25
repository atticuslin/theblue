# see https://falcon.readthedocs.io/en/stable/api/request_and_response.html

'''
Resource for updating URLs
'''
class UpdateResource(object):

	'''
	Insert link into webgraph and return success or fail
	POST at /update
	'''
	def on_post(self, req, resp):
		pass


'''
Resource for ranking URLs
'''
class RankingResource(object):

	'''
	l is list of URLs from ranking; return dictionary/JSON with URL -> PageRank Value
	POST received at /rank_list
	'''
	def on_post(self, req, resp):
		pass
