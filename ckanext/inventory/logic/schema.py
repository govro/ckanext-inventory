from ckan.lib.navl.validators import ignore_empty, not_empty
from ckan.logic.validators import (
    name_validator, boolean_validator, is_positive_integer, isodate,
    group_id_exists)


def default_inventory_entry_schema():
    schema = {
        'id': [ignore_empty, unicode],
        'title': [not_empty, unicode, name_validator],
        'group_id': [group_id_exists],
        'is_recurring': [boolean_validator],
        'recurring_interval': [is_positive_integer],
        'last_added_dataset_timestamp': [isodate],
    }
    return schema
