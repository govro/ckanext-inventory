from ckan.plugins.toolkit import BaseController, render, c, get_action

class InventoryController(BaseController):
    def index(self):
        context = {'user': c.user}
        entries = [{
            'name': 'datagov',
            'id': 'datagov',
            'ontime_entries': 3,
            'late_entries': 2
        }]
        c.entries = get_action('inventory_entry_organization_summary')(context, {})
        return render('inventory/index.html')
