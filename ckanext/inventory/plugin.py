import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class InventoryPlugin(plugins.SingletonPlugin, toolkit.DefaultGroupForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'inventory')

    # IRoutes
    def after_map(self, mapping):
        controller = 'ckanext.inventory.controllers:InventoryController'
        mapping.connect('/inventory', controller=controller, action='index')

        return mapping

    # IGroupForm
    def _modify_group_schema(self, schema):
        schema.update({
            'inventory_organization_id': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')]
        })
        return schema

    def create_group_schema(self):
        schema = super(InventoryPlugin, self).create_group_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def update_group_schema(self):
        schema = super(InventoryPlugin, self).update_group_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def show_group_schema(self):
        schema = super(InventoryPlugin, self).show_group_schema()
        schema.update({
            'inventory_organization_id': [
                tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
        })
        return schema

    def is_fallback(self):
        """Register as default handler for groups."""
        return True

    def group_types(self):
        """This should handle only organizations, not other types of groups."""
        return ['organization']
