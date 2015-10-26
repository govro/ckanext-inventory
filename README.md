# ckanext-inventory

CKAN Extension for receiving dataset inventories from organizations and tracking
their status.

## Goal

The [PSI Directive][directive] was transposed as a law and will arrive in
the Romanian Parliament. Every institution will have to provide an inventory
with their datasets and their recurring interval.

This extension will help with the registering of organizations, adding and
editing datasets in the inventory and monitoring if they are updated in the
specified timeline

[directive]: http://ec.europa.eu/digital-agenda/en/european-legislation-reuse-public-sector-information

## Requirements

This extension is written for CKAN v2.4.2.

## Installation

To install ckanext-inventory:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-inventory Python package into your virtual environment::

     pip install ckanext-inventory

3. Add ``inventory`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

## Development Installation

To install ckanext-inventory for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/govro/ckanext-inventory.git
    cd ckanext-inventory
    python setup.py develop
    pip install -r dev-requirements.txt
