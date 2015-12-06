"use strict";

// TODO @palcu: translate these

ckan.module('inventory', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/)
      this.el.on('click', this._onClick)
    },

    _onClick: function(event) {
      event.preventDefault();

      var inventory_organization_id = $('#field-inventory_organization_id').val()
      var $inventory_message_neutral = $('.inventory-message-neutral')
      var $inventory_message_negative = $('.inventory-message-negative')
      var $inventory_message_positive = $('.inventory-message-positive')

      this.sandbox.ajax({
        url: '/api/3/action/inventory_organization_show',
        data: {inventory_organization_id: inventory_organization_id},
        success: function(data) {
          $inventory_message_neutral.addClass('hide')
          $inventory_message_negative.addClass('hide')
          $inventory_message_positive.removeClass('hide')

          var $inventory_organization_name = $('.inventory-organization-name')
          $inventory_organization_name.html(data.result.title)
        }.bind(this),
        error: function(data) {
          $inventory_message_neutral.addClass('hide')
          $inventory_message_positive.addClass('hide')
          $inventory_message_negative.removeClass('hide')
        }.bind(this)
      })
    }
  };
});
