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
        self.importData('Result/nodes.json', 'Result/ways.json', 'Result/relations.json')
        self.edges = []
        self.listEdges = []
        self.totalEdges = []
        self.loadWay('Result/intersections.json')
        if (mode == 0): self.loadMatrix(filename)
        else:
            self.load(filename)
        
    def loadWay(self, filename):
        self.interDict = defaultdict(list)
        for wayid in self.ways:
            way = self.ways[wayid]
            tag = way['tags']
            nodes = way['nodes']
            if (tag.get('highway') != None):
                self.listEdges.append([nodes[0], nodes[-1]])
                if (tag.get('oneway') == None or tag['oneway'] == 'no'):
                    self.listEdges.append([nodes[-1], nodes[0]])
                for i in range(0, len(nodes)): 
                    self.interDict[nodes[i]].append([nodes[0], nodes[-1], i])
        
        # map the listEdge for easier access
        self.listEdges = list(map(tuple, self.listEdges))
        self.totalEdges = self.listEdges
        print(f"Length of listEdges: {len(self.listEdges)}")
        self.mapEdges = {}
        for i in range(len(self.listEdges)):
            self.mapEdges[self.listEdges[i]] = i
        print(f"Length of mapEdges: {len(self.mapEdges)}")
        
    def findEdge(self, u):
        # find the common intersection of the edge
        # u is a tuple of 2 node (a, b)
        a = self.interDict[u[0]]
        b = self.interDict[u[1]]
        for i in range(len(a)):
            for j in range(len(b)):
                if (a[i][0] == b[j][0] and a[i][1] == b[j][1]):
                    if (a[i][2] < b[j][2]):
                        if (self.mapEdges.get((a[i][0], a[i][1])) != None) :return (a[i][0], a[i][1])
                    else:
                        if (self.mapEdges.get((a[i][1], a[i][0])) != None): return (a[i][1], a[i][0])
        
    # another approach to load the data
    def load(self, filename):
        cur = times.time()
        index = 0
        self.tripArr = []
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
                    self.tripArr.append(edges)
            # split the list: 1,2,3,4,5,1,2,3 => [1,2,3,4,5], [1,2,3]
            for e in range(len(self.tripArr)):
                dictt = defaultdict(lambda: 0)
                for i in range(len(self.tripArr[e])):
                    dictt[self.tripArr[e][i]] += 1
                    if (dictt[self.tripArr[e][i]] == 2):
                        # break the list into 2 parts
                        self.tripArr.append(self.tripArr[e][i:])
                        self.tripArr[e] = self.tripArr[e][:i]
                        break
                #print(f"Processing trip {e}")
            print(f"Size of the tripArr: {len(self.tripArr)}")
   
        self.edges = []
        self.listEdges = set()
        for trip in self.tripArr:
            temp = []
            for i in range (len(trip)):
                inter = self.mapEdges[self.findWay(trip[i])]
                self.listEdges.add(inter)
                if (len(temp) != 0):
                    if (temp[-1] != inter):
                        temp.append(inter)
                else:
                    temp.append(inter)
            self.edges.append(temp)
        self.listEdges = list(self.listEdges)
        self.listEdges.sort()
        print(f"Length of listEdges: {len(self.listEdges)}")
        print(f"Done loading in {times.time() - cur} seconds")
        
        with open('Result/edges.json', 'w', encoding='utf8') as outfile:
            json.dump(self.edges, outfile, ensure_ascii=False)
        
        cur = times.time()
        
        self.tripDict = defaultdict(dict)
        # tripDict processing
        # tripDict structure: tripDict[node][edge] = index
        for i in range(len(self.edges)):
            for j in range(len(self.edges[i])):
                self.tripDict[self.edges[i][j]][i] = j
        
        # process...
        self.process()
        print(f"Done processing in {times.time() - cur} seconds")
                
    def process(self):
        n = len(self.listEdges)
        for li in range(n):
            sub = times.time()
            for lj in range(li+1, n):
                i = self.listEdges[li]
                j = self.listEdges[lj]
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
                                freq[self.edges[key][k]] += 1
                        else:
                            for k in range(b+1, a):
                                freq2[self.edges[key][k]] += 1    
                # compute the max frequency
                if (a != -1 and b != -1):
                    maxFreq = [-1, 0]
                    for key in freq:
                        if (freq[key] > maxFreq[1]):
                            maxFreq = [key, freq[key]]
                    if (maxFreq[1] != 0):
                        self.matrix[i][j] = maxFreq
                    maxFreq = [-1, 0]
                    for key in freq2:
                        if (freq2[key] > maxFreq[1]):
                            maxFreq = [key, freq2[key]]
                    if (maxFreq[1] != 0):
                        self.matrix[j][i] = maxFreq
            print(f"Done with edge {i} ({li}) in {times.time() - sub} seconds")
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
    
    def query(self, listEdges):
        # input = a list of edges [[node1, node2], [node3, node4], ...]
        # output = the corresponding row in the matrix
        cur = times.time()
        for i in range(len(listEdges)):
            listEdges[i] = (listEdges[i][0], listEdges[i][1])
        result = []
        for i in range(len(listEdges)):
            index = self.mapEdges[self.findWay(listEdges[i])]
            temp = []
            for j in range(len(self.listEdges)):
                if (self.matrix[index].get(self.listEdges[j]) == None):
                    temp.append(None)
                else:
                    #print(self.matrix[index][self.listEdges[j]][0])
                    temp.append(self.totalEdges[self.matrix[index][self.listEdges[j]][0]])
            result.append(temp)
        
        # output the result
        with open('Result/query.json', 'w', encoding='utf8') as outfile:
            for i in range(len(result)):
                json.dump({'edges': listEdges[i] ,'row': result[i]}, outfile, ensure_ascii=False)
                outfile.write('\n')
        
        print(f"Done query in {times.time() - cur} seconds")
            
    
    def outputMatrix(self):
        mapEdges = {}
        for i in self.mapEdges:
            mapEdges[self.combine(i)] = self.mapEdges[i]
        dict = {
            "mapEdges": mapEdges,
            "listEdges": self.listEdges,
            "matrix": self.matrix
        }
        with open('Result/busMatrix.json', 'w', encoding='utf8') as outfile:
            json.dump(dict, outfile, ensure_ascii=False)
            
    def loadMatrix(self, filename):
        with open(filename, 'r', encoding='utf8') as outfile:
            data = json.load(outfile)
            self.listEdges = data['listEdges']
            mapEdges = data['mapEdges']
            matrix = data['matrix']
        
        self.matrix = {}
        for i in matrix:
            self.matrix[int(i)] = {}
            for j in matrix[i]:
                self.matrix[int(i)][int(j)] = matrix[i][j]
        self.mapEdges = {}
        for i in mapEdges:
            self.mapEdges[self.decryption(i)] = mapEdges[i]
        print(f"Length of total: {len(self.totalEdges)}")
            


# obj = BusGraph('InputFiles/bus-history.json', mode = 1)
obj = BusGraph('Result/busMatrix.json', mode = 0)
obj.query([['5738158912', '373543511'], ["696860148","366479091"], ["366415838","366426086"]])
