#import files
from routevar import *
from stop import *
from path import *

#functions
def run():
    print("Run the program successfully.")
    obj = RouteVarQuery();
    obj.loadFromFile("Questions/vars.json");
    list = obj.searchRouteVarNameByABC("Lượt đi:");
    obj.outputAsCSV(obj.getListRouteVar());
    obj.outputAsJSON(list);
    
def run2():
    obj = StopQuery();
    obj.loadFromFile("Questions/stops.json");
    list = obj.searchStatusByABC("Đang khai thác");
    print(len(list));
    obj.outputAsCSV(list);
    obj.outputAsJSON(obj.getListStop());
    
def run3():
    obj = PathQuery();
    cnt = obj.loadFronFile("Questions/paths.json");
    lst = obj.getListPath();
    print(len(lst[4].getLng()));
    list = obj.searchLengthLatBy123(70);
    print(len(list));
    obj.outputAsJSON(list);
    obj.outputAsCSV(obj.getListPath());
    print(cnt);

#driver code
run3();