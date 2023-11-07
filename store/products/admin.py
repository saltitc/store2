from django.contrib import admin

from .models import Product, ProductCategory, CartItem

admin.site.register(ProductCategory)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "amount", "category", "rating")
    fields = (
        "title",
        "description",
        ("price", "amount"),
        "image",
        "stripe_product_price_id",
        "category",
        "rating",
    )
    readonly_fields = ("description",)
    search_fields = ("title",)
    ordering = ("-title",)


class CartItemAdmin(admin.TabularInline):
    model = CartItem
    fields = ("product", "quantity")
    extra = 0
