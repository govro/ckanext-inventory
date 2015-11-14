from ckan.plugins.toolkit import (
    BaseController, c, check_access, NotAuthorized, abort, get_action, render)

class InventoryEntryController(BaseController):
    def __before__(self, action, **params):
        super(InventoryEntryController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}
        try:
            # TODO @palcu: fix this
            check_access('user_show', context, {})
        except NotAuthorized:
            abort(401, 'You need to have an account.')

    def index(self, organization_name):
        context = {'user': c.user}
        c.entries = get_action('inventory_entry_list')\
            (context, {'name': organization_name})
        return render('inventory/entry/index.html')
