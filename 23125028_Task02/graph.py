from crs import*
from stop import*
from path import*
from routevar import*
import json
import time as times
from collections import defaultdict
from queue import PriorityQueue
import heapq

class Edge:
    # attributes
    start = Stop();
    end = Stop();
    dist = 0.00000;
    time = 0.00000;
    
    # methods
    def __init__(self, start = Stop(), end = Stop(), dist = 0.000, time = 0.000) -> None:
        self.start = start;
        self.end = end;
        self.dist = dist;
        self.time = time;
    
    # setters
    def setStart(self, start = Stop()):
        self.start = start;
        self.dist = distance(self.__start, self.__end);
    
    def setEnd(self, end = Stop()):
        self.end = end;
        self.dist = distance(self.__start, self.__end);
    
    def setDistance(self, dist = 0.00):
        self.dist = dist;
    
    def setTime(self, time = 0.000):
        self.time = time;
    
    # getters
    def getStart(self):
        return self.start;
    
    def getEnd(self):
        return self.end;

    def getDistance(self):
        return self.dist;
    
    def getTime(self):
        return self.time;
    

class Graph:
    # attributes
    __vertices = {};
    ##### vertices demonstration:
    # {
    #     stopId: [Stop, count],     ---> count to get the importance of this stopId
    #     stopId: [Stop, count],
    # }
    __edges = [];  # a list of edges: Stop1, Stop2, distance, time ----> not in used
    __adj = defaultdict(list);
    
    ##### adjacent demonstration:
    # {
    #     stopId1: [
    #         [stopId2, time, routeId, routeVarId, lat, lng],    ----> store the routeId and routeVarId for the information of the bus route
    #         [stopId3, time, routeId, routeVarId, lat, lng],    ----> possible existing 2 similar path btw 2 stop, but in different bus route
    #         ...
    #     ],
    #     stopId2: [
    #         ...
    #     ]
    # }
    
    # methods
    def __init__(self, vertices = {}, edges = [], adj = {}) -> None:
        self.__vertices = vertices;
        self.__edges = edges;
    
    # setters
    def setVertices(self, vertices = {}):
        self.__vertices = vertices;
    
    def setEdges(self, edges = []):
        self.__edges = edges;
    
    def setEdgesAt(self, edge = Edge(), index = 0):
        self.__edges[index] = edge;
    
    def appendEdge(self, edge = Edge()):
        self.__edges.append(edge);
    
    def removeEdge(self, edge = Edge()):
        self.__edges.remove(edge);
    
    def setAdjacent(self, adj = {}):
        self.__adj = adj;
    
    # getters
    def getVertices(self):
        return self.__vertices;

    def getEdges(self):
        return self.__edges;

    def getEdegsAt(self, index = 0):
        return self.__edges[index];
    
    def getAdjacent(self):
        return self.__adj;
    
    # bulid graph
    def importGraph(self, var = "", stop = "", path = ""):  
        target_crs = CRS.from_epsg(3405);
        source_crs = CRS.from_epsg(4326);
        proj = Transformer.from_crs(source_crs, target_crs);
        # get the routevar for the distance and time
        routes = RouteVarQuery();
        dct = routes.loadDistTime(var);
        # get the list of paths:
        paths = PathQuery();
        pth = paths.loadToDict(path);
        
        trans = lambda x,y: proj.transform(y, x);
        
        flag = False;
        prev = 0;
        with open(stop, encoding = 'utf8') as infile:
            # read each line in the file
            for line in infile:
                flag = False;
                # load data:
                data = json.loads(line);
                list = data["Stops"];
                routeId = int(data["RouteId"]);
                routeVarId = int(data["RouteVarId"]);
                velocity = dct[(routeId, routeVarId)];
                for i in list:
                    temp = Stop(i["StopId"], i["Code"], i["Name"], i["StopType"], i["Zone"], i["Ward"], i["AddressNo"], i["Street"],
                                i["SupportDisability"], i["Status"], i["Lng"], i["Lat"], i["Search"], i["Routes"]);
                    if (temp.getStatus() != "Đang khai thác"):
                        flag = False;
                        continue;
                    self.__vertices[temp.getStopId()] = [temp, 0];
                    #print("#1", time() - cur)
                    if (flag == False):
                        flag = True;
                        prev = temp.getStopId();
                        continue;
                    else:
                        # calculate time btw fi and temp
                        #dist = distance(self.__vertices[prev], temp);
                        lng1, lat1 = self.__vertices[prev][0].getLng(), self.__vertices[prev][0].getLat();
                        lng2, lat2 = temp.getLng(), temp.getLat();
                        dist = 0;
                        # access the lng and lat list:
                        lng = pth[(routeId, routeVarId)][0];
                        lat = pth[(routeId, routeVarId)][1];
                        cur = pth[(routeId, routeVarId)][2];  # --> initially cur = 0
                        reslat = [];
                        reslng = [];
                        minDif = 100000;
                        idx = 0;
                        if (check(lng1, lng[cur]) and check(lat1, lat[cur])):
                            reslat = [lat[cur]];
                            reslng = [lng[cur]];
                            for i in range(cur+1, len(lat)):
                                d = distance((lng2, lat2), (lng[i], lat[i]));
                                if (minDif > d):
                                    minDif = d;
                                    idx = i;
                                dist += distance(trans(lng[i], lat[i]), trans(lng[i-1], lat[i-1]));
                                reslat.append(lat[i]);
                                reslng.append(lng[i]);
                                if check(lng2, lng[i]) and check(lat2, lat[i]):
                                    pth[(routeId, routeVarId)][2] = i;
                                    break;
                                else:
                                    if i == len(lat)-1:
                                        reslat = lat[cur:idx+1];
                                        reslng = lng[cur:idx+1];
                                        dist = 0;
                                        for j in range(cur+1, idx+1):
                                            dist += distance(trans(lng[j], lat[j]), trans(lng[j-1], lat[j-1]));
                        else:
                            fl = False;
                            for i in range(0, len(lat)):
                                if check(lng1, lng[i]) and check(lat1, lat[i]):
                                    fl = True;
                                    cur = i;
                                if fl:
                                    d = distance((lng2, lat2), (lng[i], lat[i]));
                                    if (minDif > d):
                                        minDif = d;
                                        idx = i;
                                    dist += distance(trans(lng[i], lat[i]), trans(lng[i-1], lat[i-1]));
                                    reslat.append(lat[i]);
                                    reslng.append(lng[i]);
                                    if check(lng2, lng[i]) and check(lat2, lat[i]):
                                        pth[(routeId, routeVarId)][2] = i;
                                        break;
                                    else:
                                        if i == len(lat)-1:
                                            reslat = lat[cur:idx+1];
                                            reslng = lng[cur:idx+1];
                                            dist = 0;
                                            for j in range(cur+1, idx+1):
                                                dist += distance(trans(lng[j], lat[j]), trans(lng[j-1], lat[j-1]));
                        # dist = distance(x1, y1, x2, y2);
                        t = dist/velocity; 
                        #self.__edges.append(Edge(prev, temp, dist, time));
                        self.__adj[prev].append((temp.getStopId(), t, routeId, routeVarId, reslat, reslng));
                        prev = temp.getStopId();
                    #print("#2", time() - cur)
            
    
    def outputAdjacentAsJSON(self):
        with open("adjacents.json", "w", encoding='utf8') as file:
            json.dump(self.__adj, file, ensure_ascii=False);
    
    def dijkstra1Point(self, startStop = 0):
        cur = times.time();
        d = [];
        for i in range(0,10000):
            d.append(10000000);
        d[startStop] = 0;
        trace = defaultdict(list);
        trace[startStop] = [-1, -1, -1];
        ##### trace demonstration:
        # self.__adj[u] = [v, time, routeId, routeVarId]
        # --> trace[v] = [u, routeId, routeVarId]
        pq = PriorityQueue();
        ### pq.push(item) = pq.put((priority, item))
        pq.put((d[startStop], (startStop, d[startStop])));
        while (not pq.empty()):
            node = pq.get()[1];
            u = node[0];
            for e in self.__adj[u]:
                time = e[1];
                v = e[0];
                if (d[v] > d[u] + time):
                    d[v] = d[u] + time;
                    pq.put((d[v], (v, d[v])));
                    trace[v] = [u, e[2], e[3]];
        
        ## trace back
        res = {};
        #### res demonstration:
        # res = {
        #     stopId1: {
        #         "StopId": stopId1,
        #         "Path": [
        #         [stopId1, routeId, routeVarId],
        #         [stopId2, routeId, routeVarId],
        #         ...,
        #         ],
        #         "Time": time
        #     }
        # }
        for v in self.__vertices:
            if (v != startStop):
                res[v] = {"StopId": v, "Path": [], "Time": d[v]};
        for v in self.__vertices:
            if (v != startStop and d[v] != 10000000):
                start = v;
                while (trace[v][0] != -1):
                    u = trace[v][0];
                    routeId = trace[v][1];
                    routeVarId = trace[v][2];
                    res[start]["Path"].append([u, routeId, routeVarId]);
                    v = u;
                    self.__vertices[v][1] += 1;
                res[start]["Path"].reverse();
        print(times.time() - cur);
        with open ("Results/result.json", "w", encoding='utf8') as outfile:
            for key in res:
                json.dump(res[key], outfile, ensure_ascii=False);
                outfile.write('\n');
    
    # for returning the dictionary of the result
    def dijkstra1PointRes(self, startStop = 0):
        cur = times.time();
        d = [];
        d.clear();
        for i in range(0,10000):
            d.append(10000000);
        d[startStop] = 0;
        trace = [];
        trace.clear();
        for i in range(0,10000):
            trace.append([0,0,0]);
        trace[startStop] = [-1, -1, -1];
        ##### trace demonstration:
        # self.__adj[u] = [v, time, routeId, routeVarId]
        # --> trace[v] = [u, routeId, routeVarId]
        pq = PriorityQueue();
        ### pq.push(item) = pq.put((priority, item))
        pq.put((d[startStop], (startStop, d[startStop])));
        while (not pq.empty()):
            node = pq.get()[1];
            u = node[0];
            for e in self.__adj[u]:
                time = e[1];
                v = e[0];
                if (d[v] > d[u] + time):
                    d[v] = d[u] + time;
                    pq.put((d[v], (v, d[v])));
                    trace[v] = [u, e[2], e[3]];
        print("#2:", times.time() - cur);
        ## trace back
        res = {}
        check = {}
        for v in self.__vertices:
            #print(trace[v][0], end = " ", flush = True);
            if (v != startStop):
                res[v] = {"StopId": v, "Path": [], "Time": d[v]};
        for v in self.__vertices:
            if (v != startStop and d[v] != 1e7):
                start = v
                while (trace[v][0] != -1 and v != startStop and v not in check):
                    if (times.time() - cur) > 5:
                        print(v, end = " ");
                    u = trace[v][0]
                    routeId = trace[v][1]
                    routeVarId = trace[v][2]
                    res[start]["Path"].append([u, routeId, routeVarId])
                    check[v] = 1;
                    v = u
                    self.__vertices[v][1] += 1
                res[start]["Path"].reverse()
        print(startStop, times.time() - cur)
        return res
                
                
    def dijkstraStartEnd(self, startStop = 0, endStop = 0):
        cur = times.time();
        d = [];
        for i in range(0,10000):
            d.append(10000000);
        d[startStop] = 0;
        trace = defaultdict(list);
        trace[startStop] = [-1, -1, -1, -1, -1];
        ##### trace demonstration:
        # self.__adj[u] = [v, time, routeId, routeVarId,....]
        # --> trace[v] = [u, routeId, routeVarId,....]
        pq = PriorityQueue();
        ### pq.push(item) = pq.put((priority, item))
        pq.put((d[startStop], (startStop, d[startStop])));
        while (not pq.empty()):
            node = pq.get()[1];
            u = node[0];
            for e in self.__adj[u]:
                time = e[1];
                v = e[0];
                if (d[v] > d[u] + time):
                    d[v] = d[u] + time;
                    pq.put((d[v], (v, d[v])));
                    trace[v] = [u, e[2], e[3], e[4], e[5]];
        
        ## trace back
        res = {"To stopId": endStop, "Path": [], "Time": d[endStop] if d[endStop] != 10000000 else 0, "lat": [], "lng": []};
        v = endStop;
        if (d[v] != 10000000):
            while (trace[v][0] != -1):
                u = trace[v][0];
                routeId = trace[v][1];
                routeVarId = trace[v][2];
                res["Path"].append({
                    "StopId": u, 
                    "RouteId": routeId, 
                    "RouteVarId": routeVarId
                    });
                trace[v][3].reverse();
                trace[v][4].reverse();
                res["lat"].extend(trace[v][3]);
                res["lng"].extend(trace[v][4]);
                v = u;
                self.__vertices[v][1] += 1;
            res["Path"].reverse();
            res["lat"].reverse();
            res["lng"].reverse();
        print(times.time() - cur);
        with open ("result.json", "w", encoding='utf8') as outfile:
            json.dump(res, outfile, ensure_ascii=False);

    def dijkstraAllPairs(self):
        cur = times.time();
        ans = {};
        for startStop in self.__vertices:
            res = self.dijkstra1PointRes(startStop);
            ans[startStop] = {startStop: res};
        # write
        with open ("Results/result.json", "w", encoding='utf8') as outfile:
            for key in ans:
                json.dump(ans[key], outfile, ensure_ascii=False);
                outfile.write('\n');
        print("#1: ", times.time() - cur);
        
        
        # rank the importance
        list = [];
        for i in self.__vertices:
            list.append((self.__vertices[i][1], i));
        list.sort(reverse = True);
        for i in range (0, 10):
            print("Top:", i+1);
            print("StopId:", list[i][1]);
            print("Importance:", list[i][0]);
        print("#2: ", times.time() - cur);
        

# # driver code
# graph = Graph();
# graph.importGraph("Questions/vars.json", "Questions/stops.json", "Questions/paths.json");
# graph.outputAdjacentAsJSON();
# #graph.dijkstra1PointRes(461);
# graph.dijkstraAllPairs(); 
                        