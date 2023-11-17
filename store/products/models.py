import stripe
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY


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
    category = models.ForeignKey(to=ProductCategory, null=True, on_delete=models.SET_NULL)
    average_rating = models.PositiveSmallIntegerField(default=0, null=True)
    stripe_product_price_id = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"Продукт: {self.title} | Категория: {self.category.name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price["id"]
        super().save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.title)
        stripe_product_price = stripe.Price.create(
            product=stripe_product["id"],
            unit_amount=round(self.price * 100),
            currency="rub",
        )
        return stripe_product_price

    def update_average_rating(self):
        average_rating = Rating.objects.filter(product=self.id).aggregate(models.Avg("rating"))["rating__avg"]
        self.average_rating = average_rating
        self.save()


class CartQuerySet(models.QuerySet):
    def get_total_cart_cost(self):
        return sum(cart_item.get_item_cost() for cart_item in self)

    def total_amount(self):
        return sum(cart_item.quantity for cart_item in self)

    def stripe_products(self):
        line_items = []
        for cart_item in self:
            item = {
                "price": cart_item.product.stripe_product_price_id,
                "quantity": cart_item.quantity,
            }
            line_items.append(item)
        return line_items


class CartItem(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    objects = CartQuerySet.as_manager()

    def __str__(self):
        return f"{self.product.title} в корзине пользователя @{self.user.username}"

    def get_item_cost(self):
        return self.product.price * self.quantity

    def de_json(self):
        cart_item = {
            "product_title": self.product.title,
            "quantity": self.quantity,
            "price": float(self.product.price),
            "sum": float(self.get_item_cost()),
        }
        return cart_item


class Rating(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("user", "product")


class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    class Meta:
        unique_together = ["user", "product"]
