import random

from ckan.controllers.user import UserController

import ckan.lib.base as base
import ckan.lib.captcha as captcha
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
from ckan.plugins.toolkit import _
from ckan.common import request

abort = base.abort
render = base.render
DataError = dictization_functions.DataError
get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
NotFound = logic.NotFound
ValidationError = logic.ValidationError
unflatten = dictization_functions.unflatten


class InventoryUserController(UserController):
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

            password = str(random.SystemRandom().random())
            data_dict['password1'] = password
            data_dict['password2'] = password
            data_dict['state'] = model.State.PENDING
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

        h.flash_success(_('Your account registration will be reviewed.'))
        return render('home/index.html')
