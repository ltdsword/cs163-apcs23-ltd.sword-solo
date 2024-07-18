from math import*
from itertools import*
from collections import*
from heapq import*
import json
import time as times
# files
from path import*
from routevar import*
from stop import*
from crs import*
from graph import*
from aStarSearch import*
from contractionHierarchy import*
from pathCaching import*
from spawnMap import*

start = 3550
end = 3683
adj = defaultdict(list)
loadAdjacent(adj, "adjacents.json")
cach = Cache()
cach.loadCache("cache.json")
ch = ContractionHierarchy({}, mode="file", shortcutFile="CH/shortcuts.json", shcutRouteFile="CH/shcutRoute.json", rankFile="CH/rank.json", adjFile="CH/adj.json")


def runAll(start = 0, end = 0):
    # dijsktra
    dijkstra1P(adj, start, end)
    # aStar
    AStarSearch(adj, start, end, mode = 'display')
    print(f"Contracrtion Hierarchy:")
    # contraction hierarchy
    ch.query(start, end, mode = 'display')
    print("-----------------------------")
    # path caching
    print (f"Path caching (combined with A*):")
    cach.query(start, end)
    print("-----------------------------")
    # path caching combined with CH
    print (f"Path caching (combined with Contracrtion Hierarchy):")
    ch.combineWithCache(start, end, cach, mode = 'display')
    print("-----------------------------")


#driver code
runAll(start, end)