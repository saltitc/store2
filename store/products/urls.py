from django.urls import path

from .views import (
    IndexView,
    ProductsListView,
    ProductDetailView,
    RateProductView,
    CartView,
    cart_add,
    cart_remove,
    update_cart_item_quantity,
)

app_name = "products"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="detail"),
    path("product/rate/<int:pk>", RateProductView.as_view(), name="rate"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/<int:product_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:cart_item_id>/", cart_remove, name="cart_remove"),
    path("update_quantity/", update_cart_item_quantity, name="update_quantity"),
]
