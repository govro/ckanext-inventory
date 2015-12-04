from datetime import timedelta, datetime

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
        entry['next_deadline_timestamp'] = None
        if entry['last_added_dataset_timestamp']:
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

    obj = table_dict_save(data_dict, InventoryEntry, context)
    model.repo.commit()

    return table_dictize(obj, context)


def inventory_entry_update_timestamp(context, data_dict):
    session = context['session']

    result = session.query(InventoryEntry)\
                    .filter_by(id=data_dict['inventory_entry_id']).first()
    result.last_added_dataset_timestamp = datetime.now()
    result.save()


@side_effect_free
def inventory_organization_show(context, data_dict):
    model = context['model']
    group_extra = model.Session.query(model.GroupExtra) \
                       .filter_by(key='inventory_organization_id') \
                       .filter_by(value=data_dict['inventory_organization_id']) \
                       .first()

    if not group_extra:
        raise ObjectNotFound('Group extra was not found')

    organization = model.Group.get(group_extra.group_id)

    if not organization:
        raise ObjectNotFound('Organization was not found')

    return {'title': organization.title}
