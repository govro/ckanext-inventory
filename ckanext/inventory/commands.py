import unicodecsv
from os.path import isfile
import logging

from ckan import model
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

        self.context = {
            'model': model,
            'session': model.Session,
            'ignore_auth': True,
        }

        admin_user = get_action('user_show')(self.context, {'id': admin_user_name})
        self.context['user'] = admin_user['name']

        self.create_organizations_from_csv(csv_path)

    def create_organizations_from_csv(self, csv_path):
        with open(csv_path) as csvfile:
            reader = unicodecsv.reader(csvfile, delimiter='|')
            for i, row in enumerate(reader):
                if i > 50: break
                if len(row) != 2:
                    self.logger.error('Invalid CSV row {0}'.format("".join(row)))
                else:
                    self.create_organization(row[0], row[1])

    def create_organization(self, inventory_id, title):
        name = self.namefy(title)

        params = {
            'name': name,
            'title': title,
            'inventory_organization_id': inventory_id,
            'defer_commit': True,
        }

        try:
            organization = get_action('organization_create')(self.context, params)
            self.logger.info('{0} created with id {1}'.format(organization['name'], organization['id']))
        except ValidationError, e:
            try:
                self.logger.error('{0} - {1}'.format(name, e.error_summary))
            except Exception:
                pass

    def namefy(self, title):
        res = []
        for c in title:
            if c.isalnum():
                res.append(c.lower())
            elif c == ' ':
                res.append('-')
        return "".join(res)
