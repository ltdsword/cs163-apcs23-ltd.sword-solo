from math import*
import osmium as osm
from lxml import etree
import json
from collections import defaultdict

# tree = etree.parse("HoChiMinh.osm")
# root = tree.getroot()

# nodes = []
# for node in root.findall('node'):
#     node_id = node.get('id')
#     lat = node.get('lat')
#     lon = node.get('lon')
#     tags = {tag.get('k'): tag.get('v') for tag in node.findall('tag')}
#     nodes.append({
#         'id': node_id,
#         'location': (lat, lon),
#         'tags': tags
#     })


# ways = []
# for way in root.findall('way'):
#     way_id = way.get('id')
#     nodes = [nd.get('ref') for nd in way.findall('nd')]
#     tags = {tag.get('k'): tag.get('v') for tag in way.findall('tag')}
#     ways.append({
#         'id': way_id,
#         'nodes': nodes,
#         'tags': tags
#     })

# relations = []
# for relation in root.findall('relation'):
#     relation_id = relation.get('id')
#     members = [(m.get('ref'), m.get('role'), m.get('type')) for m in relation.findall('member')]
#     tags = {tag.get('k'): tag.get('v') for tag in relation.findall('tag')}
#     relations.append({
#         'id': relation_id,
#         'members': members,
#         'tags': tags
#     })

# print(f"Number of nodes: {len(nodes)}")
# print(f"Number of ways: {len(ways)}")
# print(f"Number of relations: {len(relations)}")

class HCMGraph(osm.SimpleHandler):
    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.adjNode = defaultdict(dict)
    
    def node(self, n):
        # initialize the dictionary with the id of the node
        self.nodes[n.id] = {
            'location': (n.location.lat, n.location.lon),
            'tags': dict(n.tags)
        }
    
    def way(self, w):
        self.ways[w.id] = {
            'nodes': [str(n.ref) for n in w.nodes],
            'tags': dict(w.tags)
        }

    def relation(self, r):
        self.relations[r.id] = {
            # ref = id of type of the member
            # role = role of the member in the relation (city, subarea, etc.)
            # type = type of the member (relation...)
            'members': [(str(m.ref), str(m.role), str(m.type)) for m in r.members],
            'tags': dict(r.tags)
        }
    
    def structurize(self):
        # structurize the data as graph
        # the adjacency list of the nodes comes from the ways
        # adjNode stucture = {node_id: {
        #   node_id1: way1_id,
        #   node_id2: way2_id,
        #   ...
        # }}
        #---------------------------------------------------------
        
        for way_id, way in self.ways.items():
            for i in range(len(way['nodes']) - 1):
                self.adjNode[way['nodes'][i]][way['nodes'][i + 1]] = way_id
                self.adjNode[way['nodes'][i + 1]][way['nodes'][i]] = way_id
    
    def outputAsJSON(self):
        #output to 3 files in UTF-8
        with open('nodes.json', 'w', encoding= 'utf8') as f:
            json.dump(self.nodes, f, ensure_ascii=False)
        with open('ways.json', 'w', encoding='utf8') as f:
            json.dump(self.ways, f, ensure_ascii=False)
        with open('relations.json', 'w', encoding = 'utf8') as f:
            json.dump(self.relations, f, ensure_ascii=False)
        with open('adjNode.json', 'w', encoding = 'utf8') as f:
            json.dump(self.adjNode, f, ensure_ascii=False)
    
    def importData(self, nodefile, wayfile, relationfile):
        with open(nodefile, 'r', encoding='utf8') as f:
            self.nodes = json.load(f)
        with open(wayfile, 'r', encoding='utf8') as f:
            self.ways = json.load(f)
        with open(relationfile, 'r', encoding='utf8') as f:
            self.relations = json.load(f)
        with open('adjNode.json', 'r', encoding='utf8') as f:
            self.adjNode = json.load(f)

# handler = HCMGraph()
# handler.apply_file("HoChiMinh.osm")
# handler.structurize()

# handler.outputAsJSON()

# # print the nodes
# print(f"Number of nodes: {len(handler.nodes)}")
# print(f"Number of ways: {len(handler.ways)}")
# print(f"Number of relations: {len(handler.relations)}")
