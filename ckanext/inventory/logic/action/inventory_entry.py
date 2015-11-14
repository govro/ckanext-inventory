from ckan.plugins.toolkit import (
    check_access, side_effect_free, ObjectNotFound, get_or_bust)
from ckan.lib.dictization import table_dictize


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

    return [table_dictize(entry) for entry in organization.inventory_entries]
