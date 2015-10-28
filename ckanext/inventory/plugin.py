import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class InventoryPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

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
