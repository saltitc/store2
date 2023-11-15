from django.contrib import admin

from .models import Product, ProductCategory, CartItem, Rating

admin.site.register(ProductCategory)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "amount", "category", "average_rating")
    fields = (
        "title",
        "description",
        ("price", "amount"),
        "image",
        "stripe_product_price_id",
        "category",
        "average_rating",
    )
    readonly_fields = ("description",)
    search_fields = ("title",)
    ordering = ("-title",)


class CartItemAdmin(admin.TabularInline):
    model = CartItem
    fields = ("product", "quantity")
    extra = 0


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("rating", "user", "product")
    fields = ("rating", "user", "product")
    readonly_fields = ("rating", "user", "product")
    search_fields = ("rating",)
    ordering = ("-rating",)
