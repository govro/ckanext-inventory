from ckan.plugins.toolkit import (
    BaseController, c, check_access, NotAuthorized, abort, get_action, render)
from ckan import model
from ckan.controllers.organization import OrganizationController


class InventoryEntryController(OrganizationController):
    def __before__(self, action, **params):
        super(InventoryEntryController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}
        try:
            # TODO @palcu: fix this
            check_access('user_show', context, {})
        except NotAuthorized:
            abort(401, 'You need to have an account.')

    def index(self, organization_name):
        '''This is almost the same as organization/{name}/about.'''
        group_type = self._ensure_controller_matches_group_type(organization_name)
        context = {'model': model, 'user': c.user, 'session': model.Session}
        c.group_dict = self._get_group_dict(organization_name)
        group_type = c.group_dict['type']
        self._setup_template_variables(context, {'id': organization_name},
                                       group_type=group_type)
        c.entries = get_action('inventory_entry_list')\
            (context, {'name': organization_name})
        return render('inventory/entry/index.html',
                      extra_vars={'group_type': group_type})
