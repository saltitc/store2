from django.contrib.auth import get_user_model
from django.db import models

from products.models import CartItem

User = get_user_model()


# Create your models here.
class Order(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    STATUSES = (
        (CREATED, "Создан"),
        (PAID, "Оплачен"),
        (ON_WAY, "В пути"),
        (DELIVERED, "Доставлен"),
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=256)
    address = models.CharField(max_length=256)
    cart_history = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)
    initiator = models.ForeignKey(to=User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(default=CREATED, choices=STATUSES)

    def __str__(self):
        return f"Заказ #{self.id}. {self.first_name} {self.last_name}"

    def update_after_payment(self):
        cart_items = CartItem.objects.filter(user=self.initiator)
        self.status = self.PAID
        self.cart_history = {
            "purchased_items": [cart_item.de_json() for cart_item in cart_items],
            "total_cost": float(cart_items.get_total_cart_cost()),
        }
        cart_items.delete()
        self.save()
