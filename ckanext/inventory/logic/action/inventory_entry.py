from ckan.plugins.toolkit import (
    check_access, side_effect_free, ObjectNotFound, get_or_bust, get_action)
from ckan.lib.dictization import table_dictize, table_dict_save

from ckanext.inventory.model import InventoryEntry


@side_effect_free
def inventory_entry_list(context, data_dict):
    '''Return a list of inventory entries.

    :param name: organization name
    :type name: string

    :rtype: list of dictionaries
    '''
    # TODO @palcu: define this
    # check_access('inventory_manage', context, data_dict)

    model = context['model']
    name = get_or_bust(data_dict, 'name')
    organization = model.Group.get(name)
    if not organization:
        raise ObjectNotFound('Organization was not found')

    return [table_dictize(entry, context)
            for entry in organization.inventory_entries]


def inventory_entry_create(context, data_dict):
    session = context['session']
    model = context['model']

    # TODO @palcu: remove hack
    data_dict['is_recurring'] = data_dict['recurring_interval'] > 0

    organization = get_action('organization_show')(context,
                                                   {'id': context['organization_name']})
    data_dict['group_id'] = organization['id']

    inventory_entry = table_dict_save(data_dict, InventoryEntry, context)
    model.repo.commit()

    # TODO @palcu: check something
    return {}
