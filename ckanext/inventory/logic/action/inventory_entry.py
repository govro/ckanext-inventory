from collections import defaultdict
from datetime import timedelta, datetime

import ckan.authz as authz
from ckan.plugins.toolkit import (
    side_effect_free, ObjectNotFound, get_or_bust, check_access,
    navl_validate, ValidationError)
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

    entries = [
        table_dictize(entry, context) for entry in organization.inventory_entries]

    for entry in entries:
        entry['next_deadline_timestamp'] = None
        if entry['last_added_dataset_timestamp']:
            last_added = _datestamp_to_datetime(entry['last_added_dataset_timestamp'])
            delta = timedelta(days=entry['recurring_interval'])
            entry['next_deadline_timestamp'] = last_added + delta
    return entries


@side_effect_free
def inventory_entry_organization_summary(context, data_dict):
    model = context['model']
    good_entries = defaultdict(int)
    late_entries = defaultdict(int)
    no_entries = defaultdict(int)
    organizations = {}
    inventory_entries = model.Session.query(InventoryEntry).join(model.Group)
    for entry in inventory_entries:
        if not entry.last_added_dataset_timestamp or entry.is_recurring == False:
            no_entries[entry.group_id] += 1
            continue

        next_date = entry.last_added_dataset_timestamp + timedelta(days=entry.recurring_interval)
        if next_date > datetime.now():
            good_entries[entry.group_id] += 1
        else:
            late_entries[entry.group_id] += 1
        organizations[entry.group_id] = entry.group.name

    res = []
    for k, v in organizations.items():
        res.append({
            'id': k,
            'name': v,
            'ontime_entries': good_entries.get(k, 0),
            'late_entries': late_entries.get(k, 0),
            'no_entries': no_entries.get(k, 0),
        })
    return res

@side_effect_free
def inventory_entry_list_for_user(context, data_dict):
    # TODO @palcu: DRY the code below from organization_list_for_user
    model = context['model']
    user = context['user']

    check_access('organization_list_for_user', context, data_dict)
    sysadmin = authz.is_sysadmin(user)

    orgs_q = model.Session.query(InventoryEntry).join(model.Group) \
        .filter(model.Group.is_organization == True) \
        .filter(model.Group.state == 'active')

    if not sysadmin:
        # for non-Sysadmins check they have the required permission

        # NB 'edit_group' doesn't exist so by default this action returns just
        # orgs with admin role
        permission = data_dict.get('permission', 'edit_group')

        roles = authz.get_roles_with_permission(permission)

        if not roles:
            return []
        user_id = authz.get_user_id_for_username(user, allow_none=True)
        if not user_id:
            return []

        q = model.Session.query(model.Member, model.Group) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.in_(roles)) \
            .filter(model.Member.table_id == user_id) \
            .filter(model.Member.state == 'active') \
            .join(model.Group)

        group_ids = set()
        roles_that_cascade = \
            authz.check_config_permission('roles_that_cascade_to_sub_groups')
        for member, group in q.all():
            if member.capacity in roles_that_cascade:
                group_ids |= set([
                    grp_tuple[0] for grp_tuple
                    in group.get_children_group_hierarchy(type='organization')
                    ])
            group_ids.add(group.id)

        if not group_ids:
            return []

        orgs_q = orgs_q.filter(model.Group.id.in_(group_ids))

    return [table_dictize(obj, context) for obj in orgs_q.all()]


def inventory_entry_create(context, data_dict):
    model = context['model']
    schema = context['schema']
    session = context['session']

    organization = model.Group.get(context['organization_name'])
    data_dict['group_id'] = organization.id
    # TODO @palcu: fix this
    data_dict['is_recurring'] = (data_dict['recurring_interval'] != '0')

    data, errors = navl_validate(data_dict, schema, context)

    if errors:
        session.rollback()
        raise ValidationError(errors)

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


@side_effect_free
def inventory_entry_show(context, data_dict):
    model = context['model']
    inventory_entry = model.Session.query(InventoryEntry).get(data_dict['id'])
    return table_dictize(inventory_entry, context)


def inventory_entry_update(context, data_dict):
    # TODO @palcu: DRY this w/ inventory_entry_create
    model = context['model']
    schema = context['schema']
    session = context['session']

    organization = model.Group.get(context['organization_name'])
    data_dict['group_id'] = organization.id
    data_dict['is_recurring'] = (data_dict['recurring_interval'] != '0')

    data, errors = navl_validate(data_dict, schema, context)

    if errors:
        session.rollback()
        raise ValidationError(errors)

    obj = table_dict_save(data_dict, InventoryEntry, context)
    model.repo.commit()

    return table_dictize(obj, context)
