from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from common.views import TitleMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from .models import CartItem, Product, ProductCategory



class IndexView(TitleMixin, TemplateView):
    template_name = "products/index.html"
    title = "Главная страница"


class ProductsListView(TitleMixin, ListView):
    model = Product
    template_name = "products/products.html"
    context_object_name = "products"
    paginate_by = 3
    title = "Каталог"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsListView, self).get_context_data()
        context["categories"] = ProductCategory.objects.all()
        return context


@login_required
def cart_add(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_items = CartItem.objects.filter(user=request.user, product=product)

    if not cart_items.exists():
        CartItem.objects.create(user=request.user, product=product, quantity=1)
    else:
        cart_item = cart_items.first()
        cart_item.quantity += 1
        cart_item.save()

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def cart_remove(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
