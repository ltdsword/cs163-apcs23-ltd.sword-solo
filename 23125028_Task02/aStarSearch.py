import math
from path import*
from routevar import*
from stop import*
from crs import*
from collections import defaultdict
from queue import PriorityQueue
import heapq
import json
import time as times

# we have the adjacent matrix of the graph, stored in a JSON file

# firstly, we need to load the JSON file
adj = defaultdict(list)
def loadAdjacent(adj = {}, filename = ""):
    with open(filename, "r", encoding = 'utf8') as infile:
        data = json.load(infile)
        for i in data:
            adj[int(i)] = data[i]
            
def dijkstra1P(adj = {}, start = 0, end = 0):
    cur = times.time()
    startTime = cur
    pq = PriorityQueue()
    d = [10000000] * 9000
    trace = [[0,0,0]] * 9000
    d[start] = 0
    pq.put((d[start], start))
    trace[start] = [-1,-1,-1]
    print(f"Precomute: {times.time() - cur:.20f}")
    cur = times.time()
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
    print(f"Dijkstra search time: {times.time() - cur:.20f}")
    cur = times.time()
    res = []
    v = end
    res.append(v)
    while (trace[v] != [-1,-1,-1]):
        res.append(trace[v][0])
        v = trace[v][0]
    res.reverse()
    print(res)
    print(d[end])
    print(f"Traceback time: {times.time() - cur:.20f}")
    print(f"Total time: {times.time() - startTime:.20f}")
    print("----------------------------")
    return res, d[end]
    
def AStarSearch(adj = {}, start = 0, end = 0, mode = ""):
    # we use a heuristic function h = time prediction btw current stop to the end stop
    # we choose the least value of f = g + h, with g is the cost to go to another point
    
    # convert from lat lng to x y
    target_crs = CRS.from_epsg(3405)
    source_crs = CRS.from_epsg(4326)
    proj = Transformer.from_crs(source_crs, target_crs)
    trans = lambda x,y: proj.transform(y, x)
    
    # get the position for each stop
    sq = StopQuery()
    sq.loadFromFile("Questions/stops.json")
    lstStop = sq.getListStop()
    stopPos = {}
    for i in lstStop:
        stopPos[i.getStopId()] = trans(i.getLng(), i.getLat())
        
    # get the velocity of each route and routevar
    rvq = RouteVarQuery()
    vel = rvq.loadDistTime("Questions/vars.json")
    
    cur = times.time()
    startTime = cur
    
    # function to calculate h (time estimate)
    h = lambda stopId1, stopId2, route, routeVar: sqrt((stopPos[stopId1][0] - stopPos[stopId2][0])**2 + (stopPos[stopId1][1] - stopPos[stopId2][1])**2)/vel[(route, routeVar)]
    
    pq = PriorityQueue()
    trace = defaultdict(lambda: [0,0,0])
    trace[start] = [-1, -1, -1]
    closed = {}
    d = defaultdict(lambda: 1000000)
    d[start] = 0.0
    
    pq.put((-1, start))
    if (mode == 'display'): print(f"Precompute (with ignorance to the StopQuery and RouteVarQuery): {times.time() - cur:.20f}")
    cur = times.time()
    # flag = False
    while (not pq.empty()):
        f_u, u = pq.get()
        if (u == end):
            break
        for x in adj[u]:
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
        # if (flag): break  
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
        
        
        
        
# # driver code
# loadAdjacent(adj, "adjacents.json")
# #print(adj[35])
# dijkstra1P(adj, 7269, 3435)
# AStarSearch(adj, 7269, 3435)