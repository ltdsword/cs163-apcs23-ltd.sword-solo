from math import*
from numpy import*
from collections import defaultdict
import json
import time as times
import sys
from queue import PriorityQueue

class Node:
    def __init__(self):
        self.stopId = ""
        self.routeId = ""
        self.varId = ""
        self.timestamp = 0
        self.latx = 0
        self.lngy = 0
        self.nodeType = ""
        self.nodePos = ""
        self.vehicleNumber = ""
    
    def __init__(self, stopId, routeId, varId, timestamp, latx, lngy, nodeType, nodePos, vehicleNumber):
        self.stopId = stopId
        self.routeId = routeId
        self.varId = varId
        self.timestamp = timestamp
        self.nodeType = nodeType
        self.latx = latx
        self.lngy = lngy
        self.nodePos = nodePos
        self.vehicleNumber = vehicleNumber
    
    def __str__(self):
        return str(self.stopId) + "," + str(self.routeId) + "," + str(self.varId) + "," + str(self.timestamp) + "," + str(self.latx) + "," + str(self.lngy) + "," + str(self.nodeType) + "," + str(self.nodePos) + "," + str(self.vehicleNumber)


class Vertex:
    def __init__(self, stopId = "", routeId = "", varId = "", timeStamp = 0):
        self.stopId = stopId
        self.routeId = routeId
        self.varId = varId
        self.timeStamp = timeStamp
    
    def __str__(self):
        return str(self.stopId) + "," + str(self.routeId) + "," + str(self.varId) + "," + str(self.timeStamp)
    
    def decrypt(self, str):
        data = str.split(",")
        self.stopId = data[0]
        self.routeId = data[1]
        self.varId = data[2]
        self.timeStamp = float(data[3])
    
    

class Graph:
    def __init__(self, filename1, filename2, mode= 'default'):
        self.graph = defaultdict(dict)
        self.vertices = defaultdict(lambda: 0)
        self.stops = defaultdict(list)
        self.count = 0
        if (mode == 'default'):
            self.loadData(filename1, '12')
            self.loadData(filename2, '34')
        else:
            self.loadGraph(filename1)
        self.result = defaultdict(dict)
    
    def loadData(self, filename, type):
        # load the data from CSV file
        cur = times.time()
        file = open(filename, "r")
        for line in file:
            self.count += 1
            data = line.split(",")
            # structure of CSV file:
            # stop_id1,route_id1,var_id1,timestamp1,stop_id2,route_id2,var_id2,timestamp2,
            # time_diff,latx1,lngy1,latx2,lngy2,vehicle_number1,vehicle_number2,
            # node_type1,node_type2,node_pos1,node_pos2,edge_pos,edge_type
            time_diff = float(data[8])
            timestamp1 = int(float(data[3]))
            timestamp2 = int(float(data[7]))
            vertex1 = (data[0], data[1], data[2], timestamp1)
            vertex2 = (data[4], data[5], data[6], timestamp2)
            # weight of the edge is number of transfer and time difference between two nodes
            # we prioritize the number of transfer over time difference 
            if (self.graph[vertex1].get(vertex2) == None): self.graph[vertex1][vertex2] = (2, 0)
            if (type == '12'): 
                self.graph[vertex1][vertex2] = min(self.graph[vertex1][vertex2], (0, time_diff))
            else:
                self.graph[vertex1][vertex2] = min(self.graph[vertex1][vertex2], (1, time_diff))
            if (self.count % 50000 == 0): print(f"Processed {self.count} lines in {times.time() - cur} seconds")
        file.close()
    
    def getLenVertices(self):
        return len(self.graph)
    
    def getLenEdges(self):
        leng = 0
        for key in self.graph:
            leng += len(self.graph[key])
        return leng
    
    def str(self, vertex):
        return str(vertex[0]) + "," + str(vertex[1]) + "," + str(vertex[2]) + "," + str(vertex[3])
    def destr(self, str):
        data = str.split(",")
        return (data[0], data[1], data[2], int(float(data[3]))) 

    def outputGraph(self, filename):
        # output as a JSON file
        graph = {}
        for key in self.graph:
            graph[self.str(key)] = {}
            for key2 in self.graph[key]:
                graph[self.str(key)][self.str(key2)] = self.graph[key][key2]
        with open(filename, 'w') as file:
            json.dump(graph, file, ensure_ascii=False)
    
    def loadGraph(self, filename):
        # load the graph from JSON file
        with open(filename, 'r') as file:
            graph = json.load(file)
        self.graph = defaultdict(dict)
        for key in graph:
            vertex1 = self.destr(key)
            self.vertices[vertex1] = 0
            for key2 in graph[key]:
                vertex2 = self.destr(key2)
                self.graph[vertex1][vertex2] = tuple(graph[key][key2])
    
    def loadStopId(self):
        # load the distinct stop id from the graph
        for key in self.graph:
            self.stops[key[0]].append(key) # stop_id, route_id, var_id, timestamp
                
                
    def dijkstra1Stop(self, startStop):
        # perform Dijkstra algorithm to find the shortest path from every start stop to all other stops in all timestamps
        cur = times.time()
        lst = self.stops[startStop]
        dist = defaultdict(lambda: float('inf'))
        trace = defaultdict(lambda: None)
        for start in lst:
            # dist structure = (number of transfer, time difference)
            # timeStart = timestamp of the start point
            # timeEnd = timestamp of the end point
            dist[start] = (0, 0)
            pq = PriorityQueue()
            pq.put((dist[start], start))
            while (not pq.empty()):
                u = pq.get()[1]
                for v in self.graph[u]:
                    if (dist[v] > (dist[u][0] + self.graph[u][v][0], dist[u][1] + self.graph[u][v][1])):
                        dist[v] = (dist[u][0] + self.graph[u][v][0], dist[u][1] + self.graph[u][v][1])
                        pq.put((dist[v], v))
                        trace[v] = u
            
        

    def dijkstra1Vertex(self, start):
        # Dijkstra algorithm to find the shortest path from a start point to all other points
        dist = defaultdict(lambda: float('inf'))
        trace = defaultdict(lambda: None)
        # dist structure = (number of transfer, time difference)
        # timeStart = timestamp of the start point
        # timeEnd = timestamp of the end point
        dist[start] = (0, 0)
        pq = PriorityQueue()
        pq.put((dist[start], start))
        while (not pq.empty()):
            u = pq.get()[1]
            for v in self.graph[u]:
                if (dist[v] > (dist[u][0] + self.graph[u][v][0], dist[u][1] + self.graph[u][v][1])):
                    dist[v] = (dist[u][0] + self.graph[u][v][0], dist[u][1] + self.graph[u][v][1])
                    pq.put((dist[v], v))
                    trace[v] = u
        return dist, trace
        

graph = Graph("type12_type34/type12.csv", "type12_type34/type34.csv")
#graph = Graph("graph.json", "", mode="load")
print("Number of vertices:", graph.getLenVertices())
print("Number of edges:", graph.getLenEdges())
graph.outputGraph("graph.json") 
sys.exit(0)