from ckan.controllers.user import UserController

from ckan import model
import ckan.authz as authz
import ckan.lib.base as base
import ckan.lib.captcha as captcha
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
from ckan.plugins.toolkit import _, c, check_access
from ckan.common import request

abort = base.abort
render = base.render
DataError = dictization_functions.DataError
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
unflatten = dictization_functions.unflatten


# TODO @palcu: do some kind of inheritance here
class InventoryUserController(UserController):
    def new(self, data=None, errors=None, error_summary=None):
        '''GET to display a form for registering a new user.
           or POST the form data to actually do the user registration.
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'auth_user_obj': c.userobj,
                   'schema': self._new_form_to_db_schema(),
                   'save': 'save' in request.params}

        try:
            check_access('user_create', context)
        except NotAuthorized:
            abort(401, _('Unauthorized to create a user'))

        if context['save'] and not data:
            return self._save_new(context)

        if c.user and not data:
            # #1799 Don't offer the registration form if already logged in
            return render('user/logout_first.html')

        data = data or {}
        errors = errors or {}
        error_summary = error_summary or {}
        c.inventory_organizations = get_action('inventory_organizations_show')(
            context, {})
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}

        c.is_sysadmin = authz.is_sysadmin(c.user)
        c.form = render(self.new_user_form, extra_vars=vars)
        return render('user/new.html')


    def _save_new(self, context):
        model = context['model']
        context['ignore_auth'] = True

        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')
            captcha.check_recaptcha(request)

            organization = get_action('inventory_organization_by_inventory_id')(
                context, {'id': data_dict['inventory_organization_id']})
            user = get_action('user_create')(context, data_dict)

            data_dict = {
                'id': organization['id'],
                'role': 'editor',
                'username': user['name']
            }
            logic.get_action('organization_member_create')(context, data_dict)
        except NotAuthorized:
            abort(401, _('Unauthorized to create user %s') % '')
        except NotFound, e:
            abort(404, _('User or organization not found'))
        except DataError:
            abort(400, _(u'Integrity Error'))
        except captcha.CaptchaError:
            error_msg = _(u'Bad Captcha. Please try again.')
            h.flash_error(error_msg)
            return self.new(data_dict)
        except ValidationError, e:
            errors = e.error_dict
            error_summary = e.error_summary
            return self.new(data_dict, errors, error_summary)

        model_user = model.Session.query(model.User) \
                          .filter_by(email=user['email']).first()
        model_user.set_pending()
        model_user.save()

        h.flash_success('Your account registration will be reviewed.')
        return render('home/index.html')
