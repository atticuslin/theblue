# see https://neo4j.com/docs/api/python-driver/1.7/

from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
auth=("neo4j", "password")


'''
Interface to querying Neo4j
'''
class Driver(object):

    '''
    Initialize the Neo4j Python driver
    driver is only used internally, stored in attribute _driver
    '''
    def __init__(self):
        self._driver = GraphDatabase.driver(uri, auth=auth)
