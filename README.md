# ckanext-inventory

[![Build Status](https://travis-ci.org/govro/ckanext-inventory.svg?branch=master)](https://travis-ci.org/govro/ckanext-inventory) [![Coverage Status](https://coveralls.io/repos/govro/ckanext-inventory/badge.svg?branch=master&service=github)](https://coveralls.io/github/govro/ckanext-inventory?branch=master)

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

This extension is written for CKAN v2.5.3.

## Installation

To install ckanext-inventory:

1. Activate your CKAN virtual environment, for example::

```
. /usr/lib/ckan/default/bin/activate
```

2. Clone and install the ckanext-inventory Python package into your virtual environment:

```
python setup.py develop
```

3. Add `inventory inventoryfix` to the `ckan.plugins` setting in your CKAN
   config file.

4. Restart CKAN.
