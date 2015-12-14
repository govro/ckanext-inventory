from ckan.lib.navl.validators import ignore_empty, not_empty
from ckan.logic.validators import (
    name_validator, boolean_validator, natural_number_validator, isodate,
    group_id_exists)


def default_inventory_entry_schema():
    schema = {
        'id': [unicode, ignore_empty],
        'title': [unicode, not_empty],
        'group_id': [group_id_exists],
        'is_recurring': [boolean_validator],
        'recurring_interval': [natural_number_validator],
        'last_added_dataset_timestamp': [isodate],
    }
    return schema


def default_inventory_entry_schema_create():
    schema = {
        'title': [unicode, not_empty],
        'recurring_interval': [natural_number_validator],
    }
    return schema
