import csv
from cStringIO import StringIO

from ckan.plugins.toolkit import BaseController, render, c, get_action, response

class InventoryController(BaseController):
    def index(self):
        context = {'user': c.user}
        c.entries = get_action('inventory_entry_organization_summary')(context, {})
        return render('inventory/index.html')

    def get_inventory_entries_csv(self):
        context = {'user': c.user}
        entries = get_action('inventory_entry_csv')(context, {})

        response.headers['Content-Type'] = 'text/csv'
        s = StringIO()
        writer = csv.writer(s)

        writer.writerow(['nume_organizatie', 'nume_intrare_de_inventar', 'interval_de_recurenta', 'ultima_actualizare'])
        for entry in entries:
            writer.writerow(entry)

        return s.getvalue()
