# importing files
from routevar import *
from stop import *
from math import *
from abc import ABC, abstractmethod
import json

##### Path definition:
class Path:
    # atrributes
    __lat = [],
    __lng = [],
    __routeId = "";
    __routeVarId = "";
    
    # methods
    def __init__(self, lat = [], lng = [], routeId = "", routeVarId = "") -> None:
        self.__lat = lat if lat != None else [];
        self.__lng = lng if lng != None else [];
        self.__routeId = routeId if routeId != None else "";
        self.__routeVarId = routeVarId if routeVarId != None else "";
    
    # setters
    def setLat(self, lat = []):
        self.__lat = lat;
    
    def setLng(self, lng = []):
        self.__lng = lng;
    
    def setRouteId(self, routeId = ""):
        self.__routeId = routeId;
    
    def setRouteVarId(self, routeVarId = ""):
        self.__routeVarId = routeVarId;
    
    # getters
    def getLat(self):
        return self.__lat;

    def getLng(self):
        return self.__lng;

    def getRouteId(self):
        return self.__routeId;

    def getRouteVarId(self):
        return self.__routeVarId;

    # convert functions
    def convertToString(self):
        return str(self.__lat) + "," + str(self.__lng) + "," + self.__routeId + "," + self.__routeVarId;
    
    def convertToDict(self):
        return {
            "lat": self.__lat,
            "lng": self.__lng,
            "RouteId": self.__routeId,
            "RouteVarId": self.__routeVarId
        }


##### PathQuery definition:
class PathQuery:
    # attributes
    __list = [];
    
    # methods
    def __init__(self, list = []) -> None:
        self.__list = list;
    
    def setListPath(self, list = []):
        self.__list = list;
        
    def setPathAt(self, index, path = Path()):
        self.__list[index] = path;
    
    def getListPath(self):
        return self.__list;
    
    def getPathAt(self, index):
        return self.__list[index];

    # search functions
    def searchLengthLatBy123(self, identifier = 0):
        result = filter(lambda x: identifier >= len(x.getLat()), self.__list);
        return list(result);
    
    def searchLengthLngBy123(self, identifier = 0):
        result = filter(lambda x: identifier >= len(x.getLng()), self.__list);
        return list(result);
    
    def searchRouteIdByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRouteId(), self.__list);
        return list(result);
    
    def searchRouteVarIdByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRouteVarId(), self.__list);
        return list(result);
    
    # output functions:
    def outputAsCSV(self, list = []):
        title = "lat,lng,RouteId,RouteVarId";
        
        # open file
        file = open("outputPath.csv", "w", encoding = 'utf8');
        file.write(title);
        file.write('\n');
        for i in list:
            file.write(i.convertToString());
            file.write('\n');
    
    def outputAsJSON(self, list = []):
        with open("outputPath.json", "w", encoding='utf8') as outfile:
            for i in list:
                json.dump(i.convertToDict(), outfile, ensure_ascii=False);
                outfile.write('\n');
    
    # input functions
    def loadFronFile(self, filename):
        count = 0;
        with open(filename, "r", encoding='utf8') as infile:
            for line in infile:
                data = json.loads(line);
                temp = Path(data["lat"], data["lng"], data["RouteId"], data["RouteVarId"]);
                self.__list.append(temp);
                count += len(temp.getLat())
        return count;
    
    def loadToDict(self, filename):
        dict = {};
        with open(filename, "r", encoding='utf8') as infile:
            for line in infile:
                data = json.loads(line);
                cur = 0;
                dict[(int(data["RouteId"]), int(data["RouteVarId"]))] = [data["lng"], data["lat"], cur];
        return dict;