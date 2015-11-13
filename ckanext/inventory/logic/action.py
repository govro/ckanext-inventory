from ckan.plugins.toolkit import check_access, side_effect_free
from ckan.lib.dictization import model_dictize

@side_effect_free
def pending_user_list(context, data_dict):
    check_access('sysadmin', context, {})

    model = context['model']
    query = model.Session.query(model.User).filter_by(
            state=model.State.PENDING)

    users_list = []

    for user in query.all():
        result_dict = model_dictize.user_dictize(user, context)
        users_list.append(result_dict)

    return users_list
