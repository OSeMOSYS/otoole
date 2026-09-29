import tempfile

import networkx as nx
import pydot
import pytest

from otoole.visualise import create_res
from otoole.visualise.res import add_fuel, build_graph, draw_graph, extract_nodes

url = "tests/fixtures/simplicity-v0.2.1.zip"


@pytest.mark.skip(
    "pydot deprecated, requires replacement with pygraphviz "
    + "(https://github.com/OSeMOSYS/otoole/issues/121)"
)
def test_create_res():

    _, path_to_resfile = tempfile.mkstemp(suffix=".pdf")
    create_res(url, path_to_resfile)


@pytest.mark.parametrize("fuel_label", ["", "Imported fuel"])
def test_draw_graph_exports_fuel_labels(tmp_path, monkeypatch, fuel_label):
    nodes = add_fuel([["DKBF"]]) + extract_nodes([["SEWSSTPH1"]])
    graph = build_graph(nodes, [("DKBF", "SEWSSTPH1", {})])
    graph.nodes["DKBF"]["label"] = fuel_label
    rendered_graphs = []

    def render(dot_graph, **kwargs):
        rendered_graphs.append(dot_graph)
        return b""

    monkeypatch.setattr(pydot.Dot, "create", render)
    draw_graph(graph, str(tmp_path / "res.png"))

    exported = nx.read_graphml(tmp_path / "res.graphml")
    assert exported.nodes["DKBF"]["label"] == (fuel_label or "DKBF")
    assert exported.nodes["SEWSSTPH1"]["label"] == "SEWSSTPH1"
    assert exported.has_edge("DKBF", "SEWSSTPH1")
    assert graph.nodes["DKBF"]["label"] == fuel_label
    assert rendered_graphs[0].get_node("DKBF")[0].get_label() == fuel_label
