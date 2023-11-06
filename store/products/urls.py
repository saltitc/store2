from django.urls import path

from .views import IndexView, ProductsListView, cart_add, cart_remove

app_name = "products"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products"),
    path("baskets/add/<int:product_id>/", cart_add, name="cart_add"),
    path("baskets/remove/<int:cart_item_id>/", cart_remove, name="cart_remove"),
]
