from ckan.plugins.toolkit import BaseController, render


class InventoryController(BaseController):

    def index():
        return render('index.html')
