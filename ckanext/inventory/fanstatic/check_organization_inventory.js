"use strict";

// TODO @palcu: translate these

ckan.module('inventory', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/)
      this.el.on('click', this._onClick)

      var $inventory_message = $('.inventory-message')
      $inventory_message.addClass('alert')
      $inventory_message.html('<p>Verifica organizatia inainte de a trimite formularul.</p>')
    },

    _onClick: function(event) {
      event.preventDefault();

      var inventory_organization_id = $('#field-inventory_organization_id').val()
      var $inventory_message = $('.inventory-message')

      this.sandbox.ajax({
        url: '/api/3/action/inventory_organization_show',
        data: {inventory_organization_id: inventory_organization_id},
        success: function(data) {
          $inventory_message.removeClass('alert-error')
          $inventory_message.addClass('alert-success')
          var message = '<p>Vei fi adaugat in organizatia ' + data.result.title + '.</p>'
          $inventory_message.html(message)
        }.bind(this),
        error: function(data) {
          $inventory_message.addClass('alert-error')
          $inventory_message.removeClass('alert-success')
          $inventory_message.html('<p>Nicio organizatie nu a fost gasita.</p>')
        }.bind(this)
      })
    }
  };
});
