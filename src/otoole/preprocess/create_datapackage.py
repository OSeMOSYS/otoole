import logging
import os
import sys

from datapackage import Package
from excel_to_osemosys import read_config
from longify_data import main as longify

logger = logging.getLogger()


def main(path_to_simplicity):
    """

    [{'fields': 'REGION', 'reference': {'resource': 'REGION', 'fields': 'VALUE'}}]
    """

    datapath = os.path.join(path_to_simplicity)
    package = Package(base_path=datapath)

    package.infer('data/*.csv')

    config = read_config()

    for resource in package.resources:

        name = resource.name
        if config[name]['type'] == 'param':

            foreign_keys = []

            indices = config[name]['indices']

            for index in indices:

                key = {'fields': index, 'reference': {'resource': index, 'fields': 'VALUE'}}

                foreign_keys.append(key)

            schema = resource.schema
            schema.descriptor['foreignKeys'] = foreign_keys
            schema.commit()

    filepath = os.path.join(path_to_simplicity, 'datapackage.json')
    package.save(filepath)


def validate_contents(path_to_data):

    filepath = os.path.join(path_to_data, 'datapackage.json')
    package = Package(filepath)

    for resource in package.resources:
        try:
            if resource.check_relations():
                logger.info("%s is valid", resource.name)
        except KeyError as ex:
            logger.warning("Validation error in %s: %s", resource.name, str(ex))


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    wide_folder = sys.argv[1]
    narrow_folder = sys.argv[2]

    longify(wide_folder, narrow_folder)

    main(narrow_folder)

    validate_contents(narrow_folder)
