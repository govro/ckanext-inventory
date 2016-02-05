import unicodecsv
from cStringIO import StringIO

from ckan.plugins.toolkit import (
    c, check_access, NotAuthorized, abort, get_action, render, request,
    redirect_to, _, response)

from ckan import model
from ckan.controllers.organization import OrganizationController
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic

from ckanext.inventory.logic.schema import default_inventory_entry_schema_create

unflatten = dictization_functions.unflatten
ValidationError = logic.ValidationError
NotFound = logic.NotFound


class InventoryEntryController(OrganizationController):
    def __before__(self, action, **params):
        super(InventoryEntryController, self).__before__(action, **params)
        context = {'user': c.user, 'auth_user_obj': c.userobj}

        # This is almost the same as organization/{name}/about.
        organization_name = params['organization_name']
        group_type = self._ensure_controller_matches_group_type(organization_name)
        context = {'model': model, 'user': c.user, 'session': model.Session}
        c.group_dict = self._get_group_dict(organization_name)
        group_type = c.group_dict['type']
        self._setup_template_variables(context, {'id': organization_name},
                                       group_type=group_type)

        try:
            # TODO @palcu: fix this
            check_access('user_show', context, {})
        except NotAuthorized:
            abort(401, 'You need to have an account.')

    def index(self, organization_name):
        context = {'model': model, 'user': c.user, 'session': model.Session}
        inventory_entries = get_action('inventory_entry_list')(
            context, {'name': organization_name})
        c.inventory_entries = [x for x in inventory_entries if x['is_recurring']]
        c.inventory_archived_entries = [
            x for x in inventory_entries if not x['is_recurring']]
        return render('inventory/entry/index.html',
                      extra_vars={'group_type': self._ensure_controller_matches_group_type(organization_name)})

    def new(self, data=None, errors=None, error_summary=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author,
                   'organization_name': c.organization_name,
                   'save': 'save' in request.params,
                   'schema': default_inventory_entry_schema_create()}

        if context['save'] and not data:
            return self._save_new(context)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary,
                'action': 'new'}

        c.form = render('inventory/entry/inventory_entry_form.html',
                        extra_vars=vars)
        return render('inventory/entry/new.html')

    def edit(self, organization_name, inventory_entry_id, data=None,
             errors=None, error_summary=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author,
                   'organization_name': c.organization_name,
                   'save': 'save' in request.params,
                   'schema': default_inventory_entry_schema_create()}

        if context['save'] and not data:
            return self._save_edit(inventory_entry_id, context)

        try:
            old_data = get_action('inventory_entry_show')(
                context, {'id': inventory_entry_id})
            data = data or old_data
        except NotFound:
            abort(404, _('Inventory Entry not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read inventory entry'))

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary,
                'action': 'edit'}

        c.form = render('inventory/entry/inventory_entry_form.html', extra_vars=vars)

        return render('inventory/entry/edit.html')

    def read(self, organization_name, inventory_entry_id):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author}

        c.entries = get_action('inventory_entry_list_items')(
            context, {'inventory_entry_id': inventory_entry_id})
        return render('inventory/entry/read.html',
                      extra_vars={'group_type': self._ensure_controller_matches_group_type(organization_name)})

    def bulk_new(self, data=None, errors=None, error_summary=None):
        context = {'model': model,
                   'session': model.Session,
                   'user': c.user or c.author,
                   'organization_name': c.organization_name,
                   'save': 'save' in request.params ,
                   'schema': default_inventory_entry_schema_create()}

        if context['save'] and not data:
            return self._save_new_bulk(context)

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.form = render('inventory/entry/snippets/inventory_entry_bulk_form.html',
                        extra_vars=vars)
        return render('inventory/entry/bulk_new.html')

    def csv(self, organization_name):
        # TODO @palcu: DRY code with get_inventory_entries_csv
        context = {'user': c.user}
        entries = get_action('inventory_entry_csv_single')(context, {'name': organization_name})

        response.headers['Content-Type'] = 'text/csv'
        s = StringIO()
        writer = unicodecsv.writer(s)

        writer.writerow(['nume_intrare_de_inventar', 'interval_de_recurenta', 'ultima_actualizare'])
        for entry in entries:
            writer.writerow(entry)

        return s.getvalue()

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

    def _save_new_bulk(self, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            logic.get_action('inventory_entry_bulk_create')(context, data_dict)
            h.flash_success(_('Entries have been successfully added.'))
            redirect_to('inventory_entry_bulk_new',
                        organization_name=c.organization_name)

        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.bulk_new(data_dict, errors, error_summary)

    def _save_edit(self, id, context):
        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            data_dict['id'] = id
            logic.get_action('inventory_entry_update')(context, data_dict)
            redirect_to('inventory_entry',
                        organization_name=c.organization_name)

        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)
