import ckan.lib.helpers as h
from ckan.plugins.toolkit import (
    BaseController, render, check_access, NotAuthorized, abort, get_action, c,
    redirect_to, ValidationError)


class InventoryController(BaseController):
    def __before__(self, action, **params):
        super(InventoryController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}
        try:
            check_access('sysadmin', context, {})
        except NotAuthorized:
            # TODO @palcu: you should only be in a special group, not be sysadmin
            abort(401, 'Need to be system administrator to check inventory')

    def index(self):
        context = {'user': c.user}
        c.users = get_action('inventory_pending_user_list')(context)
        return render('inventory/index.html')

    def activate_user(self, user_id):
        context = {'user': c.user}
        data_dict = {'id': user_id}

        try:
            get_action('inventory_activate_user')(context, data_dict)
            h.flash_success('Account has been activated.')
        except ValidationError as e:
            error_message = (e.message or e.error_summary
                             or e.error_dict)
            h.flash_error(error_message)
        except NotAuthorized as e:
            h.flash_error(e.message)

        return redirect_to('/inventory')
