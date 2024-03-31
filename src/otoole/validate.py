"""Ensures that technology and fuel names match the convention

For example, to validate the following list of names, you would use the
config shown below::

    theseUNIQUE_ENTRY1
    are__UNIQUE_ENTRY2
    all__UNIQUE_ENTRY1
    validUNIQUE_ENTRY2
    entryUNIQUE_ENTRY1
    in__UNIQUE_ENTRY2
    a____UNIQUE_ENTRY1
    list_UNIQUE_ENTRY2

Create a yaml validation config with the following format::

    codes:
      some_valid_codes:
        UNIQUE_ENTRY1: Description of unique entry 1
        UNIQUE_ENTRY2: Description of unique entry 2
    schema:
      schema_name:
      - name: first_entry_in_schema
        valid: ['these', 'are__', 'all__', 'valid', 'entry', 'in__', 'a____', 'list_']
        position: (1, 5) # a tuple representing the start and end position
      - name: second_entry_in_schema
        valid: some_valid_codes  # references an entry in the codes section of the
        config
        position: (6, 19) # a tuple representing the start and end position

"""

import logging
import re
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

import networkx.algorithms.isolate as isolate
import pandas as pd

from otoole.utils import get_packaged_resource, read_packaged_file
from otoole.visualise.res import create_graph

logger = logging.getLogger(__name__)


def read_validation_config():
    return read_packaged_file("validate.yaml", "otoole")


def check_for_duplicates(codes: Sequence) -> bool:
    duplicate_values = len(codes) != len(set(codes))
    return duplicate_values


def create_schema(config: Optional[Dict[str, Dict]] = None) -> Dict:
    """Populate the dict of schema with codes from the validation config

    Arguments
    ---------
    config : dict, default=None
        A configuration dictionary containing ``codes`` and ``schema`` keys
    """
    if config is None:
        config = read_validation_config()

    for resource_name, resource_schemas in config["schema"].items():
        logger.debug("%s", resource_name)
        for schema in resource_schemas:

            for items in schema["items"]:  # typing: List

                if isinstance(items["valid"], str):
                    items["valid"] = list(
                        config["codes"][items["valid"]].keys()
                    )  # typing: List
                    logger.debug("create_schema: %s", items["valid"])
                elif isinstance(items["valid"], list):
                    pass
                else:
                    raise ValueError("Entry {} is not correct".format(schema["name"]))

                if check_for_duplicates(items["valid"]):
                    raise ValueError(
                        "There are duplicate values in codes for {}", schema["name"]
                    )

    return config["schema"]


def compose_expression(schema: List) -> str:
    """Generates a regular expression from a schema

    Returns
    -------
    str
    """
    expression = "^"
    for x in schema:
        logger.debug("compose_expression: %s", x["valid"])
        valid_entries = "|".join(x["valid"])
        expression += "({})".format(valid_entries)
    return expression


def compose_multi_expression(resource: List) -> str:
    """Concatenates multiple expressions using an OR operator

    Use to validate elements using an OR operation e.g. the elements
    must match this expression OR the expression
    """
    expressions = []
    for schemas in resource:
        expressions.append(compose_expression(schemas["items"]))
    return "|".join(expressions)


def validate(expression: str, name: str) -> bool:
    """Determine if ``name`` matches the ``expression``

    Arguments
    ---------
    expression : str
    name : str

    Returns
    -------
    bool
    """
    logger.debug("Running validation for %s", name)

    valid = False

    pattern = re.compile(expression)

    if pattern.fullmatch(name):
        valid = True
    else:
        valid = False
    return valid


def validate_resource(
    input_data: Dict[str, pd.DataFrame], resource: str, schemas: List[Dict]
) -> None:
    """Validates a single resource against the validation config.

    Arguments
    ---------
    input_data: dict[str,pd.DataFrame]
        otoole internal datastore
    resource: str
    schemas : List[Dict]
        The schema from which to create a validation expression
    """

    print(
        "Validating {} with {}\n".format(
            resource, ", ".join([x["name"] for x in schemas])
        )
    )

    logger.debug(schemas)

    expression = compose_multi_expression(schemas)
    resources = get_packaged_resource(input_data, resource)

    valid_names = []
    invalid_names = []

    for row in resources:
        name = row["VALUE"]
        valid = validate(expression, row["VALUE"])
        if valid:
            valid_names.append(name)
        else:
            invalid_names.append(name)

    if invalid_names:
        msg = "{} invalid names:\n{}\n"
        print(msg.format(len(invalid_names), ", ".join(invalid_names)))
    if valid_names:
        msg = "{} valid names:\n{}\n"
        print(msg.format(len(valid_names), ", ".join(valid_names)))


def identify_orphaned_fuels_techs(
    input_data: Dict[str, pd.DataFrame]
) -> Dict[str, str]:
    """Returns a list of fuels and technologies which are unconnected

    Returns
    -------
    dict

    """
    graph = create_graph(input_data)

    number_of_isolates = isolate.number_of_isolates(graph)
    logger.debug("There are {} isolated nodes in the graph".format(number_of_isolates))

    isolated_nodes: Dict = defaultdict(list)

    for node_name in list(isolate.isolates(graph)):
        node_data = graph.nodes[node_name]
        isolated_nodes[node_data["type"]].append(node_name)

    return isolated_nodes


def main(input_data: Dict[str, pd.DataFrame], config=None):

    print("\n***Beginning validation***\n")
    schema = create_schema(config)

    for resource, schemas in schema.items():
        validate_resource(input_data, resource, schemas)

    print("\n***Checking graph structure***")
    isolated_nodes = identify_orphaned_fuels_techs(input_data)

    msg = ""
    for node_type, node_names in isolated_nodes.items():
        msg += "\n{} '{}' nodes are isolated:\n     {}\n".format(
            len(node_names), node_type, ", ".join(node_names)
        )
    print(msg)
