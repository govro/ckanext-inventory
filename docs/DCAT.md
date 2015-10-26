# Data Catalog Vocabulary (DCAT)

* [Specification](http://www.w3.org/TR/vocab-dcat/)

## How are periods specified

In [DCAT][0] they are specified by a start and an end date, like this
[example][1]. We will support just a recurring interval in days set on every
`InventoryItem`, the start date will be the date a new dataset in that
InventoryItem was added and the end date will be the start date plus the
recurring interval.

[0]: http://www.w3.org/TR/vocab-dcat/#Property:dataset_temporal
[1]: https://github.com/ckan/ckanext-dcat/blob/156ef8cadf288228630581d3302c5522d81f27d1/ckanext/dcat/tests/test_base_profile.py#L156-L163
