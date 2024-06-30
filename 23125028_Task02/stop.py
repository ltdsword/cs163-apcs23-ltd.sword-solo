# import
from math import *
from abc import ABC, abstractmethod
from crs import *
import json

#### Stop definiton:
class Stop:
    # attributes
    __stopId = 0;
    __code = "";
    __name = "";
    __stopType = "";
    __zone = "";
    __ward = "";
    __addressNo = "";
    __street = "";
    __supportDisability = "";
    __status = "";
    __lng = 0.000000;
    __lat = 0.000000;
    __search = "";
    __routes = "";
    
    # methods
    def __init__(self, stopId = 0, code = "", name = "", stopType = "", zone = "", ward = "", addressNo = "", street = "", supportDisability = "", 
                 status = "", lng = 0.0000000, lat = 0.0000000, search = "", routes = ""):
        self.__stopId = stopId;
        self.__code = code if code != None else "";
        self.__name = name if name != None else "";
        self.__stopType = stopType if stopType != None else "";
        self.__zone = zone if zone != None else "";
        self.__ward = ward if ward != None else "";
        self.__addressNo = addressNo if addressNo != None else "";
        self.__street = street if street != None else "";
        self.__supportDisability = supportDisability if supportDisability != None else "";
        self.__status = status if status != None else "";
        self.__lng = lng if lng != None else 0;
        self.__lat = lat if lat != None else 0;
        self.__search = search if search != None else "";
        self.__routes = routes if routes != None else "";
    
    # setters
    def setStopId(self, stopId = 0):
        self.__stopId = stopId;
        
    def setCode(self, code = ""):
        self.__code = code;
        
    def setName(self, name = ""):
        self.__name = name;
    
    def setStopType(self, stopType = ""):
        self.__stopType = stopType;
    
    def setZone(self, zone = ""):
        self.__zone = zone;
    
    def setWard(self, ward = ""):
        self.__ward = ward;

    def setAddressNo(self, addressNo = ""):
        self.__addressNo = addressNo;
    
    def setStreet(self, street = ""):
        self.__street = street;
    
    def setSupportDisability(self, supportDisability = ""):
        self.__supportDisability = supportDisability;
    
    def setStatus(self, status = ""):
        self.__status = status;
    
    def setLng(self, lng = 0.000000):
        self.__lng = lng;
        
    def setLat(self, lat = 0.00000):
        self.__lat = lat;
    
    def setSearch(self, search = ""):
        self.__search = search;
    
    def setRoutes(self, routes = ""):
        self.__routes = routes;
    
    # getters
    def getStopId(self):
        return self.__stopId;
        
    def getCode(self):
        return self.__code;
        
    def getName(self):
        return self.__name;
    
    def getStopType(self):
        return self.__stopType;
    
    def getZone(self):
        return self.__zone;
    
    def getWard(self):
        return self.__ward;

    def getAddressNo(self):
        return self.__addressNo;
    
    def getStreet(self):
        return self.__street;
    
    def getSupportDisability(self):
        return self.__supportDisability;
    
    def getStatus(self):
        return self.__status;
    
    def getLng(self):
        return self.__lng;
    
    def getLat(self):
        return self.__lat;
    
    def getSearch(self, search):
        return self.__search;
    
    def getRoutes(self):
        return self.__routes;

    # convert to string type to write as CSV file
    def convertToString(self):
        return str(self.__stopId) + "," + self.__code + "," + self.__name + "," + self.__stopType + "," + self.__zone + "," + self.__ward + "," + self.__addressNo + "," + self.__street + "," + self.__supportDisability + "," + self.__status + "," + str(self.__lng) + "," + str(self.__lat) + "," + self.__search + "," + self.__routes;
    
    # convert to dict type to write as JSON file
    def convertToDict(self):
        return {"StopId": self.__stopId,
                "Code": self.__code,
                "Name": self.__name,
                "StopType": self.__stopType,
                "Zone": self.__zone,
                "Ward": self.__ward,
                "AddressNo": self.__addressNo,
                "Street": self.__street,
                "SupportDisability": self.__supportDisability,
                "Status": self.__status,
                "Lng": self.__lng,
                "Lat": self.__lat,
                "Search": self.__search,
                "Routes": self.__routes}


##### StopQuery definition:
class StopQuery:
    # attributes
    __list = [];
    
    # methods
    def __init__(self, list = []) -> None:
        self.__list = list;
    
    # setter
    def setListStop(self, list = []):
        self.__list = list;
        
    # getter
    def getListStop(self):
        return self.__list;
    
    # search functions
    def searchStopIdBy123(self, identifier = 0):
        result = filter(lambda x: str(identifier) in str(x.getStopId()), self.__list);
        return list(result);
    
    def searchCodeByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getCode(), self.__list);
        return list(result);
    
    def searchNameByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getName(), self.__list);
        ans = list(result);
        return ans;
    
    def searchStopTypeByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getStopType(), self.__list);
        return list(result);
    
    def searchZoneByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getZone(), self.__list);
        return list(result);
    
    def searchWardByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getWard(), self.__list);
        return list(result);
    
    def searchAddressNoByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getAddressNo(), self.__list);
        return list(result);
    
    def searchStreetByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getStreet(), self.__list);
        return list(result);
    
    def searchSupportDisabilityByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getSupportDisability(), self.__list);
        return list(result);
    
    def searchStatusByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getStatus(), self.__list);
        return list(result);
    
    def searchLngBy123(self, identifier = 0.0):
        result = filter(lambda x: str(identifier) in str(x.getLng()), self.__list);
        return list(result);
    
    def searchLatBy123(self, identifier = 0.0):
        result = filter(lambda x: str(identifier) in str(x.getLat()), self.__list);
        return list(result);
    
    def searchSearchByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getSearch(), self.__list);
        return list(result);
    
    def searchRoutesByABC(self, identifier = ""):
        result = filter(lambda x: identifier in x.getRoutes(), self.__list);
        return list(result);
    
    # output functions
    def outputAsCSV(self, list = []):
        title = "StopId,Code,Name,StopType,Zone,Ward,AddressNo,Street,SupportDisability,Status,Lng,Lat,Search,Routes";
        # open file
        file = open("outputStop.csv", "w", encoding = 'utf8');
        file.write(title);
        file.write('\n');
        for i in list:
            file.write(i.convertToString());
            file.write('\n');
    
    def outputAsJSON(self, list = []):
        with open("outputStop.json", "w", encoding = 'utf8') as outfile:
            for i in list:
                json.dump(i.convertToDict(), outfile, ensure_ascii= False);
                outfile.write('\n');
    
    # input function
    def loadFromFile(self, filename):
        dict = {};
        with open(filename, encoding = 'utf8') as infile:
            # read each line in the file
            for line in infile:
                data = json.loads(line);
                list = data["Stops"];
                for i in list:
                    temp = Stop(i["StopId"], i["Code"], i["Name"], i["StopType"], i["Zone"], i["Ward"], i["AddressNo"], i["Street"],
                                i["SupportDisability"], i["Status"], i["Lng"], i["Lat"], i["Search"], i["Routes"]);
                    if (temp.getStopId() not in dict):
                        dict[temp.getStopId()] = 1;
                        self.__list.append(temp);
    
    
    