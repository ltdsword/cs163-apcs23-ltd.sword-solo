from stop import*
from routevar import*
from path import*
from abc import ABC, abstractmethod
from math import*
import json

class Map:
    points = [];
    lines = [];
    polygons = [];
    
    def __init__(self, points = [], lines = [], polygons = []) -> None:
        self.points = points;
        self.lines = lines;
        self.polygons = polygons;
    
    def addPoint(self, point = []):
        if len(point) == 0:
            return;
        else:
            self.points.append(point);
    
    def addLine(self, line = []):
        if len(line) == 0:
            return;
        else:
            self.lines.append(line);
    
    def addPolygon(self, polygon = []):
        if len(polygon) == 0:
            return;
        else:
            self.polygons.append(polygon);
    
    def addPointInLine(self, index, point = []):
        if (len(point) == 0):
            return;
        else:
            self.lines[index].append(point);
    
    def addPointInPolygon(self, index, point = []):
        if (len(point) == 0):
            return;
        else:
            self.polygons[index].append(point);
    
    def spawnMap(self, filename):
        # the structure of a geojson file
        dict = {
            "type": "FeatureCollection",
            "features": [
            ]
        }
        
        # x = [lat, lng]
        point = lambda x: {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "coordinates": x,
                "type": "Point"
            }
        }
        
        # x = [[lat, lng], [lat, lng], ....]
        line = lambda x: {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": x,
                    "type": "LineString"
                }
            }
        
        # polygon x = [[lat, lng], [lat, lng], ....];
        polygon = lambda x: {
            "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": x,
                    "type": "Polygon"
                }
        }
        
        for i in self.points:
            dict["features"].append(point(i));
        for i in self.lines:
            dict["features"].append(line(i));
        for i in self.polygons:
            dict["features"].append(polygon(i));
        
        with open(filename, 'w', encoding = 'utf8') as file:
            json.dump(dict, file, ensure_ascii=False, indent=4);


# driver code
# obj = PathQuery();
# obj.loadFronFile("Questions/paths.json");
# stops = StopQuery();
# stops.loadFromFile("Questions/stops.json");
# list = stops.getListStop();

# with open("result.json", "r", encoding='utf8') as file:
#     data = json.load(file);
#     lat = data["lat"];
#     lng = data["lng"];
#     points = [];
#     for i in range(0, len(lng)):
#         points.append([lng[i], lat[i]]);

#spawn json file

# jmap = Map();
# jmap.addLine(points);
# # for path in obj.getListPath():
# #      lng = path.getLng();
# #      lat = path.getLat();
# #      points = [];
# #      for i in range(0, len(lng)):
# #          points.append([lng[i], lat[i]]);
# #      jmap.addLine(points);

# # for stop in list:
# #      lng = stop.getLng();
# #      lat = stop.getLat();
# #      jmap.addPoint([lng, lat]);
# jmap.spawnMap("points.geoJSON");
            
        