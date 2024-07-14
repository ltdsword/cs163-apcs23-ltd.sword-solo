import math
from path import*
from routevar import*
from stop import*
from crs import*
from collections import defaultdict, deque
from queue import PriorityQueue
import heapq
import json
import time as times
from aStarSearch import*
from bisect import bisect_left, bisect_right # for binary search, equivalent to lower_bound and upper_bound in C++

# use the contraction hierarchy algorithm to speed up the search
# since this graph is a directed graph, we need to build the forward (adj) and backward (rev) graph

def shortedAdj(adj = {}):
    # we put the lat and lng out of the adj list
    # instead, we use the node as the key to store the lat and lng
    lat = {}                    # lat = {(node 1, node 2, route, routeVar): lat}
    lng = {}                    # lng = {(node 1, node 2, route, routeVar): lng}
    newadj = defaultdict(list)  # new adj = {node: [(stop1, time, route, routeVar), 
                                #                   (stop2, time, route, routeVar), 
                                #                   ...
                                #                   (stopn, time, route, routeVar)]
                                #            }
    for node in adj:
        dictt = {}
        # make newadj[node] unique
        for x in adj[node]:
            if (x[0] not in dictt): dictt[x[0]] = (x[1], x[2], x[3])
            else:
                if (dictt[x[0]][0] > x[1]):
                    dictt[x[0]] = (x[1], x[2], x[3])
            lat[(node, x[0], x[2], x[3])] = x[4]
            lng[(node, x[0], x[2], x[3])] = x[5]
        for x in dictt:
            newadj[node].append((x, dictt[x][0], dictt[x][1], dictt[x][2]))
        newadj[node].sort()
    return newadj, lat, lng

class DGraph:
    def __init__(self, adj):         # we use the new adj list to create the graph (no lat and lng in the adj list)
        self.adj = adj               # adj[u] represent the points that node u can go to
        self.rev = defaultdict(list) # rev[u] represent the points that come to node u
        self.time = defaultdict(int) # time from node u to node v
        
        # create the reverse graph
        for node in adj:
            for x in adj[node]:
                self.rev[x[0]].append((node, x[1], x[2], x[3]))
                self.time[(node, x[0])] = min(self.time[(node, x[0])], x[1]) if (node, x[0]) in self.time else x[1]
        
        for node in self.rev: 
            self.rev[node].sort()
    
    def getTime(self, u, v):
        if ((u, v) not in self.time):
            return 1e9
        return self.time[(u, v)]
    
    def getAdj(self, u):
        return self.adj[u]
    
    def getRev(self, u):
        return self.rev[u]
    
    def append(self, u, v, time, route, routeVar):
        self.adj[u].append((v, time, route, routeVar))
        self.rev[v].append((u, time, route, routeVar))
        time[(u, v)] = time
    
    def setAdj(self, adj):
        self.adj = adj
        self.rev = defaultdict(list)
        self.time = defaultdict(int)
        
        # create the reverse graph
        for node in adj:
            for x in adj[node]:
                self.rev[x[0]].append((node, x[1], x[2], x[3]))
                self.time[(node, x[0])] = x[1]

    def setTime(self, u, v, time):
        self.time[(u, v)] = time


# contraction hierarchy algorithm class

class ContractionHierarchy:
    def __init__(self, adj = {}, mode = "", shortcutFile = "", shcutRouteFile = "", rankFile = "", adjFile = ""):
        if (mode == "file"):
            with open (adjFile, encoding = 'utf8') as infile:
                data = json.load(infile)
            for i in data:
                adj[int(i)] = data[i]
            self.graph = DGraph(adj)
            self.rank = defaultdict(int)
            self.shortcut = defaultdict(list)
            self.order = []
            self.shcutRoute = {}
            self.inputShortcut(shortcutFile, shcutRouteFile, rankFile)
            self.nodes = set()
            for node in self.graph.adj:
                self.nodes.add(node)
            for node in self.graph.rev:
                self.nodes.add(node)
        else:
            self.graph = DGraph(adj)
            self.rank = defaultdict(int)
            self.shortcut = defaultdict(list)
            self.contracted = set()
            self.order = []  # store the nodes in the order of contraction
            self.shcutRoute = {}  # store the route and routeVar of the shortcut
            # shcutRoute[(A,B)] = (route, routeVar)
            self.nodes = set()
            for node in self.graph.adj:
                self.nodes.add(node)
            for node in self.graph.rev:
                self.nodes.add(node)
            self.countDiff = defaultdict(lambda: 0)
            self.precompute(mode="edgeDiff")
            
    def computeEdgeDiff(self, node):
        edgeDiff = -(len(self.graph.adj[node]) + len(self.graph.rev[node]))
        # get the neighbors of the node
        forward = self.graph.adj[node]
        backward = self.graph.rev[node]

        for u in backward:  # u = (stopId, time, route, routeVar)
            time = times.time()
            maxP = 0
            d = defaultdict(lambda: 1e8)
            count = defaultdict(lambda: 0)
            for v in forward:
                count[v[0]] += 1
            d[u[0]] = 0
            d[node] = self.graph.getTime(u[0], node)
            for v in forward: # v = (stopId, time, route, routeVar)
                maxP = max(maxP, self.graph.getTime(u[0], node) + self.graph.getTime(node, v[0]))
            
            # perform a standard dijkstra from u to the subgraph excluding the node
            pq = PriorityQueue()
            pq.put((d[u[0]], u[0]))
            while not pq.empty():
                point = pq.get()[1]
                for v in self.graph.adj[point]:
                    count[v[0]] += 1
                    if (v[0] == node):
                        continue
                    if d[v[0]] > d[point] + v[1]:
                        d[v[0]] = d[point] + v[1]
                        pq.put((d[v[0]], v[0]))
                    
                    # if a node is settled, we check the value of the node with maxP
                    # if the value of the node is greater than maxP, we can break the loop
                    if count[v[0]] == len(self.graph.rev[v[0]]):
                        if d[v[0]] > maxP:
                            break
            
            for v in forward:
                if (d[v[0]] > self.graph.getTime(u[0], node) + self.graph.getTime(node, v[0])):
                    edgeDiff += 1
        return edgeDiff
        
    def precompute(self, mode = ""):
        if (mode == 'degree'):
            cur = times.time()
            # for simple, we use the degree of the node as the rank of the node, which is the number of neighbors of the node
            # ascending in the deg of nodes.
            for node in self.nodes:
                self.rank[node] = len(self.graph.adj[node]) + len(self.graph.rev[node])
            rank = sorted(self.rank, key = self.rank.get)
            idx = 1
            for node in rank:
                self.rank[node] = idx
                idx += 1
            self.order = sorted(self.rank, key = self.rank.get)
            
            initadj = self.graph.adj.copy()
            initrev = self.graph.rev.copy()
            
            # we contract all the node in the order to get the shortcut
            for node in self.order:
                start = times.time()
                self.contract(node)
                print(f"Contract node {node} in {times.time() - start:.20f}")
                
            self.graph.adj = initadj.copy()
            self.graph.rev = initrev.copy()
                
            # add the shortcuts to the graphs
            self.addShortcut()
                            
            print(f"Precomputation time: {times.time() - cur:.20f}")
            
        elif (mode == 'edgeDiff'):
            pqNode = PriorityQueue()
            cur = times.time()
            # we compute the edge difference of the node
            for node in self.nodes:
                edgeDiff = self.computeEdgeDiff(node)
                pqNode.put((edgeDiff, node))
                self.countDiff[node] = edgeDiff
            
            # now we have the nodes in the order of edge difference
            # we combine contracting the node along with lazy updating of the edge difference
            
            initadj = self.graph.adj.copy()
            initrev = self.graph.rev.copy()
            
            idx = 1
            while (not pqNode.empty()):
                start = times.time()
                tmp = pqNode.get()
                node = tmp[1]
                ed = tmp[0]
                edgeDiff = self.computeEdgeDiff(node)
                #edgeDiff = self.countDiff[node]
                if (pqNode.empty() or edgeDiff <= pqNode.queue[0][0]):
                    self.order.append(node)
                    self.rank[node] = idx
                    idx += 1
                    self.contract(node)
                    print(f"Contract node {node} in {times.time() - start:.20f}")
                else:
                    pqNode.put((edgeDiff, node))
                
                if (len(pqNode.queue) <= 2):
                    print(len(pqNode.queue))
            
            self.graph.adj = initadj.copy()
            self.graph.rev = initrev.copy()
            
            # add the shortcuts to the graphs
            self.addShortcut()
            print(f"Number of shortcuts: {len(self.shortcut)}")
            print(f"Precomputation time: {times.time() - cur:.20f}")
            
        else:
            # default mode is degree
            self.precompute(mode = 'degree')
            
            
    def contract(self, node):
        # get the neighbors of the node
        forward = self.graph.adj[node]
        backward = self.graph.rev[node]
        # if (node == 694):
        #     print("here")
        
        for u in backward:  # u = (stopId, time, route, routeVar)
            self.countDiff[u[0]] -= 1
            time = times.time()
            maxP = 0
            d = [1e9]*9000
            count = [0]*9000
            for v in forward:
                count[v[0]] += 1
            d[u[0]] = 0
            d[node] = self.graph.getTime(u[0], node)
            for v in forward: # v = (stopId, time, route, routeVar)
                maxP = max(maxP, self.graph.getTime(u[0], node) + self.graph.getTime(node, v[0]))
            
            # perform a standard dijkstra from u to the subgraph excluding the node
            pq = PriorityQueue()
            pq.put((d[u[0]], u[0]))
            while not pq.empty():
                point = pq.get()[1]
                for v in self.graph.adj[point]:
                    count[v[0]] += 1
                    if (v[0] == node):
                        continue
                    if d[v[0]] > d[point] + v[1]:
                        d[v[0]] = d[point] + v[1]
                        pq.put((d[v[0]], v[0]))
                    
                    # if a node is settled, we check the value of the node with maxP
                    # if the value of the node is greater than maxP, we can break the loop
                    if count[v[0]] == len(self.graph.rev[v[0]]):
                        if d[v[0]] > maxP:
                            break
            
            # print(times.time() - time)
            
            for v in forward: # v = (stopId, time, route, routeVar)
                self.countDiff[v[0]] -= 1
                if u[0] == v[0]:
                    continue
                
                # add a shortcut from u to v
                if (d[v[0]] > self.graph.getTime(u[0], node) + self.graph.getTime(node, v[0])): # if the shortcut is better than the path
                    # check if there is a shortcut from u to v
                    # if we modify the shortcut, we need to store the new shortcut along with the point that the shortcut is from
                    # for example, A -> B -> C, if we want to add a shortcut from A to C, we need to store B in the shortcut
                    # so, the shortcut structure is shortcut[(A,C)] = [B, time]
                    if (u[0], v[0]) in self.shortcut:
                        shortcut = self.shortcut[(u[0], v[0])]
                        if shortcut[1] > u[1] + v[1]:
                            # update the shortcut
                            shortcut[0] = node
                            shortcut[1] = u[1] + v[1]
                            if ((u[0], node) in self.shortcut): # from u to node is already a shortcut
                                self.shcutRoute[(node, v[0])] = (v[2], v[3]) # we just need to update the route and routeVar from node to v
                                                                             # since the route and routeVar from u to node has been stored in the shchtRoute
                            elif ((node, v[0]) in self.shortcut):
                                self.shcutRoute[(u[0], node)] = (u[2], u[3])
                            else:  # if there is no shortcut from u to node and from node to v
                                self.shcutRoute[(u[0], node)] = (u[2], u[3])
                                self.shcutRoute[(node, v[0])] = (v[2], v[3])
                        self.shortcut[(u[0], v[0])] = shortcut
                                                
                        # add newly added shortcut to the graphs
                        # just need to update the list, not add a new one
                        idx = bisect_left(self.graph.adj[u[0]], (v[0], u[1] + v[1], 0, 0))
                        if (idx < len(self.graph.adj[u[0]])): 
                            self.graph.adj[u[0]][idx] = (v[0], u[1] + v[1], 0, 0)
                            self.graph.time[(u[0], v[0])] = u[1] + v[1]
                        idx = bisect_left(self.graph.rev[v[0]], (u[0], u[1] + v[1], 0, 0))
                        if (idx < len(self.graph.rev[v[0]])): 
                            self.graph.rev[v[0]][idx] = (u[0], u[1] + v[1], 0, 0)
                    else:
                        self.shortcut[(u[0], v[0])] = [node, u[1] + v[1]]
                        self.countDiff[v[0]] += 1
                        self.countDiff[u[0]] += 1
                        if ((u[0], node) in self.shortcut): # from u to node is already a shortcut
                            self.shcutRoute[(node, v[0])] = (v[2], v[3]) # we just need to update the route and routeVar from node to v
                                                                         # since the route and routeVar from u to node has been stored in the shchtRoute
                        elif ((node, v[0]) in self.shortcut):
                            self.shcutRoute[(u[0], node)] = (u[2], u[3])
                        else:  # if there is no shortcut from u to node and from node to v
                            self.shcutRoute[(u[0], node)] = (u[2], u[3])
                            self.shcutRoute[(node, v[0])] = (v[2], v[3])
                            
                        # add newly added shortcut to the graphs
                        idx = bisect_left(self.graph.adj[u[0]], (v[0], u[1] + v[1], 0, 0))
                        if (idx < len(self.graph.adj[u[0]]) and self.graph.adj[u[0]][idx][0] == v[0]):
                            self.graph.adj[u[0]][idx] = (v[0], u[1] + v[1], 0, 0)
                        else:
                            self.graph.adj[u[0]].insert(idx, (v[0], u[1] + v[1], 0, 0))
                        self.graph.time[(u[0], v[0])] = u[1] + v[1]
                        idx = bisect_left(self.graph.rev[v[0]], (u[0], u[1] + v[1], 0, 0))
                        if (idx < len(self.graph.rev[v[0]]) and self.graph.rev[v[0]][idx][0] == u[0]):
                            self.graph.rev[v[0]][idx] = (u[0], u[1] + v[1], 0, 0)
                        else:
                            self.graph.rev[v[0]].insert(idx, (u[0], u[1] + v[1], 0, 0))
        
        
        # remove the node from the graph
        for u in backward:
            self.graph.adj[u[0]] = [(v[0], v[1], v[2], v[3]) for v in self.graph.adj[u[0]] if v[0] != node]
            self.graph.rev[u[0]] = [(v[0], v[1], v[2], v[3]) for v in self.graph.rev[u[0]] if v[0] != node]
        for v in forward:
            self.graph.adj[v[0]] = [(u[0], u[1], u[2], u[3]) for u in self.graph.adj[v[0]] if u[0] != node]
            self.graph.rev[v[0]] = [(u[0], u[1], u[2], u[3]) for u in self.graph.rev[v[0]] if u[0] != node]
        del self.graph.adj[node]
        del self.graph.rev[node]
    
    def addShortcut(self):
        # add the shortcut edges to the initial graph
        for sc in self.shortcut:
            idx = bisect_left(self.graph.adj[sc[0]], (sc[1], self.shortcut[sc][1], 0, 0))
            if (idx < len(self.graph.adj[sc[0]]) and self.graph.adj[sc[0]][idx][0] == sc[1]):
                self.graph.adj[sc[0]][idx] = (sc[1], self.shortcut[sc][1], 0, 0)
            else:
                self.graph.adj[sc[0]].insert(idx, (sc[1], self.shortcut[sc][1], 0, 0))
                
            idx = bisect_left(self.graph.rev[sc[1]], (sc[0], self.shortcut[sc][1], 0, 0))
            if (idx < len(self.graph.rev[sc[1]]) and self.graph.rev[sc[1]][idx][0] == sc[0]):
                self.graph.rev[sc[1]][idx] = (sc[0], self.shortcut[sc][1], 0, 0)
            else:
                self.graph.rev[sc[1]].insert(idx, (sc[0], self.shortcut[sc][1], 0, 0))
    
    def outputShortcutAsJSON(self):
        # change the structure of the shortcut and shcutRoute to fit the JSON format
        # structure after changing:
        # shortcut = {node 1: [[node 2, mid node, time], [node 3, mid node, time], ...]}
        # shcutRoute = {node 1: [[node 2, route, routeVar], [node 2, route, routeVar], ...]}
        
        shortcut = defaultdict(list)
        shcutRoute = defaultdict(list) 
        for sc in self.shortcut:
            shortcut[sc[0]].append([sc[1], self.shortcut[sc][0], self.shortcut[sc][1]])
        
        for sc in self.shcutRoute:
            shcutRoute[sc[0]].append([sc[1], self.shcutRoute[sc][0], self.shcutRoute[sc][1]])
        
        # output the shortcut and the route, routeVar of the shortcut to a JSON file
        with open ("CH/shortcuts.json", 'w', encoding='utf8') as outfile:
            json.dump(shortcut, outfile, ensure_ascii=False)
    
        with open ("CH/shcutRoute.json", 'w', encoding='utf8') as outfile:
            json.dump(shcutRoute, outfile, ensure_ascii=False)
        
        # output the rank of the node to a JSON file
        with open ("CH/rank.json", 'w', encoding='utf8') as outfile:
            json.dump(self.rank, outfile, ensure_ascii=False)
        
        # output the adjacent list with shortcut to a JSON file
        with open ("CH/adj.json", 'w', encoding='utf8') as outfile:
            json.dump(self.graph.adj, outfile, ensure_ascii=False)
    
    def inputShortcut(self, shortcutFile, shcutRouteFile, rankFile):
        with open (shortcutFile, encoding='utf8') as infile:
            shortcut = json.load(infile)
        with open (shcutRouteFile, encoding= 'utf8') as infile:
            shcutRoute = json.load(infile)
        
        # reformat the shortcut and shcutRoute to fit the structure of the class
        # structure after reformatting:
        # shortcut = {(node 1, node 2): [mid node, time]}
        # shcutRoute = {(node 1, node 2): [route, routeVar]}
        
        for node in shortcut:
            for sc in shortcut[node]:
                self.shortcut[(int(node), sc[0])] = [sc[1], sc[2]]
        
        for node in shcutRoute:
            for sc in shcutRoute[node]:
                self.shcutRoute[(int(node), sc[0])] = [sc[1], sc[2]]
        
        with open (rankFile, encoding= 'utf8') as infile:
            rank = json.load(infile)
        for i in rank:
            self.rank[int(i)] = rank[i]
        self.order = sorted(self.rank, key = self.rank.get) 
                
    def unpack(self, u, v, mode = "") -> list:
        # unpack the path from u to v
        if (mode == "adj"):
        # return a reverse path from u to v for easier to append to the result
            if (u, v) in self.shortcut:
                shortcut = self.shortcut[(u, v)]
                return self.unpack(shortcut[0], v, mode) + self.unpack(u, shortcut[0], mode)
            else:
                return [u]
        elif mode == "rev":
            if (u, v) in self.shortcut:
                shortcut = self.shortcut[(u, v)]
                return self.unpack(u, shortcut[0], mode) + self.unpack(shortcut[0], v, mode)
            else:
                return [v]
        else: return self.unpack(u, v, mode="adj")
        
    def query(self, start = 0, stop = 0):
        cur = times.time()
        # bidirectional dijkstra on the upward graph of start and stop
        # we use the forward graph to do the search on the source node
        # and the backward graph to do the search on the target node
        traceStart = defaultdict(lambda: [0,0,0])
        traceStop = defaultdict(lambda: [0,0,0])
        dStart = defaultdict(lambda: 1e8)
        dStop = defaultdict(lambda: 1e8)
        dStart[start] = 0
        dStop[stop] = 0
        traceStart[start] = [-1,-1,-1]
        traceStop[stop] = [-1,-1,-1]
        pqStart = PriorityQueue()
        pqStop = PriorityQueue()
        pqStart.put((dStart[start], start))
        pqStop.put((dStop[stop], stop))
        
        visitedStart = set()
        visitedStop = set()
        visitedStart.add(start)
        visitedStop.add(stop)
        
        intersect = 0
        
        while (not pqStart.empty() or not pqStop.empty()):
            if not pqStart.empty():
                u = pqStart.get()[1]
                if (u in visitedStop):
                    if (dStart[intersect] + dStop[intersect] > dStart[u] + dStop[u]):
                        intersect = u
                for v in self.graph.adj[u]:
                    if dStart[v[0]] > dStart[u] + v[1] and self.rank[u] < self.rank[v[0]]:
                        visitedStart.add(v[0])
                        dStart[v[0]] = dStart[u] + v[1]
                        pqStart.put((dStart[v[0]], v[0]))
                        traceStart[v[0]] = [u, v[2], v[3]]
            if not pqStop.empty():
                u = pqStop.get()[1]
                if (u in visitedStart):
                    if (dStart[intersect] + dStop[intersect] > dStart[u] + dStop[u]):
                        intersect = u
                for v in self.graph.rev[u]:
                    if dStop[v[0]] > dStop[u] + v[1] and self.rank[u] < self.rank[v[0]]:
                        visitedStop.add(v[0])
                        dStop[v[0]] = dStop[u] + v[1]
                        pqStop.put((dStop[v[0]], v[0]))
                        traceStop[v[0]] = [u, v[2], v[3]]
        
        print(f"Intersect at node {intersect}")
        # trace back to get the path
        res = []
        v = intersect
        if (intersect == -1):
            v = stop
            while (traceStart[v] != [-1,-1,-1] and traceStart[v] != [0,0,0]):
                res.append(traceStart[v][0])
                v = traceStart[v][0]
            res.reverse()
        else:
            res.append(intersect)
            while (traceStart[v][0] != -1):
                # unpacked the path after contracting from v to traceStart[v][0]
                res = res + self.unpack(traceStart[v][0], v, mode="adj")
                v = traceStart[v][0]
            res.reverse()
            v = intersect
            while (traceStop[v] != [-1,-1,-1]):
                res = res + self.unpack(v, traceStop[v][0], mode="rev")
                v = traceStop[v][0]
        
        print(res)
        print(f"Time: {dStart[intersect] + dStop[intersect]}")
        print(f"Query time: {times.time() - cur:.20f}")
        
        
        

# driver code
adj = defaultdict(list)
loadAdjacent(adj, "adjacents.json")
adj, lat, lng = shortedAdj(adj)
cur = times.time()
ch = ContractionHierarchy({}, mode="file", shortcutFile="CH/shortcuts.json", shcutRouteFile="CH/shcutRoute.json", rankFile="CH/rank.json", adjFile="CH/adj.json")
#ch.outputShortcutAsJSON()
ch.query(7269, 3435)
print(f"Total time: {times.time() - cur:.20f}")