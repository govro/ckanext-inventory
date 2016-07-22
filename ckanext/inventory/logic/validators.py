from datetime import datetime
from ckanext.inventory.model import InventoryEntry
from ckan.plugins.toolkit import Invalid, _


def inventory_package_id_exists(value, context):
    session = context['session']

    if not value:
        raise Invalid(_('No inventory entry provided'))

    result = session.query(InventoryEntry).filter_by(id=value).first()

    if not result:
        raise Invalid(_('Not found') + ': %s' % value)

    return value
