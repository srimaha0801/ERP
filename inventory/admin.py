from django.contrib import admin
from .models import  Branch,Product,Stock,StockTransfer

admin.site.register(Branch)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(StockTransfer)