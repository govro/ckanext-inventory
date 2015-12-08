import unicodecsv
from os.path import isfile
import logging

from ckan import model
from ckan.lib.create_test_data import CreateTestData
from ckan.lib.munge import munge_title_to_name
from ckan.plugins.toolkit import CkanCommand, get_action, ValidationError


class GenerateOrganizationsCommand(CkanCommand):
    """
    Generate organizations and their IDs from a CSV.

    paster generate_organizations <CSV_PATH> -c <CONFIG_PATH>
    """

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2
    min_args = 1

    def __init__(self, name):
        super(GenerateOrganizationsCommand, self).__init__(name)

    def command(self):
        self._load_config()
        self.logger = logging.getLogger(__name__)

        if len(self.args) != 2:
            self.logger.error('You must specify the path to the CSV and admin user')
            return

        csv_path, admin_user_name = self.args

        if not isfile(csv_path):
            self.logger.error('CSV file does not exist at that path')
            return

        group_dicts = self.create_organization_dicts_from_csv(csv_path)
        CreateTestData().create_groups(group_dicts, admin_user_name)

    def create_organization_dicts_from_csv(self, csv_path):
        group_dicts = []
        with open(csv_path) as csvfile:
            reader = unicodecsv.reader(csvfile, delimiter='|')
            for i, row in enumerate(reader):
                if len(row) != 2:
                    self.logger.error('Invalid CSV row {0}'.format("".join(row)))
                else:
                    group_dicts.append(self.create_organization_dict(row[0], row[1]))
        return group_dicts

    def create_organization_dict(self, inventory_id, title):
        return {
            'name': munge_title_to_name(title),
            'title': title,
            'inventory_organization_id': inventory_id,
            'is_organization': True,
            'type': 'organization',
        }
