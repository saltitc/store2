from django.db import models

from users.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products_images")
    category = models.ForeignKey(
        to=ProductCategory, null=True, on_delete=models.SET_NULL
    )
    rating = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"Продукт: {self.title} | Категория: {self.category.name}"


class CartQuerySet(models.QuerySet):
    def get_total_cart_cost(self):
        return sum(cart_item.get_item_cost() for cart_item in self)

    def total_amount(self):
        return sum(cart_item.quantity for cart_item in self)


class CartItem(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    objects = CartQuerySet.as_manager()

    def __str__(self):
        return f"{self.product.title} в корзине пользователя @{self.user.username}"

    def get_item_cost(self):
        return self.product.price * self.quantity
    