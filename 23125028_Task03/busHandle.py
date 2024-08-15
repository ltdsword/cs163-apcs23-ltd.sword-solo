import json
from math import*
from lxml import etree
import osmium as osm
from HCMGraph import*
from collections import defaultdict
from spawnMap import*
import time as times

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
        HCMGraph.__init__(self)
        self.matrix = defaultdict(dict) # adjacency list of the graph
        self.busRoute = defaultdict(dict)
        self.filename = filename
        self.importData('nodes.json', 'ways.json', 'relations.json')
        self.edges = defaultdict(lambda: 0)
        self.loadGraph(filename)
    
    def loadGraph(self, filename):
        maxlen = 0
        minlen = 0
        count = 0
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                cur = times.time()
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
                    # just for counting
                    maxlen = max(maxlen, len(edges))
                    minlen = min(minlen, len(edges))
                    count += 1
                    # hash the edges to tuple
                    edges = list(map(tuple, edges))
                    # brute force to add the edges to the matrix
                    for i in range(len(edges)-1):
                        self.edges[edges[i]] += 1
                        for j in range(i+1, len(edges)):
                            for k in range(i+1, j):
                                if (k not in self.matrix[(edges[i], edges[j])]):
                                    self.matrix[(edges[i], edges[j])][k] = 1
                                else:
                                    self.matrix[(edges[i], edges[j])][k] += 1
                                if ('max' not in self.matrix[(edges[i], edges[j])]):
                                    self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
                                else:
                                    if (self.matrix[(edges[i], edges[j])][k] > self.matrix[(edges[i], edges[j])]['max'][1]):
                                        self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
                    if (len(edges) > 0): self.edges[edges[-1]] += 1
                print(f"Done with bus {vehicleNumber} in {times.time() - cur} seconds")
        print(f"Max length: {maxlen}, Min length: {minlen}")
        print(f"Number of trip: {count}")
                        
    def combine(self, u):
        # combine the edges of the node u
        # u is a tuple of 2 node (a, b)
        return f"{u[0]}-{u[1]}"
    
    def decryption(self, u):
        # decryption the edges of the node u
        # u is a string of 2 node "a-b"
        return tuple(map(int, u.split('-')))

    def combine2(self, u, v):
        # combine the edges of the node u and v
        # u and v is a tuple of 2 node (a, b)
        return self.combine(u) + "," + self.combine(v)
    
    def combine2String(self, u, v):
        return u + "," + v

    def split(self, u):
        # split the edges of the node u
        # u is a string of 2 node "a-b,c-d"
        return list(map(self.decryption, u.split(',')))
    
    def outputMatrix(self):
        #process the matrix to output as a json file
        # change the key in the matrix to string
        matrix = {}
        for key in self.matrix:
            matrix[self.combine2(key[0], key[1])] = self.matrix[key]
            for k in self.matrix[key]:
                if (k != 'max'):
                    matrix[self.combine2(key[0], key[1])][self.combine(k)] = self.matrix[key][k]
        
        with open('busMatrix.json', 'w', encoding='utf8') as outfile:
            json.dump(matrix, outfile, ensure_ascii=False)
    
    def outputEdgeMatrix(self):
        # process the edges to output as a json file
        mat = {}
        # decrypt the edges
        # for key in self.edges:
        #     edges.append(self.decryption(key))
        edges = list(self.edges.keys())
        result = {"edges": edges}
        for i in range(len(edges)):
            temp = []
            for j in range(len(edges)):
                if ((edges[i], edges[j]) in self.matrix):
                    temp.append(self.matrix[(edges[i], edges[j])]['max'][0])
                else:
                    temp.append("null")
            mat[self.combine(edges[i])] = temp
        result["matrix"] = mat
        with open('busEdgeMatrix.json', 'w', encoding='utf8') as outfile:
            json.dump(result, outfile, ensure_ascii=False)
            
        


obj = BusGraph('bus-history.json')
obj.outputMatrix()
obj.outputEdgeMatrix()       

