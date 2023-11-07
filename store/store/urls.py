from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from orders.views import stripe_webhook_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls", namespace="products")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("users/", include("users.urls", namespace="users")),
    path("webhook/stripe/", stripe_webhook_view, name="stripe_webhook"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
