import ckan.lib.mailer as mailer


def send_activate_user_notification():
    # TODO @palcu: remove hardcoded value
    recipient_name = 'CKAN Gov Admin'
    recipient_email = 'alex.palcuie+activate-ckan@gmail.com'
    subject = 'Activate CKAN User'
    # TODO @palcu: i18n and remove hardcoded stuff
    body = "Please go an activate the new users: {0}.".format('http://data.local.gov.ro:5000/inventory/admin')
    mailer.mail_recipient(recipient_name, recipient_email, subject, body)
