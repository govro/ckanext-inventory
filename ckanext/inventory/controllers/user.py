from ckan.controllers.user import UserController

import ckan.lib.base as base
import ckan.lib.captcha as captcha
import ckan.lib.helpers as h
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic
from ckan.common import c, request, response

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

        try:
            data_dict = logic.clean_dict(unflatten(
                logic.tuplize_dict(logic.parse_params(request.params))))
            context['message'] = data_dict.get('log_message', '')
            captcha.check_recaptcha(request)

            inventory_organization_id = data_dict.pop('inventory_organization_id')
            user = get_action('user_create')(context, data_dict)

            self._add_user_to_organization(model, user,
                                           inventory_organization_id)
        except NotAuthorized:
            abort(401, _('Unauthorized to create user %s') % '')
        except NotFound, e:
            abort(404, _('User not found'))
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

        h.flash_success('Your account registration will be reviewed.')
        return render('home/index.html')

    def _add_user_to_organization(self, model, user, inventory_organization_id):
        rev = model.repo.new_revision()
        rev.author = user['name']

        # TODO @palcu: Do error handling if inventory_organization_id does not
        # exist
        organization_extra = model.meta.Session.query(model.GroupExtra) \
                                  .filter_by(key='inventory_organization_id') \
                                  .filter_by(value=inventory_organization_id).first()

        member = model.Member(table_name='user',
                              table_id=user['id'],
                              group_id=organization_extra.group_id,
                              state='active',
                              capacity='editor')
        model.Session.add(member)
        model.repo.commit()
