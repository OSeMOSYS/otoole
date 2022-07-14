"""Creates a datapackage from a collection of CSV files of OSeMOSYS input data

- Uses Frictionless Data datapackage concept to build a JSON schema of the dataset
- Enforces relations between sets and indices in parameter files
"""

import logging
import os
from frictionless import Package
from typing import Dict

logger = logging.getLogger()


def generate_package(package: Package, config: Dict[str, Dict]) -> Package:
    """Adds schema information to a basic Resource

    Arguments
    ---------
    package: Package
        A frictionless Package
    config: Dict[str, Dict]
        A user-configuration dictionary

    Returns
    -------
    dict

    Notes
    -----
    [{'fields': 'REGION', 'reference': {'resource': 'REGION', 'fields': 'VALUE'}}]
    """

    logger.debug(f"Auto-identified resources {package.resources}")

    # package.licenses = [
    #     {
    #         "name": "CC-BY-4.0",
    #         "path": "https://creativecommons.org/licenses/by/4.0/",
    #         "title": "Creative Commons Attribution 4.0",
    #     }
    # ]

    # package.title = "The OSeMOSYS Simplicity Example Model"

    # package.name = "osemosys_model_simplicity"

    # package.contributors = [
    #     {
    #         "title": "Will Usher",
    #         "email": "wusher@kth.se",
    #         "path": "https://www.kth.se/profile/wusher/",
    #         "role": "author",
    #     }
    # ]

    for resource in package.resources:  # typing: Resource

        name = resource.title  # Use the title which preserves case

        logger.debug(f"Updating resource '{name}'")

        if config[name]["type"] == "param":

            indices = config[name]["indices"]
            logger.debug("Indices of %s are %s", name, indices)

            fields = []
            foreign_keys = []
            for index in indices:
                key = {
                    "fields": index,
                    "reference": {"resource": index.lower(), "fields": "VALUE"},
                }
                foreign_keys.append(key)
                field = {"name": index, "type": config[index]["dtype"]}

                fields.append(field)

            value_field = {"name": "VALUE", "type": config[name]["dtype"]}

            fields.append(value_field)

            resource.schema.fields = fields
            resource.schema.foreign_keys = foreign_keys
            resource.schema.primary_key = indices
            resource.schema.missing_values = [""]

        elif config[name]["type"] == "set":

            fields = []
            value_field = {"name": "VALUE", "type": config[name]["dtype"]}

            fields.append(value_field)
            resource.schema.fields = fields
            resource.schema.missing_values = [""]

        logger.debug(f"Schema for resource {name}: {resource.schema}")

    return package


def validate_contents(path_to_package):

    filepath = os.path.join(path_to_package)
    package = Package(filepath)

    for resource in package.resources:
        try:
            if resource.check_relations():
                logger.info("%s is valid", resource.name)
        except KeyError as ex:
            logger.warning("Validation error in %s: %s", resource.name, str(ex))
