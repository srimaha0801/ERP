from django.urls import path
from .views import AddBranchView,AddProductView,AddStockView,CreateStockTransferView,ApproveTransferView,StockTransferListView,BranchStockView

urlpatterns = [
    path('/branch/add/', AddBranchView.as_view()),
    path('/product/add/', AddProductView.as_view()),
    path('/stock/add/', AddStockView.as_view()),
    path('/branch/<int:pk>/stock-summary/', BranchStockView.as_view()),
    path('/transfers/create/', CreateStockTransferView.as_view()),
    path('/transfers/<uuid:pk>/approve/', ApproveTransferView.as_view()),
    path('/transfers/', StockTransferListView.as_view()),

]