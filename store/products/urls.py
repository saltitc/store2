from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import IndexView, ProductsListView

app_name = 'products'

urlpatterns = [
     path('', IndexView.as_view(), name='index'),
     path('products/', ProductsListView.as_view(), name='products')
]