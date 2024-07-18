# import files
from pyproj import *
from math import *
from abc import ABC, abstractmethod
#from stop import *
from routevar import *
import time

# functions:
def convertToXY(lng = 0.00000, lat = 0.00000):
    spawn = time.time();
    target_crs = CRS.from_epsg(3405);
    source_crs = CRS.from_epsg(4326);
    print(time.time()-spawn);
    proj = Transformer.from_crs(source_crs, target_crs);
    x, y = proj.transform(lat, lng);
    return x,y if (x, y != inf, inf) else (0.000,0.000);

def distance(a = tuple(), b = tuple()):
    return sqrt(pow((a[0] - b[0]), 2) + pow((a[1] - b[1]), 2));

def check(x, y):
    return abs(x-y) <= 1e-5;

# driver code
# lat1 = 10.77304554;
# lat2 = 10.773046;
# st = time.time();
# for i in range (0,1):
#     p = check(lat1,lat2);
# print(p);
# print((time.time()-st));
