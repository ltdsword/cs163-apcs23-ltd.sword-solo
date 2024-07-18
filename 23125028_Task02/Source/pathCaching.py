from math import*
from crs import*
from collections import defaultdict, Counter
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

def findCommon(path1 = [], path2 = [], d = []):
    len1 = len(path1)
    len2 = len(path2)
    dp = [[0] * (len2 + 1) for i in range(len1 + 1)]
    maxLen = 0
    index = 0
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if (path1[i - 1] == path2[j - 1]):
                dp[i][j] = dp[i - 1][j - 1] + 1
                if (dp[i][j] > maxLen):
                    maxLen = dp[i][j]
                    index = i
    
    if (maxLen == 0):
        return [[], 0]
    
    return [path1[index - maxLen: index], d[path1[index-1]] - d[path1[index - maxLen]]]
                

class Cache:
    def __init__(self) -> None:
       self.graph = Graph()
       self.cache = defaultdict(dict)
       # cache structure: {zone1: {zone2: [[path1, path2, ...], time]}}
       self.zones = defaultdict(list)
       self.adj = defaultdict(list)
       self.stops = {}
       self.stopPos = {}
       self.vel = {}
       # we find the common path between two stops in two different zones, and then save it to the cache
    
    def dijkstra1Point(self, start):
        cur = times.time()
        zoneStart = str(self.stops[start][0].getZone())
        # print((zoneStart))
        pq = PriorityQueue()
        d = defaultdict(lambda: 1e7)
        trace = defaultdict(lambda: [0,0,0])
        d[start] = 0
        pq.put((d[start], start))
        trace[start] = [-1,-1,-1]
        while (not pq.empty()):
            u = pq.get()[1]
            for x in adj[u]:
                v = x[0]
                time = x[1]
                route = x[2]
                routeVar = x[3]
                if (d[v] > d[u] + time):
                    d[v] = d[u] + time
                    trace[v] = [u, route, routeVar]
                    pq.put((d[v], v))
        # trace back
        for v in self.stops:
            end = v
            if (v != start and d[v] != 1e7):
                zone = str(self.stops[v][0].getZone())
                res = []
                res.append(v)
                while (trace[v] != [-1,-1,-1]):
                    res.append(trace[v][0])
                    v = trace[v][0]
                res.reverse()
                if zone not in self.cache[zoneStart]:
                    self.cache[zoneStart][zone] = [res, d[end]]
                    #f.write(f"{res}\n")
                else: 
                    #f.write(f"{res} {self.cache[zoneStart][zone]}\n")
                    self.cache[zoneStart][zone][0], self.cache[zoneStart][zone][1] = findCommon(self.cache[zoneStart][zone][0], res, d)
                #print(f"{self.cache[(zoneStart, zone)]} {zoneStart} {zone}")
        print(f"Time from {start}: {times.time() - cur:.20f}")

    def caching(self, filename = ""): # filename to save the cache
        cur = times.time()
        # we run all-pair dijkstra to find the shortest path between all pairs of stops
        self.graph.importGraph("Questions/vars.json", "Questions/stops.json", "Questions/paths.json")
        rvq = RouteVarQuery()
        self.vel = rvq.loadDistTime("Questions/vars.json")
        self.adj = self.graph.getAdjacent()
        self.stops = self.graph.getVertices()
        # get the position for each stop
        # convert from lat lng to x y
        target_crs = CRS.from_epsg(3405)
        source_crs = CRS.from_epsg(4326)
        proj = Transformer.from_crs(source_crs, target_crs)
        trans = lambda x,y: proj.transform(y, x)
        
        for key in self.stops:
            self.stopPos[key] = trans(self.stops[key][0].getLng(), self.stops[key][0].getLat())
        
        #f = open("test.txt", "w")
        for start in self.stops:
            self.dijkstra1Point(start)
        #f.close()
            
        print(f"Total time (all pairs): {times.time() - cur:.20f}")
        
        # now we've found the cache for all pairs of stops
        
        # modify the structure of the cache to be fit with the json format
        #if (35 in self.cache): del self.cache[35]
        
        with open(filename, "w", encoding='utf8') as outfile:
            json.dump(self.cache, outfile, ensure_ascii=False)
    
    def loadCache(self, filename = ""):
        self.graph.importGraph("Questions/vars.json", "Questions/stops.json", "Questions/paths.json")
        self.adj = self.graph.getAdjacent()
        self.stops = self.graph.getVertices()
        with open(filename, "r", encoding='utf8') as infile:
            self.cache = json.load(infile)
        # get the velocity of each route and routevar
        rvq = RouteVarQuery()
        self.vel = rvq.loadDistTime("Questions/vars.json")
        # get the position for each stop
        # convert from lat lng to x y
        target_crs = CRS.from_epsg(3405)
        source_crs = CRS.from_epsg(4326)
        proj = Transformer.from_crs(source_crs, target_crs)
        trans = lambda x,y: proj.transform(y, x)
        
        for key in self.stops:
            self.stopPos[key] = trans(self.stops[key][0].getLng(), self.stops[key][0].getLat())
                
    def dijkstra1Pair(self, start = 0, end = 0):
        pq = PriorityQueue()
        d = defaultdict(lambda: 1e7)
        trace = defaultdict(lambda: [0,0,0])
        d[start] = 0
        pq.put((d[start], start))
        trace[start] = [-1,-1,-1]
        while (not pq.empty()):
            u = pq.get()[1]
            for x in self.adj[u]:
                v = x[0]
                time = x[1]
                route = x[2]
                routeVar = x[3]
                if (d[v] > d[u] + time):
                    d[v] = d[u] + time
                    trace[v] = [u, route, routeVar]
                    pq.put((d[v], v))
        # trace back
        res = []
        v = end
        res.append(v)
        while (trace[v] != [-1,-1,-1]):
            res.append(trace[v][0])
            v = trace[v][0]
        res.reverse()
        return res, d[end]
    
    def aStarSearch(self, start = 0, end = 0, mode = ""):
        # we use a heuristic function h = time prediction btw current stop to the end stop
        # we choose the least value of f = g + h, with g is the cost to go to another point
        
        cur = times.time()
        startTime = cur
        
        # we already have the stops list and the adj list
        # to get the position of a stop: self.stops[stopId][0].getLng(), self.stops[stopId][0].getLat()
        
        # function to calculate h (time estimate)
        h = lambda stopId1, stopId2, route, routeVar: sqrt((self.stopPos[stopId1][0] - self.stopPos[stopId2][0])**2 + (self.stopPos[stopId1][1] - self.stopPos[stopId2][1])**2)/self.vel[(route, routeVar)]
        
        pq = PriorityQueue()
        trace = defaultdict(lambda: [0,0,0])
        trace[start] = [-1, -1, -1]
        closed = {}
        d = defaultdict(lambda: 1000000)
        d[start] = 0.0
        
        pq.put((-1, start))
        # flag = False
        while (not pq.empty()):
            f_u, u = pq.get()
            if (u == end):
                break
            for x in self.adj[u]:
                #if (trace[x[0]] == [0, 0, 0]):
                    v = x[0]
                    # if (v == end):
                    #     flag = True
                    time = x[1]
                    route = x[2]
                    routeVar = x[3]
                    tentative_time = d[u] + time
                    if (tentative_time < d[v]):
                        trace[v] = [u, route, routeVar]
                        d[v] = tentative_time
                        #print(d[v])
                        ftmp = tentative_time + h(v, end, route, routeVar)
                        if (v in closed and ftmp >= closed[v]): continue
                        else: 
                            pq.put((ftmp, v))
                            if (v in closed): del closed[v]
            closed[u] = f_u
        if (mode == 'display'): print(f"A* search time: {times.time() - cur:.20f}")
        cur = times.time()
        #trace back
        res = []
        v = end
        while (trace[v] != [-1,-1,-1]):
            res.append(trace[v][0])
            v = trace[v][0]
        res.reverse()
        res.append(end)
        if (mode == 'display'):
            print(res)
            print(d[end])
            print(f"Traceback time: {times.time() - cur:.20f}")
            print(f"Total time: {times.time() - startTime:.20f}")
            print("----------------------------")
        return res, d[end]
            
    def query(self, start = 0, end = 0):
        cur = times.time()
        zoneStart = str(self.stops[start][0].getZone())
        zoneEnd = str(self.stops[end][0].getZone())
        if (zoneEnd in self.cache[zoneStart] and self.cache[zoneStart][zoneEnd][1] != 0):
            lst = self.cache[zoneStart][zoneEnd]
            mid1 = lst[0][0]
            mid2 = lst[0][-1]
            time = lst[1]
            path1 = self.aStarSearch(start, mid1)
            path2 = self.aStarSearch(mid2, end)
            res = path1[0] + lst[0][1:-1] + path2[0]
            time += path1[1] + path2[1]
            print(res)
            print(f"Time: {time}")
        else:
            path = self.aStarSearch(start, end)
            print(path[0])
            print(f"Time(no caching): {path[1]}")
        print(f"Query time: {times.time() - cur:.20f}")
    
            


# driver code
# adj = defaultdict(list)
# loadAdjacent(adj, "adjacents.json")
# cach = Cache()
# cach.loadCache("cache.json")
# cach.query(6860, 1568)
# dijkstra1P(adj, 6860, 1568)
# cach.aStarSearch(6860, 1568, mode="display")
# lst = [35, 89, 90, 1409, 1413, 1416, 1891, 388, 390, 569, 573, 433, 503, 546, 504, 505, 506, 547, 507, 548, 508, 509, 553, 510, 555, 259, 260, 261, 262, 263, 265, 266, 267, 270, 271, 272, 273, 275, 277, 1115, 1239]
# lst2 = [35, 89, 90, 1409, 1413, 1416, 1891, 388, 390, 569, 573, 433, 503, 546, 504, 505, 506, 547, 507, 548, 508, 509, 553, 510, 555, 259, 260, 261, 262, 263, 265, 266, 267, 270, 271, 272, 273, 275, 277, 1115, 1152, 1156, 1155, 1158, 1160, 4592, 1157, 4586, 1162, 1164, 1161, 1166, 1163, 1168, 1167, 1170, 1220, 1169, 1172, 1171, 7609, 3233, 1173, 1174, 1176, 1175, 1177, 1178, 1179, 1180, 1181, 1182, 1183, 1184, 1185, 1206, 1205, 1207, 1208, 1211, 1209, 1212, 1210, 1214, 1216, 1213, 1218, 3232, 7608, 1215, 1222]
# print(findCommon(lst, lst2, [0]*9000))