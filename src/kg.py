import networkx as nx
import csv

class KG:
    def __init__(self):
        self.G = nx.DiGraph()

    def load_from_csv(self, nodes_csv, edges_csv):
        with open(nodes_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.G.add_node(row['id'], type=row['type'], name=row['name'])
        with open(edges_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.G.add_edge(row['source'], row['target'], rel=row['rel'])

    def get_company_directors(self, company_id):
        directors = []
        for u, v, d in self.G.edges(data=True):
            if v == company_id and d.get('rel') == 'DIRECTOR_OF':
                directors.append(self.G.nodes[u]['name'])
        return directors

    def find_company_node(self, company_name):
        for n,d in self.G.nodes(data=True):
            if d.get('type')=='Company' and d.get('name','').lower()==company_name.lower():
                return n
        return None
