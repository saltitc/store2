from products.models import CartItem, FavoriteProduct


def cart_items(request):
    user = request.user
    if user.is_authenticated:
        items = CartItem.objects.filter(user=user)
        count = items.total_amount()
        return {"cart_items": items, "count_of_cart_items": count, "cart_items_ids": set(items.values_list("product__id", flat=True))}
    return {"cart_items": [], "count_of_cart_items": 0, "cart_items_ids": []}


def wishlist_items(request):
    user = request.user
    items = FavoriteProduct.objects.filter(user=user.id)
    return {
        "wishlist_items": items,
        "wishlist_items_count": items.count(),
        "wishlist_items_ids": set(items.values_list("product__id", flat=True)),
    }
