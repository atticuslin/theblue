import unittest
import random

from app import url_exists, update, get_next_crawl

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

	def test_url_not_exists():
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
	def test_many_insertions(self):
		testData = generateTestData(100)
		for docid in testData:
			update(docid, testData[docid]["url"], testData[docid]["out_links"])
			assert url_exists(testData[docid]["url"])

	# TODO: finish this once we have get_url
	def test_update_out_links(self):
		update("0", "https://www.site-0.com", [])
		assert url_exists("https://www.site-0.com")



# tests get_next_crawl function
class TestGetNextCrawl(unittest.TestCase):

	# tests when there should be no more links to crawl
	def test_no_crawl_links(self):
		assert len(get_next_crawl()) == 0

	# tests when there should be one link to crawl next
	def test_one_crawl_link(self):
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		next_crawl = get_next_crawl()
		assert len(next_crawl) == 1
		assert next_crawl[0] == "https://www.site-1.com"

	# tests that the urls are removed from the queue when returned
	def test_urls_removed(self):
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		get_next_crawl()
		next_crawl = get_next_crawl()
		assert len(next_crawl) == 0

	# tests that outlinks from separate links are all added to the queue properly
	def test_several_links():
		update("0", "https://www.site-0.com", ["https://www.site-1.com", "https://www.site-2.com"])
		update("0", "https://www.site-3.com", ["https://www.site-4.com", "https://www.site-5.com"])
		assert len(get_next_crawl()) == 4

	# tests if a link that is in the queue is updated then it should be removed
	def test_follow_up_links():
		update("0", "https://www.site-0.com", ["https://www.site-1.com"])
		update("0", "https://www.site-1.com", ["https://www.site-2.com", "https://www.site-3.com"])
		assert len(get_next_crawl()) == 2

	# tests if an outlink from 2 different sites overlap it doesn't get added twice
	def test_overlap_links():
		update("0", "https://www.site-0.com", ["https://www.site-2.com"])
		update("0", "https://www.site-1.com", ["https://www.site-2.com", "https://www.site-3.com"])
		assert len(get_next_crawl()) == 2

		


if __name__ == '__main__':
	unittest.main()