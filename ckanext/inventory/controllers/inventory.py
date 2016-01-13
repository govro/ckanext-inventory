from ckan.plugins.toolkit import BaseController, render, c

class InventoryController(BaseController):
    def index(self):
        entries = [{
            'name': 'datagov',
            'id': 'datagov',
            'ontime_entries': 3,
            'late_entries': 2
        }]
        c.entries = entries
        return render('inventory/index.html')
