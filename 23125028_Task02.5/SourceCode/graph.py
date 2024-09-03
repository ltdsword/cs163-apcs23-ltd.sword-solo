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
        self.vertices = defaultdict(lambda: 0)
        self.graph = defaultdict(list)
        self.stops = defaultdict(set)
        self.count = 0
        if (mode == 'default'):
            self.graph = defaultdict(dict)
            self.stops = defaultdict(list)
            self.loadData(filename1, '12')
            self.loadData(filename2, '34')
        elif (mode == 'alter'):
            self.loadData2(filename1, '12')
            self.loadData2(filename2, '34')
        else:
            self.loadGraph(filename1)
        self.result = defaultdict(dict)

    
    # consider the edge type for contraction the node
    
    def loadData(self, filename, type):
        # load the data from CSV file
        #cur = times.time()
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
            vertex1 = (data[0], timestamp1)
            vertex2 = (data[4], timestamp2)
            edgetype = data[20]
            # weight of the edge is number of transfer and time difference between two nodes
            # we prioritize the number of transfer over time difference 
            if (self.graph[vertex1].get(vertex2) == None): self.graph[vertex1][vertex2] = (2, 99999999, 'inf')
            if (type == '12'):
                self.graph[vertex1][vertex2] = min(self.graph[vertex1][vertex2], (0, time_diff, edgetype))
            else:
                self.graph[vertex1][vertex2] = min(self.graph[vertex1][vertex2], (1, time_diff, edgetype))
            
            #if (self.count % 50000 == 0): print(f"Processed {self.count} lines in {times.time() - cur} seconds")
        file.close()
    
    def contract(self):
        cur = times.time()
        # contract the edge having type = 2 or 3
        count = 0
        delete = defaultdict(set)
        lst = set()
        addi = defaultdict(dict)
        for key in self.graph:
            for key2 in self.graph[key]:
                if (self.graph[key][key2][2] == '2' or self.graph[key][key2][2] == '3'):
                    if (key2 not in self.graph): continue
                    for key3 in self.graph[key2]:
                        if (key3 == key): continue
                        if (key3 not in self.graph[key2]): continue
                        addi[key][key3] = (self.graph[key][key2][0] + self.graph[key2][key3][0], self.graph[key][key2][1] + self.graph[key2][key3][1], self.graph[key2][key3][2])
                        count += 1
                        delete[key2].add(key3)
                    delete[key].add(key2)
                    lst.add(key2)
                    count += 1
        print(f"Number of edges to be contracted: {count}")
        count = 0
        # add the new edge
        for key in addi:
            count += len(addi[key])
            for key2 in addi[key]:
                self.graph[key][key2] = addi[key][key2]
        print(f"Number of edges added: {count}")
        print("Number of vertices:", len(self.graph))
        print("Number of edges:", self.getLenEdges())
        # delete the edge having type = 2 or 3
        count = 0
        for key in delete:
            for key2 in delete[key]:
                count += 1
                del self.graph[key][key2]
        print(f"Number of edges deleted: {count}")
        print(f"Number of nodes deleted: {len(lst)}")
        print("Number of edges:", self.getLenEdges())
        for key in lst:
            self.graph.pop(key)
        print("Number of vertices:", len(self.graph))
        print("Number of edges:", self.getLenEdges())
        print(f"Done contracting in {times.time() - cur} seconds")
    
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
        with open(filename, 'r', encoding='utf8') as file:
            graph = json.load(file)
        self.graph = defaultdict(dict)
        for key in graph:
            vertex1 = self.destr(key)
            for key2 in graph[key]:
                vertex2 = self.destr(key2)
                self.graph[vertex1][vertex2] = tuple(graph[key][key2])
    
    def loadStopId(self):
        # load the distinct stop id from the graph
        for key in self.graph:
            self.stops[key[0]].append(key) # stop_id, route_id, var_id, timestamp
        print("Number of stops:", len(self.stops))
                
                
    def dijkstra1Stop(self, startStop):
        # perform Dijkstra algorithm to find the shortest path from every start stop to all other stops in all timestamps
        cur = times.time()
        lst = self.stops[startStop]
        record = defaultdict(set)
        mini = {}
        print(f"Processing {startStop} with {len(lst)} vertices")
        dist = defaultdict(lambda: (9999, float(99999999), None))
        defaultTuple = (9999, float(99999999), None)
        trace = defaultdict(lambda: None)
        pq = PriorityQueue()
        for start in lst:
            # dist structure = (number of transfer, time difference, start point)
            #print(f"Processing {start}")
            dist[start] = (0, 0, start)
            trace[start] = None
            pq.put((dist[start], start))
        
        while (not pq.empty()):
            u = pq.get()[1]
            if (u not in record[u[0]]):
                record[u[0]].add(u)
                if (u[0] not in mini): mini[u[0]] = u
                else:
                    if (dist[u] < dist[mini[u[0]]]):
                        mini[u[0]] = u
            else:
                continue
            for v in self.graph[u]:
                edge = self.graph[u][v]
                time_diff = edge[1]
                numoftrans = edge[0]
                if (dist[v] > (dist[u][0] + numoftrans, dist[u][1] + time_diff, dist[u][2])):
                    dist[v] = (dist[u][0] + numoftrans, dist[u][1] + time_diff, dist[u][2])
                    pq.put((dist[v], v))
                    trace[v] = u
        
        for stop in mini:
            if (stop == startStop): continue
            minDist = dist[mini[stop]]
            minStop = mini[stop]
            # the minimum distance = minDist
            # the stop that has the minimum distance = minStop
            # trace back to increase the importance of the stop
            # increse by 1 in self.vertices[stop]
            minStart = minDist[2]
            while (minStop != minStart and minStop != None):
                self.vertices[minStop[0]] += 1
                minStop = trace[minStop]
        print(f"Processed {startStop}, trace back in {times.time() - cur} seconds")
    
    def dijkstraAllStop(self):
        self.loadStopId()
        cur = times.time()
        count = 0
        for stop in self.stops:
            self.dijkstra1Stop(stop)
            count += 1
            print(f"Processed {stop}, ({count}/4148) in {times.time() - cur} seconds")
            
    def outputImportance(self, filename):
        # output the importance of each stop to a file
        # the vertices should be sorted by the largest importance to the smallest importance
        vertices = sorted(self.vertices.items(), key=lambda x: x[1], reverse=True)
        with open(filename, 'w', encoding='utf8') as file:
            for vertex in vertices:
                json.dump(vertex, file, ensure_ascii=False)
                file.write("\n")

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

    def loadImportance(self, filename):
        with open(filename, 'r', encoding='utf8') as file:
            for line in file:
                data = json.loads(line)
                self.vertices[data[0]] = data[1]
                
    def findTopK(self, k):
        self.loadImportance("importance.json")
        vertices = sorted(self.vertices.items(), key=lambda x: x[1], reverse=True)
        file = open(f"top{k}.txt", "w")
        for i in range(k):
            file.write(str(vertices[i]) + "\n")
        return vertices[:k]
        
        

# driver code

graph = Graph("graph.json", "", mode="load")
print("Number of vertices:", graph.getLenVertices())
print("Number of edges:", graph.getLenEdges())
# query phase
print(graph.findTopK(15))


sys.exit(0)