from ckan.plugins.toolkit import (
    BaseController, c, check_access, NotAuthorized, abort, get_action, render,
    request, redirect_to)
from ckan import model
from ckan.controllers.organization import OrganizationController
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic

unflatten = dictization_functions.unflatten
ValidationError = logic.ValidationError


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

    def new(self, data=None, errors=None, error_summary=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author,
                   'organization_name': c.organization_name,
                   'save': 'save' in request.params}

        if context['save']:
            return self._save_new(context)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.form = render('inventory/entry/new_entry_form.html', extra_vars=vars)
        return render('inventory/entry/new.html')

    def edit(self):
        return render('inventory/entry/edit.html')

    def _save_new(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            logic.get_action('inventory_entry_create')(context, data_dict)
            redirect_to('inventory_entry',
                        organization_name=c.organization_name)

        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)
