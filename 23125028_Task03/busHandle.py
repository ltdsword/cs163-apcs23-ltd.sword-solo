import json
from math import*
from lxml import etree
import osmium as osm
from HCMGraph import*
from collections import defaultdict

# handle the bus-history.json file

# description of the file
# each line is a json object, contains:
# vehicleNumber: the number of the bus
# routeId, varId: the route and variant of the bus
# tripList: a list of trips, each trip contains:
### [{
###   "timeStamp": the time the trip started,
###   "edgesOfPath2": [node id 1, node id 2], [node id 3, node id 4], ..., [node id n-1, node id n]
### }, ...]

# create a class to handle the bus-history.json file
# inherit from the map in HCMGraph.py

class BusGraph(HCMGraph):
    def __init__(self, filename):
        self.graph = defaultdict(list) # adjacency list of the graph
        self.busRoute = defaultdict(dict)
        self.filename = filename
        self.loadGraph(filename)
    
    def loadGraph(self, filename):
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                data = json.loads(line, strict=False)
                vehicleNumber = data['vehicleNumber']
                routeId = data['routeId']
                varId = data['varId']
                tripList = data['tripList']
                self.busRoute[vehicleNumber] = {
                    'routeId': routeId,
                    'varId': varId,
                    'tripList': tripList
                }
                for trip in tripList:
                    edges = trip['edgesOfPath2']
                    for i in range(len(edges)):
                        u, v = edges[i][0], edges[i][1]
                        # since we have default dict, we don't need to check if u, v is in the graph
                        self.graph[u].append(v)
                        self.graph[v].append(u)
    
    def outputAsJSON(self):
        with open('busGraph.json', 'w', encoding='utf8') as f:
            json.dump(self.graph, f, ensure_ascii=False)


obj = BusGraph('bus-history.json')
obj.importData('nodes.json', 'ways.json', 'relations.json')
obj.outputAsJSON()