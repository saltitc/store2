from products.models import CartItem


def cart_items(request):
    user = request.user
    return {
        "cart_items": CartItem.objects.filter(user=user) if user.is_authenticated else []
    }
