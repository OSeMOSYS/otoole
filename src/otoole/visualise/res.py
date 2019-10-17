"""Visualise the reference energy system
"""
import logging
import sys
from typing import Dict, List, Tuple

import networkx as nx
from datapackage import Package


def load_datapackage(path_to_datapackage: str):

    package = Package(path_to_datapackage)

    return package


def main(path_to_datapackage):

    package = load_datapackage(path_to_datapackage)

    # region = package.get_resource('REGION').read()

    technologies = package.get_resource('TECHNOLOGY').read()
    storage = package.get_resource('STORAGE').read()
    fuel = package.get_resource('FUEL').read()
    emission = package.get_resource('EMISSION').read()

    def extract_nodes(package_rows: List[List], node_type='technology',
                      color='red', shape='circle') -> List:
        nodes = [(x[0], {'type': node_type, 'name': x,
                         'fillcolor': color, 'shape': shape,
                         'style': 'filled'}
                  )
                 for x in package_rows]

        return nodes

    def add_fuel(package_rows: List[List]) -> List:
        nodes = [(x[0],
                 {'type': 'fuel', 'style': 'filled', 'shape': 'circle', 'height': 0.1, 'width': 0.1, 'label': ""})
                 for x in package_rows]
        return nodes

    def extract_edges(package_rows: List[Dict], from_column, to_column, value_attribute_name, from_edge: bool = True):
        """[]
        """
        if from_edge:
            edges = [(x[from_column], x[to_column],
                     {value_attribute_name: float(x['VALUE']), 'dir': 'none'})
                     for x in package_rows]
        else:
            edges = [(x[from_column], x[to_column],
                     {value_attribute_name: float(x['VALUE']), 'label': x[from_column]})
                     for x in package_rows]

        return edges

    nodes = extract_nodes(technologies, shape='rectangle', color='yellow')
    nodes += extract_nodes(storage, node_type='storage', shape='triangle', color='lightblue')
    nodes += add_fuel(fuel)
    nodes += extract_nodes(emission, node_type='emission', color='grey')
    nodes += [('AnnualDemand',
               {'type': 'demand', 'fillcolor': 'green',
                'name': 'AccumulatedAnnualDemand',
                'style': 'filled'}
               )
              ]

    input_activity = package.get_resource('InputActivityRatio').read(keyed=True)
    output_activity = package.get_resource('OutputActivityRatio').read(keyed=True)
    emission_activity = package.get_resource('EmissionActivityRatio').read(keyed=True)
    tech2storage = package.get_resource('TechnologyToStorage').read(keyed=True)
    techfromstorage = package.get_resource('TechnologyFromStorage').read(keyed=True)
    acc_demand = package.get_resource('AccumulatedAnnualDemand').read(keyed=True)
    spec_demand = package.get_resource('SpecifiedAnnualDemand').read(keyed=True)

    edges = extract_edges(input_activity, 'FUEL', 'TECHNOLOGY', 'input_ratio', from_edge=False)

    edges += extract_edges(output_activity, 'TECHNOLOGY', 'FUEL', 'output_ratio')

    edges += extract_edges(emission_activity, 'TECHNOLOGY', 'EMISSION', 'emission_ratio')

    edges += extract_edges(tech2storage, 'TECHNOLOGY', 'STORAGE', 'input_ratio')

    edges += extract_edges(techfromstorage, 'STORAGE', 'TECHNOLOGY', 'ouput_ratio')

    edges += [(x['FUEL'], 'AnnualDemand',
              {'Demand': float(x['VALUE']), 'label': x['FUEL']})
              for x in acc_demand]
    edges += [(x['FUEL'], 'AnnualDemand',
              {'Demand': float(x['VALUE']), 'label': x['FUEL']})
              for x in spec_demand]

    graph = build_graph(nodes, edges)
    draw_graph(graph)


def draw_graph(graph):

    pygraph = nx.nx_agraph.to_agraph(graph)
    pygraph.graph_attr['rankdir'] = 'LR'
    pygraph.graph_attr['splines'] = 'ortho'
    pygraph.graph_attr['concentrate'] = 'true'

    pygraph.layout(prog='dot')
    pygraph.draw('res.png')


def build_graph(nodes: List[Tuple], edges: List[Tuple[str, str, Dict]]):
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    main(path_to_datapackage)
