from datetime import timedelta

from ckan.model import Group, GroupExtra
from ckan.plugins.toolkit import (
    side_effect_free, ObjectNotFound, get_or_bust, get_action)
from ckan.lib.dictization import table_dictize, table_dict_save
from ckan.lib.helpers import _datestamp_to_datetime

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

    entries = [table_dictize(entry, context) for entry in organization.inventory_entries]

    for entry in entries:
        last_added = _datestamp_to_datetime(entry['last_added_dataset_timestamp'])
        delta = timedelta(days=entry['recurring_interval'])
        entry['next_deadline_timestamp'] = last_added + delta
    return entries


def inventory_entry_create(context, data_dict):
    model = context['model']

    # TODO @palcu: remove hack
    data_dict['is_recurring'] = data_dict['recurring_interval'] > 0

    organization = get_action('organization_show')(
        context, {'id': context['organization_name']})
    data_dict['group_id'] = organization['id']

    table_dict_save(data_dict, InventoryEntry, context)
    model.repo.commit()

    # TODO @palcu: check something saved entry is ok
    return {}


def inventory_organizations_show(context, data_dict):
    model = context['model']
    pairs = model.Session.query(Group, GroupExtra).join(GroupExtra)
    return [(pair[1].value, " - ".join([pair[1].value, pair[0].title])) for pair in pairs]
