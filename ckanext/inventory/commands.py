import csv
from os.path import isfile
import logging

from ckan.plugins.toolkit import CkanCommand


class GenerateOrganizationsCommand(CkanCommand):
    """
    Generate organizations and their IDs from a CSV.

    paster generate_organizations <CSV_PATH> -c <CONFIG_PATH>
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def __init__(self, name):
        super(GenerateOrganizationsCommand, self).__init__(name)

    def command(self):
        self._load_config()
        self.log = logging.getLogger(__name__)

        if len(self.args) != 1:
            self.log.error('You must specify the path to the CSV')
            return

        csv_path = self.args[0]
        if not isfile(csv_path):
            self.log.error('CSV file does not exist at that path')
            return

        self.create_organizations_from_csv(csv_path)

    def create_organizations_from_csv(self, csv_path):
        with open(csv_path) as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            for row in reader:
                if len(row) > 2:
                    self.log.error('Invalid CSV row {0}'.format("".join(row)))
                else:
                    self.create_organization(row[0], row[1])

    def create_organization(self, id, name):
        pass
