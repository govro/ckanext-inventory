import ckan.logic.schema
from routes.mapper import SubMapper
from ckan.plugins import (implements, IConfigurer, IGroupForm, IRoutes,
                          SingletonPlugin, IActions, IConfigurable)
from ckan.plugins.toolkit import (
    add_template_directory, add_public_directory, add_resource,
    DefaultOrganizationForm, get_validator, get_converter)
from ckanext.inventory.logic.action import (
    pending_user_list, activate_user, organization_by_inventory_id)
from ckanext.inventory.logic.action.inventory_entry import inventory_entry_list
from ckanext.inventory.model import model_setup


class InventoryPlugin(SingletonPlugin, DefaultOrganizationForm):
    implements(IGroupForm, inherit=True)
    implements(IConfigurer)
    implements(IActions)
    implements(IConfigurable)
    implements(IRoutes, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        add_template_directory(config_, 'templates')
        add_public_directory(config_, 'public')
        add_resource('fanstatic', 'inventory')

    # IRoutes
    def before_map(self, mapping):
        INVENTORY_USER_CONTROLLER = """
            ckanext.inventory.controllers.user:InventoryUserController"""
        mapping.connect('/user/register',
                        controller=INVENTORY_USER_CONTROLLER,
                        action='register')
        return mapping

    def after_map(self, mapping):
        INVENTORY_ADMIN_CONTROLLER = """
            ckanext.inventory.controllers.inventory_admin:InventoryAdminController"""
        with SubMapper(mapping, controller=INVENTORY_ADMIN_CONTROLLER) as m:
            m.connect('inventory_admin_index',
                      '/inventory/admin',
                      action='index')
            m.connect('inventory_activate_user',
                      '/inventory/admin/activate_user/{user_id}',
                      action='activate_user')

        INVENTORY_MANAGE_CONTROLLER = """
            ckanext.inventory.controllers.inventory_manage:InventoryManageController"""
        mapping.connect('/inventory/manage',
                        controller=INVENTORY_MANAGE_CONTROLLER,
                        action='index')

        INVENTORY_ENTRY_CONTROLLER = """
            ckanext.inventory.controllers.inventory_entry:InventoryEntryController"""
        with SubMapper(mapping, controller=INVENTORY_ENTRY_CONTROLLER) as m:
            m.connect('inventory_entry',
                      '/organization/entry/{organization_name}',
                      action='index')
            m.connect('inventory_entry_new',
                      '/organization/entry/{organization_name}/new',
                      action='new')
            m.connect('inventory_entry_edit',
                      '/organization/entry/{organization_name}/edit/{inventory_entry_id}',
                      action='edit')


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
        return {'inventory_pending_user_list': pending_user_list,
                'inventory_activate_user': activate_user,
                'inventory_organization_by_inventory_id': organization_by_inventory_id,
                'inventory_entry_list': inventory_entry_list}

    # IConfigurable
    def configure(self, config):
        model_setup()
