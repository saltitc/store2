from django.urls import path

from .views import (CartManageView, CartView,  # update_cart_item_quantity,
                    IndexView, ProductDetailView, ProductsListView,
                    RateProductView, WishlistManageView, WishlistView)

app_name = "products"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("products/", ProductsListView.as_view(), name="products"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="detail"),
    path("product/rate/<int:pk>", RateProductView.as_view(), name="rate"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/manage", WishlistManageView.as_view(), name="wishlist_manage"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/manage/", CartManageView.as_view(), name="cart_manage"),
    path("cart/manage/<int:product_id>/", CartManageView.as_view(), name="remove_from_cart"),
]
