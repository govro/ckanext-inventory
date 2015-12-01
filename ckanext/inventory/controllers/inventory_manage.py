from ckan.plugins.toolkit import (
    BaseController, c, check_access, NotAuthorized, abort, get_action, render)


class InventoryManageController(BaseController):
    def __before__(self, action, **params):
        super(InventoryManageController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}
        try:
            check_access('user_show', context, {})
        except NotAuthorized:
            abort(401, 'You need to have an account.')

    def index(self):
        context = {'user': c.user}
        c.organizations = get_action('organization_list_for_user')(
            context, {'permission': 'create_dataset'})
        return render('inventory/manage/index.html')
