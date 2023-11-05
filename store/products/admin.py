from django.contrib import admin

from .models import Product, ProductCategory

admin.site.register(ProductCategory)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'amount', 'category')
    fields = ('title', 'description', ('price', 'amount'), 'image', 'category')
    readonly_fields = ('description',)
    search_fields = ('title',)
    ordering = ('-title',)