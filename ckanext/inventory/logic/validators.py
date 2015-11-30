from datetime import datetime
from ckanext.inventory.model import InventoryEntry
from ckan.plugins.toolkit import Invalid, _

def update_package_inventory_entry(value, context):
    model = context['model']
    session = context['session']

    if not value:
        raise Invalid(_('No inventory entry provided'))

    result = session.query(InventoryEntry).filter_by(id=value).first()

    if not result:
        raise Invalid(_('Not found') + ': %s' % value)

    # TODO @palcu: use a hook from IPackageController
    result.last_added_dataset_timestamp = datetime.now()
    result.save()

    return value
