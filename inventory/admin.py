from django.contrib import admin
from .models import  Branch,Product,Stock,StockTransfer

admin.site.urls(Branch)
admin.site.urls(Product)
admin.site.urls(Stock)
admin.site.urls(StockTransfer)