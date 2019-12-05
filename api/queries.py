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
    Cypher params: $doc_id, $url, $outlinks
    '''
    update = (
        "MERGE (n:Page {url: $url})\n"
        "SET n.visited = true\n"
        "SET n.doc_id = $doc_id\n"
        "WITH n\n"
        "OPTIONAL MATCH (n)-[old:LINKSTO]->()\n"
        "DELETE old\n"
        "WITH n\n"
        "UNWIND $outlinks AS o\n"
        "MERGE (outlink:Page {url: o})\n"
        "MERGE (n)-[:LINKSTO]->(outlink)\n"
        "RETURN outlink.url AS url, EXISTS(outlink.visited) AND outlink.visited AS visited\n"
        # "FOREACH (o IN $outlinks |\n"
        # "    MERGE (outlink:Page {url: o})\n"
        # "    MERGE (n)-[:LINKSTO]->(outlink)\n"
        # ")\n"
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
        "WHERE n.doc_id IN $doc_ids\n"
        "RETURN n.doc_id AS doc_id, n.pagerank as pagerank\n"
    )
    
    
    '''
    Query string for getting all visited nodes
    '''
    get_unvisited_urls = (
        "MATCH (n:Page)\n"
        "WHERE NOT EXISTS(n.visited) OR NOT n.visited\n"
        "RETURN n.url AS url\n"
    )
    
    
    '''
    Query string for getting a page's outlinks
    Cypher params: $url
    '''
    get_outlinks = (
        "MATCH (:Page {url: $url})-->(out)\n"
        "RETURN out.url AS url, EXISTS(out.visited) AND out.visited AS visited\n"
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
            session.run("CREATE INDEX ON :Page(doc_id)")
            session.run("CREATE CONSTRAINT ON (n:Page) ASSERT n.url IS UNIQUE")
            session.run("CREATE CONSTRAINT ON (n:Page) ASSERT n.doc_id IS UNIQUE")
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
    @param doc_id document ID of base node to update
    @param url URL of base node to update
    @param outlinks list of outlinks of base node
    @return list of dicts for each outlink node with url and visited keys
    '''
    def update(self, doc_id: str, url: str, outlinks: List[str]):
        result = self.run_cypher(QueryString.update,
                                 parameters={"doc_id": doc_id,
                                             "url": url,
                                             "outlinks": outlinks})
        return result.data()


    '''
    Run pagerank and write value to graph
    '''
    def run_pagerank(self):
        self.run_cypher(QueryString.update_pagerank)
    
    
    '''
    Get pagerank values for doc_ids
    @param doc_ids list of doc_ids to get pagerank values for
    @return dictionary with key for each doc_id, value as pagerank
    '''
    def get_pagerank(self, doc_ids: List[str]):
        result = self.run_cypher(QueryString.get_pagerank,
                                 parameters={"doc_ids": doc_ids})
        data = result.data()
        return {n["doc_id"]: n["pagerank"] for n in data}
    
    
    '''
    Get all unvisited urls
    @return list of unvisited urls
    '''
    def get_unvisited_urls(self):
         result = self.run_cypher(QueryString.get_unvisited_urls)
         return [n["url"] for n in result.data()]
    
    
    '''
    Get the outlinks of a url
    @param url URL to get outlinks of
    @return list of nodes with properties
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
    print(driver.update('0', 'a', ['b', 'c']))
    print(driver.update('1', 'b', ['d', 'a']))
    print(driver.update('2', 'c', ['e', 'b']))
    
    print(driver.get_outlinks('c'))
    
    driver.run_pagerank()
    print(driver.get_pagerank(['0', '1', '2']))
    
    print(driver.get_unvisited_urls())


if __name__ == "__main__":
    example_test()
