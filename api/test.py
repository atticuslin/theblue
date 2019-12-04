import unittest
import random

from api import exists as url_exists, update, get_next_crawl, get_out_links, rank

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

# tests if the url_exists function works properly
class TestUrlExists(unittest.TestCase):

	def test_url_not_exists(self):
		assert not url_exists("https://www.site-0.com")


# tests if the update function works properly
class TestUpdate(unittest.TestCase):

	# tests adding a single link
	def test_single_insertion(self):
		update("0", "https://www.site-0.com", [])
		assert url_exists("https://www.site-0.com")

	# tests adding two separate links
	def test_two_insertions(self):
		update("0", "https://www.site-0.com", [])
		assert url_exists("https://www.site-0.com")
		assert not url_exists("https://www.site-1.com")
		update("1", "https://www.site-1.com", [])
		assert url_exists("https://www.site-1.com")

	# tests adding 100 links just to make sure it can handle it
	def test_insertion_load(self):
		testData = generateTestData(100)
		for docid in testData:
			update(docid, testData[docid]["url"], testData[docid]["out_links"])
			assert url_exists(testData[docid]["url"])
		for docid in testData:
			assert len(get_out_links(testData[docid]["url"])) == len(testData[docid]["out_links"])


	# tests that out_links are inserted properly
	def test_out_links_insertion(self):
		update("1", "https://www.site-1.com", ["https://www.site-0.com"])
		out_links = get_out_links("https://www.site-1.com")
		assert len(out_links) == 1
		assert out_links[0] == "https://www.site-1.com"

	# tests updating the out_links for a certain node
	def test_update_out_links(self):
		update("1", "https://www.site-1.com", ["https://www.site-0.com"])
		update("2", "https://www.site-2.com", [])
		assert len(get_out_links("https://www.site-1.com")) == 1
		update("1", "https://www.site-1.com", ["https://www.site-0.com", "https://www.site-2.com"])
		out_links = get_out_links("https://www.site-1.com")
		assert len(out_links) == 2
		assert "https://www.site-0.com" in out_links
		assert "https://www.site-2.com" in out_links

	def test_remove_out_links(self):
		update("1", "https://www.site-1.com", ["https://www.site-0.com"])
		assert len(get_out_links("https://www.site-1.com")) == 1
		update("1", "https://www.site-1.com", [])
		assert len(get_out_links("https://www.site-1.com")) == 0

	# tests updating 100 links just to make sure it can handle it
	def test_update_load(self):
		testData = generateTestData(100)
		for docid in testData:
			update(docid, testData[docid]["url"], testData[docid]["out_links"])
			assert url_exists(testData[docid]["url"])
		updateData = generateTestData(100)
		for docid in updateData:
			update(docid, updateData[docid]["url"], updateData[docid]["out_links"])
			assert len(get_out_links(updateData[docid]["url"])) == len(updateData[docid]["out_links"])


# tests get_next_crawl function
class TestGetNextCrawl(unittest.TestCase):

	# tests that we have the default links to start crawling
	def test_default_crawl_links(self):
		assert len(get_next_crawl()) == 5

	# tests when there should be no more links to crawl
	def test_no_crawl_links(self):
		get_next_crawl()	# clear the default starter links
		assert len(get_next_crawl()) == 0

	# tests when there should be one link to crawl next
	def test_one_crawl_link(self):
		get_next_crawl()	# clear the default starter links
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		next_crawl = get_next_crawl()
		assert len(next_crawl) == 1
		assert next_crawl[0] == "https://www.site-1.com"

	# tests that the urls are removed from the queue when returned
	def test_urls_removed(self):
		get_next_crawl()	# clear the default starter links
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		get_next_crawl()
		next_crawl = get_next_crawl()
		assert len(next_crawl) == 0

	# tests that outlinks from separate links are all added to the queue properly
	def test_several_links(self):
		get_next_crawl()	# clear the default starter links
		update("0", "https://www.site-0.com", ["https://www.site-1.com", "https://www.site-2.com"])
		update("0", "https://www.site-3.com", ["https://www.site-4.com", "https://www.site-5.com"])
		assert len(get_next_crawl()) == 4

	# tests if a link that is in the queue is updated then it should be removed
	def test_follow_up_links(self):
		get_next_crawl()	# clear the default starter links
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		update("0", "https://www.site-1.com", ["https://www.site-2.com", "https://www.site-3.com"])
		assert len(get_next_crawl()) == 2

	# tests if an outlink from 2 different sites overlap it doesn't get added twice
	def test_overlap_links(self):
		get_next_crawl()	# clear the default starter links
		update("0", "https://www.site-0.com", ["https://www.site-2.com"])
		update("0", "https://www.site-1.com", ["https://www.site-2.com", "https://www.site-3.com"])
		assert len(get_next_crawl()) == 2

# tests get_next_crawl function
class TestRank(unittest.TestCase):

	# tests ranking one link 
	def test_single(self):
		update("0", "https://www.site-0.com", [])
		assert len(rank(["https://www.site-0.com"])) == 1

	# tests ranking several links 
	def test_many(self):
		testData = generateTestData(10)
		urls = []
		for docid in testData:
			urls.append(testData[docid]["url"])
			update(docid, testData[docid]["url"], testData[docid]["out_links"])
		assert len(rank(urls)) == 10

	# tests ranking an empty list
	def test_empty(self):
		assert len(rank([])) == 0

	def test_unknown_url(self):
		rankings = rank(["https://www.site-0.com"])
		assert len(rankings) == 1
		assert rankings["https://www.site-0.com"] == 0



if __name__ == '__main__':
	unittest.main()