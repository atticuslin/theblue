# see https://neo4j.com/docs/api/python-driver/1.7/
from typing import List
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
auth=("neo4j", "test")


'''
Class for getting cypher query strings
'''
class QueryString():
    
    '''
    Query string for updating the webgraph
    Cypher params: $url, $outlinks
    '''
    update = (
        "MERGE (n:Page {url: $url})\n"
        "SET n.visited = true\n"
        "WITH n\n"
        "OPTIONAL MATCH (n)-[old:LINKSTO]->()\n"
        "DELETE old\n"
        "FOREACH (o IN $outlinks |\n"
        "    MERGE (outlink:Page {url: o})\n"
        "    MERGE (n)-[:LINKSTO]->(outlink)\n"
        ")\n"
    )
    
    
    '''
    Query string for running and writing the pagerank algorithm
    '''
    update_pagerank = (
        "CALL algo.pageRank("
        "'MATCH (p:Page) WHERE p.visited RETURN id(p) as id', "
        "'MATCH (p1:Page)-[:LINKSTO]->(p2:Page) WHERE p2.visited RETURN id(p1) as source, id(p2) as target', "
        "{graph: 'cypher', iterations:20, dampingFactor:0.85, "
        "write: true, writeProperty:'pagerank'})\n"
    )
    

    '''
    Query string for getting pagerank values
    Cypher params: $urls
    '''
    get_pagerank = (
        "MATCH (n:Page)\n"
        "WHERE n.url IN $urls\n"
        "RETURN n.url, n.pagerank\n"
    )
    
    
    '''
    Query string for getting a page's outlinks
    For testing only
    Cypher params: $url
    '''
    get_outlinks = (
        "MATCH (:Page {url: $url})-->(out)\n"
        "RETURN out.url\n"
    )
    
    
    '''
    Query string for deleting the entire webgraph
    For testing only
    '''
    delete_graph = (
        "MATCH (n)\n"
        "DETACH DELETE n\n"
    )
    
    

'''
Interface to querying Neo4j
'''
class Driver():

    '''
    Initialize the Neo4j Python driver
    '''
    def __init__(self):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        with self.driver.session() as session:
            session.run("CREATE INDEX ON :Page(url)")
            session.run("CREATE CONSTRAINT ON (n:Page) ASSERT n.url IS UNIQUE")
    
        self.profile = False
    
    
    '''
    Run a cypher query string
    @param query_string query string to run
    @param parameters dictionary of parameters for query
    @return result of query
    '''
    def run_cypher(self, 
                   query_string: str, 
                   parameters=None):
        # add profile to query string
        if self.profile:
            query_string = "PROFILE\n" + query_string
        # create new session and transaction
        with self.driver.session() as session:
            result = session.run(query_string, parameters=parameters)
        # print profile results
        if self.profile:
            summary = result.summary()
            print(f"{summary.statement}")
            print(f"  {summary.result_available_after}")
            print(f"  {summary.result_consumed_after}")
        return result
    
    
    '''
    Update the webgraph
    @param url URL of base node to update
    @param outlinks list of outlinks of base node
    '''
    def update(self, url: str, outlinks: List[str]):
        self.run_cypher(QueryString.update,
                        parameters={"url": url,
                                    "outlinks": outlinks})


    '''
    Run pagerank and write value to graph
    '''
    def run_pagerank(self):
        self.run_cypher(QueryString.update_pagerank)
    
    
    '''
    Get pagerank values for urls
    @param urls list of urls to get pagerank values for
    @return list with dict of url, pagerank values for each url in urls
    '''
    def get_pagerank(self, urls: List[str]):
        result = self.run_cypher(QueryString.get_pagerank,
                                 parameters={"urls": urls})
        return result.data()

    
    '''
    Get the outlinks of a url
    For testing only
    @param url URL to get outlinks of
    '''
    def get_outlinks(self, url: str):
        result = self.run_cypher(QueryString.get_outlinks,
                                 parameters={"url": url})
        return result.data()
    
    
    '''
    Delete the entire webgraph
    For testing only
    '''
    def delete_graph(self):
        assert(auth[1] == "test")
        self.run_cypher(QueryString.delete_graph)



def example_test():
    driver = Driver()
    driver.delete_graph()
    driver.update('a', ['b', 'c'])
    driver.update('b', ['d', 'a'])
    driver.update('c', ['e', 'b'])
    
    print(driver.get_outlinks('a'))
    
    driver.run_pagerank()
    print(driver.get_pagerank(['a', 'b', 'c', 'd']))


if __name__ == "__main__":
    example_test()
