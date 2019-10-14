"""Visualise the reference energy system
"""
import logging
import sys
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
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

    def extract_nodes(package_rows: List[List], node_type='technology', color='red', shape='circle') -> List:
        nodes = [(x[0], {'type': node_type, 'name': x,
                         'fillcolor': color, 'shape': shape,
                         'style': 'filled'})
                 for x in package_rows]

        return nodes

    nodes = extract_nodes(technologies, shape='square', color='yellow')
    nodes += extract_nodes(storage, node_type='storage', shape='triangle', color='blue')
    nodes += extract_nodes(fuel, node_type='fuel', color='white')
    nodes += extract_nodes(emission, node_type='emission', color='grey')

    input_activity = package.get_resource('InputActivityRatio').read(keyed=True)
    output_activity = package.get_resource('OutputActivityRatio').read(keyed=True)
    emission_activity = package.get_resource('EmissionActivityRatio').read(keyed=True)

    edges = [(x['FUEL'], x['TECHNOLOGY'], {'input_ratio': float(x['VALUE'])}) for x in input_activity]

    edges += [(x['TECHNOLOGY'], x['FUEL'], {'output_ratio': float(x['VALUE'])}) for x in output_activity]

    edges += [(x['TECHNOLOGY'], x['EMISSION'], {'emission_ratio': float(x['VALUE'])}) for x in emission_activity]

    graph = build_graph(nodes, edges)
    draw_graph(graph)


def draw_graph(graph):

    pos = nx.nx_agraph.graphviz_layout(graph, prog='neato')

    nx.nx_agraph.write_dot(graph, 'file.dot')
    nx.draw_networkx(graph, pos=pos)
    # write_dot(graph, 'file.dot')
    plt.savefig("res.png")


def build_graph(nodes: List[Tuple], edges: List[Tuple[str, str, Dict]]):
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    main(path_to_datapackage)
