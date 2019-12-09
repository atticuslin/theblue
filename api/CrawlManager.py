from typing import Union, List

'''
Class for managing crawled links
'''
class CrawlManager():
    
    '''
    Initialize the crawl manager
    @param driver neo4j interface class
    '''
    def __init__(self, driver):
        self.done = False
        self.driver = driver
        self.init()
    
    
    '''
    (Re)initialize the uncrawled URL data structures and index
    '''
    def init(self):
        # get list of uncrawled URLs from neo4j
        self.url_list = self.driver.get_uncrawled_urls()
        self.url_set = set(self.url_list)
        self.idx = 0
        # if all URLs have been crawled
        if len(self.url_list) == 0:
            self.done = True
    
    
    '''
    Add new uncrawled url(s)
    @param urls URL or list of URLs to add
    '''
    def add(self, urls: Union[str, List[str]]):
        if isinstance(urls, str):
            urls = {urls}
        elif isinstance(urls, list):
            urls = set(urls)
        else:
            raise TypeError
        # add new urls to set and list
        self.url_list += list(urls - self.url_set)
        self.url_set |= urls
    
    
    '''
    Get the next uncrawled URL
    @return next uncrawled URL or None if all URLs have been crawled
    '''
    def get_next_url(self):
        # if index is out of range, reinitialize
        if self.idx >= len(self.url_list):
            self.init()
        # if there are no more uncrawled URLs
        if self.done:
            return None
        # get the next url
        res = self.url_list[self.idx]
        self.idx += 1
        return res
