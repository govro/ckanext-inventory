from ckan.lib.dictization import table_dictize, table_dict_save

from ckanext.inventory.model import InventoryItem


def inventory_item_create(context, data_dict):
    model = context['model']
    obj = table_dict_save(data_dict, InventoryItem, context)
    model.repo.commit()

    return table_dictize(obj, context)
