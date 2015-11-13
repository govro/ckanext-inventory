import ckan.logic.schema
from ckan.plugins import (implements, IConfigurer, IGroupForm, IRoutes,
                          SingletonPlugin, IActions)
from ckan.plugins.toolkit import (
    add_template_directory, add_public_directory, add_resource,
    DefaultOrganizationForm, get_validator, get_converter)
from ckanext.inventory.logic.action import pending_user_list

class InventoryPlugin(SingletonPlugin, DefaultOrganizationForm):
    implements(IGroupForm, inherit=True)
    implements(IConfigurer)
    implements(IActions)
    implements(IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        add_template_directory(config_, 'templates')
        add_public_directory(config_, 'public')
        add_resource('fanstatic', 'inventory')

    # IRoutes
    def before_map(self, mapping):
        controller = 'ckanext.inventory.controllers.user:InventoryUserController'
        mapping.connect('/user/register', controller=controller,
                        action='register')
        return mapping

    def after_map(self, mapping):
        controller = 'ckanext.inventory.controllers.inventory:InventoryController'
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

    # IActions
    def get_actions(self):
        return {'inventory_pending_user_list': pending_user_list}
