import unittest
import random
import queries
import time

'''
Generates random test data to be used with the graph
@param num_links is the number of links you want in the test data
'''
def generateTestData(num_links):
	# first we generate a list of tuples like (docid, link) to use
	links = []
	for i in range(num_links):
		links.append((str(i), "http://www.site-"+str(i)+".com"))

	data = {}
	for docid, link in links:
		data[docid] = { "url": link, "out_links": [] }
		for i in random.sample(range(num_links), random.randint(0, num_links//2)):
			data[docid]["out_links"].append(links[i][0])

	return data

################################################################################################
#																			Actual Tests 																						 #
################################################################################################

# tests if the update function works properly
class TestUpdate(unittest.TestCase):

	# tests updating and adding out links
	def test_add_out_links(self):
		update_driver = queries.Driver()
		update_driver.update("0", "https://www.site-0.com", [])
		assert len(update_driver.get_outlinks("https://www.site-0.com")) == 0
		update_driver.update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		assert len(update_driver.get_outlinks("https://www.site-0.com")) == 1

	# tests updating and removing out links
	def test_remove_out_links(self):
		update_driver = queries.Driver()
		update_driver.update("1", "https://www.site-1.com", ["https://www.site-2.com"])
		assert len(update_driver.get_outlinks("https://www.site-0.com")) == 1
		update_driver.update("1", "https://www.site-1.com", [])
		assert len(update_driver.get_outlinks("https://www.site-0.com")) == 0

	# tests updating 1000 links in under 15 seconds
	def test_efficiency(self):
		update_driver = queries.Driver()
		testData = generateTestData(1000)
		start = time.time()
		for docid in testData:
			update_driver.update(docid, testData[docid]["url"], testData[docid]["out_links"])
		end = time.time()
		assert (end-start) < 15


# tests getting page rank
class TestRank(unittest.TestCase):

	# tests ranking single node
	def test_solo_node(self):
		rank_driver = queries.Driver()
		rank_driver.update("0", "https://www.site-0.com", [])
		rank_driver.run_pagerank()
		rankings = rank_driver.get_pagerank(["0"])
		assert len(rankings) == 1
		assert rankings["https://www.site-0.com"] > 0

	# tests ranking one link in a graph
	def test_single(self):
		rank_driver = queries.Driver()
		rank_driver.update("0", "https://www.site-0.com", [])
		rank_driver.update("1", "https://www.site-1.com", ["https://www.site-0.com"])
		rank_driver.update("2", "https://www.site-2.com", ["https://www.site-0.com"])
		rank_driver.update("3", "https://www.site-3.com", ["https://www.site-0.com"])
		rank_driver.run_pagerank()
		rankings = rank_driver.get_pagerank(["0"])
		assert len(rankings) == 1
		assert rankings["0"] > 0

	# tests ranking multiple links
	def test_multi(self):
		rank_driver = queries.Driver()
		rank_driver.update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		rank_driver.update("1", "https://www.site-1.com", ["https://www.site-0.com"])
		rank_driver.update("2", "https://www.site-2.com", ["https://www.site-0.com"])
		rank_driver.update("3", "https://www.site-3.com", ["https://www.site-0.com"])
		rank_driver.run_pagerank()
		rankings = rank_driver.get_pagerank(["0", "1"])
		assert len(rankings) == 2
		assert rankings["0"] > 0
		assert rankings["1"] > 0
		assert rankings["0"] > rankings["1"]

	# tests rankings an unknown url
	def test_unknown_url(self):
		rank_driver = queries.Driver()
		rank_driver.update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		rank_driver.run_pagerank()
		rankings = rank_driver.get_pagerank(["100"])
		assert len(rankings) == 1
		assert rankings["100"] == 0

	# tests that it can rank 100 pages in under a second
	def test_efficiency(self):
		rank_driver = queries.Driver()
		testData = generateTestData(100)
		for docid in testData:
			rank_driver.update(docid, testData[docid]["url"], testData[docid]["out_links"])
		start = time.time()
		rank_driver.run_pagerank()
		rankings = rank_driver.get_pagerank(testData.keys())
		end = time.time()
		assert (end-start) < 1

if __name__ == '__main__':
	unittest.main()