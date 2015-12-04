from ckan.lib.dictization import table_dictize, table_dict_save
from ckan.plugins.toolkit import side_effect_free

from ckanext.inventory.model import InventoryItem, InventoryEntry


def inventory_item_create(context, data_dict):
    model = context['model']
    obj = table_dict_save(data_dict, InventoryItem, context)
    model.repo.commit()

    return table_dictize(obj, context)


@side_effect_free
def inventory_entry_list_items(context, data_dict):
    session = context['session']
    model = context['model']

    results = session.query(InventoryItem)\
                     .filter_by(inventory_entry_id=data_dict['inventory_entry_id'])
    return [(x.package_entry.id, x.package_entry.title) for x in results]
