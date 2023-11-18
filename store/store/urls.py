from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from orders.views import stripe_webhook_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("products.urls", namespace="products")),
    path("orders/", include("orders.urls", namespace="orders")),
    path("users/", include("users.urls", namespace="users")),
    path("webhook/stripe/", stripe_webhook_view, name="stripe_webhook"),
    path("accounts/", include("allauth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
