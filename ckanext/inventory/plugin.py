import ckan.logic.schema
from routes.mapper import SubMapper
from ckan.lib.plugins import DefaultTranslation
from ckan.plugins import (
    implements, IConfigurer, IGroupForm, IRoutes, SingletonPlugin, IActions,
    IConfigurable, IDatasetForm, IValidators, ITranslation)
from ckan.plugins.toolkit import (
    add_template_directory, add_public_directory, add_resource,
    DefaultOrganizationForm, get_validator, get_converter, DefaultDatasetForm,
    get_action, c, add_ckan_admin_tab)
from ckanext.inventory.logic.action import (
    pending_user_list, activate_user, organization_by_inventory_id)
from ckanext.inventory.logic.action.inventory_entry import (
    inventory_entry_list, inventory_entry_create, inventory_organizations_show)
from ckanext.inventory.logic.validators import update_package_inventory_entry
from ckanext.inventory.model import model_setup


class InventoryPlugin(SingletonPlugin, DefaultOrganizationForm, DefaultTranslation):
    implements(IGroupForm)
    implements(IConfigurer)
    implements(IActions)
    implements(IConfigurable)
    implements(IRoutes, inherit=True)
    implements(ITranslation)

    # IConfigurer
    def update_config(self, config):
        add_template_directory(config, 'templates')
        add_public_directory(config, 'public')
        # TODO @palcu: translate this string
        add_ckan_admin_tab(config, 'inventory_admin_index', 'Activate Users')
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
                'inventory_entry_list': inventory_entry_list,
                'inventory_entry_create': inventory_entry_create,
                'inventory_organizations_show': inventory_organizations_show}

    # IConfigurable
    def configure(self, config):
        model_setup()


class InventoryPluginFix(SingletonPlugin, DefaultDatasetForm):
    '''Hack because methods from DefaultOrganizationForm overlap with
    DefaultDatasetForm. You should add inventory and invetoryfix to your config
    to load both classes.
    '''
    implements(IDatasetForm)
    implements(IValidators)

    # IDatasetForm
    def _modify_package_schema(self, schema):
        schema.update({
            'inventory_entry_id': [get_converter('convert_to_extras'),
                                   get_converter('update_package_inventory_entry')]
        })
        return schema

    def create_package_schema(self):
        schema = super(InventoryPluginFix, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(InventoryPluginFix, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(InventoryPluginFix, self).show_package_schema()
        schema.update({
            'inventory_entry_id': [get_converter('convert_from_extras'),
                                   get_validator('ignore_missing')]
        })
        return schema

    def setup_template_variables(self, context, data_dict):
        """Add inventory entries that the user has access to."""
        # TODO @palcu: send this to it's own logic method
        organizations = get_action('organization_list_for_user')(
            context, {'permission': 'create_dataset'})

        inventory_entries = []
        for organization in organizations:
            inventory_entries += get_action('inventory_entry_list')(
                context, {'name': organization['id']})
        c.inventory_entries = [(x['id'], x['title']) for x in inventory_entries]

        super(InventoryPluginFix, self).setup_template_variables(context,
                                                                 data_dict)

    def package_types(self):
        return ['dataset']

    # IValidators
    def get_validators(self):
        return {
            'update_package_inventory_entry': update_package_inventory_entry
        }

    def is_fallback(self):
        """Register as default handler for groups."""
        return False
