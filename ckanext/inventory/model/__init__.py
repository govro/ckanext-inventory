"""Examples taken from:
https://github.com/ckan/ckanext-harvest/blob/master/ckanext/harvest/model/__init__.py
https://github.com/ckan/ckanext-spatial/blob/master/ckanext/spatial/model/package_extent.py
"""

# TODO @palcu: split this file into it's own modules
# However those global variables are fucking shit

from logging import getLogger

from sqlalchemy import Table, Column, ForeignKey, types
from sqlalchemy.orm import backref, relation

from ckan import model
from ckan.model.meta import metadata, mapper
from ckan.model.types import make_uuid
from ckan.model.domain_object import DomainObject


log = getLogger(__name__)

inventory_entry_table = None
inventory_item_table = None


class InventoryDomainObject(DomainObject):
    pass


class InventoryEntry(InventoryDomainObject):
    pass


class InventoryItem(InventoryDomainObject):
    pass


def model_setup():
    if inventory_entry_table is None:
        define_inventory_tables()
        log.debug('Inventory tables are defined in memory')

    if not inventory_entry_table.exists():
        inventory_entry_table.create()
        inventory_item_table.create()
        log.debug('Inventory tables created')
    else:
        log.debug('Inventory tables already exist')
        # Future migrations go here


def define_inventory_tables():
    define_inventory_entry_table()
    define_inventory_item_table()


def define_inventory_entry_table():
    global inventory_entry_table
    inventory_entry_table = Table(
        'inventory_entry',
        metadata,
        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        Column('title', types.UnicodeText, default=u''),
        Column('group_id', types.UnicodeText, ForeignKey('group.id')),
        Column('is_recurring', types.Boolean, default=False),
        Column('recurring_interval', types.Integer, default=0),
        Column('last_added_dataset_timestamp', types.DateTime)
    )
    mapper(InventoryEntry, inventory_entry_table, properties={
        'group': relation(model.Group, lazy=True, backref=u'inventory_entries')
    })


def define_inventory_item_table():
    global inventory_item_table
    inventory_item_table = Table(
        'inventory_item',
        metadata,
        Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
        Column('inventory_entry_id',
               types.UnicodeText,
               ForeignKey('inventory_entry.id')),
        Column('package_id', types.UnicodeText, ForeignKey('package.id'))
    )
    mapper(InventoryItem, inventory_item_table, properties={
        'inventory_entry': relation(InventoryEntry,
                                    lazy=True,
                                    backref=backref('inventory_items',
                                                    cascade='all,delete-orphan')),
        'package_entry': relation(model.Package,
                                  lazy=True,
                                  backref=backref('inventory_items',
                                                  cascade='all,delete-orphan')),
    })
