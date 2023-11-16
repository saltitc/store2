from products.models import CartItem


def cart_items(request):
    user = request.user
    return {"cart_items": CartItem.objects.filter(user=user) if user.is_authenticated else []}


def get_cart_items_count(request):
    user = request.user
    count = CartItem.objects.filter(user=user.id).total_amount()
    data = {"count_of_cart_items": count}
    return data
