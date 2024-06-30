# import
from math import *
from abc import ABC, abstractmethod
import json

##### RouteVar definition:
class RouteVar:
    #attributes
    __routeId = 0;
    __routeVarId = 0;
    __routeVarName = "";
    __routeVarShortName = "";
    __routeNo = "";
    __startStop = "";
    __endStop = "";
    __distance = 0.0;
    __outbound = True;
    __runningTime = 0;
    
    # methods
    def __init__(self, routeId = 0, routeVarId = 0, routeVarName = "", routeVarShortName = "", routeNo = "", 
                 startStop = "", endStop = "", distance = 0.0000, outbound = True, runningTime = 0) -> None:
        self.__routeId = routeId;
        self.__routeVarId = routeVarId;
        self.__routeVarName = routeVarName;
        self.__routeVarShortName = routeVarShortName;
        self.__routeNo = routeNo;
        self.__startStop = startStop;
        self.__endStop = endStop;
        self.__distance = distance;
        self.__outbound = outbound;
        self.__runningTime = runningTime;
    
    # setters
    def setRouteId(self, routeId):
        self.__routeId = routeId;
    
    def setRouteVarId(self, routeVarId):
        self.__routeVarId = routeVarId;
    
    def setRouteVarName(self, routeVarName):
        self.__routeVarName = routeVarName;
    
    def setRouteVarShortName(self, routeVarShortName):
        self.__routeVarShortName = routeVarShortName;
    
    def setRouteNo(self, routeNo):
        self.__routeNo = routeNo;
    
    def setStartStop(self, startStop):
        self.__startStop = startStop;
    
    def setEndStop(self, endStop):
        self.__endStop = endStop;
    
    def setDistance(self, distance):
        self.__distance = distance;
    
    def setOutbound(self, outbound):
        self.__outbound = outbound;
        
    def setRunningTime(self, runningTime):
        self.__runningTime = runningTime;
        
    # getters
    def getRouteId(self):
        return self.__routeId;
    
    def getRouteVarId(self):
        return self.__routeVarId;
    
    def getRouteVarName(self):
        return self.__routeVarName;
    
    def getRouteVarShortName(self):
        return self.__routeVarShortName;
    
    def getRouteNo(self):
        return self.__routeNo;

    def getStartStop(self):
        return self.__startStop;
    
    def getEndStop(self):
        return self.__endStop;

    def getDistance(self):
        return self.__distance;
    
    def getOutbound(self):
        return self.__outbound;

    def getRunningTime(self):
        return self.__runningTime;
    
    # convert to dictionary type to write as JSON file
    def convertToDict(self):
        return {"RouteId": self.__routeId,
                "RouteVarId": self.__routeVarId,
                "RouteVarName": self.__routeVarName,
                "RouteVarShortName": self.__routeVarShortName,
                "RouteNo": self.__routeNo,
                "StartStop": self.__startStop,
                "EndStop": self.__endStop,
                "Distance": self.__distance,
                "Outbound": self.__outbound,
                "RunningTime": self.__outbound}
    
##### RouteVarQuery definition:
class RouteVarQuery:
    # attributes
    __list = []
    
    # methods
    def __init__(self, list = []) -> None:
        self.__list = list;
    
    # setter
    def setListRouteVar(self, list = []):
        self.__list = list;
    
    # getter
    def getListRouteVar(self):
        return self.__list;
    
    # search funtions
    def searchRouteIdBy123(self, identifier = 0):
        result = filter(lambda x: str(identifier) in str(x.getRouteId()), self.__list);
        return list(result);
    
    def searchRouteVarIdBy123(self, identifier = 0):
        result = filter(lambda x: str(identifier) in str(x.getRouteVarId()), self.__list);
        return list(result);
    
    def searchRouteVarNameByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRouteVarName(), self.__list);
        return list(result);
    
    def searchRouteVarShortNameByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRouteVarShortName(), self.__list);
        return list(result);
    
    def searchRouteNoByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRouteNo(), self.__list);
        return list(result);
    
    def searchStartStopByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getStartStop(), self.__list);
        return list(result);
    
    def searchEndStopByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getEndStop(), self.__list);
        return list(result);
    
    def searchDistanceBy123(self, identifier = 0):
        result = filter(lambda x: str(identifier) in str(x.getDistance()), self.__list);
        return list(result);
    
    # default: identifier = True
    def searchOutbound(self, identifier = True):
        result = filter(lambda x: identifier == x.getOutbound(), self.__list);
        return list(result);
    
    def searchRunningTimeBy123(self, identifier = 0):
        result = filter(lambda x: str(identifier) in str(x.getRunningTime()), self.__list);
        return list(result);
    
    # output functions
    def outputAsCSV(self, list = []):
        check = lambda x: "True" if x == True else "False";
        def outstr(x):
            s = str(x.getRouteId()) + "," + str(x.getRouteVarId()) + "," + x.getRouteVarName() + "," + x.getRouteVarShortName() + "," + x.getRouteNo() + "," + x.getStartStop() + "," + x.getEndStop() + "," + str(x.getDistance()) + "," + check(x.getOutbound()) + "," + str(x.getRunningTime());
            return s;
        title = "RouteId,RouteVarId,RouteVarName,RouteVarShortName,RouteNo,StartStop,EndStop,Distance,Outbound,RunningTime";
        
        # open file
        file = open("outputRouteVar.csv", "w", encoding="utf8");
        
        file.write(title);
        file.write('\n');
        for i in list:
            file.write(outstr(i));
            file.write('\n');
            
        file.close();
          
    
    def outputAsJSON(self, list = []):
        with open('outputRouteVar.json', "w", encoding = 'utf8') as outfile:
            for i in list:
                json.dump(i.convertToDict(), outfile, ensure_ascii = False);
                outfile.write('\n');
        
        # file = open('data.txt');
        # data = file.read();
        # file.close();
        # print(data);
        
    # input function
    def loadFromFile(self, filename):
        # file = open('data.txt', 'w', encoding = "utf8");
        with open(filename, encoding = "utf8") as json_file:
            # read each line the the JSON file
            for line in json_file:
                data = json.loads(line);
                for i in data:
                    temp = RouteVar(i["RouteId"], i["RouteVarId"], i["RouteVarName"], i["RouteVarShortName"], i["RouteNo"], i["StartStop"], 
                                i["EndStop"], i["Distance"], i["Outbound"], i["RunningTime"]);
                    self.__list.append(temp);
                # file.write(str(data));
                # file.write('\n');
        
        # file.close()
    
    def loadDistTime(self, filename):
        dict = {}; # this dictionary stores the velocity of each routevar
        with open(filename, encoding = 'utf8') as json_file:
            # read each line the the JSON file
            for line in json_file:
                data = json.loads(line);
                for i in data:
                    temp = RouteVar(i["RouteId"], i["RouteVarId"], i["RouteVarName"], i["RouteVarShortName"], i["RouteNo"], i["StartStop"], 
                                i["EndStop"], i["Distance"], i["Outbound"], i["RunningTime"]);
                    dict[(temp.getRouteId(), temp.getRouteVarId())] = temp.getDistance()/temp.getRunningTime();
        return dict;


        

            
    
        
    
    
    
    