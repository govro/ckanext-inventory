import ckan.logic.schema
from ckan.plugins import (implements, IConfigurer, IGroupForm, IRoutes,
    SingletonPlugin)
from ckan.plugins.toolkit import (add_template_directory,
    add_public_directory, add_resource, DefaultOrganizationForm,
    get_validator, get_converter)


class InventoryPlugin(SingletonPlugin, DefaultOrganizationForm):
    implements(IGroupForm, inherit=True)
    implements(IConfigurer)
    implements(IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        add_template_directory(config_, 'templates')
        add_public_directory(config_, 'public')
        add_resource('fanstatic', 'inventory')

    # IRoutes
    def after_map(self, mapping):
        controller = 'ckanext.inventory.controllers:InventoryController'
        mapping.connect('/inventory', controller=controller, action='index')

        return mapping

    # IGroupForm
    def form_to_db_schema(self):
        schema = super(InventoryPlugin, self).form_to_db_schema()
        schema.update({
            'inventory_organization_id': [
                get_validator('ignore_missing'),
                get_converter('convert_to_extras')]
        })
        return schema

    def db_to_form_schema(self):
        schema = ckan.logic.schema.default_show_group_schema()
        schema.update({
            'inventory_organization_id': [
                get_validator('ignore_missing'),
                get_converter('convert_from_extras')]
        })
        return schema

    def is_fallback(self):
        """Register as default handler for groups."""
        return False

    def group_types(self):
        """This should handle only organizations, not other types of groups."""
        return ['organization']
