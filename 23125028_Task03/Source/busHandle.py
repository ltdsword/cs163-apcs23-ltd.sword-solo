import json
from math import*
from lxml import etree
import osmium as osm
from HCMGraph import*
from collections import defaultdict
from spawnMap import*
import time as times
from itertools import combinations

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
    def __init__(self, filename, mode = 0):
        HCMGraph.__init__(self)
        self.matrix = defaultdict(dict)
        self.busRoute = defaultdict(dict)
        self.filename = filename
        self.importData('Result/nodes.json', 'Result/ways.json', 'Result/relations.json')
        self.edges = defaultdict(lambda: 0)
        if (mode == 0): self.load(filename)
        else: self.load2(filename)
    
    def process(self, route, var):
        tripList = self.busRoute[(route, var)]['tripList']
        for trip in tripList:
            sub = times.time()
            edges = trip['edgesOfPath2']
            # # just for counting
            # maxlen = max(maxlen, len(edges))
            # minlen = min(minlen, len(edges))
            # count += 1
            # hash the edges to tuple
            edges = list(map(tuple, edges))
            # brute force to add the edges to the matrix
            for i in range(len(edges)-1):
                self.edges[edges[i]] += 1
                for j in range(i+1, len(edges)):
                    for k in range(i+1, j):
                        if (self.matrix[(edges[i], edges[j])].get(k) == None):
                            self.matrix[(edges[i], edges[j])][k] = 1
                        else:
                            self.matrix[(edges[i], edges[j])][k] += 1
                        if (self.matrix[(edges[i], edges[j])].get('max') == None):
                            self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
                        else:
                            if (self.matrix[(edges[i], edges[j])][k] > self.matrix[(edges[i], edges[j])]['max'][1]):
                                self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
            if (len(edges) > 0): self.edges[edges[-1]] += 1
            print(f"Done with trip in {times.time() - sub} seconds with {len(edges)} edges")
        
    
    def load(self, filename): # this approach consumes way too much memory
        # estimate memory: O(N*N*N/2) => about 40GB RAM needed
        # maxlen = 0
        # minlen = 0
        count = 0
        with open ('InputFiles/busEdges.json', 'r', encoding='utf8') as outfile:
            data = json.load(outfile)
            for key in data:
                self.edges[self.decryption(key)] = data[key]
        self.listEdges = list(self.edges.keys())
        for i in range(len(self.listEdges)):
            self.edges[self.listEdges[i]] = i
        with open(filename, 'r', encoding='utf8') as f:
            for line in f:
                cur = times.time()
                data = json.loads(line, strict=False)
                tripList = data['tripList']
                count += 1
                for trip in tripList:
                    sub = times.time()
                    edges = trip['edgesOfPath2']
                    # # just for counting
                    # maxlen = max(maxlen, len(edges))
                    # minlen = min(minlen, len(edges))
                    # count += 1
                    # hash the edges to tuple
                    edges = list(map(tuple, edges))
                    # convert the edges to the index in listEdges for faster processing
                    for i in range(len(edges)):
                        edges[i] = self.edges[edges[i]]
                    # brute force to add the edges to the matrix
                    for i in range(len(edges)-1):
                        self.edges[edges[i]] += 1
                        for j in range(i+1, len(edges)):
                            for k in range(i+1, j):
                                if (self.matrix[(edges[i], edges[j])].get(edges[k]) == None):
                                    self.matrix[(edges[i], edges[j])][edges[k]] = 1
                                else:
                                    self.matrix[(edges[i], edges[j])][edges[k]] += 1
                                # if (self.matrix[(edges[i], edges[j])].get('max') == None):
                                #     self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
                                # else:
                                #     if (self.matrix[(edges[i], edges[j])][k] > self.matrix[(edges[i], edges[j])]['max'][1]):
                                #         self.matrix[(edges[i], edges[j])]['max'] = [k, self.matrix[(edges[i], edges[j])][k]]
                    #if (len(edges) > 0): self.edges[edges[-1]] += 1
                    # print(f"Done with trip in {times.time() - sub} seconds with {len(edges)} edges")
                print(f"Done with line {count} in {times.time() - cur} seconds")
        # print(f"Max length: {maxlen}, Min length: {minlen}")
        # print(f"Number of trip: {count}")
    
    # another approach to load the data
    def load2(self, filename):
        # estimate memory: O(N*N) = 3.81GB RAM needed
        cur = times.time()
        index = 0
        self.tripDict = defaultdict(dict)
        self.tripArr = []
        # load edges
        with open ('InputFiles/busEdges.json', 'r', encoding='utf8') as outfile:
            data = json.load(outfile)
            for key in data:
                self.edges[self.decryption(key)] = data[key]
        self.listEdges = list(self.edges.keys())
        for i in range(len(self.listEdges)):
            self.edges[self.listEdges[i]] = i
        with open(filename, 'r', encoding = 'utf8') as outfile:
            for line in outfile:
                data = json.loads(line, strict=False)
                # vehicleNumber = data['vehicleNumber']
                # routeId = int(data['routeId'])
                # varId = int(data['varId'])
                tripList = data['tripList']
                for trip in tripList:
                    edges = trip['edgesOfPath2']
                    edges = list(map(tuple, edges))
                    # convert the edges to the index in listEdges for faster processing
                    for i in range(len(edges)):
                        edges[i] = self.edges[edges[i]]
                    self.tripArr.append(edges)
                    for i in range(len(edges)):
                        self.tripDict[edges[i]][index] = i
                    index += 1 # index of the edge of path
        print(f"Done loading in {times.time() - cur} seconds")
        cur = times.time()
        n = len(self.listEdges)
        print(f"Number of edges: {n}") 
        # brute force to add the edges to the matrix
        # for i in range(n):
        #     for j in range(i+1, n):
        #         freq = defaultdict(lambda: 0)
        #         freq2 = defaultdict(lambda: 0)
        #         for key in self.tripDict[j]:
        #             if (self.tripDict[i].get(key) != None): 
        #                 a = self.tripDict[i][key]
        #                 b = self.tripDict[j][key]
        #                 if (a < b):
        #                     for k in range(a+1, b):
        #                         freq[self.tripArr[key][k]] += 1
        #                 else:
        #                     for k in range(b+1, a):
        #                         freq2[self.tripArr[key][k]] += 1    
        #         # compute the max frequency
        #         maxFreq = [(-1, -1), 0]
        #         for key in freq:
        #             if (freq[key] > maxFreq[1]):
        #                 maxFreq = [key, freq[key]]
        #         if (maxFreq[1] != 0):
        #             self.matrix[(i,j)] = maxFreq
        #         else :
        #             self.matrix[(i,j)] = "null"
        #         maxFreq = [(-1, -1), 0]
        #         for key in freq2:
        #             if (freq2[key] > maxFreq[1]):
        #                 maxFreq = [key, freq2[key]]
        #         if (maxFreq[1] != 0):
        #             self.matrix[(j,i)] = maxFreq
        #         else:
        #             self.matrix[(j,i)] = "null"
        #     print(f"Done with edge {i} in {times.time() - cur} seconds")
        #    self.loadMatrix()
        # self.queryRange(0, n)
                
                    
    def query1Pair(self, edge1, edge2, d = {}):
        # find the common index of the two edges
        # edge1 and edge2 are tuple of 2 nodes
        freq = defaultdict(lambda: 0)
        for i in self.tripDict[edge2]:
            if (d.get(i) != None): 
                a = self.tripDict[edge1][i]
                b = self.tripDict[edge2][i]
                for k in range(a+1, b):
                    freq[self.tripArr[i][k]] += 1
        # compute the max frequency
        maxFreq = [(-1, -1), 0]
        for key in freq:
            if (freq[key] > maxFreq[1]):
                maxFreq = [key, freq[key]]
        return maxFreq[0]

    def queryRange(self, left, right):
        # query from the range of [left...right]
        # brute force to add the edges to the matrix
        n = len(self.listEdges)
        for i in range(left, right):
            sub = times.time()
            for j in range(i+1, n):
                a = -1
                b = -1
                freq = defaultdict(lambda: 0)
                freq2 = defaultdict(lambda: 0)
                for key in self.tripDict[j]:
                    if (self.tripDict[i].get(key) != None): 
                        a = self.tripDict[i][key]
                        b = self.tripDict[j][key]
                        if (a < b):
                            for k in range(a+1, b):
                                freq[self.tripArr[key][k]] += 1
                        else:
                            for k in range(b+1, a):
                                freq2[self.tripArr[key][k]] += 1    
                # compute the max frequency
                if (a != -1 and b != -1):
                    maxFreq = [(-1, -1), 0]
                    for key in freq:
                        if (freq[key] > maxFreq[1]):
                            maxFreq = [key, freq[key]]
                    if (maxFreq[1] != 0):
                        self.matrix[i][j] = maxFreq
                    else :
                        self.matrix[i][j] = "null"
                    maxFreq = [(-1, -1), 0]
                    for key in freq2:
                        if (freq2[key] > maxFreq[1]):
                            maxFreq = [key, freq2[key]]
                    if (maxFreq[1] != 0):
                        self.matrix[j][i] = maxFreq
                    else:
                        self.matrix[j][i] = "null"
            print(f"Done with edge {i} in {times.time() - sub} seconds")
        self.outputMatrix()
        
                
        
    def combine(self, u):
        # combine the edges of the node
        # u is a tuple of 2 node (a, b)
        return f"{u[0]}-{u[1]}"
    
    def decryption(self, u):
        # decryption the edges of the node u
        # u is a string of 2 node "a-b"
        return tuple(map(str, u.split('-')))

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
    
    def outputEdges(self):
        # output the edges of the graph
        edges = {}
        cnt = 0
        for key in self.edges:
            edges[self.combine(key)] = self.edges[key]
            cnt += 1
        with open('Result/busEdges.json', 'w', encoding='utf8') as outfile:
            json.dump(edges, outfile, ensure_ascii=False)
        print(f"Number of edges: {cnt}")
    
    def outputMatrix(self):
        with open('Result/busMatrix.json', 'w', encoding='utf8') as outfile:
            json.dump(self.matrix, outfile, ensure_ascii=False)
    
    def outputEdgeMatrix(self):
        # process the edges to output as a json file
        mat = {}
        # decrypt the edges
        # for key in self.edges:
        #     edges.append(self.decryption(key))
        edges = list(self.listEdges)
        result = {"edges": self.listEdges}
        for i in range(len(edges)):
            temp = []
            for j in range(len(edges)):
                if ((edges[i], edges[j]) in self.matrix):
                    temp.append(self.matrix[(edges[i], edges[j])]['max'][0])
                else:
                    temp.append("null")
            mat[self.combine(edges[i])] = temp
        result["matrix"] = mat
        with open('Result/busEdgeMatrix.json', 'w', encoding='utf8') as outfile:
            json.dump(self.matrix, outfile, ensure_ascii=False)
            
    def loadMatrix(self):
        with open('Result/busMatrix.json', 'r', encoding='utf8') as outfile:
            self.matrix = json.load(outfile)
            
        


obj = BusGraph('Result/bus-history.json', mode = 1)
obj.outputEdges()

