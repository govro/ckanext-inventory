import ckan.lib.helpers as h
from ckan.plugins.toolkit import (
    check_access, side_effect_free, ObjectNotFound, get_or_bust, _)
from ckan.lib.dictization import model_dictize
from ckan.lib.mailer import send_reset_link


@side_effect_free
def pending_user_list(context, data_dict):
    check_access('sysadmin', context, {})

    model = context['model']
    query = model.Session.query(model.User) \
                 .filter_by(state=model.State.PENDING)

    users_list = []

    for user in query.all():
        groups = user.get_groups()
        if groups:
            result_dict = model_dictize.user_dictize(user, context)
            result_dict['group_name'] = user.get_groups()[0].title
            users_list.append(result_dict)

    return users_list


def activate_user(context, data_dict):
    check_access('sysadmin', context, {})

    model = context['model']
    id = get_or_bust(data_dict, 'id')

    user_obj = model.User.get(id)
    if not user_obj:
        raise ObjectNotFound('User was not found')

    user_obj.activate()
    user_obj.save()
    try:
        send_reset_link(user_obj)
    except Exception, e:
        h.flash_error(_('Could not send reset link: %s') % unicode(e))


@side_effect_free
def organization_by_inventory_id(context, data_dict):
    model = context['model']
    id = get_or_bust(data_dict, 'id')

    group_extra = model.meta.Session.query(model.GroupExtra) \
                       .filter_by(key='inventory_organization_id') \
                       .filter_by(value=id).first()
    if group_extra is None:
        raise ObjectNotFound('No GroupExtra with specificied inventory id')

    organization = model.meta.Session.query(model.Group) \
                        .filter_by(id=group_extra.group_id).first()
    if organization is None:
        raise ObjectNotFound('No organization with specificied inventory id')

    return model_dictize.group_dictize(organization, context)
