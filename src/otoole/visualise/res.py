"""Visualise the reference energy system
"""
import logging
import sys
from typing import Dict, List, Tuple

import networkx as nx
from datapackage import Package

logger = logging.getLogger(__name__)


def load_datapackage(path_to_datapackage: str) -> Package:

    package = Package(path_to_datapackage)

    return package


def create_res(path_to_datapackage: str, path_to_resfile: str):
    """Create a reference energy system diagram from a Tabular Data Package

    Arguments
    ---------
    path_to_datapackage : str
        The path to the ``datapackage.json``
    path_to_resfile : str
        The path to the PNG file to be created
    """
    logger.debug(path_to_resfile, path_to_resfile)
    package = load_datapackage(path_to_datapackage)

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

    def add_fuel(package_rows: List[List]) -> List[Tuple[str, Dict]]:
        """Add fuel nodes

        Arguments
        ---------
        package_rows : list of dict

        Returns
        -------
        list of tuple
            A list of node names along with a dict of node attributes
        """
        nodes = [(x[0],
                 {'type': 'fuel', 'style': 'filled', 'shape': 'circle', 'height': 0.1, 'width': 0.1, 'label': ""})
                 for x in package_rows]
        return nodes

    def extract_edges(package_rows: List[Dict], from_column: str,
                      to_column: str, parameter_name: str,
                      directed: bool = True) -> List[Tuple[str, str, Dict]]:
        """Add edges from a Tabular Data Table

        Arguments
        ---------
        package_rows : list of dict
        from_column : str
            The name of the column to use as source of the edge
        to_column: str
            The name of the column to use as a destination of the edge
        parameter_name: str
            The name of the parameter
        directed: bool, default=True
            Specifies whether the edge should have an arrow or not

        Returns
        -------
        list of tuple
            A list of edges with from/to nodes names and edge attributes
        """
        if directed:
            edges = [(x[from_column], x[to_column],
                     {parameter_name: float(x['VALUE']), 'dir': 'none'})
                     for x in package_rows]
        else:
            edges = [(x[from_column], x[to_column],
                     {parameter_name: float(x['VALUE']), 'xlabel': x[from_column]})
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

    edges = extract_edges(input_activity, 'FUEL', 'TECHNOLOGY', 'input_ratio', directed=False)

    edges += extract_edges(output_activity, 'TECHNOLOGY', 'FUEL', 'output_ratio')

    edges += extract_edges(emission_activity, 'TECHNOLOGY', 'EMISSION', 'emission_ratio')

    edges += extract_edges(tech2storage, 'TECHNOLOGY', 'STORAGE', 'input_ratio')

    edges += extract_edges(techfromstorage, 'STORAGE', 'TECHNOLOGY', 'ouput_ratio')

    edges += [(x['FUEL'], 'AnnualDemand',
              {'Demand': float(x['VALUE']), 'xlabel': x['FUEL']})
              for x in acc_demand]
    edges += [(x['FUEL'], 'AnnualDemand',
              {'Demand': float(x['VALUE']), 'xlabel': x['FUEL']})
              for x in spec_demand]

    graph = build_graph(nodes, edges)
    draw_graph(graph, path_to_resfile)


def draw_graph(graph, path_to_resfile):
    """Layout the graph and write it to disk

    Uses pygraphviz to set some graph attributes, layout the graph
    and write it to disk

    Arguments
    ---------
    path_to_resfile : str
        The file path of the PNG image file that will be created
    """

    pygraph = nx.nx_agraph.to_agraph(graph)
    pygraph.graph_attr['rankdir'] = 'LR'
    pygraph.graph_attr['splines'] = 'ortho'
    pygraph.graph_attr['concentrate'] = 'true'

    pygraph.layout(prog='dot')
    pygraph.draw(path_to_resfile)


def build_graph(nodes: List[Tuple], edges: List[Tuple[str, str, Dict]]):
    """Builds the graph using networkx

    Arguments
    ---------
    nodes : list
    edges : list

    Returns
    -------
    networkx.DiGraph
        A directed graph representing the reference energy system
    """
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    path_to_datapackage = sys.argv[1]
    path_to_resfile = sys.argv[2]
    create_res(path_to_datapackage, path_to_resfile)
