"""Visualise the reference energy system
"""
import logging
import os
from typing import Dict, List, Tuple

import networkx as nx  # mypy: ignore
import pandas as pd

from otoole.utils import get_packaged_resource

logger = logging.getLogger(__name__)


def extract_nodes(
    package_rows: List[List], node_type="technology", color="red", shape="circle"
) -> List[Tuple[str, Dict]]:
    """Add nodes from a Tabular Data Table

    Arguments
    ---------
    package_rows : list of dict
    node_type : str, default='technology'
    color : str, default='red'
    shape : str, default='circle'

    Returns
    -------
    list of tuple
        A list of nodes with attributes
    """
    nodes = [
        (
            x[0],
            {
                "type": node_type,
                "fillcolor": color,
                "shape": shape,
                "style": "filled",
                "label": x[0],
            },
        )
        for x in package_rows
    ]

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
    nodes = [
        (
            x[0],
            {
                "type": "fuel",
                "style": "filled",
                "shape": "circle",
                "height": 0.1,
                "width": 0.1,
                "label": "",
            },
        )
        for x in package_rows
    ]
    return nodes


def extract_edges(
    package_rows: List[Dict],
    from_column: str,
    to_column: str,
    parameter_name: str,
    directed: bool = True,
) -> List[Tuple[str, str, Dict]]:
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
        edges = [
            (
                x[from_column],
                x[to_column],
                {parameter_name: float(x["VALUE"]), "dir": "none"},
            )
            for x in package_rows
        ]
    else:
        edges = [
            (
                x[from_column],
                x[to_column],
                {parameter_name: float(x["VALUE"]), "xlabel": x[from_column]},
            )
            for x in package_rows
        ]

    return edges


def create_graph(input_data: Dict[str, pd.DataFrame]):
    """Creates a graph of technologies and fuels

    Arguments
    ---------
    input_data : Dict[str, pd.DataFrame]
        Internal datastore for otoole input data

    Returns
    -------
    graph
        networkx.DiGraph
    """

    technologies = [[x] for x in input_data["TECHNOLOGY"]["VALUE"]]
    storage = [[x] for x in input_data["STORAGE"]["VALUE"]]
    fuel = [[x] for x in input_data["FUEL"]["VALUE"]]
    emission = [[x] for x in input_data["EMISSION"]["VALUE"]]

    nodes = extract_nodes(technologies, shape="rectangle", color="yellow")
    nodes += extract_nodes(
        storage, node_type="storage", shape="triangle", color="lightblue"
    )
    nodes += add_fuel(fuel)
    nodes += extract_nodes(emission, node_type="emission", color="grey")
    nodes += [
        (
            "AnnualDemand",
            {
                "type": "demand",
                "fillcolor": "green",
                "label": "AccumulatedAnnualDemand",
                "style": "filled",
            },
        )
    ]

    input_activity = get_packaged_resource(input_data, "InputActivityRatio")
    output_activity = get_packaged_resource(input_data, "OutputActivityRatio")
    emission_activity = get_packaged_resource(input_data, "EmissionActivityRatio")
    tech2storage = get_packaged_resource(input_data, "TechnologyToStorage")
    techfromstorage = get_packaged_resource(input_data, "TechnologyFromStorage")
    acc_demand = get_packaged_resource(input_data, "AccumulatedAnnualDemand")
    spec_demand = get_packaged_resource(input_data, "SpecifiedAnnualDemand")

    edges = extract_edges(
        input_activity, "FUEL", "TECHNOLOGY", "input_ratio", directed=False
    )

    edges += extract_edges(output_activity, "TECHNOLOGY", "FUEL", "output_ratio")

    edges += extract_edges(
        emission_activity, "TECHNOLOGY", "EMISSION", "emission_ratio"
    )

    edges += extract_edges(tech2storage, "TECHNOLOGY", "STORAGE", "input_ratio")

    edges += extract_edges(techfromstorage, "STORAGE", "TECHNOLOGY", "ouput_ratio")

    edges += [
        (x["FUEL"], "AnnualDemand", {"Demand": float(x["VALUE"]), "xlabel": x["FUEL"]})
        for x in acc_demand
    ]
    edges += [
        (x["FUEL"], "AnnualDemand", {"Demand": float(x["VALUE"]), "xlabel": x["FUEL"]})
        for x in spec_demand
    ]

    graph = build_graph(nodes, edges)

    return graph


def create_res(input_data: Dict[str, pd.DataFrame], path_to_resfile: str):
    """Create a reference energy system diagram

    Arguments
    ---------
    input_data : Dict[str, pd.DataFrame]
        Internal datastore for otoole input data
    path_to_resfile : str
        The path to the image file to be created
    """

    graph = create_graph(input_data)
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
    for node, attributes in graph.nodes.data():
        logger.debug("%s: %s", node, attributes)
    for source, sink, attributes in graph.edges.data():
        logger.debug("%s-%s: %s", source, sink, attributes)

    filename, ext = os.path.splitext(path_to_resfile)
    nx.write_graphml(graph, filename + ".graphml")
    dot_graph = nx.nx_pydot.to_pydot(graph)

    dot_graph.set("rankdir", "LR")
    dot_graph.set("splines", "ortho")
    dot_graph.set("concentrate", "true")

    image_format = ext.strip(".")

    image = dot_graph.create(prog="dot", format=image_format)
    with open(path_to_resfile, "wb") as image_file:
        image_file.write(image)


def build_graph(
    nodes: List[Tuple[str, Dict]], edges: List[Tuple[str, str, Dict]]
) -> nx.DiGraph:
    """Builds the graph using networkx

    Arguments
    ---------
    nodes : list
        A list of node tuples
    edges : list
        A list of edge tuples

    Returns
    -------
    networkx.DiGraph
        A directed graph representing the reference energy system
    """
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph
