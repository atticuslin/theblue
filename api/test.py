import unittest
import random
import queries

################################################################################################
#																		Test Drivers Creation																			 #
#																																															 #
#	- general drivers to use in tests, some tests create their own drivers because they edit the #
#			webgraph in irreversible ways																														 #
################################################################################################

# empty driver for testing
empty_driver = queries.Driver()

# driver with a single node with no outlinks for testing
solo_node_driver = queries.Driver()
solo_node_driver.update('0', "https://www.site-0.com", [])

# driver with a single node with no outlinks for testing
single_node_driver = queries.Driver()
single_node_driver.update('0', "https://www.site-0.com", ["https://www.site-1.com", "https://www.site-2.com"])

# driver with various nodes all connected for testing
multi_node_driver = queries.Driver()
multi_node_driver.update('0', "https://www.site-0.com", ["https://www.site-1.com", "https://www.site-2.com", "https://www.site-3.com"])
multi_node_driver.update('1', "https://www.site-1.com", ["https://www.site-2.com"])
multi_node_driver.update('2', "https://www.site-2.com", ["https://www.site-0.com"])
multi_node_driver.update('3', "https://www.site-3.com", [])

################################################################################################
#																		Helper Functions																					 #
################################################################################################

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
		assert len(update_driver.get_out_links("https://www.site-0.com")) == 0
		update_driver.update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		assert len(update_driver.get_out_links("https://www.site-0.com")) == 1

	# tests updating and removing out links
	def test_remove_out_links(self):
		update_driver = queries.Driver()
		update_driver.update("1", "https://www.site-1.com", ["https://www.site-2.com"])
		assert len(update_driver.get_out_links("https://www.site-0.com")) == 1
		update_driver.update("1", "https://www.site-1.com", [])
		assert len(update_driver.get_out_links("https://www.site-0.com")) == 0

	# tests updating 100 links just to make sure it can handle it
	def test_update_load(self):
		update_driver = queries.Driver()
		testData = generateTestData(100)
		for docid in testData:
			update_driver.update(docid, testData[docid]["url"], testData[docid]["out_links"])
			assert url_exists(testData[docid]["url"])
		updateData = generateTestData(100)
		for docid in updateData:
			update_driver.update(docid, updateData[docid]["url"], updateData[docid]["out_links"])
			assert len(get_out_links(updateData[docid]["url"])) == len(updateData[docid]["out_links"])


# tests get_next_crawl function
class TestGetNextCrawl(unittest.TestCase):

	# tests an empty driver to make sure there is no links to crawl
	def test_empty(self):
		assert len(empty_driver.get_next_crawl()) == 0

	# tests when there should be some out links
	def test_some(self):
		assert len(single_node_driver.get_next_crawl()) == 2

	# tests to make sure links are removed properly
	def test_removal(self):
		get_crawl_driver = queries.Driver()
		get_crawl_driver.update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		assert len(get_crawl_driver.get_next_crawl()) == 1
		get_crawl_driver.update("1", "https://www.site-1.com", [])
		assert len(get_crawl_driver.get_next_crawl()) == 0

	# tests that links to crawl are added properly
	def test_addition(self):
		get_crawl_driver = queries.Driver()
		get_crawl_driver.update('0', "https://www.site-0.com", [])
		assert len(get_crawl_driver.get_next_crawl()) == 0
		get_crawl_driver.update('0', "https://www.site-0.com", ["https://www.site-1.com", "https://www.site-2.com"])
		assert len(get_crawl_driver.get_next_crawl()) == 2

	# tests if an outlink from 2 different sites overlap it doesn't get added twice
	def test_overlap_links(self):
		get_crawl_driver = queries.Driver()
		get_crawl_driver.update("0", "https://www.site-0.com", ["https://www.site-2.com"])
		assert len(get_crawl_driver.get_next_crawl()) == 1
		get_crawl_driver.update("0", "https://www.site-1.com", ["https://www.site-2.com", "https://www.site-3.com"])
		assert len(get_crawl_driver.get_next_crawl()) == 2

# tests get_next_crawl function
class TestRank(unittest.TestCase):

	# tests ranking empty graph
	def test_empty(self):
		assert len(empty_driver.rank([])) == 1

	# tests ranking one link
	def test_single(self):
		assert len(single_node_driver.rank(["https://www.site-0.com"])) == 1

	# tests ranking multiple links
	def test_multi(self):
		assert len(multi_node_driver.rank(["https://www.site-0.com","https://www.site-1.com", "https://www.site-2.com", "https://www.site-3.com"])) == 4

	def test_unknown_url(self):
		rankings = multi_node_driver.rank(["https://www.site-100.com"])
		assert len(rankings) == 1
		assert rankings["https://www.site-0.com"] == 0

if __name__ == '__main__':
	unittest.main()