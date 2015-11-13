from ckan.plugins.toolkit import (BaseController, render, check_access,
        NotAuthorized, abort, get_action, c)


class InventoryController(BaseController):
    def __before__(self, action, **params):
        super(InventoryController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}
        try:
            check_access('sysadmin', context, {})
        except NotAuthorized:
            # TODO @palcu: you should only be in a special group, not be sysadmin
            abort(401, _('Need to be system administrator to check inventory'))

    def index(self):
        context = {'user': c.user}
        users_list = get_action('inventory_pending_user_list')(context)
        c.users = users_list
        return render('inventory/index.html')
