from ckan.plugins.toolkit import BaseController, render


class InventoryController(BaseController):
    def index(self):
        return render('index.html')
