from math import*
from crs import*
from collections import defaultdict
from queue import PriorityQueue
import heapq
import json
import time as times
# file
from graph import*
from aStarSearch import*
from path import*
from routevar import*
from stop import*

class Cache:
    def __init__(self) -> None:
       self.graph = Graph()
       self.cache = defaultdict(list)
       self.zones = defaultdict(list)
       # we find the common path between two stops in two different zones, and then save it to the cache

    def caching(self, filename = ""): # filename to save the cache
        # we run all-pair dijkstra to find the shortest path between all pairs of stops
        self.graph.importGraph("Questions/vars.json", "Questions/stops.json", "Questions/paths.json")
        
    def query(self, start = 0, end = 0):
        pass    


# driver code
adj = defaultdict(list)
loadAdjacent(adj, "adjacents.json")
#caching(adj, "cache.json")
